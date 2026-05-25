import os
import json

class GeyserCompilator:
    def __init__(self, folder_projektu):
        self.folder_projektu = folder_projektu

    def kompiluj(self, token_zabezpieczajacy, pliki_png, namespace, base_item):
        geyser_definitions = []
        for plik in pliki_png:
            nazwa_czysta = os.path.splitext(plik)[0]
            # Pełna spójność ze zsynchronizowanym hashem z plików Javy i Bedrocka
            nazwa_zabezpieczona = f"{token_zabezpieczajacy}_{nazwa_czysta}"
            string_modelu = f"{namespace}:{nazwa_zabezpieczona}"
            
            geyser_definitions.append({
                "bedrock_options": { "item_model": string_modelu },
                "components": { "minecraft:icon": nazwa_czysta },
                "type": "definition"
            })

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

        # 🟢 Zmiana: Zapis pliku bezpośrednio w folderze projektu, bez robienia syfu i podfolderów
        with open(os.path.join(self.folder_projektu, "geyser_mappings.json"), "w", encoding="utf-8") as f:
            json.dump(geyser_mappings_json, f, indent=2)
