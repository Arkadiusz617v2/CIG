import os
import json
import uuid
import shutil

class BedrockCompilator:
    def __init__(self, folder_final):
        self.folder_final = folder_final

    def kompiluj(self, nazwa_paczki, opis_paczki, token_zabezpieczajacy, folder_source, pliki_png):
        print("\n⚙️ [Bedrock Compilator] Rozpoczynam budowanie struktur Bedrock...")
        
        # 🟢 Zapis bezpośrednio do GEN/bedrock_compilator_folder
        bedrock_folder = os.path.join(self.folder_final, "bedrock_compilator_folder")
        bedrock_textures_dir = os.path.join(bedrock_folder, "textures", "items", token_zabezpieczajacy)
        
        os.makedirs(bedrock_textures_dir, exist_ok=True)

        uuid_header = str(uuid.uuid4())
        uuid_module = str(uuid.uuid4())
        
        manifest_json = {
            "format_version": 2,
            "header": {
                "description": opis_paczki,
                "name": nazwa_paczki,
                "uuid": uuid_header,
                "version": [1, 0, 0],
                "min_engine_version": [1, 20, 0]
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

        texture_data = {}
        for plik in pliki_png:
            nazwa_czysta = os.path.splitext(plik)[0]
            texture_data[nazwa_czysta] = {
                "textures": f"textures/items/{token_zabezpieczajacy}/{nazwa_czysta}"
            }
            shutil.copy(os.path.join(folder_source, plik), os.path.join(bedrock_textures_dir, plik))

        item_texture_json = {
            "resource_pack_name": nazwa_paczki.lower().replace(" ", "_"),
            "texture_name": "atlas.items",
            "texture_data": texture_data
        }

        os.makedirs(os.path.join(bedrock_folder, "textures"), exist_ok=True)
        with open(os.path.join(bedrock_folder, "textures", "item_texture.json"), "w", encoding="utf-8") as f:
            json.dump(item_texture_json, f, indent=2)
            
        print("  ✔️ Folder 'bedrock_compilator_folder' został utworzony w folderze GEN.")
