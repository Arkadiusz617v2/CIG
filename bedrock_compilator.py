import os
import json
import uuid
import shutil

class BedrockCompilator:
    def __init__(self, folder_projektu):
        self.folder_projektu = folder_projektu

    def kompiluj(self, nazwa_paczki, opis_paczki, token_zabezpieczajacy, folder_source, pliki_png):
        bedrock_folder = os.path.join(self.folder_projektu, "bedrock_compilator_folder")
        bedrock_textures_dir = os.path.join(bedrock_folder, "textures", "items")
        os.makedirs(bedrock_textures_dir, exist_ok=True)

        manifest_json = {
            "format_version": 2,
            "header": {
                "description": opis_paczki, "name": nazwa_paczki,
                "uuid": str(uuid.uuid4()), "version": [1, 0, 0], "min_engine_version": [1, 20, 0]
            },
            "modules": [
                {
                    "description": opis_paczki, "type": "resources",
                    "uuid": str(uuid.uuid4()), "version": [1, 0, 0]
                }
            ]
        }
        with open(os.path.join(bedrock_folder, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest_json, f, indent=2)

        texture_data = {}
        for plik in pliki_png:
            nazwa_czysta = os.path.splitext(plik)[0]
            nazwa_zabezpieczona = f"{token_zabezpieczajacy}_{nazwa_czysta}"
            
            texture_data[nazwa_czysta] = {
                "textures": f"textures/items/{nazwa_zabezpieczona}"
            }
            shutil.copy(os.path.join(folder_source, plik), os.path.join(bedrock_textures_dir, f"{nazwa_zabezpieczona}.png"))

        os.makedirs(os.path.join(bedrock_folder, "textures"), exist_ok=True)
        with open(os.path.join(bedrock_folder, "textures", "item_texture.json"), "w", encoding="utf-8") as f:
            json.dump({"resource_pack_name": nazwa_paczki.lower().replace(" ", "_"), "texture_name": "atlas.items", "texture_data": texture_data}, f, indent=2)
