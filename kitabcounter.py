import json
from collections import Counter

# Path ke file hadis.json
file_path = 'sumberjson/hadis.json'

# Membaca file JSON
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Menginisialisasi Counter untuk menghitung jumlah hadis per Kitab_Id
kitab_counter = Counter()

# Iterasi melalui setiap entri dalam data
for entry in data:
    kitab_id = entry.get('Kitab_Id')
    if kitab_id:
        kitab_counter[kitab_id] += 1

# Menampilkan hasil
for kitab_id, count in kitab_counter.items():
    print(f"{kitab_id} - {count}")