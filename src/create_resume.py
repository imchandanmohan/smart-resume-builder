import os
import json
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
from api.grok_client import call_groq_api  # You should already have this

class VoiceAssistant:
    def __init__(self, user_bio, bot_bio, experience, memory_folder='src'):
        self.user_bio = user_bio
        self.bot_bio = bot_bio
        self.experience = experience
        self.memory_folder = memory_folder
        self.memory_file = os.path.join(memory_folder, "core_memory.jsonl")
        self.messages = [
            {
                'role': 'system',
                'content': f"You are {bot_bio['name']}, a {bot_bio['age']} year old professional from {bot_bio['location']} "
                           f"with {experience} years of experience in resume writing. You're here to help {user_bio['name']} "
                           f"from {user_bio['location']} craft an excellent resume. Start the conversation warmly and guide them through the process."
            }
        ]
        os.makedirs(memory_folder, exist_ok=True)
        open(self.memory_file, 'a', encoding='utf-8').close()
        self._initiate_context()

    def _initiate_context(self):
        response_data = call_groq_api(self.messages, temperature=0.5, max_tokens=100)
        res_message = response_data.get("choices", [])[0].get("message", {}).get("content", "")
        self._respond_assistant(res_message)
        self._save_memory("System: " + self.messages[0]['content'], res_message)
        self._speak(res_message)

    def _listen(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎤 Listening...")
            recognizer.pause_threshold = 1
            audio = recognizer.listen(source)
        try:
            print("🧠 Recognizing...")
            query = recognizer.recognize_google(audio, language='en-in')
            print(f"🗣️ User said: {query}")
            return query
        except Exception as e:
            print("❌ Could not understand, please try again...", e)
            return None

    def _save_memory(self, user_input, bot_response):
        with open(self.memory_file, "a", encoding="utf-8") as f:
            json.dump({"user": user_input, "bot": bot_response}, f)
            f.write("\n")

    def _respond_user(self, query):
        self.messages.append({'role': 'user', 'content': query})

    def _respond_assistant(self, response):
        self.messages.append({'role': 'assistant', 'content': response})

    def _speak(self, text):
        speech = gTTS(text=text, lang='en', slow=False)
        filename = "captured_voice.mp3"
        speech.save(filename)
        playsound(filename)
        os.remove(filename)

    def respond(self, query):
        self._respond_user(query)
        response_data = call_groq_api(self.messages, temperature=0.5, max_tokens=150)
        res_message = response_data.get("choices", [])[0].get("message", {}).get("content", "")
        self._respond_assistant(res_message)
        self._save_memory(query, res_message)
        self._speak(res_message)

    def run(self):
        while True:
            query = self._listen()
            if query:
                if 'exit' in query.lower() or 'stop' in query.lower():
                    farewell = "Goodbye. Talk to you soon."
                    self._speak(farewell)
                    self._save_memory(query, farewell)
                    break
                self.respond(query)

# 🏁 Entry point
if __name__ == "__main__":
    user_biodata = {
        "name": "Chandan",
        "location": "Washington D.C."
    }

    bot_biodata = {
        "name": "Alex",
        "talking style": "soft, expressive and funny",
        "age": "40",
        "location": "Washington D.C."
    }

    assistant = VoiceAssistant(user_bio=user_biodata, bot_bio=bot_biodata, experience=15)
    assistant.run()
