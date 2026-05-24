import os
import json

class GeyserCompilator:
    def __init__(self, folder_final):
        self.folder_final = folder_final

    def kompiluj(self, token_zabezpieczajacy, pliki_png, namespace, base_item):
        print("\n⚙️ [Geyser Compilator] Rozpoczynam składanie mapowań Geysera...")
        
        # 🟢 Zapis bezpośrednio do GEN/geyser_compilator_folder
        geyser_folder = os.path.join(self.folder_final, "geyser_compilator_folder")
        os.makedirs(geyser_folder, exist_ok=True)

        geyser_definitions = []
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
            
        print("  ✔️ Folder 'geyser_compilator_folder' został utworzony w folderze GEN.")
