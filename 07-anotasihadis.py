import json
import sys
from anthropic import Anthropic

def get_api_key():
    """Read API key from haikukey.txt file"""
    try:
        with open('haikukey.txt', 'r') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading API key: {str(e)}")
        return None

def extract_details(client, hadis, terjemahan):
    # Extract Perawi_Ar
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        temperature=0,
        messages=[
            {"role": "user", "content": f"Ekstrak nama-nama tokoh yang menjadi jalur hadis secara urut dalam bahasa Arab dari teks berikut, pisahkan dengan koma tanpa nomor urut, tanpa menambahkan kalimat pengantar atau format apapun: {hadis}"}
        ]
    )
    perawi_ar = message.content[0].text.strip()

    # Extract Perawi_Id
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        temperature=0,
        messages=[
            {"role": "user", "content": f"Ekstrak nama-nama tokoh yang menjadi jalur hadis secara urut dalam bahasa Indonesia dari teks berikut, pisahkan dengan koma tanpa nomor urut, tanpa menambahkan kalimat pengantar atau format apapun: {terjemahan}"}
        ]
    )
    perawi_id = message.content[0].text.strip()

    # Extract Premis without any prefix or formatting
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        temperature=0,
        messages=[
            {"role": "user", "content": f"Ekstrak kalimat inti hadis dari teks berikut tanpa menambahkan kalimat pengantar atau format apapun: {terjemahan}"}
        ]
    )
    premis = message.content[0].text.strip()

    # Extract Topik with comma-separated format
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        temperature=0,
        messages=[
            {"role": "user", "content": f"""Ekstrak 1-10 topik yang dibahas dalam hadis berikut dalam bentuk kata atau frasa (bukan kalimat), dipisahkan dengan koma. 
            Topik harus berupa konsep, nilai, prinsip, atau hal non-person (boleh lokasi atau waktu). 
            Jangan masukkan nama-nama orang berikut ini ke dalam topik: {perawi_id}. 
            Jangan tambahkan kalimat pengantar atau penjelasan apapun. 
            Teks hadis: {terjemahan}"""}
        ]
    )
    topik = message.content[0].text.strip()

    # Filter out any remaining topics that match perawi names
    perawi_list = [name.strip().lower() for name in perawi_id.split(',')]
    topik_list = [t.strip() for t in topik.split(',')]
    filtered_topik = [t for t in topik_list if t.lower() not in perawi_list]
    topik = ', '.join(filtered_topik)

    return perawi_ar, perawi_id, premis, topik

def append_to_output(item, output_file):
    """Append a single processed item to the output file"""
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

def get_last_processed_id(output_file):
    """Get the hadis_id of the last processed item"""
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data:
                return data[-1].get('hadis_id')
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return None

def process_json(input_file, output_file):
    try:
        # Read input file
        print("Loading input file...")
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = json.load(f)

        # Get the last processed hadis_id
        last_processed_id = get_last_processed_id(output_file)
        start_processing = False if last_processed_id else True

        # Initialize Anthropic client
        api_key = get_api_key()
        if not api_key:
            raise Exception("Failed to read API key from haikukey.txt")
        client = Anthropic(api_key=api_key)

        # Define the stop_id
        stop_id = "ha62169"

        # Process each entry
        total_items = len(input_data)
        for i, item in enumerate(input_data):
            current_hadis_id = item.get('hadis_id')

            if not start_processing:
                if current_hadis_id == last_processed_id:
                    start_processing = True
                    print(f"Resuming from hadis_id: {current_hadis_id}")
                continue

            print(f"\nProcessing item {i+1} of {total_items} (hadis_id: {current_hadis_id})...")

            # Extract details
            hadis = item.get('Hadis', '')
            terjemahan = item.get('Terjemahan', '')

            try:
                perawi_ar, perawi_id, premis, topik = extract_details(client, hadis, terjemahan)
            except Exception as e:
                print(f"Error during extraction for item {i+1}:")
                print(f"Error details: {str(e)}")
                sys.exit(1)

            print(f"Extracted data for item {i+1}:")
            print(f"Perawi_Ar: {perawi_ar}")
            print(f"Perawi_Id: {perawi_id}")
            print(f"Premis: {premis}")
            print(f"Topik: {topik}")
            print("-" * 50)

            # Update item with extracted data
            item['Perawi_Ar'] = perawi_ar
            item['Perawi_Id'] = perawi_id
            item['Premis'] = premis
            item['Topik'] = topik

            # Append processed item to output file
            append_to_output(item, output_file)

            # Check if we need to stop processing
            if current_hadis_id == stop_id:
                print(f"Reached stop_id: {stop_id}. Stopping processing.")
                break

        print("\nProcessing complete!")

    except KeyboardInterrupt:
        print("\nProcess interrupted by user!")
        sys.exit(1)

    except Exception as e:
        print(f"\nUnexpected error occurred:")
        print(f"Error details: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    input_file = 'terjemahhadis.json'
    output_file = 'anotasihadis.json'
    process_json(input_file, output_file)