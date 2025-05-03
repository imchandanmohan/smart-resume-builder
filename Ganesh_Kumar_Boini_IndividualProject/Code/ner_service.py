import os
import torch
import string
from transformers import AutoTokenizer, AutoModelForTokenClassification, AutoConfig
from NER.text_cleaner import clean_text

class NERService:
    def __init__(self, checkpoint_dir=None):
        current_dir = os.path.dirname(os.path.abspath(__file__))

        if checkpoint_dir is None:
            checkpoint_dir = os.path.join(current_dir, "checkpoint-4896")
        elif not os.path.isabs(checkpoint_dir):
            checkpoint_dir = os.path.join(current_dir, checkpoint_dir)

        self.checkpoint_dir = checkpoint_dir
        self.device = self._detect_device()

        self.config = AutoConfig.from_pretrained(
            self.checkpoint_dir, local_files_only=True
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.checkpoint_dir, local_files_only=True
        )
        self.model = AutoModelForTokenClassification.from_pretrained(
            self.checkpoint_dir,
            config=self.config,
            local_files_only=True
        ).to(self.device)

    def _detect_device(self):
        if torch.backends.mps.is_available():
            print("Device set to use mps:0")
            return torch.device('mps')
        elif torch.cuda.is_available():
            print("Device set to use cuda:0")
            return torch.device('cuda')
        else:
            print("Device set to use cpu")
            return torch.device('cpu')

    def predict(self, text: str):
        cleaned_text = clean_text(text)
        inputs = self.tokenizer(
            cleaned_text, return_tensors='pt', add_special_tokens=True
        )
        input_ids = inputs['input_ids'][0]
        attention_mask = inputs['attention_mask'][0]

        max_len    = 512
        chunk_size = max_len - 2
        overlap    = 100

        all_entities = []
        start = 0

        while start < len(input_ids):
            end = min(start + chunk_size, len(input_ids))
            chunk_input_ids = input_ids[start:end]
            chunk_attention_mask = attention_mask[start:end]

            # Re-add CLS / SEP for this chunk
            chunk_input_ids = torch.cat([
                torch.tensor([self.tokenizer.cls_token_id], device=self.device),
                chunk_input_ids.to(self.device),
                torch.tensor([self.tokenizer.sep_token_id], device=self.device)
            ])
            chunk_attention_mask = torch.cat([
                torch.tensor([1], device=self.device),
                chunk_attention_mask.to(self.device),
                torch.tensor([1], device=self.device)
            ])

            chunk_input_ids = chunk_input_ids.unsqueeze(0)
            chunk_attention_mask = chunk_attention_mask.unsqueeze(0)

            with torch.no_grad():
                outputs = self.model(
                    input_ids=chunk_input_ids,
                    attention_mask=chunk_attention_mask
                )
                logits      = outputs.logits
                probs       = torch.softmax(logits, dim=-1)
                preds       = torch.argmax(probs, dim=-1)[0].cpu().numpy()
                prob_values = probs[0].max(dim=-1).values.detach().cpu().numpy()

            tokens = self.tokenizer.convert_ids_to_tokens(chunk_input_ids[0])

            # ─────────────────────────────────────────────────
            # NEW: Merge subword tokens and skip special tokens
            # ─────────────────────────────────────────────────
            merged_entities = []
            for token, pred_idx, prob_val in zip(tokens, preds, prob_values):
                label = self.model.config.id2label[pred_idx]

                # Skip non-entities or useless tokens entirely
                if label == "O" or token in {"[CLS]", "[SEP]"}:
                    continue

                # If token is a WP subword (starts "##") and same label as last → merge
                if token.startswith("##") and merged_entities and \
                   merged_entities[-1]["label"] == label:
                    # append subword (minus the "##") to existing text
                    merged_entities[-1]["text"] += token.replace("##", "")
                    # keep the higher confidence score
                    prev_score = merged_entities[-1]["score"]
                    merged_entities[-1]["score"] = max(prev_score, round(float(prob_val),4))
                else:
                    # first occurrence of this entity piece
                    merged_entities.append({
                        "text": token,
                        "label": label,
                        "score": round(float(prob_val), 4)
                    })

            # add this chunk’s merged entities
            all_entities.extend(merged_entities)

            start += chunk_size - overlap

        # ─────────────────────────────────────────────────
        # NEW: Final cleanup – normalize & filter
        # ─────────────────────────────────────────────────
        clean_entities = []
        for ent in all_entities:
            # lower-case + strip punctuation at ends
            text = ent["text"].lower().strip(string.punctuation)
            # drop if too short or purely numeric
            if len(text) < 2 or text.isdigit():
                continue
            ent["text"] = text
            clean_entities.append(ent)

        return {
            "text": cleaned_text,
            "entities": clean_entities
        }
