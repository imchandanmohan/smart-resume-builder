import openai
import os
from dotenv import load_dotenv
from datetime import datetime

# Load API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class OpenAITTS:
    def __init__(self, model="tts-1", voice="fable", output_dir="'/src/texttospeech/'tts_outputs"):
        self.model = model
        self.voice = voice
        self.output_dir = output_dir
        self.valid_models = ["tts-1", "tts-1-hd"]
        self.valid_voices = ["alloy", "echo", "fable", "nova", "onyx", "shimmer"]

        if self.model not in self.valid_models:
            raise ValueError(f"Invalid model: {self.model}")
        if self.voice not in self.valid_voices:
            raise ValueError(f"Invalid voice: {self.voice}")

        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def synthesize(self, text, filename_prefix="tts"):
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{filename_prefix}_{timestamp}.mp3"
        full_path = os.path.join(self.output_dir, filename)

        print(f"🎤 Synthesizing with model: {self.model}, voice: {self.voice}")
        try:
            response = openai.audio.speech.create(
                model=self.model,
                voice=self.voice,
                input=text
            )
            with open(full_path, "wb") as f:
                f.write(response.content)
            print(f"Audio saved as {full_path}")
        except Exception as e:
            print(f"Error during synthesis: {e}")

# Example usage
if __name__ == "__main__":
    tts = OpenAITTS(model="tts-1-hd", voice="nova")
    text = """Oh wow... haha, I can’t believe that just happened! 
    So there I was, standing in line, thinking... hmm, should I really buy another coffee today?
    And then—bam! The person in front of me turns around and says, "You look like you need a double shot." *laughs*
    I mean... was it that obvious? Haha! Anyway, I got the coffee. No regrets.Sometimes, you just gotta treat yourself, 
    right?"""
    tts.synthesize(text, filename_prefix="friendly_voice")
