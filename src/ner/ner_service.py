import os
import torch
import json
from transformers import AutoTokenizer, AutoModelForTokenClassification, AutoConfig, pipeline
from utils.text_cleaner import clean_text
import string

class NERService:
    def __init__(self, checkpoint_dir=None):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if checkpoint_dir is None:
            checkpoint_dir = os.path.abspath(
                os.path.join(current_dir, "../../artifacts/ner_model/checkpoint-4896")
            )
        else:
            checkpoint_dir = os.path.abspath(checkpoint_dir)

        self.checkpoint_dir = checkpoint_dir
        self.device = self._detect_device()

        self.config = AutoConfig.from_pretrained(self.checkpoint_dir, local_files_only=True)
        self.tokenizer = AutoTokenizer.from_pretrained(self.checkpoint_dir, local_files_only=True)
        self.model = AutoModelForTokenClassification.from_pretrained(
            self.checkpoint_dir,
            config=self.config,
            local_files_only=True
        ).to(self.device)

        self.pipeline = pipeline(
            "token-classification",
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy="simple",
            device=-1 if self.device.type == 'cpu' else 0
        )

    # def _detect_device(self):
    #     if torch.backends.mps.is_available():
    #         return torch.device('mps')
    #     elif torch.cuda.is_available():
    #         return torch.device('cuda')
    #     else:
    #         return torch.device('cpu')

    def _detect_device(self):
        return torch.device('cpu')  # ✅ Force to always use CPU

    def predict(self, text: str):
        cleaned_text = clean_text(text)
        preds = self.pipeline(cleaned_text)

        entity_list = []
        for p in preds:
            word = p['word'].strip()
            if word not in string.punctuation:
                entity_list.append({
                    "text": word,
                    "label": p['entity_group'],
                    "score": round(p['score'], 4)
                })

        return {
            "text": cleaned_text,
            "entities": entity_list
        }






"""
from src.ner.ner_service import NERService
if __name__ == "__main__":
    ner_service = NERService(checkpoint_dir="../../artifacts/ner_model/checkpoint-4896")

    text = "Built an ETL pipeline on AWS Glue and improved data ingestion by 35%."
    result = ner_service.predict(text)

    print(result)
"""