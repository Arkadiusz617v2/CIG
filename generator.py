import os
import json
import uuid
import shutil
import argparse
from utils import pobierz_wymiary_png
from processor_2d import Item2DProcessor
from processor_3d import Item3DProcessor

def main():
    # 🎛️ REJESTRACJA ARGUMENTÓW STARTOWYCH (Dokładnie jak w java2bedrock)
    parser = argparse.ArgumentParser(description="Minecraft 1.21.4+ Modular Custom Pack Generator")
    parser.add_argument("-n", "--namespace", default="gui", help="Prefix/Namespace dla modeli (np. gui, custom)")
    parser.add_argument("-b", "--base", default="red_dye", help="ID przedmiotu bazowego z Javy (np. red_dye, paper)")
    parser.add_argument("-p", "--packname", default="Custom Items Pack", help="Nazwa tworzonej paczki zasobów")
    parser.add_argument("-o", "--description", default="Zbudowane za pomoca generatora", help="Opis paczki w pliku manifestu")
    parser.add_argument("-t", "--type", default="1", choices=["1", "2"], help="Typ generowania dla calej sesji (1 = Płaski 2D, 2 = Przestrzenny 3D)")
    parser.add_argument("-l", "--lod", type=int, default=32, help="Dystans optymalizacji LOD dla przedmiotów 3D")
    args = parser.parse_args()

    proc_2d = Item2DProcessor()
    proc_3d = Item3DProcessor()
    
    # Foldery wejściowe i wyjściowe są stałym standardem programu
    folder_source = "obrazy_png"
    folder_output = "wyjscie"
    
    java_modele = os.path.join(folder_output, "paczka_java", "assets", "minecraft", "models", "item")
    java_items = os.path.join(folder_output, "paczka_java", "assets", "minecraft", "items")
    java_textures = os.path.join(folder_output, "paczka_java", "assets", "minecraft", "textures", "item")
    bedrock_textures = os.path.join(folder_output, "paczka_bedrock", "textures", "items")
    bedrock_root = os.path.join(folder_output, "paczka_bedrock")
    geyser_root = os.path.join(folder_output, "geyser")

    # Automatyczne przygotowanie środowiska
    os.makedirs(folder_source, exist_ok=True)
    
    pliki_png = [f for f in os.listdir(folder_source) if f.endswith('.png')]
    if not pliki_png:
        print(f"❌ Blad: Folder '{folder_source}' jest pusty!")
        print("👉 Wrzuc tam pliki tekstur .png swoich przedmiotów i uruchom komende ponownie.")
        return

    # Czyszczenie i tworzenie świeżych folderów wyjściowych
    shutil.rmtree(folder_output, ignore_errors=True)
    os.makedirs(java_modele, exist_ok=True)
    os.makedirs(java_items, exist_ok=True)
    os.makedirs(java_textures, exist_ok=True)
    os.makedirs(bedrock_textures, exist_ok=True)
    os.makedirs(geyser_root, exist_ok=True)

    java_cases = []
    geyser_definitions = []
    texture_data_bedrock = {}
    komendy_do_wyswietlenia = []
    ostatni_geyser_json = {}

    print(f"📂 Rozpoczeto masowe przetwarzanie dla {len(pliki_png)} tekstur...\n")

    for plik in pliki_png:
        nazwa_czysta = os.path.splitext(plik)[0]
        w, h = pobierz_wymiary_png(os.path.join(folder_source, plik))
        
        # Informacja o formacie 32x32
        if w == 32 and h == 32:
            print(f"  » {plik}: Wykryto format 32x32 (rozmiar jest jak najbardziej git!)")
        else:
            print(f"  » {plik}: Wykryto rozmiar {w}x{h}")

        string_modelu = f"{args.namespace}:custom/{nazwa_czysta}"

        # Bezpieczne kopiowanie binarne plików graficznych
        shutil.copy(os.path.join(folder_source, plik), os.path.join(java_textures, f"{nazwa_czysta}.png"))
        shutil.copy(os.path.join(folder_source, plik), os.path.join(bedrock_textures, f"{nazwa_czysta}.png"))

        # Izolacja trybów w osobnych klasach procesorów (0% konfliktów)
        if args.type == "2":
            case_java_wpis, bedrock_texture_wpis, ostatni_geyser_json = proc_3d.przetworz(
                nazwa_czysta, string_modelu, args.lod, args.namespace, args.baza, geyser_definitions
            )
            java_cases.append(case_java_wpis)
            texture_data_bedrock[nazwa_czysta] = bedrock_texture_wpis
        else:
            model_java_json, case_java_wpis, bedrock_texture_wpis, ostatni_geyser_json = proc_2d.przetworz(
                nazwa_czysta, string_modelu, args.namespace, args.baza, geyser_definitions
            )
            java_cases.append(case_java_wpis)
            texture_data_bedrock[nazwa_czysta] = bedrock_texture_wpis
            
            # Zapis unikalnego pliku modelu Javy dla przedmiotu 2D
            with open(os.path.join(java_modele, f"{nazwa_czysta}.json"), "w", encoding="utf-8") as f:
                json.dump(model_java_json, f, indent=2)

        # Generowanie komendy give
        cmd = f'/give @s {args.baza}[item_model="{string_modelu}"]'
        komendy_do_wyswietlenia.append((nazwa_czysta, cmd))

    # ZAPIS ZBIORCZY ARCHIWALNY
    glowny_item_java = {
        "model": {
            "type": "minecraft:select", "property": "minecraft:item_model",
            "cases": java_cases, "fallback": {"type": "minecraft:model", "model": f"minecraft:item/{args.baza}"}
        }
    }
    with open(os.path.join(java_items, f"{args.baza}.json"), "w", encoding="utf-8") as f:
        json.dump(glowny_item_java, f, indent=2)

    with open(os.path.join(folder_output, "paczka_java", "pack.mcmeta"), "w", encoding="utf-8") as f:
        json.dump({"pack": {"pack_format": 46, "description": args.description}}, f, indent=2)

    os.makedirs(os.path.join(bedrock_root, "textures"), exist_ok=True)
    nazwa_bez_spacji = args.packname.lower().replace(" ", "_")
    
    with open(os.path.join(bedrock_root, "textures", "item_texture.json"), "w", encoding="utf-8") as f:
        json.dump({"resource_pack_name": nazwa_bez_spacji, "texture_name": "atlas.items", "texture_data": texture_data_bedrock}, f, indent=2)

    manifest_json = {
        "format_version": 2,
        "header": {"description": args.description, "name": args.packname, "uuid": str(uuid.uuid4()), "version": [1, 0, 0], "min_engine_version": [1, 21, 40]},
        "modules": [{"description": args.description, "type": "resources", "uuid": str(uuid.uuid4()), "version": [1, 0, 0]}]
    }
    with open(os.path.join(bedrock_root, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest_json, f, indent=2)

    with open(os.path.join(geyser_root, "geyser_mappings.json"), "w", encoding="utf-8") as f:
        json.dump(ostatni_geyser_json, f, indent=2)

    print("\n====================================================")
    print("🎉 PACZKI WYGENEROWANE POMYSLNIE W FOLDERZE 'wyjscie'!")
    print("====================================================")
    for nazwa, komenda in komendy_do_wyswietlenia:
        print(f"🔹 {nazwa}:\n   {komenda}\n")
    print("====================================================")

if __name__ == "__main__":
    main()
