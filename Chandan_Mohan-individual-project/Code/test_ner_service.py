import sys
import os
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)
from utils.text_cleaner import smart_post_process_regex, merge_broken_tokens_and_clean

from src.ner.ner_service import NERService

if __name__ == "__main__":
    ner_service = NERService(checkpoint_dir="artifacts/ner_model/checkpoint-4896")

    text = "Familiar with one or more machine learning or statistical modeling tools such as R, Matlab and scikit learn "
    result = ner_service.predict(text)

    entities = result['entities']
    entities = smart_post_process_regex(entities)    # Clean labels
    entities = merge_broken_tokens_and_clean(entities)          # Merge broken tokens

    final_result = {
        "text": result['text'],
        "entities": entities
    }

    # Add this line:
    print(final_result)
