import os
import json

# Path ke direktori terjemahanjson
input_dir = 'terjemahanjson'

# Path ke file output yang relatif terhadap lokasi script
output_file = 'terjemahhadis.json'

# Inisialisasi list untuk menyimpan semua data JSON
combined_data = []

# Ambil semua file JSON dalam direktori terjemahanjson, kecuali h4-shahihmuslim.json
json_files = [f for f in os.listdir(input_dir) if f.endswith('.json') and f != 'h4-shahihmuslim.json']

# Urutkan file berdasarkan nama file
json_files_sorted = sorted(json_files, key=os.path.basename)

# Loop melalui semua file JSON yang telah diurutkan
for filename in json_files_sorted:
    file_path = os.path.join(input_dir, filename)
    
    # Baca file JSON
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        combined_data.extend(data)

# Simpan hasil gabungan ke file terjemahhadis.json
with open(output_file, 'w', encoding='utf-8') as outfile:
    json.dump(combined_data, outfile, ensure_ascii=False, indent=4)

print(f"File JSON telah digabungkan dan disimpan sebagai {output_file}")