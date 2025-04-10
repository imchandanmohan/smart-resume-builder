import json

def get_ats_rules():
    file_path = "/Users/chandanmohan/Desktop/smart-resume-builder/src/assets/resume/ATS_RULES.json"
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            rules = data["ats_optimization_rules"]["skills"]["rules"]
            return "\n".join(f"- {rule}" for rule in rules)
    except Exception as e:
        return f"Error: {e}"

def get_skills_guidelines():
    file_path = "/Users/chandanmohan/Desktop/smart-resume-builder/src/assets/resume/LLM_FILLING_GUIDELINES_WITH_STYLE_AND_LIMITS.json"
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            skills = data["skills_and_interests"]["skills"]
            return (
                f"- Type: {skills['type']}\n"
                f"- Maximum items allowed: {skills['max_items']}\n"
                f"- Maximum length per item: {skills['max_item_length']} characters"
            )
    except Exception as e:
        return f"Error: {e}"

def get_skills_style_guidelines():
    file_path = "/Users/chandanmohan/Desktop/smart-resume-builder/src/assets/resume/LLM_FILLING_GUIDELINES_WITH_STYLE.json"
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            skills = data["skills_and_interests"]["skills"]
            rules = data["skills_and_interests"]["rules"]
            
            skills_formatted = "\n".join(f"- {item}" for item in skills)
            rules_formatted = "\n".join(f"- {item}" for item in rules)
            
            return f"Skills Style Guidelines:\n{skills_formatted}\n\nAdditional Rules:\n{rules_formatted}"
    except Exception as e:
        return f"Error: {e}"

import json

def get_resume_example_skills():
    file_path = "/Users/chandanmohan/Desktop/smart-resume-builder/src/assets/resume/RESUME_EXAMPLE_OUTPUT.json"
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            skills = data["skills_and_interests"]["skills"]
            
            output_lines = ["Resume Example – Skills:"]
            for category, items in skills.items():
                output_lines.append(f"{category}:")
                for item in items:
                    output_lines.append(f"  - {item}")
                    
            return "\n".join(output_lines)
    except Exception as e:
        return f"Error: {e}"
    


if __name__ == "__main__":
    print("=== ATS Optimization Rules ===")
    print(get_ats_rules())
    print("\n=== Skills Guidelines with Limits ===")
    print(get_skills_guidelines())
    print("\n=== Skills Style Guidelines ===")
    print(get_skills_style_guidelines())
    print("\n=== Resume Example Skills ===")
    print(get_resume_example_skills())
