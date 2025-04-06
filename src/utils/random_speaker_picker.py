import os
import random

def get_random_speaker_folder():
    base_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'assets', 'agentvoice', 'prerecorded', 'v2_en')
    )

    all_files = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.mp3'):
                rel_path = os.path.relpath(root, base_path)
                if rel_path != ".":
                    all_files.append(os.path.join(root, file))

    if not all_files:
        return None

    random_file = random.choice(all_files)
    speaker_folder = os.path.relpath(os.path.dirname(random_file), base_path).split(os.sep)[0]
    
    return speaker_folder

if __name__ == "__main__":
    speaker = get_random_speaker_folder()
    print("Random speaker picked:", speaker)
