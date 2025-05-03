import json
from collections import Counter
import os

# Set correct absolute path from project root
ABS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'processed', 'jb_ner.jsonl'))

def analyze_job_description_focus(file_path=ABS_PATH):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    label_counter = Counter()

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                for ent in data.get("entities", []):
                    label = ent.get("label")
                    if label:
                        label_counter[label] += 1
            except json.JSONDecodeError:
                continue

    if not label_counter:
        return [], "No labels found in the job description data."

    sorted_labels = label_counter.most_common()

    top_labels = [label for label, _ in sorted_labels[:3]]
    message_parts = []

    if "IMPACT" in top_labels:
        message_parts.append("demonstrates measurable results and outcomes")
    if "ACTION" in top_labels:
        message_parts.append("uses strong action verbs to describe contributions")
    if "HARD" in top_labels:
        message_parts.append("highlights technical and platform-specific skills")
    if "SOFT" in top_labels:
        message_parts.append("shows collaboration and communication abilities")
    if "METRIC" in top_labels:
        message_parts.append("quantifies achievements using data or KPIs")

    if message_parts:
        summary = (
            f"This job description emphasizes {', '.join(top_labels)}.\n\n"
            f"👉 Make sure your resume {', and '.join(message_parts)}."
        )
    else:
        summary = "No actionable insight found from labels."

    return sorted_labels, summary
