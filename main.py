import os
import secrets
import argparse
import shutil
from utils import pobierz_wymiary_png
from bedrock_compilator import BedrockCompilator
from java_compilator import JavaCompilator
from geyser_compilator import GeyserCompilator

def generuj_losowy_hash(dlugosc=12):
    znaki = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(secrets.choice(znaki) for _ in range(dlugosc))

def main():
    print("====================================================")
    print("   🎛️ MODULARNY KOMPILATOR PACZEK MINECRAFT 1.21.4+ ")
    print("====================================================\n")

    parser = argparse.ArgumentParser(description="Minecraft 1.21.4+ Modular Custom Pack Generator")
    parser.add_argument("-n", "--namespace", default="gui", help="Prefix/Namespace dla modeli")
    parser.add_argument("-b", "--base", default="red_dye", help="ID przedmiotu bazowego z Javy")
    parser.add_argument("-p", "--packname", default="Custom Items Pack", help="Nazwa tworzonej paczki zasobów")
    parser.add_argument("-o", "--description", default="Zbudowane za pomoca generatora", help="Opis paczki")
    parser.add_argument("-t", "--type", default="1", help="Typ przedmiotów w sesji (1 = 2D, 2 = 3D)")
    parser.add_argument("-l", "--lod", type=int, default=32, help="Dystans optymalizacji LOD")
    args = parser.parse_args()

    folder_source = "obrazy_png"
    folder_final = "GEN"  # 🟢 DZIAŁAMY TYLKO NA FOLDERZE GEN

    os.makedirs(folder_source, exist_ok=True)
    
    pliki_png = [f for f in os.listdir(folder_source) if f.endswith('.png')]
    if not pliki_png:
        print(f"❌ Blad: Folder lokalny '{folder_source}' jest pusty!")
        return

    token_zabezpieczajacy = generuj_losowy_hash()
    print(f"🔒 Wygenerowano wspólny klucz ochrony plików: {token_zabezpieczajacy}")

    # Resetujemy folder GEN na starcie nowej sesji
    shutil.rmtree(folder_final, ignore_errors=True)
    os.makedirs(folder_final, exist_ok=True)

    # 🚀 Uruchomienie kompilatorów bezpośrednio na folderze GEN
    bedrock_runner = BedrockCompilator(folder_final)
    bedrock_runner.kompiluj(args.packname, args.description, token_zabezpieczajacy, folder_source, pliki_png)

    java_runner = JavaCompilator(folder_final)
    java_runner.kompiluj(args.description, token_zabezpieczajacy, folder_source, pliki_png, args.namespace, args.base)

    geyser_runner = GeyserCompilator(folder_final)
    geyser_runner.kompiluj(token_zabezpieczajacy, pliki_png, args.namespace, args.base)

    # 📝 LISTA KOMEND I STRUKTURA GUI.YML
    komendy = []
    gui_items_yml = []
    aktualny_slot = 10 

    for plik in pliki_png:
        nazwa_czysta = os.path.splitext(plik)[0]
        string_modelu = f"{args.namespace}:{token_zabezpieczajacy}/{nazwa_czysta}"
        
        komendy.append(f"🔹 {nazwa_czysta}:\n/give @s {args.base}[item_model=\"{string_modelu}\"]")
        
        item_yml_block = (
            f"  przedmiot_{nazwa_czysta}:\n"
            f"    material: {args.base.upper()}\n"
            f"    slot: {aktualny_slot}\n"
            f"    item_model: '{string_modelu}'\n"
            f"    display_name: '&aCustom {nazwa_czysta.capitalize()}'\n"
            f"    lore:\n"
            f"      - '&7Wygenerowano automatycznie przez'\n"
            f"      - '&7Twoj Generator 1.21.4+'"
        )
        gui_items_yml.append(item_yml_block)
        aktualny_slot += 1

    # Zapisywanie commands.txt w GEN
    with open(os.path.join(folder_final, "commands.txt"), "w", encoding="utf-8") as f:
        f.write("=== WYGENEROWANE KOMENDY DLA TEJ SESJI (Minecraft 1.21.4+) ===\n\n")
        f.write("\n\n".join(komendy))

    # Zapisywanie gui.yml w GEN
    with open(os.path.join(folder_final, "gui.yml"), "w", encoding="utf-8") as f:
        f.write("# ====================================================\n")
        f.write("# 🚀 AUTORSKIE MENU SERWEROWE MINECRAFT 1.21.4+\n")
        f.write("# ====================================================\n\n")
        f.write("menu_title: '&8Moje Customowe Przedmioty'\n")
        f.write("open_command: custommenu\n")
        f.write("size: 54\n\n")
        f.write("items:\n")
        f.write("\n".join(gui_items_yml))
    print("  ✔️ Wygenerowano plik konfiguracyjny gui.yml w folderze GEN.")

    print("\n====================================================")
    print("🎉 KOMPILACJA ZAKOŃCZONA SUKCESEM!")
    print(f"📁 Wszystkie gotowe paczki oraz gui.yml trafily do folderu: '{folder_final}/'")
    print("====================================================")

if __name__ == "__main__":
    main()
