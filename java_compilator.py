import os
import json
import shutil

class JavaCompilator:
    def __init__(self, folder_final):
        self.folder_final = folder_final

    def kompiluj(self, opis_paczki, token_zabezpieczajacy, folder_source, pliki_png, namespace, base_item):
        print("\n⚙️ [Java Compilator] Rozpoczynam budowanie struktur dla Java Edition...")
        
        # 🟢 Zapis bezpośrednio do GEN/java_compilator_folder
        java_folder = os.path.join(self.folder_final, "java_compilator_folder")
        java_modele_dir = os.path.join(java_folder, "assets", "minecraft", "models", "item", token_zabezpieczajacy)
        java_items_dir = os.path.join(java_folder, "assets", "minecraft", "items")
        java_textures_dir = os.path.join(java_folder, "assets", "minecraft", "textures", "item", token_zabezpieczajacy)
        
        os.makedirs(java_modele_dir, exist_ok=True)
        os.makedirs(java_items_dir, exist_ok=True)
        os.makedirs(java_textures_dir, exist_ok=True)

        pack_mcmeta = {
            "pack": {
                "description": opis_paczki,
                "pack_format": 46,
                "supported_formats": {
                    "min_inclusive": 46,
                    "max_inclusive": 999
                },
                "min_format": 46,
                "max_format": 999
            }
        }
        
        with open(os.path.join(java_folder, "pack.mcmeta"), "w", encoding="utf-8") as f:
            json.dump(pack_mcmeta, f, indent=2)

        java_cases = []
        for plik in pliki_png:
            nazwa_czysta = os.path.splitext(plik)[0]
            string_modelu = f"{namespace}:{token_zabezpieczajacy}/{nazwa_czysta}"
            
            shutil.copy(os.path.join(folder_source, plik), os.path.join(java_textures_dir, plik))

            model_2d_json = {
                "parent": "minecraft:item/generated",
                "textures": {
                    "layer0": f"minecraft:item/{token_zabezpieczajacy}/{nazwa_czysta}"
                }
            }
            with open(os.path.join(java_modele_dir, f"{nazwa_czysta}.json"), "w", encoding="utf-8") as f:
                json.dump(model_2d_json, f, indent=2)

            case_wpis = {
                "when": string_modelu,
                "model": {
                    "type": "minecraft:model",
                    "model": f"minecraft:item/{token_zabezpieczajacy}/{nazwa_czysta}"
                }
            }
            java_cases.append(case_wpis)

        glowny_item_java = {
            "model": {
                "type": "minecraft:select",
                "property": "minecraft:item_model",
                "cases": java_cases,
                "fallback": {
                    "type": "minecraft:model",
                    "model": f"minecraft:item/{base_item}"
                }
            }
        }

        with open(os.path.join(java_items_dir, f"{base_item}.json"), "w", encoding="utf-8") as f:
            json.dump(glowny_item_java, f, indent=2)
            
        print("  ✔️ Folder 'java_compilator_folder' został utworzony w folderze GEN.")
