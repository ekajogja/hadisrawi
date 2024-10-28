import csv
import json
import os

# Path ke file CSV dan JSON
csv_file_path = 'sumbercsv/perawi.csv'
json_file_path = 'sumberjson/perawi.json'

# Memastikan folder sumberjson ada, jika tidak, buat folder tersebut
if not os.path.exists('sumberjson'):
    os.makedirs('sumberjson')

# Header baru
new_header = [
    'indeks_perawi', 'nama_Ar', 'nama_Id', 'alias_Ar', 'alias_Id', 'gelar_Ar', 'gelar_Id',
    'orang_tua_Ar', 'orang_tua_Id', 'pasangan_Ar', 'pasangan_Id', 'saudara_Ar', 'saudara_Id',
    'anak_Ar', 'anak_Id', 'tempat_tanggal_lahir', 'tempat_tinggal_Ar', 'tempat_tinggal_Id',
    'tempat_tanggal_wafat_Ar', 'tempat_tanggal_wafat_Id', 'guru_Ar', 'guru_Id', 'murid_Ar',
    'murid_Id', 'minat', 'tag', 'kitab_Ar', 'kitab_Id', 'indeks_murid', 'indeks_guru',
    'tempat_lahir_Ar', 'tempat_lahir_Id', 'tanggal_lahir', 'tanggal_lahir_hijriah',
    'tanggal_lahir_masehi', 'tanggal_wafat_hijriah', 'tanggal_wafat_masehi', 'tempat_wafat_Ar',
    'tempat_wafat_Id', 'alasan_wafat', 'pemeriksa', 'penashih'
]

# Membaca data dari file CSV
data = []
with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        # Memetakan nilai dari kolom lama ke kolom baru
        new_row = {
            'indeks_perawi': row['scholar_indx'],
            'nama_Ar': '',
            'nama_Id': row['name'],
            'alias_Ar': '',
            'alias_Id': '',
            'gelar_Ar': '',
            'gelar_Id': row['grade'],
            'orang_tua_Ar': '',
            'orang_tua_Id': row['parents'],
            'pasangan_Ar': '',
            'pasangan_Id': row['spouse'],
            'saudara_Ar': '',
            'saudara_Id': row['siblings'],
            'anak_Ar': '',
            'anak_Id': row['children'],
            'tempat_tanggal_lahir': row['birth_date_place'],
            'tempat_tinggal_Ar': '',
            'tempat_tinggal_Id': row['places_of_stay'],
            'tempat_tanggal_wafat_Ar': '',
            'tempat_tanggal_wafat_Id': row['death_date_place'],
            'guru_Ar': '',
            'guru_Id': row['teachers'],
            'murid_Ar': '',
            'murid_Id': row['students'],
            'minat': row['area_of_interest'],
            'tag': row['tags'],
            'kitab_Ar': '',
            'kitab_Id': row['books'],
            'indeks_murid': row['students_inds'],
            'indeks_guru': row['teachers_inds'],
            'tempat_lahir_Ar': '',
            'tempat_lahir_Id': row['birth_place'],
            'tanggal_lahir': row['birth_date'],
            'tanggal_lahir_hijriah': row['birth_date_hijri'],
            'tanggal_lahir_masehi': row['birth_date_gregorian'],
            'tanggal_wafat_hijriah': row['death_date_hijri'],
            'tanggal_wafat_masehi': row['death_date_gregorian'],
            'tempat_wafat_Ar': '',
            'tempat_wafat_Id': row['death_place'],
            'alasan_wafat': row['death_reason'],
            'pemeriksa': '',
            'penashih': ''
        }
        data.append(new_row)

# Menyimpan data ke file JSON
with open(json_file_path, mode='w', encoding='utf-8') as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)

print(f"Data telah berhasil dikonversi dan disimpan ke {json_file_path}")