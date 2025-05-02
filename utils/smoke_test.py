#!/usr/bin/env python3
import os
from openai import OpenAI
from groq import Groq

def main():
    # Load keys from env
    openai_key  = os.getenv("OPENAI_API_KEY")
    groq_key    = os.getenv("GROQ_API_KEY")
    together_key= os.getenv("TOGETHER_API_KEY")

    # OpenAI smoke test
    print("→ Testing OpenAI…")
    ocli = OpenAI(api_key=openai_key)
    oresp = ocli.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user","content":"Hello from smoke test"}]
    )
    print("OpenAI replied:", oresp.choices[0].message.content, "\n")

    # Groq smoke test
    print("→ Testing Groq…")
    gcli = Groq(api_key=groq_key)
    gresp = gcli.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role":"user","content":"Hello from smoke test"}]
    )
    print("Groq replied:", gresp.choices[0].message.content, "\n")

    # Together smoke test (corrected)
    print("→ Testing Together…")
    tcli = OpenAI(
        api_key=together_key,
        base_url="https://api.together.xyz/v1",
    )
    tresp = tcli.chat.completions.create(
        model="togethercomputer/llama-2-7b-chat",
        messages=[{"role":"user","content":"Hello from smoke test"}]
    )
    print("Together replied:", tresp.choices[0].message.content, "\n")

if __name__ == "__main__":
    main()