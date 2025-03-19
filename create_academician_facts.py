import json

# JSON dosyasını yükleyin
with open('academic_data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Prolog formatına dönüştürme
prolog_data = []

for academician in data:
    # Akademisyen bilgisi (name, department, discipline, profile_url)
    prolog_data.append(f"academician(\"{academician['name']}\", \"{academician['department']}\", \"{academician['discipline']}\", \"{academician['profile_url']}\").")
    
    # Anahtar kelimeler (keywords)
    for keyword in academician.get('keywords', []):
        prolog_data.append(f"keyword(\"{academician['name']}\", \"{keyword}\").")
    
    # Yayınlar (publications)
    for publication in academician.get('publications', []):
        prolog_data.append(f"publication(\"{academician['name']}\", \"{publication}\").")

# Prolog verisini dosyaya yazma
with open("academician_facts.pl", "w", encoding="utf-8") as f:
    f.write("\n".join(prolog_data))

print("Prolog verisi dosyaya kaydedildi.")
