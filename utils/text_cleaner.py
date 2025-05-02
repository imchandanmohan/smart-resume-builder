import re
import string
from nltk.corpus import stopwords

# Download if missing
# import nltk
# nltk.download('stopwords')

STOPWORDS = set(stopwords.words('english'))

from nltk.corpus import stopwords

# One-time download if not done
# import nltk
# nltk.download('stopwords')

STOPWORDS = set(stopwords.words('english'))

def clean_text(text: str) -> str:
    """
    Only lowercase the text.
    Do NOT remove punctuation.
    Do NOT remove stopwords.
    """
    return text.lower()


import re

# Define regex patterns
METRIC_PATTERN = re.compile(r"\b\d+\s*[%$]?\b")  # matches "35", "35%", "$1000"
HARD_SKILL_HINTS = re.compile(r"(aws|azure|spark|tensorflow|snowflake|kubernetes|glue|pandas|numpy|postgres|powerbi)", re.I)

def smart_post_process_regex(entities):
    """
    Post-process NER output:
    - Merge consecutive tokens
    - Use regex/text matching to fix entity labels
    """
    merged_entities = []
    temp_entity = None

    for ent in entities:
        word = ent['text']
        label = ent['label']
        score = ent['score']

        # Merge tokens of same label
        if temp_entity and temp_entity['label'] == label:
            temp_entity['text'] += ' ' + word
            temp_entity['score'] = max(temp_entity['score'], score)
        else:
            if temp_entity:
                merged_entities.append(temp_entity)
            temp_entity = {
                'text': word,
                'label': label,
                'score': score
            }

    # Add last
    if temp_entity:
        merged_entities.append(temp_entity)

    # --- Second pass: regex-based label correction ---
    final_entities = []
    for ent in merged_entities:
        text = ent['text'].strip().lower()

        # Fix if metric pattern
        if METRIC_PATTERN.fullmatch(text):
            ent['label'] = 'METRIC'

        # Fix if hard skill hint
        elif HARD_SKILL_HINTS.search(text):
            ent['label'] = 'HARD'

        final_entities.append(ent)

    return final_entities


import nltk
import re
import string
from nltk.corpus import stopwords

# Make sure you have stopwords downloaded once:
# nltk.download('stopwords')

STOPWORDS = set(stopwords.words('english'))

def merge_broken_tokens_and_clean(entities):
    """
    Merge broken tokens like 'aw' + '##s' → 'aws'.
    Remove 'and', stopwords after merging.
    """
    merged = []
    i = 0
    while i < len(entities):
        current = entities[i]
        word = current['text']

        # Check if next token exists and is a broken continuation
        if i + 1 < len(entities):
            next_word = entities[i + 1]['text']

            # Merge aw + ##s (Huggingface wordpiece tokenization)
            if next_word.startswith('##'):
                combined_word = word + next_word[2:]  # remove ## and merge
                combined_entity = {
                    'text': combined_word,
                    'label': current['label'],
                    'score': max(current['score'], entities[i+1]['score'])
                }
                merged.append(combined_entity)
                i += 2
                continue

            # Skip common stopwords like "and", "on", "by"
            if next_word.lower() in STOPWORDS:
                merged.append(current)
                i += 2
                continue

        # No merging needed
        merged.append(current)
        i += 1

    # --- Final cleanup: remove stopwords inside merged text ---
    final_entities = []
    for ent in merged:
        words = ent['text'].split()
        filtered_words = [word for word in words if word.lower() not in STOPWORDS]
        cleaned_text = ' '.join(filtered_words)

        # Only keep if something remains
        if cleaned_text.strip():
            ent['text'] = cleaned_text.strip()
            final_entities.append(ent)

    return final_entities
