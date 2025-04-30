# src/extractors/extractor_fusion.py

import json
import os
from utils.llm_client import LLMClient
from src.custom_exception import CustomException
from src.logger import get_logger

# Initialize logger for tracking activities inside this module
logger = get_logger(__name__)

class BaseExtractor:
    """
    BaseExtractor (LLM-powered text-to-JSON extraction)

    This class abstracts the common functionality needed to:
    - Load plain text from a file
    - Query an LLM backend (OpenAI, Groq, Together)
    - Parse LLM output into structured JSON
    - Save JSON output cleanly

    Designed for extensibility: child classes should define their own prompt templates and extraction logic.
    """

    def __init__(self, txt_path: str, output_path: str):
        """
        Initializes the extractor with paths and loads text data.
        Also instantiates an LLM client for API communication.
        """
        self.txt_path = txt_path
        self.output_path = output_path
        self.text = self._load_text()  # Read input text immediately
        self.client = LLMClient()      # Create LLM API client instance

    def _load_text(self) -> str:
        """
        Loads text content from the provided file path.
        Returns:
            Loaded text as a single string.
        Raises:
            CustomException if the file is missing or unreadable.
        """
        try:
            if not os.path.exists(self.txt_path):
                logger.info(f"Text file not found at {self.txt_path}")
                raise FileNotFoundError(f"Text file not found: {self.txt_path}")  # <-- raise built-in exception

            with open(self.txt_path, 'r', encoding='utf-8') as f:
                text = f.read()
                logger.info(f"Loaded text file successfully: {self.txt_path}")
                return text
        except Exception as e:
            logger.exception("Failed to load text file.")
            raise CustomException("Error loading text file.", e)  # <-- here you already handle and wrap any error


    def _save_json(self, data: dict):
        """
        Saves the provided dictionary into a JSON file at the output path.
        Args:
            data: A dictionary object to be serialized into JSON.
        Raises:
            CustomException if writing fails.
        """
        try:
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved extracted JSON successfully: {self.output_path}")
        except Exception as e:
            logger.exception("Failed to save JSON file.")
            raise CustomException("Error saving JSON file.", e)

    def extract_with_llm(self, prompt: str, model_name: str, vendor: str = "openai"):
        """
        Sends a prompt to the LLM, receives the structured response, and saves it.
        Args:
            prompt: The input prompt string to send to the LLM.
            model_name: Name of the model to be used (e.g., 'gpt-3.5-turbo').
            vendor: The provider name (default 'openai', could be 'groq', 'together', etc.).
        Raises:
            CustomException if any stage (API call, JSON parsing, saving) fails.
        """
        try:
            logger.info(f"Sending extraction request to LLM: {vendor} / {model_name}")

            # 1️⃣ Get the response text from the LLM API
            response = self.client.get_llm_response(prompt, model_name, vendor)
            logger.info(f"✅ LLM responded successfully. Response length: {len(response)}")

            # 2️⃣ Always log and validate the response first
            logger.debug(f"📝 Full LLM Response:\n{response}")

            if not response.strip():
                logger.error("❌ LLM returned an empty response.")
                raise CustomException("LLM returned empty response.")

            # 3️⃣ Try parsing the returned response as JSON
            try:
                # Clean LLM response to remove markdown code blocks
                if response.startswith("```json"):
                    response = response.lstrip("```json").rstrip("```").strip()
                elif response.startswith("```"):
                    response = response.lstrip("```").rstrip("```").strip()

                print("==== LLM RAW RESPONSE ====")
                print(repr(response))
                print("==========================")
                data = json.loads(response)
            except json.JSONDecodeError as json_error:
                logger.error(f"❌ Failed to decode LLM response as JSON:\n{response}")
                raise CustomException("LLM returned invalid JSON.", json_error)

            # 4️⃣ Save the structured JSON output
            self._save_json(data)
            logger.info("✅ Extraction and JSON save completed.")

        except Exception as e:
            logger.exception("❌ Extraction with LLM failed.")
            raise CustomException("Extraction with LLM failed.", e)

