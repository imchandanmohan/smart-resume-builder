import re
import spacy
import nltk
from typing import List
from nltk.corpus import stopwords
from NER.ner_service import NERService 

class TextPreprocessor:
    """
    Class-based text preprocessing with modular methods for
    cleaning, tokenization, lemmatization, stopword removal,
    NER filtering, and POS filtering.
    """

    def __init__(self, remove_ner=True, keep_numbers=False):
        self.nlp = spacy.load("en_core_web_sm")
        self.stop_words = set(stopwords.words("english"))
        self.allowed_pos = {"NOUN", "PROPN", "ADJ", "VERB"}  # Added VERB
        self.ner_labels_to_ignore = {"PERSON", "GPE", "DATE"}  # Removed PRODUCT/ORG
        self.remove_ner = remove_ner
        self.clean_regex = r"[^a-z0-9\s]" if keep_numbers else r"[^a-z\s]"
        self.ner = NERService()

    def clean_text(self, text: str) -> str:
        """
        Lowercase, remove URLs, emails, non-ASCII, and punctuation.
        """
        text = text.lower()
        text = re.sub(r"https?://\S+|www\.\S+", "", text)
        text = re.sub(r"\S+@\S+", "", text)
        text = re.sub(r"[^\x00-\x7F]+", " ", text)
        text = re.sub(r"[^a-z0-9\s]", " ", text)  # Allow numbers
        # In clean_text(), retain numbers with context:
        text = re.sub(r"[^a-z0-9+\-]", " ", text)  # Keep "+", "-", and numbers
        text = re.sub(r"\s+", " ", text)
        return text.strip()
    

    def tokenize(self, text: str) -> List[spacy.tokens.Token]:
        """
        Tokenize using spaCy NLP pipeline.
        """
        return list(self.nlp(text))

    def remove_named_entities(self, tokens: List[spacy.tokens.Token]) -> List[spacy.tokens.Token]:
        """
        Filter out named entities like organizations, locations, etc.
        """
        return [token for token in tokens if token.ent_type_ not in self.ner_labels_to_ignore]

    def remove_stopwords(self, tokens: List[spacy.tokens.Token]) -> List[spacy.tokens.Token]:
        """
        Remove NLTK stopwords from the tokens.
        """
        return [token for token in tokens if token.text not in self.stop_words]

    def filter_by_pos(self, tokens: List[spacy.tokens.Token]) -> List[spacy.tokens.Token]:
        """
        Keep only tokens with desired POS tags.
        """
        return [token for token in tokens if token.pos_ in self.allowed_pos and len(token.text) > 2]

    def lemmatize(self, tokens: List[spacy.tokens.Token]) -> List[str]:
        """
        Convert tokens to their lemmatized forms.
        """
        return [token.lemma_ for token in tokens]

    def preprocess(self, text: str) -> List[str]:
        """
        Complete preprocessing pipeline.
        """
        cleaned = self.clean_text(text)
        tokens = self.tokenize(cleaned)
        if self.remove_ner:
            tokens = self.remove_named_entities(tokens)
        tokens = self.remove_stopwords(tokens)
        tokens = self.filter_by_pos(tokens)
        return self.lemmatize(tokens)
    
    # NEW helper -----------------------------------------
    def split_by_label(self, text: str):
        """
        Returns two token lists: hard_tokens, soft_tokens
        using NERService labels (HARD / SOFT).
        """
        ents = self.ner.predict(text)["entities"]
        hard = [e["text"].lower() for e in ents if e["label"] == "HARD"]
        soft = [e["text"].lower() for e in ents if e["label"] == "SOFT"]
        return hard, soft


def init_nlp_resources():
    """
    Ensure NLTK stopwords are available.
    """
    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("stopwords")
