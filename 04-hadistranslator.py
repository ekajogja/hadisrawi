import json
import time
import os
from anthropic import Anthropic

def get_api_key():
    """Read API key from haikukey.txt file"""
    try:
        with open('haikukey.txt', 'r') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading API key: {str(e)}")
        return None

def translate_hadith(client, arabic_text):
    """Translate Arabic hadith text to Indonesian using Claude API"""
    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            temperature=0,
            system="You are a helpful assistant that translates Arabic text to Indonesian. Provide only the translation without any additional explanation.",
            messages=[
                {
                    "role": "user",
                    "content": f"Translate this Arabic text to Indonesian: {arabic_text}"
                }
            ]
        )
        return message.content

    except Exception as e:
        print(f"Error dalam terjemahan: {str(e)}")
        return None

def load_or_create_translated_data(filename):
    """Load existing translations or create a new list"""
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error: File {filename} tidak valid. Membuat file baru.")
    return []

def find_last_translated_id(translated_data):
    """Find the last translated hadis_id"""
    if translated_data:
        return translated_data[-1]['hadis_id']
    return None

def main():
    # Get API key
    api_key = get_api_key()
    if not api_key:
        print("Gagal membaca API key dari haikukey.txt")
        return

    # Initialize Anthropic client
    client = Anthropic(api_key=api_key)

    source_filename = 'resultjson/h6-sunanad-darimi.json'
    output_filename = 'terjemahanjson/h6-sunanad-darimi.json'

    try:
        # Read source JSON file
        print(f"Membaca file {source_filename}...")
        with open(source_filename, 'r', encoding='utf-8') as f:
            source_data = json.load(f)

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_filename), exist_ok=True)

        # Load existing translations or create new list
        translated_data = load_or_create_translated_data(output_filename)

        # Find the last translated hadis_id
        last_translated_id = find_last_translated_id(translated_data)

        total = len(source_data)
        processed = 0

        # Find the starting index based on the last translated hadis_id
        start_index = 0
        if last_translated_id:
            for i, hadith in enumerate(source_data):
                if hadith['hadis_id'] == last_translated_id:
                    start_index = i + 1
                    break

        print(f"Mulai menerjemahkan dari hadis_id: {source_data[start_index]['hadis_id']} ({start_index + 1}/{total})")

        # Process hadith one by one starting from the next hadis_id
        for i in range(start_index, total):
            hadith = source_data[i]
            print(f"\nMemproses hadis ID: {hadith['hadis_id']} ({i + 1}/{total})")

            translation = translate_hadith(client, hadith['Hadis'])
            if translation:
                translated_hadith = hadith.copy()
                translated_hadith['Terjemahan'] = str(translation)  # Convert to string
                translated_data.append(translated_hadith)
                print(f"Hadis {hadith['hadis_id']} berhasil diterjemahkan")
                print(f"Progress: {i + 1}/{total} ({((i + 1)/total)*100:.1f}%)")

                # Save progress after each translation
                with open(output_filename, 'w', encoding='utf-8') as f:
                    json.dump(translated_data, f, ensure_ascii=False, indent=4)
                print("Progress disimpan ke file")

            # Add delay between requests to respect API rate limits
            time.sleep(1)

        print(f"\nSelesai: {len(translated_data)} terjemahan telah ditambahkan ke {output_filename}")

    except FileNotFoundError:
        print(f"Error: File {source_filename} tidak ditemukan")
    except Exception as e:
        print(f"Error memproses file: {str(e)}")
        if 'translated_data' in locals():
            # Save progress in case of error
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(translated_data, f, ensure_ascii=False, indent=4)
            print("Progress disimpan sebelum error")

if __name__ == "__main__":
    main()