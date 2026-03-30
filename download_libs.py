"""
Télécharge les librairies JS localement pour fonctionnement hors-ligne.
Usage : python download_libs.py
Les fichiers sont placés dans ./static/
"""
import urllib.request
import os

os.makedirs("static", exist_ok=True)

libs = {
    "papaparse.min.js": "https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js",
    "xlsx.full.min.js": "https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js",
    "mermaid.min.js": "https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.6.1/mermaid.min.js",
    "jspdf.umd.min.js": "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js",
}

for filename, url in libs.items():
    path = os.path.join("static", filename)
    print(f"Téléchargement {filename}...", end=" ")
    urllib.request.urlretrieve(url, path)
    size = os.path.getsize(path) // 1024
    print(f"✓ {size} Ko")

print("\nToutes les librairies sont dans ./static/")
print("L'outil fonctionnera désormais sans accès internet.")
