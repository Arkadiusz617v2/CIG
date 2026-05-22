import os
import json
import uuid
import shutil
import argparse
from utils import pobierz_wymiary_png
from processor_2d import Item2DProcessor
from processor_3d import Item3DProcessor

def main():
    parser = argparse.ArgumentParser(description="Minecraft 1.21.4+ Modular Custom Pack Generator")
    parser.add_argument("--namespace", default="gui")
    parser.add_argument("--base", default="red_dye")
    parser.add_argument("--packname", default="Custom Items Pack")
    parser.add_argument("--description", default="Wygenerowane przez GitHub")
    parser.add_argument("--type", default="1")
    parser.add_argument("--lod", type=int, default=32)
    args = parser.parse_args()

    proc_2d = Item2DProcessor()
    proc_3d = Item3DProcessor()
    
    folder_source = "obrazy_png"
    folder_output = "wyjscie"
    
    java_modele = os.path.join(folder_output, "paczka_java", "assets", "minecraft", "models", "item")
    java_items = os.path.join(folder_output, "paczka_java", "assets", "minecraft", "items")
    java_textures = os.path.join(folder_output, "paczka_java", "assets", "minecraft", "textures", "item")
    bedrock_textures = os.path.join(folder_output, "paczka_bedrock", "textures", "items")
    bedrock_root = os.path.join(folder_output, "paczka_bedrock")
    geyser_root = os.path.join(folder_output, "geyser")

    os.makedirs(folder_source, exist_ok=True)
    
    pliki_png = [f for f in os.listdir(folder_source) if f.endswith('.png')]
    if not pliki_png:
        print(f"❌ Blad: Folder '{folder_source}' jest pusty!")
        print("👉 Wrzuc pliki tekstur .png do swojego folderu i uruchom sesje ponownie.")
        return

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

    print(f"📂 Rozpoczeto zbiorcza sesje dla {len(pliki_png)} plików PNG.\n")

    for plik in pliki_png:
        nazwa_czysta = os.path.splitext(plik)[0]
        w, h = pobierz_wymiary_png(os.path.join(folder_source, plik))
        
        # 🟩 CAŁKOWICIE POPRAWIONA AKCEPTACJA ROZMIARÓW (Wsparcie dla 16x16, 32x32 i innych)
        if w is not None and h is not None:
            print(f"  » {plik}: Wczytano format {w}x{h} - rozmiar jest w 100% git!")
        else:
            print(f"  » {plik}: Wczytano plik graficzny tekstury.")

        string_modelu = f"{args.namespace}:custom/{nazwa_czysta}"

        shutil.copy(os.path.join(folder_source, plik), os.path.join(java_textures, f"{nazwa_czysta}.png"))
        shutil.copy(os.path.join(folder_source, plik), os.path.join(bedrock_textures, f"{nazwa_czysta}.png"))

        if args.type == "2": # Tryb 3D z odległością LOD
            case_java_wpis, bedrock_texture_wpis, ostatni_geyser_json = proc_3d.przetworz(
                nazwa_czysta, string_modelu, args.lod, args.namespace, args.base, geyser_definitions
            )
            java_cases.append(case_java_wpis)
            texture_data_bedrock[nazwa_czysta] = bedrock_texture_wpis
        else: # Standardowy tryb 2D dla płaskich ikon
            model_java_json, case_java_wpis, bedrock_texture_wpis, ostatni_geyser_json = proc_2d.przetworz(
                nazwa_czysta, string_modelu, args.namespace, args.base, geyser_definitions
            )
            java_cases.append(case_java_wpis)
            texture_data_bedrock[nazwa_czysta] = bedrock_texture_wpis
            
            with open(os.path.join(java_modele, f"{nazwa_czysta}.json"), "w", encoding="utf-8") as f:
                json.dump(model_java_json, f, indent=2)

        # 📋 AUTOMATYCZNE GENEROWANIE KOMENDY GIVE (Format 1.21.4+)
        cmd = f'/give @s {args.base}[item_model="{string_modelu}"]'
        komendy_do_wyswietlenia.append((nazwa_czysta, cmd))

    # ZAPIS ZBIORCZY PLIKÓW KOŃCOWYCH
    glowny_item_java = {
        "model": {
            "type": "minecraft:select", "property": "minecraft:item_model",
            "cases": java_cases, "fallback": {"type": "minecraft:model", "model": f"minecraft:item/{args.base}"}
        }
    }
    with open(os.path.join(java_items, f"{args.base}.json"), "w", encoding="utf-8") as f:
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

    # 📣 WYŚWIETLENIE KOMEND W KONSOLI GITHUBA
    print("\n====================================================")
    print("📋 KOMENDY DO PRZYWOŁANIA PRZEDMIOTÓW (WERSJA 1.21.4+):")
    print("====================================================")
    for nazwa, komenda in komendy_do_wyswietlenia:
        print(f"🔹 Przedmiot: {nazwa}")
        print(f"   {komenda}\n")
    print("====================================================")

if __name__ == "__main__":
    main()
