import json
import sqlite3

# Path ke file JSON
json_file = 'terjemahhadis.json'

# Path ke file SQLite
sqlite_file = 'hadis.db'

# Membuat koneksi ke SQLite
conn = sqlite3.connect(sqlite_file)
cursor = conn.cursor()

# Membuat tabel hadis jika belum ada
cursor.execute('''
CREATE TABLE IF NOT EXISTS hadis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hadis_id TEXT,
    Hadis TEXT,
    Kitab_Ar TEXT,
    Penulis TEXT,
    Terjemahan TEXT,
    Penjelasan TEXT,
    Penerjemah TEXT,
    Penashih TEXT
);
''')

# Membaca data dari file JSON
with open(json_file, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Memasukkan data ke dalam tabel hadis
for hadis in data:
    cursor.execute('''
    INSERT INTO hadis (hadis_id, Hadis, Kitab_Ar, Penulis, Terjemahan, Penjelasan, Penerjemah, Penashih)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    ''', (hadis['hadis_id'], hadis['Hadis'], hadis['Kitab_Ar'], hadis['Penulis'], hadis['Terjemahan'], hadis['Penjelasan'], hadis['Penerjemah'], hadis['Penashih']))

# Menyimpan perubahan dan menutup koneksi
conn.commit()
conn.close()

print(f"Data telah berhasil diimpor ke {sqlite_file}")