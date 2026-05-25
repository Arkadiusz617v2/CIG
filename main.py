import os
import secrets
import argparse
import shutil

# Import Twoich 3 osobnych, odizolowanych plików kompilatorów
from bedrock_compilator import BedrockCompilator
from java_compilator import JavaCompilator
from geyser_compilator import GeyserCompilator

def generuj_losowy_hash(dlugosc=12):
    """Generuje unikalny ciąg znaków chroniący paczkę przed wyciągnięciem tekstur."""
    znaki = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(secrets.choice(znaki) for _ in range(dlugosc))

def main():
    print("====================================================")
    print("   🎛️ LOKALNY SILNIK KOMPILACJI PLIKÓW PNG (1.21.4+) ")
    print("====================================================\n")

    # Rejestracja standardowych argumentów startowych z menu Actions
    parser = argparse.ArgumentParser(description="Minecraft 1.21.4+ Pack Generator")
    parser.add_argument("-n", "--namespace", default="gui", help="Prefix/Namespace dla modeli")
    parser.add_argument("-b", "--base", default="red_dye", help="ID przedmiotu bazowego z Javy (Vanilla)")
    parser.add_argument("-p", "--packname", default="Custom Items Pack", help="Nazwa tworzonej paczki zasobów")
    parser.add_argument("-o", "--description", default="Zbudowane za pomoca generatora", help="Opis paczki")
    args = parser.parse_args()

    # Ścieżka źródłowa, do której Twoja strona WWW wrzuciła czyste pliki .png
    folder_source = "obrazy_png"
    folder_final_gen = "GEN"
    nazwa_bezpieczna = args.packname.replace(" ", "_")
    folder_projektu = os.path.join(folder_final_gen, nazwa_bezpieczna)

    # Sprawdzamy czy folder źródłowy w ogóle istnieje
    if not os.path.exists(folder_source):
        os.makedirs(folder_source, exist_ok=True)
        print(f"📁 Folder źródłowy '{folder_source}' był pusty.")
        print("👉 Upewnij się, że strona Drag & Drop przesłała pliki graficzne przed uruchomieniem.")
        return

    # Skanujemy czyste, fizyczne pliki graficzne na dysku
    pliki_png = [f for f in os.listdir(folder_source) if f.endswith('.png')]
    if not pliki_png:
        print(f"❌ Blad: Brak plików tekstur .png w katalogu '{folder_source}'!")
        return

    # Generujemy jeden bezpieczny hasz sesji do binarnego maskowania nazw plików
    token_zabezpieczajacy = generuj_losowy_hash()
    print(f"🔒 Klucz ochrony tekstur (Obfuscation): {token_zabezpieczajacy}")

    # Przygotowanie struktur wyjściowych w folderze GEN
    os.makedirs(folder_final_gen, exist_ok=True)
    shutil.rmtree(folder_projektu, ignore_errors=True)
    os.makedirs(folder_projektu, exist_ok=True)

    # 🚀 URUCHOMIENIE KOMPILATORÓW (Zapisują dane bezpośrednio wewnątrz folderu projektu w GEN)
    bedrock_runner = BedrockCompilator(folder_projektu)
    bedrock_runner.kompiluj(args.packname, args.description, token_zabezpieczajacy, folder_source, pliki_png)

    java_runner = JavaCompilator(folder_projektu)
    java_runner.kompiluj(args.packname, args.description, token_zabezpieczajacy, folder_source, pliki_png, args.namespace, args.base)

    geyser_runner = GeyserCompilator(folder_projektu)
    geyser_runner.kompiluj(token_zabezpieczajacy, pliki_png, args.namespace, args.base)

    # 📝 REJESTRACJA KOMEND GIVE ORAZ GENEROWANIE KONFIGURACJI DELUXEMENUS
    komendy = []
    gui_items_yml = []
    aktualny_slot = 10

    for plik in pliki_png:
        nazwa_czysta = os.path.splitext(plik)[0]
        # Tworzymy zsynchronizowany, unikalny string modelu (np. gui:hash_miecz)
        string_modelu = f"{args.namespace}:{token_zabezpieczajacy}_{nazwa_czysta}"
        
        komendy.append(f"🔹 {nazwa_czysta}:\n/give @s {args.base}[item_model=\"{string_modelu}\"]")
        
        gui_items_yml.append(
            f"  przedmiot_{nazwa_czysta}:\n"
            f"    material: {args.base.upper()}\n"
            f"    slot: {aktualny_slot}\n"
            f"    item_model: '{string_modelu}'\n"
            f"    display_name: '&aCustom {nazwa_czysta.capitalize()}'\n"
            f"    lore:\n"
            f"      - '&7Wygenerowano automatycznie przez strone'\n"
            f"      - '&7Generator 1.21.4+'"
        )
        aktualny_slot += 1

    # Zapisywanie commands.txt w katalogu paczki
    with open(os.path.join(folder_projektu, "commands.txt"), "w", encoding="utf-8") as f:
        f.write("=== WYGENEROWANE KOMENDY DLA TEJ SESJI (Minecraft 1.21.4+) ===\n\n" + "\n\n".join(komendy))

    # Zapisywanie pliku deluxmenus_item_gui.yml w katalogu paczki
    with open(os.path.join(folder_projektu, "deluxmenus_item_gui.yml"), "w", encoding="utf-8") as f:
        f.write("# ====================================================\n"
                "# 🚀 GOTOWA KONFIGURACJA GEYSER/JAVA POD DELUXEMENUS\n"
                "# ====================================================\n\n"
                "menu_title: '&8Moje Customowe Przedmioty'\n"
                "open_command: custommenu\n"
                "size: 54\n\n"
                "items:\n" + "\n".join(gui_items_yml))
    print("  ✔️ Wygenerowano plik konfiguracyjny deluxmenus_item_gui.yml w folderze GEN.")

    # 📦 PAKOWANIE KOŃCOWE FOLDERÓW ROBOCZYCH DO CZYSCHYCH ARCHIWÓW ZIP
    path_java_tmp = os.path.join(folder_projektu, "java_compilator_folder")
    path_bedrock_tmp = os.path.join(folder_projektu, "bedrock_compilator_folder")
    
    shutil.move(os.path.join(folder_projektu, "java_compilator_folder"), path_java_tmp)
    shutil.move(os.path.join(folder_projektu, "bedrock_compilator_folder"), path_bedrock_tmp)

    shutil.make_archive(os.path.join(folder_projektu, args.packname), 'zip', path_java_tmp)
    shutil.make_archive(os.path.join(folder_projektu, f"bedrock_{nazwa_bezpieczna}"), 'zip', path_bedrock_tmp)

    # Usuwamy foldery robocze, zostawiając w folderze paczki tylko czyste ZIPy, komendy i gui.yml
    shutil.rmtree(path_java_tmp, ignore_errors=True)
    shutil.rmtree(path_bedrock_tmp, ignore_errors=True)

    print(f"\n====================================================")
    print("🎉 KOMPILACJA ZAKOŃCZONA SUKCESEM!")
    print(f"📁 Wszystkie gotowe paczki oraz pliki konfiguracyjne znajdziesz w: 'GEN/{nazwa_bezpieczna}/'")
    print("====================================================")

if __name__ == "__main__":
    main()
