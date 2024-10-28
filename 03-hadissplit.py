import json
import os

# Membaca file hadis.json
input_file_path = 'sumberjson/hadis.json'
output_dir_path = 'resultjson/'

# Fungsi untuk membaca file hadis.json secara bertahap
def read_hadis_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
            for hadis in data:
                yield hadis
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return

# Menambahkan hadis_id dan memecah file berdasarkan Kitab_Id
hadis_id_counter = 1
kitab_dict = {}

for hadis in read_hadis_file(input_file_path):
    # Menambahkan hadis_id sebagai properti paling atas
    hadis_id = f"ha{str(hadis_id_counter).zfill(5)}"
    hadis = {'hadis_id': hadis_id, **hadis}
    
    # Memecah file berdasarkan Kitab_Id
    kitab_id = hadis['Kitab_Id'].lower().replace(' ', '')
    if kitab_id not in kitab_dict:
        kitab_dict[kitab_id] = []
    kitab_dict[kitab_id].append(hadis)
    
    hadis_id_counter += 1

# Menyimpan hasil ke file terpisah di folder resultjson
os.makedirs(output_dir_path, exist_ok=True)

for idx, (kitab_id, hadis_list) in enumerate(kitab_dict.items(), start=1):
    output_file_path = os.path.join(output_dir_path, f'h{idx}-{kitab_id}.json')
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(hadis_list, file, ensure_ascii=False, indent=4)

print(f"File has been successfully processed and saved to {output_dir_path}")