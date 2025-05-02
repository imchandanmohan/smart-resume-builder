#%%
# pylint: disable=line-too-long,missing-module-docstring
# pylint: disable=trailing-whitespace,unspecified-encoding,invalid-name,wrong-import-order


from src.assets.resume.prompt_data import prompt_data
import json
with open('src/TextExtraction/together_extracted.json', 'r') as f:
    description = json.load(f)
print(description['job_title'])
# Now you can access the data:
print(prompt_data.keys())
#%%

def generate_name_section(data):
    """Generate the Name section with example, ATS rules, style guidelines, and limits."""
    # Extract example data, ATS rules, guidelines, and limits.
    name_example = data["RESUME_EXAMPLE_OUTPUT"]["name"]
    ats_name_rules = data["ATS_RULES"]["ats_optimization_rules"]["name"]["rules"]
    style_name_guidelines = data["LLM_FILLING_GUIDELINES_WITH_STYLE"]["name"]["rules"]
    name_limit = data["LLM_FILLING_GUIDELINES_WITH_STYLE_AND_LIMITS"]["name"]["max_length"]
    
    section = "=== NAME ===\n"
    section += f"Example: {name_example}\n"
    section += "ATS Rules: " + ", ".join(ats_name_rules) + "\n"
    section += "Style Guidelines: " + ", ".join(style_name_guidelines) + "\n"
    section += f"Limit (max characters): {name_limit}\n"

    return section

def generate_contact_section(data):
    """Generate the Contact section with example, ATS rules, style guidelines, and limits."""
    contact_example = data["RESUME_EXAMPLE_OUTPUT"]["contact"]
    ats_contact_rules = data["ATS_RULES"]["ats_optimization_rules"]["contact"]["rules"]
    style_contact_guidelines = data["LLM_FILLING_GUIDELINES_WITH_STYLE"]["contact"]["rules"]
    # Limits for each contact field are defined in the "contact" sub-dictionary.
    contact_limits = data["LLM_FILLING_GUIDELINES_WITH_STYLE_AND_LIMITS"]["contact"]
    
    section = "=== CONTACT ===\n"
    section += f"Example: {contact_example}\n"
    section += "ATS Rules: " + ", ".join(ats_contact_rules) + "\n"
    section += "Style Guidelines: " + ", ".join(style_contact_guidelines) + "\n"
    section += f"Limits: {contact_limits}\n"

    return section

def generate_education_section(data):
    """Generate the Education section with example, ATS rules, style guidelines, and limits."""
    education_example = data["RESUME_EXAMPLE_OUTPUT"]["education"]
    ats_education_rules = data["ATS_RULES"]["ats_optimization_rules"]["education"]["rules"]
    style_education_guidelines = data["LLM_FILLING_GUIDELINES_WITH_STYLE"]["education"]["rules"]
    education_limits = data["LLM_FILLING_GUIDELINES_WITH_STYLE_AND_LIMITS"]["education"]
    
    section = "=== EDUCATION ===\n"
    section += f"University: {education_example.get('university', 'N/A')}\n"
    section += f"Degree: {education_example.get('degree', 'N/A')}\n"
    section += f"GPA: {education_example.get('gpa', 'N/A')}\n"
    section += f"Graduation Date: {education_example.get('graduation_date', 'N/A')}\n"
    if education_example.get("awards"):
        section += "Awards: " + ", ".join(education_example["awards"]) + "\n"
    section += "ATS Rules: " + ", ".join(ats_education_rules) + "\n"
    section += "Style Guidelines: " + ", ".join(style_education_guidelines) + "\n"
    section += f"Limits: {education_limits}\n"
    return section

