import json
import time
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

def main():
    # Get API key
    api_key = get_api_key()
    if not api_key:
        print("Gagal membaca API key dari haikukey.txt")
        return

    # Initialize Anthropic client
    client = Anthropic(api_key=api_key)
    filename = 'resultjson/h1-al-muwaththa.json'
    
    try:
        # Read JSON file
        print(f"Membaca file {filename}...")
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        total = len(data)
        processed = 0
        
        print(f"Mulai menerjemahkan {total} hadis...")
        
        # Process all hadith
        for hadith in data:
            if not hadith.get('Terjemahan'):  # Only translate if no translation exists
                print(f"\nMemproses hadis ID: {hadith['hadis_id']} ({processed + 1}/{total})")
                
                translation = translate_hadith(client, hadith['Hadis'])
                if translation:
                    hadith['Terjemahan'] = translation
                    processed += 1
                    print(f"Hadis {hadith['hadis_id']} berhasil diterjemahkan")
                    print(f"Progress: {processed}/{total} ({(processed/total)*100:.1f}%)")
                    
                    # Save progress every 10 translations
                    if processed % 10 == 0:
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=4)
                        print("Progress disimpan ke file")
                
                # Add delay between requests to respect API rate limits
                time.sleep(1)
        
        # Final save
        print("\nMenyimpan hasil akhir...")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"\nSelesai: {processed} terjemahan telah ditambahkan ke {filename}")
        
    except FileNotFoundError:
        print(f"Error: File {filename} tidak ditemukan")
    except Exception as e:
        print(f"Error memproses file: {str(e)}")
        # Save progress in case of error
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("Progress disimpan sebelum error")

if __name__ == "__main__":
    main()