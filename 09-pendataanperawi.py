import json
import os
from openai import OpenAI
import time

# Baca API Key dari file
def get_api_key():
    try:
        with open('openaikey.txt', 'r') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading API key: {str(e)}")
        return None

# Fungsi untuk menyimpan data satu per satu
def append_to_output(item, output_file):
    try:
        # Read existing data if file exists
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        # Append new item
        data.append(item)

        # Write back to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"Error appending to output file: {str(e)}")
        raise

# Cek indeks terakhir yang sudah diproses
def get_last_processed_index(output_file):
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data:
                return data[-1].get('indeks_perawi')
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return None

# Fungsi untuk meminta terjemahan dari API OpenAI
def translate_text(client, text, target_lang):
    few_shot_examples = {
        "Arabic": [
            {"input": "Prophet Muhammad(saw) ( محمّد صلّی اللہ علیہ وآلہ وسلّم ( رضي الله عنه", "output": "محمد بن عبد الله"},
            {"input": "Rasool Allah", "output": "رسول الله"},
            {"input": "'Abdullah ibn 'Abd al-Muttalib [9991] / Amina bint Wahb b 'Abd Munaf bin Zuhrah", "output": "عبد الله بن عبد المطلب [9991] / آمينة بنت وهب بنت عبد مناف بن زهرة"}
        ],
        "Indonesian": [
            {"input": "محمد بن عبد الله", "output": "Muhammad bin Abdullah"},
            {"input": "رسول الله", "output": "Rasulullah"},
            {"input": "عبد الله بن عبد المطلب [9991] / آمينة بنت وهب بنت عبد مناف بن زهرة", "output": "Abdullah bin Abd al-Muttalib [9991] / Amina binti Wahb binti Abd Munaf bin Zuhrah"}
        ]
    }

    examples = "\n".join([f"Input: {ex['input']}\nOutput: {ex['output']}" for ex in few_shot_examples[target_lang]])
    prompt = f"Sebagai seorang ahli bahasa {target_lang}, terjemahkan teks berikut ke dalam bahasa {target_lang} menggunakan contoh berikut:\n{examples}\nInput: {text}\nOutput:"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Translate the following text into {target_lang} using the provided examples."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=150,
        top_p=0.9
    )
    return response.choices[0].message.content.strip()

# Memulai pemrosesan data
def process_json(input_file, output_file):
    try:
        # Read input file
        print("Loading input file...")
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = json.load(f)

        # Get the last processed indeks_perawi
        last_processed_index = get_last_processed_index(output_file)
        start_processing = False if last_processed_index else True

        # Initialize OpenAI client
        api_key = get_api_key()
        if not api_key:
            raise Exception("Failed to read API key from openaikey.txt")
        client = OpenAI(api_key=api_key)

        # Process each entry
        total_items = len(input_data)
        for i, item in enumerate(input_data):
            current_index = item.get('indeks_perawi')

            if not start_processing:
                if current_index == last_processed_index:
                    start_processing = True
                    print(f"Resuming from indeks_perawi: {current_index}")
                continue

            print(f"\nProcessing item {i+1} of {total_items} (indeks_perawi: {current_index})...")

            # Translate relevant fields
            try:
                for key, value in item.items():
                    if key.endswith("_Id") and value:
                        ar_key = key.replace("_Id", "_Ar")
                        print(f"Translating {key} to Arabic...")
                        item[ar_key] = translate_text(client, value, "Arabic")
                        print(f"Translated {key} to Arabic: {item[ar_key]}")
                        print(f"Translating {key} to Indonesian...")
                        item[key] = translate_text(client, value, "Indonesian")
                        print(f"Translated {key} to Indonesian: {item[key]}")
                        time.sleep(0.12)  # Delay to respect rate limits

            except Exception as e:
                print(f"Error during translation for item {i+1}:")
                print(f"Error details: {str(e)}")
                break

            print(f"Translated data for item {i+1}:")
            print(json.dumps(item, ensure_ascii=False, indent=4))
            print("-" * 50)

            # Append processed item to output file
            append_to_output(item, output_file)

        print("\nProcessing complete!")

    except KeyboardInterrupt:
        print("\nProcess interrupted by user!")
        raise

    except Exception as e:
        print(f"\nUnexpected error occurred:")
        print(f"Error details: {str(e)}")
        raise

if __name__ == "__main__":
    input_file = 'sumberjson/perawi.json'
    output_file = 'data_perawi.json'
    process_json(input_file, output_file)