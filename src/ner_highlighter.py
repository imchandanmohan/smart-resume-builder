import fitz  # PyMuPDF
import json

class ResumeNERHighlighter:
    def __init__(self, pdf_path: str, jsonl_path: str):
        self.pdf_path = pdf_path
        self.jsonl_path = jsonl_path
        self.doc = fitz.open(pdf_path)
        self.phrases = self._load_phrases()

    def _load_phrases(self):
        allowed_labels = {"ACTION", "HARD", "METRIC", "IMPACT", "SOFT"}
        phrases = []

        with open(self.jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    for ent in item.get("ner_result", {}).get("entities", []):
                        cleaned_text = " ".join(ent["text"].split())
                        label = ent["label"].upper()

                        # Normalize and validate label
                        if label == "SOFTSKILL":
                            label = "SOFT"
                        if label not in allowed_labels or not cleaned_text:
                            continue

                        phrases.append((cleaned_text, label))

        # Sort longer phrases first to avoid partial overlaps
        phrases.sort(key=lambda x: len(x[0]), reverse=True)
        return phrases


    def highlight_pdf(self):
        color_map = {
            'ACTION': (1.0, 0.6, 0.6),   # Soft Red
            'HARD': (1.0, 0.8, 0.4),     # Orange-Yellow
            'METRIC': (0.6, 0.9, 0.6),   # Light Green
            'IMPACT': (0.4, 0.9, 0.9),   # Aqua Blue
            'SOFT': (1.0, 1.0, 0.6)      # Pale Yellow
        }

        for page_num, page in enumerate(self.doc):
            for phrase, label in self.phrases:
                label = label.upper()
                if label not in color_map:
                    continue  # Skip unknown labels

                try:
                    matches = page.search_for(phrase)
                    if matches:
                        for loc in matches:
                            rect = page.add_rect_annot(loc)
                            rect.set_colors(
                                stroke=color_map[label],
                                fill=tuple(c * 0.85 for c in color_map[label])
                            )
                            rect.set_opacity(0.3)
                            rect.update()
                        print(f"[✅ FOUND] '{phrase}' ({label}) on page {page_num}")
                    else:
                        print(f"[❌ NOT FOUND] '{phrase}' ({label}) on page {page_num}")
                except Exception as e:
                    print(f"[WARN] Could not annotate '{phrase}' ({label}): {e}")


    def save(self, output_path: str):
        self.doc.save(output_path)
        self.doc.close()

    def process(self, output_path: str):
        self.highlight_pdf()
        self.save(output_path)

    @staticmethod
    def split_large_entities(entities):
        new_entities = []
        for ent in entities:
            text = ent['text']
            if len(text.split()) > 10:
                parts = text.split(",")
                for part in parts:
                    part = part.strip()
                    if part:
                        new_entities.append({
                            "text": part,
                            "label": ent['label'],
                            "score": ent['score']
                        })
            else:
                new_entities.append(ent)
        return new_entities


# Example usage
if __name__ == "__main__":
    pdf_path = "/Users/chandanmohan/Desktop/smart-resume-builder/artifacts/resume/resume.pdf"
    jsonl_path = "/Users/chandanmohan/Desktop/smart-resume-builder/artifacts/processed/resume_ner.jsonl"
    output_path = "/Users/chandanmohan/Desktop/smart-resume-builder/junk_files/highlighted_resume.pdf"

    rh = ResumeNERHighlighter(pdf_path, jsonl_path)
    rh.process(output_path)
    print(f"✅ Highlighted file saved at: {output_path}")