def generate_work_experience_section(data):
    """Generate the Work Experience section with example, ATS rules, style guidelines, and limits."""
    work_experiences = data["RESUME_EXAMPLE_OUTPUT"]["work_experience"]
    ats_work_rules = data["ATS_RULES"]["ats_optimization_rules"]["work_experience"]["rules"]
    style_work_guidelines = data["LLM_FILLING_GUIDELINES_WITH_STYLE"]["work_experience"]["rules"]
    work_limits = data["LLM_FILLING_GUIDELINES_WITH_STYLE_AND_LIMITS"]["work_experience"]
    
    section = "=== WORK EXPERIENCE ===\n"
    for idx, job in enumerate(work_experiences, start=1):
        section += f"\nJob {idx}:\n"
        section += f"  Company: {job.get('company', 'N/A')}\n"
        section += f"  Title: {job.get('title', 'N/A')}\n"
        section += f"  Location: {job.get('location', 'N/A')}\n"
        section += f"  Dates: {job.get('dates', 'N/A')}\n"
        responsibilities = job.get("responsibilities", [])
        if responsibilities:
            section += "  Responsibilities:\n"
            for resp in responsibilities:
                section += f"    - {resp}\n"
    section += "\nATS Rules: " + ", ".join(ats_work_rules) + "\n"
    section += "Style Guidelines: " + ", ".join(style_work_guidelines) + "\n"
    section += f"Limits: {work_limits}\n"
    return section

def generate_leadership_experience_section(data):
    """Generate the Leadership Experience section with example, guidelines, and limits."""
    leadership_experiences = data["RESUME_EXAMPLE_OUTPUT"]["leadership_experience"]
    ats_leadership_rules = data["ATS_RULES"]["ats_optimization_rules"].get(
        "leadership_experience", {"rules": ["No specific ATS rules"]}
    )["rules"]
    style_leadership_guidelines = data["LLM_FILLING_GUIDELINES_WITH_STYLE"].get(
        "leadership_experience", {}
    ).get("rules", ["No specific style guidelines"])
    leadership_limits = data["LLM_FILLING_GUIDELINES_WITH_STYLE_AND_LIMITS"].get(
        "leadership_experience", {"max_entries": "N/A"}
    )
    
    section = "=== LEADERSHIP EXPERIENCE ===\n"
    for idx, lead in enumerate(leadership_experiences, start=1):
        section += f"\nLeadership {idx}:\n"
        section += f"  Organization: {lead.get('organization', 'N/A')}\n"
        section += f"  Title: {lead.get('title', 'N/A')}\n"
        section += f"  Location: {lead.get('location', 'N/A')}\n"
        section += f"  Dates: {lead.get('dates', 'N/A')}\n"
        responsibilities = lead.get("responsibilities", [])
        if responsibilities:
            section += "  Responsibilities:\n"
            for resp in responsibilities:
                section += f"    - {resp}\n"
    section += "\nATS Rules: " + ", ".join(ats_leadership_rules) + "\n"
    section += "Style Guidelines: " + ", ".join(style_leadership_guidelines) + "\n"
    section += f"Limits: {leadership_limits}\n"
    return section

def generate_skills_section(data):
    """Generate the Skills section with example, ATS rules, style guidelines, and limits."""
    skills_example = data["RESUME_EXAMPLE_OUTPUT"]["skills_and_interests"]["skills"]
    ats_skills_rules = data["ATS_RULES"]["ats_optimization_rules"]["skills"]["rules"]
    style_skills_guidelines = data["LLM_FILLING_GUIDELINES_WITH_STYLE"]["skills_and_interests"]["rules"]
    skills_limits = data["LLM_FILLING_GUIDELINES_WITH_STYLE_AND_LIMITS"]["skills_and_interests"]["skills"]
    
    section = "=== SKILLS & INTERESTS ===\n"
    for group, skills in skills_example.items():
        section += f"{group}: " + ", ".join(skills) + "\n"
    section += "\nATS Rules: " + ", ".join(ats_skills_rules) + "\n"
    section += "Style Guidelines: " + ", ".join(style_skills_guidelines) + "\n"
    section += f"Limits: {skills_limits}\n"
    return section

def build_full_prompt(data):
    """Build the full prompt by combining all individual section functions."""
    sections = [
        generate_name_section(data),
        generate_contact_section(data),
        generate_education_section(data),
        generate_work_experience_section(data),
        generate_leadership_experience_section(data),
        generate_skills_section(data)
    ]
    full_prompt = "\n\n".join(sections)
    return full_prompt

if __name__ == "__main__":
    # Build and print the full resume prompt that includes examples, ATS rules, style guidelines, and limits.
    Full_Prompt_Text = build_full_prompt(prompt_data)
    print("Generated Resume Prompt:\n")
    print(Full_Prompt_Text)

# %%
