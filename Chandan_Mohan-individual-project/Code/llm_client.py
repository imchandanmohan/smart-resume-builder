from dotenv import load_dotenv
import os
from fpdf import FPDF
import fitz
import subprocess
from groq import Groq
import openai
import time
from together import Together
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from dotenv import load_dotenv
import random
# Add these to your imports at the top
from requests.exceptions import Timeout, ConnectionError
from openai import APIError  # For OpenAI errors
from groq import APIError as GroqAPIError  # Groq-specific errors

load_dotenv()

# Load API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

from openai import OpenAI


logger = get_logger(__name__)



class LLMClient:
    def __init__(self):
        try:
            # Initialize OpenAI client
            self.openai_api_key = os.environ.get("OPENAI_API_KEY")
            if not self.openai_api_key:
                logger.warning("OPENAI_API_KEY not found in environment variables.")
                raise CustomException("Failed to find OPENAI_API_KEY.")
            # Initialize Groq client
            self.groq_api_key = os.environ.get("GROQ_API_KEY")
            if self.groq_api_key:
                self.groq_client = Groq(api_key=self.groq_api_key)
            else:
                logger.warning("GROQ_API_KEY not found in environment variables.")
                raise CustomException("Failed to find GROQ_API_KEY.")
            
            # Initialize Together client
            self.together_api_key = os.environ.get("TOGETHER_API_KEY")
            if self.together_api_key:
                self.together_client = Together(api_key=self.together_api_key)
            else:
                logger.warning("TOGETHER_API_KEY not found in environment variables.")
                raise CustomException("Failed to find TOGETHER_API_KEY.")
            
            self.max_retries = 3  # or any number you want
            self.retry_delay = 2  # in seconds

            logger.info("LLMClient initialized successfully.")

        except Exception as e:
            logger.exception("Failed to initialize LLM clients.")
            raise CustomException("Failed to initialize LLM clients.", e)


    def _retry_api_call(self, func, *args, **kwargs):
        """
        Enhanced retry mechanism with:
        - Exponential backoff with jitter
        - Selective exception handling
        - Proper exception chaining
        - Configurable status code filtering
        """
        last_exception = None
        retry_wait = self.retry_delay  # Initial delay

        # Define retriable conditions
        retriable_errors = (APIError, Timeout, ConnectionError)
        retriable_status_codes = {429, 500, 502, 503, 504}

        for attempt in range(self.max_retries + 1):  # Includes initial attempt
            try:
                logger.info(f"Attempt {attempt + 1}/{self.max_retries + 1}")
                return func(*args, **kwargs)
                
            except retriable_errors as e:
                last_exception = e
                if hasattr(e, 'response') and e.response.status_code not in retriable_status_codes:
                    logger.warning(f"Non-retriable status code: {e.response.status_code}")
                    break

                logger.warning(f"Retriable error: {str(e)}")
                self._handle_retry_delay(attempt, retry_wait)
                retry_wait *= 2  # Exponential backoff
                retry_wait += random.uniform(0, 1)  # Jitter

            except Exception as e:
                logger.error(f"Non-retriable error: {str(e)}")
                raise  # Re-raise non-retriable exceptions immediately

        logger.error(f"All {self.max_retries} retry attempts failed")
        raise CustomException("API call failed after retries") from last_exception

    def _handle_retry_delay(self, attempt, base_delay):
        """Handle retry delay with logging"""
        sleep_time = base_delay * (2 ** attempt)  # Exponential component
        jitter = random.uniform(0, base_delay)  # Add jitter
        total_sleep = sleep_time + jitter
        
        logger.info(f"Attempt {attempt + 1}: "
                    f"Waiting {total_sleep:.2f}s before retry")
        time.sleep(total_sleep)



    def _get_groq_response(self, prompt, model_name):
        """
        Sends a prompt to the specified Groq LLM model and returns the generated response.

        Parameters:
        prompt (str): The user prompt to send to the model.
        model_name (str): The Groq model name to use.

        Returns:
        str: The generated response text from the model.

        Raises:
        CustomException: If the API call fails or environment variables are not properly set.
        """

        logger.info(f"Groq API call initiated with model: {model_name}")

        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            logger.error("GROQ_API_KEY not found in environment variables.")
            raise CustomException("GROQ_API_KEY not found in environment variables.")

        try:
            client = Groq(api_key=api_key)
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=model_name,
            )
            response_text = chat_completion.choices[0].message.content
            logger.info(f"Groq API call successful. Model: {model_name}")
            return response_text

        except Exception as e:
            logger.exception("Failed to get response from Groq API.")
            raise CustomException("Error during Groq API call.", e)


    def _get_chatgpt_response(self, prompt, model_name):
        """
        Sends a prompt to the specified ChatGPT model and returns the generated response.
        """

        logger.info(f"ChatGPT API call initiated with model: {model_name}")

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment variables.")
            raise CustomException("OPENAI_API_KEY not found in environment variables.")

        try:
            client = OpenAI(api_key=OPENAI_API_KEY)  # ✅ new way
            chat_completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
            response_text = chat_completion.choices[0].message.content
            logger.info(f"ChatGPT API call successful. Model: {model_name}")
            return response_text

        except Exception as e:
            logger.exception("Failed to get response from ChatGPT API.")
            raise CustomException("Error during ChatGPT API call.", e)

    def _get_together_response(self, prompt, model_name):
        """
        Sends a prompt to the specified Together AI model and returns the generated response.
        """

        logger.info(f"Together AI API call initiated with model: {model_name}")

        if not self.together_api_key:
            logger.error("TOGETHER_API_KEY not found in environment variables.")
            raise CustomException("TOGETHER_API_KEY not found in environment variables.")

        try:
            client = Together()  # ✅ No need to manually pass the API key
            chat_completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
            response_text = chat_completion.choices[0].message.content
            logger.info(f"Together AI API call successful. Model: {model_name}")
            return response_text

        except Exception as e:
            logger.exception("Failed to get response from Together AI API.")
            raise CustomException("Error during Together AI call.", e)

        
    def get_llm_response(self, prompt, model_name, vendor="openai"):
        """
        Sends a prompt to the specified LLM vendor and model, returns the generated response.
        """
        vendor = vendor.lower()
        logger.info(f"LLM request initiated. Vendor: {vendor}, Model: {model_name}")

        try:
            if vendor == "openai":
                if not self.openai_api_key:
                    raise CustomException("OPENAI_API_KEY not set.")
                openai.api_key = self.openai_api_key
                response = self._retry_api_call(self._get_chatgpt_response, prompt, model_name)

            elif vendor == "groq":
                if not self.groq_api_key:
                    raise CustomException("GROQ_API_KEY not set.")
                response = self._retry_api_call(self._get_groq_response, prompt, model_name)

            elif vendor == "together":
                if not self.together_api_key:
                    raise CustomException("TOGETHER_API_KEY not set.")
                response = self._retry_api_call(self._get_together_response, prompt, model_name)
            
            else:
                logger.error(f"Unsupported vendor: {vendor}")
                raise CustomException(f"Unsupported vendor: {vendor}")

            # ✅ Now after getting response, log success
            logger.info(f"Successfully fetched LLM response from {vendor} using model {model_name}.")
            
            return response

        except Exception as e:
            logger.exception(f"Failed to get LLM response from {vendor}.")
            raise CustomException(f"Failed to get response from {vendor} LLM.", e)

    

if __name__ == "__main__":
    try:
        # Initialize client
        client = LLMClient()

        # Define a simple test prompt
        prompt = "Tell me a short interesting fact about space."
        model_name_openai = "gpt-3.5-turbo"
        model_name_groq = "llama3-8b-8192"  # Example model
        model_name_together = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"  # Example model

        # Test OpenAI ChatGPT
        try:
            openai_response = client.get_llm_response(prompt, model_name_openai, vendor="openai")
            print("\nOpenAI Response:\n", openai_response)
        except CustomException as e:
            print("\nOpenAI Test Failed:", e)
        
        # Test Groq
        try:
            groq_response = client.get_llm_response(prompt, model_name_groq, vendor="groq")
            print("\nGroq Response:\n", groq_response)
        except CustomException as e:
            print("\nGroq Test Failed:", e)

        # Test Together
        try:
            together_response = client.get_llm_response(prompt, model_name_together, vendor="together")
            print("\nTogether AI Response:\n", together_response)
        except CustomException as e:
            print("\nTogether AI Test Failed:", e)

    except Exception as main_e:
        print("An error occurred while testing:", main_e)

