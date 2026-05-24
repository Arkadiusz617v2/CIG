import os
import json
import shutil

class JavaCompilator:
    def __init__(self, folder_wyjsciowy):
        self.folder_wyjsciowy = folder_wyjsciowy

    def kompiluj(self, opis_paczki, token_zabezpieczajacy, folder_source, pliki_png, namespace, base_item):
        print("\n⚙️ [Java Compilator] Rozpoczynam budowanie struktur dla Java Edition...")
        
        # Definiowanie ścieżek wewnątrz folderu kompilatora Javy
        java_folder = os.path.join(self.folder_wyjsciowy, "java_compilator_folder")
        java_modele_dir = os.path.join(java_folder, "assets", "minecraft", "models", "item", token_zabezpieczajacy)
        java_items_dir = os.path.join(java_folder, "assets", "minecraft", "items")
        java_textures_dir = os.path.join(java_folder, "assets", "minecraft", "textures", "item", token_zabezpieczajacy)
        
        os.makedirs(java_modele_dir, exist_ok=True)
        os.makedirs(java_items_dir, exist_ok=True)
        os.makedirs(java_textures_dir, exist_ok=True)

        # 🧱 1. BUDOWANIE PLIKU PACK.MCMETA OD ZERA (Zakres 1.21.4 do Latest)
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
        print("  ✔️ Utworzono uniwersalny plik pack.mcmeta (Format 46 -> 999).")

        java_cases = []

        # 🧱 2. DYNAMICZNA PĘTLA BUDOWANIA STRUKTUR DLA KAŻDEGO PLIKU PNG
        for plik in pliki_png:
            nazwa_czysta = os.path.splitext(plik)[0]
            string_modelu = f"{namespace}:{token_zabezpieczajacy}/{nazwa_czysta}"
            
            # Kopiowanie binarne grafiki do folderu chronionego hashem sesji
            shutil.copy(
                os.path.join(folder_source, plik),
                os.path.join(java_textures_dir, plik)
            )

            # Generowanie indywidualnego modelu przedmiotu 2D w locie
            model_2d_json = {
                "parent": "minecraft:item/generated",
                "textures": {
                    "layer0": f"minecraft:item/{token_zabezpieczajacy}/{nazwa_czysta}"
                }
            }
            
            with open(os.path.join(java_modele_dir, f"{nazwa_czysta}.json"), "w", encoding="utf-8") as f:
                json.dump(model_2d_json, f, indent=2)

            # Dokładamy kolejny czysty klocek do tabeli selektora (Cases)
            case_wpis = {
                "when": string_modelu,
                "model": {
                    "type": "minecraft:model",
                    "model": f"minecraft:item/{token_zabezpieczajacy}/{nazwa_czysta}"
                }
            }
            java_cases.append(case_wpis)

        # 🧱 3. ZAPIS JEDNEGO GŁÓWNEGO PLIKU ZBIORCZEGO (Format 1.21.4+)
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
            
        print(f"  ✔️ Zbudowano wielopoziomowy selektor dla Javy w pliku items/{base_item}.json")
        print("✅ [Java Compilator] Folder 'java_compilator_folder' został pomyślnie utworzony.")
