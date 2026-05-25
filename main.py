import os
import secrets
import argparse
import shutil
import urllib.request
import re
import json
import time  # Potrzebne do odczekania przed ponowną próbą

from bedrock_compilator import BedrockCompilator
from java_compilator import JavaCompilator
from geyser_compilator import GeyserCompilator

def generuj_losowy_hash(dlugosc=12):
    znaki = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(secrets.choice(znaki) for _ in range(dlugosc))

def wyciagnij_folder_id(url):
    match = re.search(r"folders/([a-zA-Z0-9-_]+)", url)
    return match.group(1) if match else url

def skanuj_i_pobierz_z_gdrive(folder_url, docelowy_folder):
    folder_id = wyciagnij_folder_id(folder_url)
    print(f"🔍 [Google Drive] Skanowanie folderu o ID: {folder_id}...")
    
    # Próba wczytania danych z Google Drive (3 próby w razie błędu sieci)
    html = ""
    for proba in range(1, 4):
        try:
            direct_url = f"https://google.com{folder_id}"
            req = urllib.request.Request(direct_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
                break # Jeśli się udało, przerywamy pętlę prób
        except Exception as e:
            print(f"⚠️ [Próba {proba}/3] Chwilowy błąd sieci: {e}. Ponawiam za 3 sekundy...")
            if proba == 3:
                print(f"❌ Nie udalo sie przeskanować dysku po 3 próbach: {e}")
                return False
            time.sleep(3)

    pliki_do_pobrania = []
    # Wyciąganie par [ID, Nazwa] z kodu źródłowego strony Google Drive przy użyciu ulepszonego wyrażenia regularnego
    matches = re.findall(r'\["([a-zA-Z0-9-_]{25,})",\["([^"]+\.png)"', html)
    for fid, fname in matches:
        if {'id': fid, 'name': fname} not in pliki_do_pobrania:
            pliki_do_pobrania.append({'id': fid, 'name': fname})

    if not pliki_do_pobrania:
        print("❌ Brak plików .png w tym folderze lub folder nie jest publiczny (Ustaw: 'Każdy mający link').")
        return False

    print(f"🟩 Wykryto {len(pliki_do_pobrania)} plików .png w chmurze. Rozpoczynam pobieranie...")
    
    for plik in pliki_do_pobrania:
        fid = plik['id']
        fname = plik['name']
        if not fname.endswith(".png"): fname += ".png"
        
        url_pobierania = f"https://google.com{fid}"
        
        # Pobieranie pojedynczego pliku również zabezpieczamy potrójną próbą
        for proba_pliku in range(1, 4):
            try:
                urllib.request.urlretrieve(url_pobierania, os.path.join(docelowy_folder, fname))
                print(f"  » Pobrano pomyślnie: {fname}")
                break
            except Exception as e:
                if proba_pliku == 3:
                    print(f"  » ❌ Błąd pobierania pliku {fname}: {e}")
                time.sleep(1)
                
    return True

def main():
    print("====================================================")
    print("   🎛️ SYSTEM AUTOMATYZACJI I SPÓJNOŚCI GEYSER/JAVA ")
    print("====================================================\n")

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--namespace", default="gui")
    parser.add_argument("-b", "--base", default="red_dye")
    parser.add_argument("-p", "--packname", default="Custom Items Pack")
    parser.add_argument("-o", "--description", default="Zbudowane za pomoca generatora")
    parser.add_argument("--gdrive_url", default="")
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

    if not args.gdrive_url:
        print("❌ Blad: Brak linku do Google Drive!")
        return

    if not skanuj_i_pobierz_z_gdrive(args.gdrive_url, folder_source):
        return

    pliki_png = [f for f in os.listdir(folder_source) if f.endswith('.png')]
    if not pliki_png:
        print("❌ Blad: Brak tekstur do kompilacji.")
        return

    token_zabezpieczajacy = generuj_losowy_hash()
    print(f"🔒 Klucz ochrony (Obfuscation): {token_zabezpieczajacy}")

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
            f"      - '&7Generator 1.21.4+'"
        )
        aktualny_slot += 1

    with open(os.path.join(folder_projektu, "commands.txt"), "w", encoding="utf-8") as f:
        f.write("=== WYGENEROWANE KOMENDY (Minecraft 1.21.4+) ===\n\n" + "\n\n".join(komendy))

    with open(os.path.join(folder_projektu, "deluxmenus_item_gui.yml"), "w", encoding="utf-8") as f:
        f.write("menu_title: '&8Moje Customowe Przedmioty'\nopen_command: custommenu\nsize: 54\n\nitems:\n" + "\n".join(gui_items_yml))

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
