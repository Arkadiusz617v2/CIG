import os
import json

class GeyserCompilator:
    def __init__(self, folder_wyjsciowy):
        self.folder_wyjsciowy = folder_wyjsciowy

    def kompiluj(self, token_zabezpieczajacy, pliki_png, namespace, base_item):
        print("\n⚙️ [Geyser Compilator] Rozpoczynam składanie mapowań Geysera...")
        
        geyser_folder = os.path.join(self.folder_wyjsciowy, "geyser_compilator_folder")
        os.makedirs(geyser_folder, exist_ok=True)

        geyser_definitions = []

        # 🧱 DYNAMICZNE BUDOWANIE TABLICY DEFINICJI
        for plik in pliki_png:
            nazwa_czysta = os.path.splitext(plik)[0]
            string_modelu = f"{namespace}:{token_zabezpieczajacy}/{nazwa_czysta}"
            
            def_wpis = {
                "bedrock_options": {
                    "item_model": string_modelu
                },
                "components": {
                    "minecraft:icon": nazwa_czysta
                },
                "type": "definition"
            }
            geyser_definitions.append(def_wpis)

        # Tworzenie pełnego, nadrzędnego szkieletu pliku Geysera w kodzie
        geyser_mappings_json = {
            "format_version": 2,
            "items": {
                f"minecraft:{base_item}": [
                    {
                        "bedrock_identifier": f"{namespace}:{base_item}",
                        "model": "minecraft:geometry.item_2d",
                        "definitions": geyser_definitions
                    }
                ]
            }
        }

        with open(os.path.join(geyser_folder, "geyser_mappings.json"), "w", encoding="utf-8") as f:
            json.dump(geyser_mappings_json, f, indent=2)
            
        print("  ✔️ Plik geyser_mappings.json (Format API v2) został w całości złożony w kodzie.")
        print("✅ [Geyser Compilator] Folder 'geyser_compilator_folder' jest gotowy.")
