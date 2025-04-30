# src/ner/ner_predictor.py

import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


class NERPredictor:
    def __init__(self, model_checkpoint: str, label2id: dict, id2label: dict):
        """
        Initializes the NER predictor using a pre-trained model.
        Args:
            model_checkpoint: Huggingface model path or name.
            label2id: Required label2id mapping.
            id2label: Required id2label mapping.
        """
        self.device = self._detect_device()
        self.tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
        
        # Load model with correct label mappings
        self.model = AutoModelForTokenClassification.from_pretrained(
            model_checkpoint,
            num_labels=len(label2id),
            id2label=id2label,
            label2id=label2id
        ).to(self.device)
        
        self.pipeline = pipeline(
            "token-classification",
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy="simple",
            device=-1 if self.device.type == 'cpu' else 0
        )

    def _detect_device(self):
        """
        Detects the best device (MPS for Mac, CUDA for GPU, CPU fallback).
        """
        if torch.backends.mps.is_available():
            return torch.device('mps')
        elif torch.cuda.is_available():
            return torch.device('cuda')
        else:
            return torch.device('cpu')

    def predict(self, text: str):
        """
        Predicts entities from input text.

        Args:
            text: Input text to analyze.

        Returns:
            List of dictionaries: [{"text": ..., "label": ...}, ...]
        """
        results = self.pipeline(text)
        cleaned = []
        for r in results:
            cleaned.append({
                "text": r["word"],
                "label": r["entity_group"]
            })
        return cleaned


import os
from src.ner.ner_predictor import NERPredictor

if __name__ == "__main__":
    # Get absolute path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_checkpoint = os.path.abspath(
        os.path.join(current_dir, "../../artifacts/ner_model/checkpoint-4896")
    )

    # Use original label mapping used during training
    label2id = {
        "SKILL": 0,
        "PROJECT": 1,
        "TOOL": 2,
        "EDUCATION": 3,
        "EXPERIENCE": 4
    }
    id2label = {v: k for k, v in label2id.items()}

    ner = NERPredictor(
        model_checkpoint=model_checkpoint,
        label2id=label2id,
        id2label=id2label
    )

    text = "Built an ETL pipeline on AWS Glue and improved data ingestion by 35%."
    output = ner.predict(text)
    print(output)
