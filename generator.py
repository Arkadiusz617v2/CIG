import os
import json
import uuid
import shutil
from utils import pobierz_wymiary_png
from processor_2d import Item2DProcessor
from processor_3d import Item3DProcessor

class MainGeneratorEngine:
    def __init__(self):
        self.proc_2d = Item2DProcessor()
        self.proc_3d = Item3DProcessor()
        
        self.folder_obrazow = "obrazy_png"
        self.folder_wyjsciowy = "wyjscie"
        
        self.java_modele = os.path.join(self.folder_wyjsciowy, "paczka_java", "assets", "minecraft", "models", "item")
        self.java_items = os.path.join(self.folder_wyjsciowy, "paczka_java", "assets", "minecraft", "items")
        self.java_textures = os.path.join(self.folder_wyjsciowy, "paczka_java", "assets", "minecraft", "textures", "item")
        self.bedrock_textures = os.path.join(self.folder_wyjsciowy, "paczka_bedrock", "textures", "items")
        self.bedrock_root = os.path.join(self.folder_wyjsciowy, "paczka_bedrock")
        self.geyser_root = os.path.join(self.folder_wyjsciowy, "geyser")

    def przygotuj_foldery(self):
        os.makedirs(self.folder_obrazow, exist_ok=True)
        os.makedirs(self.java_modele, exist_ok=True)
        os.makedirs(self.java_items, exist_ok=True)
        os.makedirs(self.java_textures, exist_ok=True)
        os.makedirs(self.bedrock_textures, exist_ok=True)
        os.makedirs(self.geyser_root, exist_ok=True)

    def uruchom_sesje(self):
        print("====================================================")
        print("   🎛️ MODULARNY GENERATOR MINECRAFT 1.21.4+ (PY)   ")
        print("====================================================\n")

        self.przygotuj_foldery()

        pliki_png = [f for f in os.listdir(self.folder_obrazow) if f.endswith('.png')]
        if not pliki_png:
            print(f"❌ Folder '{self.folder_obrazow}' jest pusty! Wrzuć tam grafiki.")
            return

        namespace = input("1. Podaj NAMESPACE dla modeli (np. gui, custom) [Domyślnie: gui]: ").strip() or "gui"
        nazwa_paczki = input("2. Podaj NAZWĘ dla swojej paczki zasobów: ").strip() or "Custom Items Pack"
        opis_paczki = input("3. Podaj OPIS dla paczki: ").strip() or "Zbudowane w Pythonie"
        przedmiot_bazowy = input("4. Podaj ID przedmiotu bazowego (np. red_dye, paper): ").strip() or "red_dye"

        drive_in = input("\n[Google Drive] Podaj ID folderu wejściowego [Enter = Pomiń]: ").strip()
        if drive_in:
            print(f"📥 Symulacja pobierania masowego z Google Drive...")

        java_cases = []
        geyser_definitions = []
        texture_data_bedrock = {}
        komendy_do_wyswietlenia = []
        ostatni_geyser_json = {}  # Tutaj przechowamy gotowy plik wygenerowany przez procesor

        print(f"\n📂 Rozpoczęto zbiorczą sesję dla {len(pliki_png)} plików PNG.\n")

        for plik in pliki_png:
            nazwa_czysta = os.path.splitext(plik)[0]
            w, h = pobierz_wymiary_png(os.path.join(self.folder_obrazow, plik))
            
            print(f"--- Konfiguracja przedmiotu dla pliku: {plik} ---")
            if w == 32 and h == 32:
                print("🟩 Rozmiar pliku to 32x32 - format jest git!")
            else:
                print(f"ℹ️ Rozmiar pliku: {w}x{h}")
                
            odpowiedz = input(f"Zmień nazwę przedmiotu '{nazwa_czysta}' (Kliknij Enter żeby zostawić): ").strip()
            nazwa_custom = odpowiedz if odpowiedz else nazwa_czysta

            typ = input("Wybierz typ przedmiotu (1 = Płaski 2D, 2 = Przestrzenny 3D): ").strip()
            
            try:
                lod_input = input("Podaj dystans optymalizacji LOD (Bloki) [Domyślnie: 32]: ").strip()
                dystans_lod = int(lod_input) if lod_input else 32
            except ValueError:
                dystans_lod = 32

            # Kopiowanie grafik binarne
            shutil.copy(os.path.join(self.folder_obrazow, plik), os.path.join(self.java_textures, f"{nazwa_custom}.png"))
            shutil.copy(os.path.join(self.folder_obrazow, plik), os.path.join(self.bedrock_textures, f"{nazwa_custom}.png"))

            string_modelu = f"{namespace}:custom/{nazwa_custom}"

            # SILNIK TYLKO PRZEKAZUJE DANE I ODBIERA GOTOWE STRUKTURY (W TYM PEŁNY GEYSER JSON)
            if typ == "2":
                case_java_wpis, bedrock_texture_wpis, ostatni_geyser_json = self.proc_3d.przetworz(
                    nazwa_custom, string_modelu, dystans_lod, namespace, przedmiot_bazowy, geyser_definitions
                )
                java_cases.append(case_java_wpis)
                texture_data_bedrock[nazwa_custom] = bedrock_texture_wpis
            else:
                model_java_json, case_java_wpis, bedrock_texture_wpis, ostatni_geyser_json = self.proc_2d.przetworz(
                    nazwa_custom, string_modelu, namespace, przedmiot_bazowy, geyser_definitions
                )
                java_cases.append(case_java_wpis)
                texture_data_bedrock[nazwa_custom] = bedrock_texture_wpis
                
                # Zapis pojedynczego pliku modelu Javy 2D
                with open(os.path.join(self.java_modele, f"{nazwa_custom}.json"), "w", encoding="utf-8") as f:
                    json.dump(model_java_json, f, indent=2)

            cmd = f'/give @s {przedmiot_bazowy}[item_model="{string_modelu}"]'
            komendy_do_wyswietlenia.append((nazwa_custom, cmd))
            print(f"✅ Przedmiot '{nazwa_custom}' pomyślnie dodany do plików.\n")

        # ZAPIS ZBIORCZY PLIKÓW KOŃCOWYCH
        glowny_item_java = {
            "model": {
                "type": "minecraft:select", "property": "minecraft:item_model",
                "cases": java_cases, "fallback": {"type": "minecraft:model", "model": f"minecraft:item/{przedmiot_bazowy}"}
            }
        }
        with open(os.path.join(self.java_items, f"{przedmiot_bazowy}.json"), "w", encoding="utf-8") as f:
            json.dump(glowny_item_java, f, indent=2)

        with open(os.path.join(self.folder_wyjsciowy, "paczka_java", "pack.mcmeta"), "w", encoding="utf-8") as f:
            json.dump({"pack": {"pack_format": 46, "description": opis_paczki}}, f, indent=2)

        os.makedirs(os.path.join(self.bedrock_root, "textures"), exist_ok=True)
        nazwa_bez_spacji = nazwa_paczki.lower().replace(" ", "_")
        
        with open(os.path.join(self.bedrock_root, "textures", "item_texture.json"), "w", encoding="utf-8") as f:
            json.dump({"resource_pack_name": nazwa_bez_spacji, "texture_name": "atlas.items", "texture_data": texture_data_bedrock}, f, indent=2)

        manifest_json = {
            "format_version": 2,
            "header": {"description": opis_paczki, "name": nazwa_paczki, "uuid": str(uuid.uuid4()), "version": [1, 0, 0], "min_engine_version": [1, 21, 40]},
            "modules": [{"description": opis_paczki, "type": "resources", "uuid": str(uuid.uuid4()), "version": [1, 0, 0]}]
        }
        with open(os.path.join(self.bedrock_root, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest_json, f, indent=2)

        # SILNIK ZAPISUJE GOTOWY PLIK ZWRÓCONY PRZEZ PROCESOR
        with open(os.path.join(self.geyser_root, "geyser_mappings.json"), "w", encoding="utf-8") as f:
            json.dump(ostatni_geyser_json, f, indent=2)

        drive_out = input("[Google Drive] Podaj ID folderu wyjściowego (Takeout) [Enter = Pomiń]: ").strip()
        if drive_out:
            print(f"📤 Symulacja wysyłania plików na Google Drive...")

        print("\n====================================================")
        print("🎉 SESJA ZAKOŃCZONA! KOMENDY DO PRZYWOŁANIA PRZEDMIOTÓW:")
        print("====================================================")
        for nazwa, komenda in komendy_do_wyswietlenia:
            print(f"🔹 {nazwa}:\n   {komenda}\n")
        print("====================================================")

if __name__ == "__main__":
    engine = MainGeneratorEngine()
    engine.uruchom_sesje()
