#%%
# pylint: disable=line-too-long, trailing-whitespace, missing-module-docstring, unspecified-encoding, broad-exception-caught, unused-argument, too-many-locals, redefined-outer-name, invalid-name, wrong-import-order, unused-import

import json
import openai
import os
from src.api.together_client import query_together_ai
from src.assets.resume.prompt_data import prompt_data
from prompt import (
    generate_name_section,
    generate_contact_section,
    generate_education_section,
    generate_work_experience_section,
    generate_leadership_experience_section,
    generate_skills_section
)
with open('src/TextExtraction/together_extracted.json', 'r') as f:
    job_description = json.load(f)
    print(job_description)
with open('src/TextExtraction/resume_extracted.json', 'r') as j:
    resume_extracted = json.load(j)
    print(resume_extracted)
#print(generate_skills_section(prompt_data))
#%%
# Assume the Together AI API key is already set in your environment.
# (For demonstration we use openai.Completion.create as a placeholder.)
def normalize(field):
    """
    If the field is a list, join its elements into one string.
    Otherwise, return it (or empty string) so you can safely call .strip().
    """
    if isinstance(field, list):
        return "\n".join(field)
    return field or ""

def transform_resume_section(section_name: str, section_rules: str, description_content: str, extracted_content: str, max_tokens: int = 250) -> str:
    """
    Build and send a prompt to the LLM using the section rules, the job description excerpt, 
    and the resume-extracted content. The goal is to adjust the resume content so that it aligns
    closer with the job description. If no additional matching information is found, the original content is returned.
    
    Parameters:
       section_name (str): Name of the section (e.g., "Name", "Contact").
       section_rules (str): The rules/guidelines text for this section.
       description_content (str): Job description text relevant to this section.
       extracted_content (str): The candidate's extracted resume content for this section.
       max_tokens (int): Maximum number of tokens for LLM output.
       
    Returns:
       str: The reformatted section output from the LLM.
    """
    prompt = (
        f"You are given formatting rules for the '{section_name}' section:\n"
        f"{section_rules}\n\n"
        "You are also provided with an excerpt from the job description and the candidate's extracted resume content for this section.\n"
        "Your task is to adjust the resume extracted content so it resembles the job description more closely. "
        "If there is any overlap or similar important information, emphasize and integrate that into the final output. "
        "If nothing relevant is found, simply return the original extracted content unchanged.\n\n"
        "Job Description Excerpt:\n"
        f"{description_content if description_content.strip() else 'None'}\n\n"
        "Candidate's Resume Extract:\n"
        f"{extracted_content if extracted_content.strip() else 'None'}\n\n"
        "Please provide a coherent paragraph (do NOT use bullet points) as the final output."
    )
    
    try:
        return query_together_ai(
            prompt=prompt
        ).strip()
    except Exception as e:
        print(f"Error during LLM call for section '{section_name}':", e)
        return extracted_content

def build_and_save_full_formatted_resume():
    """
    Calls the transformation function for each resume section using:
       - The output from our rules-generating functions (e.g., generate_name_section)
       - The appropriate job description excerpt and resume extraction
    Then, saves the final transformed sections in a JSON file.
    """
    # Load the job description and resume extracted data from your JSON files.
    # Adjust these file paths to match your project's structure.

    
    # Call our existing functions to get the section rules for each section.
    name_section_rules = generate_name_section(prompt_data)
    contact_section_rules = generate_contact_section(prompt_data)
    education_section_rules = generate_education_section(prompt_data)
    work_section_rules = generate_work_experience_section(prompt_data)
    leadership_section_rules = generate_leadership_experience_section(prompt_data)
    skills_section_rules = generate_skills_section(prompt_data)
    
    # Extract corresponding excerpts from the job description and resume extraction.
    # (These keys must match those used in your JSON files; adjust if needed.)
    description_name       = normalize(job_description.get("name", "")).strip()
    description_contact    = normalize(job_description.get("contact", "")).strip()
    description_education  = normalize(job_description.get("education", "")).strip()
    description_work       = normalize(job_description.get("responsibilities", "")).strip()
    description_leadership = normalize(job_description.get("leadership", "")).strip()
    description_skills     = normalize(job_description.get("skills", "")).strip()
    
    extracted_name            = normalize(resume_extracted.get("name", "")).strip()
    extracted_contact         = normalize(resume_extracted.get("contact", "")).strip()
    extracted_education       = normalize(resume_extracted.get("education", "")).strip()
    extracted_work            = normalize(resume_extracted.get("work_experience", "")).strip()
    extracted_leadership      = normalize(resume_extracted.get("leadership_experience", "")).strip()
    extracted_skills          = normalize(resume_extracted.get("skills", "")).strip()

    
    # Transform each section using the LLM.
    final_name = transform_resume_section("Name", name_section_rules, description_name, extracted_name, max_tokens=150)
    final_contact = transform_resume_section("Contact", contact_section_rules, description_contact, extracted_contact, max_tokens=150)
    final_education = transform_resume_section("Education", education_section_rules, description_education, extracted_education, max_tokens=200)
    final_work = transform_resume_section("Work Experience", work_section_rules, description_work, extracted_work, max_tokens=300)
    final_leadership = transform_resume_section("Leadership Experience", leadership_section_rules, description_leadership, extracted_leadership, max_tokens=200)
    final_skills = transform_resume_section("Skills & Interests", skills_section_rules, description_skills, extracted_skills, max_tokens=150)
    
    # Combine all sections into a dictionary.
    formatted_resume = {
        "Name": final_name,
        "Contact": final_contact,
        "Education": final_education,
        "Work Experience": final_work,
        "Leadership Experience": final_leadership,
        "Skills & Interests": final_skills
    }
    
    # Save to a JSON file.
    output_filename = "final_formatted_resume_sections.json"
    with open(output_filename, "w") as outfile:
        json.dump(formatted_resume, outfile, indent=4)
    
    return formatted_resume

def clean_resume_section(section_name: str, section_content: str) -> str:
    """
    Use LLM to review and clean the final formatted resume section, removing unnecessary strings
    like '\n', '===', and any repetitive or formatting-related text artifacts.

    Parameters:
        section_name (str): Name of the section being cleaned.
        section_content (str): The content of the resume section needing cleaning.

    Returns:
        str: Cleaned and refined resume section content.
    """
    prompt = (
        f"The following text is a formatted section from a resume (section: '{section_name}') but has formatting errors and unnecessary artifacts:\n\n"
        f"{section_content}\n\n"
        "Clean the provided content by removing any unnecessary headings like '=== SECTION ===', '\n', and any redundant or repetitive text. "
        "Return a clean, concise, well-formatted paragraph suitable for a professional resume."
    )

    try:
        cleaned_content = query_together_ai(prompt=prompt).strip()
        return cleaned_content
    except Exception as e:
        print(f"Error during cleaning LLM call for section '{section_name}': {e}")
        return section_content


if __name__ == "__main__":
    final_formatted_resume = build_and_save_full_formatted_resume()

    cleaned_resume = {}
    for section, content in final_formatted_resume.items():
        cleaned_resume[section] = clean_resume_section(section, content)

    # Save cleaned resume sections
    output_filename_cleaned = "final_cleaned_resume_sections.json"
    with open(output_filename_cleaned, "w") as outfile:
        json.dump(cleaned_resume, outfile, indent=4)

    print(f"Cleaned resume sections have been saved to '{output_filename_cleaned}':\n")
    print(json.dumps(cleaned_resume, indent=4))


#%%
