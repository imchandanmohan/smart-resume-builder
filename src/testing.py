import requests
import json

# Step 1: Define available resume-related functions
def get_functions():
    return {
        "functions": [
            {
                "name": "fetch_skill_section",
                "description": "Retrieves the list of skills from the user's resume data."
            },
            {
                "name": "add_skill_section",
                "description": "Adds a new skill or set of skills to the skill section of the resume."
            },
            {
                "name": "update_skill_section",
                "description": "Updates existing skills in the skill section."
            },
            {
                "name": "delete_skill_section",
                "description": "Removes one or more skills from the skill section."
            },
            {
                "name": "fetch_experience_section",
                "description": "Fetches all professional experiences."
            },
            {
                "name": "add_experience_section",
                "description": "Adds a new professional experience entry."
            },
            {
                "name": "update_experience_section",
                "description": "Updates an experience entry."
            },
            {
                "name": "delete_experience_section",
                "description": "Deletes an experience entry."
            },
            {
                "name": "fetch_education_section",
                "description": "Retrieves education-related entries."
            },
            {
                "name": "add_education_section",
                "description": "Adds a new education entry."
            },
            {
                "name": "update_education_section",
                "description": "Modifies an existing education entry."
            },
            {
                "name": "delete_education_section",
                "description": "Removes an education entry."
            },
            {
                "name": "update_core_memory",
                "description": "update core memory of what user ask to remeamber"
            }
        ]
    }

# Step 2: Prompt builder (accepting user_input argument)
def get_prompt(user_input):
    return f"""
You are an intent recognizer for a resume assistant.

Below is a list of functions with their descriptions:
- fetch_skill_section: Retrieves the list of skills from the user's resume data.
- add_skill_section: Adds a new skill or set of skills to the skill section of the resume.
- update_skill_section: Updates existing skills in the skill section.
- delete_skill_section: Removes one or more skills from the skill section.
- fetch_experience_section: Fetches all professional experiences.
- add_experience_section: Adds a new professional experience entry.
- update_experience_section: Updates an experience entry.
- delete_experience_section: Deletes an experience entry.
- fetch_education_section: Retrieves education-related entries.
- add_education_section: Adds a new education entry.
- update_education_section: Modifies an existing education entry.
- delete_education_section: Removes an education entry.

Your task:
- Match the user's command to the most appropriate function name (from above).
- If no match is found, set "intended_function" to null and provide a helpful message.
- If the input is irrelevant (e.g., "Who is Akbar?"), return a crisp message explaining this tool is for resumes.

Format your response exactly like this:

Examples:

User: "I want to add my recent job as a backend engineer"
Response:
{{
  "user_command": "I want to add my recent job as a backend engineer",
  "intended_function": "add_experience_section",
  "message": "You can use the 'add_experience_section' function to add your job experience."
}}

User: "Can you show me all my degrees?"
Response:
{{
  "user_command": "Can you show me all my degrees?",
  "intended_function": "fetch_education_section",
  "message": "Sure! Use the 'fetch_education_section' function to view your education entries."
}}

User: "Who is Akbar?"
Response:
{{
  "user_command": "Who is Akbar?",
  "intended_function": null,
  "message": "I'm here to help with your resume. Let's focus on that!"
}}

Now here’s the user’s text:
{user_input}
"""


# Step 3: Call Ollama with streaming response
def ollama(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama2", "prompt": prompt},
        stream=True
    )
    output = ""
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            output += data.get("response", "")
    return output

# Step 4: Main script
def main():
    count=0
    while count<5:
        user_input = input("Type something here: ")
        prompt = get_prompt(user_input)  # Pass the user_input to the prompt
        result = ollama(prompt)
        print("\nResponse from Ollama:\n")
        print(result)
        count+=1

if __name__ == "__main__":
    main()
