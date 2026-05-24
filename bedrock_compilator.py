import os
import json
import uuid
import shutil

class BedrockCompilator:
    def __init__(self, folder_wyjsciowy):
        self.folder_wyjsciowy = folder_wyjsciowy

    def kompiluj(self, nazwa_paczki, opis_paczki, token_zabezpieczajacy, folder_source, pliki_png):
        print("\n⚙️ [Bedrock Compilator] Rozpoczynam budowanie struktur Bedrock...")
        
        # Tworzenie folderu wyjściowego z końcówką _folder zgodnie z Twoim planem
        bedrock_folder = os.path.join(self.folder_wyjsciowy, "bedrock_compilator_folder")
        bedrock_textures_dir = os.path.join(bedrock_folder, "textures", "items", token_zabezpieczajacy)
        
        os.makedirs(bedrock_textures_dir, exist_ok=True)

        # 🧱 1. BUDOWANIE MANIFEST.JSON OD ZERA (Generowanie unikalnych UUID i personalizacja)
        uuid_header = str(uuid.uuid4())
        uuid_module = str(uuid.uuid4())
        
        manifest_json = {
            "format_version": 2,
            "header": {
                "description": opis_paczki,
                "name": nazwa_paczki,
                "uuid": uuid_header,
                "version": [1, 0, 0],
                "min_engine_version": [1, 21, 40]
            },
            "modules": [
                {
                    "description": opis_paczki,
                    "type": "resources",
                    "uuid": uuid_module,
                    "version": [1, 0, 0]
                }
            ]
        }

        with open(os.path.join(bedrock_folder, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest_json, f, indent=2)
        print("  ✔️ Wygenerowano plik manifest.json z unikalnymi kluczami UUID.")

        # 🧱 2. BUDOWANIE ITEM_TEXTURE.JSON ORAZ PRZENOSZENIE OBRAZKÓW
        texture_data = {}
        
        for plik in pliki_png:
            nazwa_czysta = os.path.splitext(plik)[0]
            
            # Wpis tekstury z zsynchronizowanym hashem sesji dla pełnej ochrony przed kradzieżą
            texture_data[nazwa_czysta] = {
                "textures": f"textures/items/{token_zabezpieczajacy}/{nazwa_czysta}"
            }
            
            # Kopiowanie binarne pliku tekstury z Twojego folderu wejściowego na PC
            shutil.copy(
                os.path.join(folder_source, plik),
                os.path.join(bedrock_textures_dir, plik)
            )

        item_texture_json = {
            "resource_pack_name": nazwa_paczki.lower().replace(" ", "_"),
            "texture_name": "atlas.items",
            "texture_data": texture_data
        }

        os.makedirs(os.path.join(bedrock_folder, "textures"), exist_ok=True)
        with open(os.path.join(bedrock_folder, "textures", "item_texture.json"), "w", encoding="utf-8") as f:
            json.dump(item_texture_json, f, indent=2)
            
        print(f"  ✔️ Złożono i zapisano lokalnie plik item_texture.json dla {len(pliki_png)} przedmiotów.")
        print("✅ [Bedrock Compilator] Folder 'bedrock_compilator_folder' jest gotowy.")
