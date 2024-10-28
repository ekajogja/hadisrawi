import csv
import json

# Nama file CSV dan JSON yang akan digunakan
csv_file_path = 'sumbercsv/hadis.csv'
json_file_path = 'sumberjson/hadis.json'

# Header yang diharapkan (7 kolom)
headers = ["Hadis", "Kitab", "Penulis", "Terjemahan", "Penjelasan", "Penerjemah", "Penashih"]

# Membaca file CSV dan mengonversinya ke JSON
with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file, fieldnames=headers)
    
    # Membaca baris demi baris
    data = []
    for row in csv_reader:
        # Memastikan setiap baris memiliki 7 properti
        for header in headers:
            if header not in row:
                row[header] = None  # Jika kolom tidak ada, isi dengan None
        data.append(row)

# Menyimpan data ke file JSON
with open(json_file_path, mode='w', encoding='utf-8') as json_file:
    json.dump(data, json_file, indent=4, ensure_ascii=False)

print(f"File CSV '{csv_file_path}' telah berhasil dikonversi ke JSON '{json_file_path}'.")