import os
import secrets
import argparse
import shutil
import base64
import json
import uuid

from bedrock_compilator import BedrockCompilator
from java_compilator import JavaCompilator
from geyser_compilator import GeyserCompilator

def generuj_losowy_hash(dlugosc=12):
    znaki = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(secrets.choice(znaki) for _ in range(dlugosc))

def main():
    print("====================================================")
    print("   🎛️ SYSTEM DEKODOWANIA I SPÓJNOŚCI GEYSER/JAVA   ")
    print("====================================================\n")

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--namespace", default="gui")
    parser.add_argument("-b", "--base", default="red_dye")
    parser.add_argument("-p", "--packname", default="Custom Items Pack")
    parser.add_argument("-o", "--description", default="Zbudowane za pomoca generatora")
    parser.add_argument("--pliki_nazwy", default="")
    parser.add_argument("--pliki_tekstury", default="")
    args = parser.parse_args()

    folder_source = "obrazy_png"
    folder_final_gen = "GEN"
    nazwa_bezpieczna = args.packname.replace(" ", "_")
    folder_projektu = os.path.join(folder_final_gen, nazwa_bezpieczna)

    shutil.rmtree(folder_source, ignore_errors=True)
    os.makedirs(folder_source, exist_ok=True)
    
    os.makedirs(folder_final_gen, exist_ok=True)
    shutil.rmtree(folder_projektu, ignore_errors=True)
    os.makedirs(folder_projektu, exist_ok=True)

    if not args.pliki_nazwy or not args.pliki_tekstury:
        print("❌ Blad: Brak nazw przedmiotów lub kodów tekstur w formularzu!")
        return

    # Rozdzielanie masowych list wpisanych przez użytkownika
    nazwy_list = [n.strip() for n in args.pliki_nazwy.split(",") if n.strip()]
    kody_list = [k.strip() for k in args.pliki_tekstury.split(",") if k.strip()]

    if len(nazwy_list) != len(kody_list):
        print("❌ Blad: Liczba nazw przedmiotów nie zgadza sie z liczba wklejonych kodów tekstur!")
        return

    # 🟩 DEKODOWANIE TEKSTU I GENEROWANIE PLIKÓW PNG W LOCIE
    print("🎨 Wbudowany generator: Tworzenie plików .png z podanych kodów...")
    for nazwa, kod_b64 in zip(nazwy_list, kody_list):
        if not nazwa.endswith(".png"):
            nazwa += ".png"
            
        # Oczyszczanie kodu Base64 w razie wklejenia pełnego formatu URL (data:image/png;base64,...)
        if "base64," in kod_b64:
            kod_b64 = kod_b64.split("base64,")[1]
            
        sciezka_pliku = os.path.join(folder_source, nazwa)
        try:
            with open(sciezka_pliku, "wb") as fh:
                fh.write(base64.b64decode(kod_b64))
            print(f"  ✔️ Wygenerowano plik graficzny: {nazwa}")
        except Exception as e:
            print(f"  ❌ Blad generowania pliku {nazwa}: {e}")

    pliki_png = [f for f in os.listdir(folder_source) if f.endswith('.png')]
    if not pliki_png:
        print("❌ Blad: Nie udalo sie wygenerować zadnej tekstury z podanych danych!")
        return

    token_zabezpieczajacy = generuj_losowy_hash()
    print(f"\n🔒 Klucz ochrony (Obfuscation): {token_zabezpieczajacy}")

    # Uruchomienie zsynchronizowanych kompilatorów
    bedrock_runner = BedrockCompilator(folder_projektu)
    bedrock_runner.kompiluj(args.packname, args.description, token_zabezpieczajacy, folder_source, pliki_png)

    java_runner = JavaCompilator(folder_projektu)
    java_runner.kompiluj(args.packname, args.description, token_zabezpieczajacy, folder_source, pliki_png, args.namespace, args.base)

    geyser_runner = GeyserCompilator(folder_projektu)
    geyser_runner.kompiluj(token_zabezpieczajacy, pliki_png, args.namespace, args.base)

    komendy = []
    gui_items_yml = []
    aktualny_slot = 10

    for plik in pliki_png:
        nazwa_czysta = os.path.splitext(plik)[0]
        string_modelu = f"{args.namespace}:{token_zabezpieczajacy}_{nazwa_czysta}"
        
        komendy.append(f"🔹 {nazwa_czysta}:\n/give @s {args.base}[item_model=\"{string_modelu}\"]")
        
        gui_items_yml.append(
            f"  przedmiot_{nazwa_czysta}:\n"
            f"    material: {args.base.upper()}\n"
            f"    slot: {aktualny_slot}\n"
            f"    item_model: '{string_modelu}'\n"
            f"    display_name: '&aCustom {nazwa_czysta.capitalize()}'\n"
            f"    lore:\n"
            f"      - '&7Wygenerowano automatycznie przez'\n"
            f"      - '&7Wbudowany Generator 1.21.4+'"
        )
        aktualny_slot += 1

    with open(os.path.join(folder_projektu, "commands.txt"), "w", encoding="utf-8") as f:
        f.write("=== WYGENEROWANE KOMENDY (Minecraft 1.21.4+) ===\n\n" + "\n\n".join(komendy))

    with open(os.path.join(folder_projektu, "deluxmenus_item_gui.yml"), "w", encoding="utf-8") as f:
        f.write("# ====================================================\n# 🚀 GOTOWA KONFIGURACJA GEYSER/JAVA POD DELUXEMENUS\n# ====================================================\n\nmenu_title: '&8Moje Customowe Przedmioty'\nopen_command: custommenu\nsize: 54\n\nitems:\n" + "\n".join(gui_items_yml))

    # Pakowanie paczek do czystych archiwów .zip i czyszczenie logów
    path_java_tmp = os.path.join(folder_projektu, f"java_{nazwa_bezpieczna}_temp")
    path_bedrock_tmp = os.path.join(folder_projektu, "bedrock_temp")
    
    shutil.move(os.path.join(folder_projektu, "java_compilator_folder"), path_java_tmp)
    shutil.move(os.path.join(folder_projektu, "bedrock_compilator_folder"), path_bedrock_tmp)

    shutil.make_archive(os.path.join(folder_projektu, args.packname), 'zip', path_java_tmp)
    shutil.make_archive(os.path.join(folder_projektu, f"bedrock_{nazwa_bezpieczna}"), 'zip', path_bedrock_tmp)

    shutil.rmtree(path_java_tmp, ignore_errors=True)
    shutil.rmtree(path_bedrock_tmp, ignore_errors=True)

    print(f"\n✅ Kompilacja udana! Wszystko spakowano w folderze: GEN/{nazwa_bezpieczna}/")

if __name__ == "__main__":
    main()
