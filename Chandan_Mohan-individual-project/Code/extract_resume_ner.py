import os
import sys
import json
from openai import OpenAI
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from config.paths_config import PROCESSED_RESUME_TEXT_FILE_PATH, PROCESSED_RESUME_NER_PATH
from src.logger import get_logger
from src.custom_exception import CustomException

# Initialize
load_dotenv()
logger = get_logger(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_TEMPLATE = """
You are an intelligent resume sentence extractor and tagger.

You will be given a plain-text resume. Your task is to:
- Only extract **full, meaningful content sentences** related to experience, projects, or education.
- Completely ignore **headings**, **school names**, **job titles**, **locations**, and **skills lists**.
- Do not extract bullet symbols, colons, dashes, or sentence fragments.
- Only extract value-adding statements (e.g., achievements, responsibilities, measurable outcomes).
- ACTION: Action verbs at the beginning of each experience bullet (e.g., Collaborated, Managed, Improved). Use present tense for current roles and past tense for previous ones.
- HARD: Hard skills and platform-specific tools mentioned throughout the resume (e.g., SQL, Excel, Salesforce). Also listed at the bottom under "Skills" and reflected in the experience section.
- METRICS: (numbers/percentages) that demonstrate tangible contributions or improvements made in each role.
- IMPACT: Statements that describe the type of impact (e.g., increased efficiency by 20%, reduced costs, optimized workflow), often preceding the numbers.
- SOFT: Soft skills and general professional qualities (e.g., collaborated with teams, recommended solutions, identified problems).

⚠️ IMPORTANT RULES:
- ❌ Do NOT extract section headers (e.g., "PROJECTS", "SKILLS", "EDUCATION").
- ❌ Do NOT include job titles, school names, dates, locations, or any metadata.
- ❌ Do NOT extract raw skills lists (e.g., "Python, SQL, TensorFlow") unless used inside a full sentence.
- ✅ Do extract content from any part of the resume — including skills — if the line is a complete sentence that demonstrates usage (e.g., “Built a model using Python”).
- ✅ Only extract clean, fully formed, standalone sentences with meaning.
- ✅ Do NOT duplicate or overlap any content.
- calculate ATS based on this
-🔹 ATS_Score = (w_k * KeywordMatch) + (w_f * FormatScore) + (w_s * SectionCompleteness) + (w_m * QuantifiedAchievements)
Where:
w_k = Keyword Match (%)
% of required keywords/phrases from the job description found in the resume.
Penalize keyword stuffing (e.g., duplicate keywords used unnaturally).
w_f = Format Compliance (%)
Score based on use of ATS-friendly format (e.g., no tables, images, text boxes, or headers/footers).
Full points only if layout is parsable by basic ATS systems.
w_s = Section Accuracy (%)
Measures presence and labeling of key sections: Contact Info, Summary, Experience, Education, Skills.
Must follow standard naming ("Experience" instead of "My Journey").
w_m = Measurable Achievements (%)
% of experience bullet points that include metrics, results, or outcomes (e.g., “Increased sales by 35%”).
- w_k + w_f + w_s + w_m == 1  # Total weight must equal 1
- w_k >= 0.5  # Ensure KeywordMatch has majority weight

For each valid sentence:
- Include:
  - `"source"`: One of "experience", "education", "projects", or "other"
  - `"original_text"`: The sentence exactly as written in the resume
  - `"ner_result"`: {
      "text": same sentence in lowercase,
      "entities": a list of {
          "text": extracted phrase,
          "label": one of: HARD, SOFT, IMPACT, METRIC, ACTION,
          "score": float between 0.4 and 1.0
      }
    }

Return result as a **JSON array** (not JSONL or multiple objects).

Example format:
[
  {
    "source": "education",
    "original_text": "Worked on Terraform scripts in AWS for infrastructure deployment.",
    "ner_result": {
      "text": "worked on terraform scripts in aws for infrastructure deployment.",
      "entities": [
        {"text": "terraform scripts in aws", "label": "HARD", "score": 0.91},
        {"text": "infrastructure deployment", "label": "ACTION", "score": 0.85}
      ]
    }
  }
]

Now extract from the resume below:
"""


def extract_resume_ner():
    try:
        # Step 1: Load resume text
        with open(PROCESSED_RESUME_TEXT_FILE_PATH, "r", encoding="utf-8") as f:
            resume_text = f.read()

        logger.info("Resume loaded. Sending to LLM...")

        # Step 2: Build prompt
        full_prompt = PROMPT_TEMPLATE + "\n\n" + resume_text

        # Step 3: Call OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.2
        )

        result_text = response.choices[0].message.content.strip()

        # Step 4: Clean up markdown if wrapped
        if result_text.startswith("```json"):
            result_text = result_text.lstrip("```json").rstrip("```").strip()
        elif result_text.startswith("```"):
            result_text = result_text.lstrip("```").rstrip("```").strip()

        # Step 5: Parse and write output
        parsed = json.loads(result_text)

        with open(PROCESSED_RESUME_NER_PATH, "w", encoding="utf-8") as f_out:
            for record in parsed:
                json.dump(record, f_out)
                f_out.write("\n")

        logger.info(f"✅ NER extraction complete. Saved to: {PROCESSED_RESUME_NER_PATH}")

    except Exception as e:
        logger.error(f"NER extraction failed: {e}")
        raise CustomException(f"Resume NER extraction failed: {e}", sys)

if __name__ == "__main__":
    extract_resume_ner()
