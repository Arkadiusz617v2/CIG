import os
import secrets
import argparse
import shutil
import urllib.request
import re

from bedrock_compilator import BedrockCompilator
from java_compilator import JavaCompilator
from geyser_compilator import GeyserCompilator

def generuj_losowy_hash(dlugosc=12):
    znaki = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(secrets.choice(znaki) for _ in range(dlugosc))

def pobierz_z_catbox_multi_format(catbox_url, docelowy_folder):
    match = re.search(r"\/c\/([a-zA-Z0-9]+)", catbox_url)
    album_id = match.group(1) if match else catbox_url
    
    url_txt = f"https://catbox.moe{album_id}"
    print(f"🔍 [Catbox Engine] Wczytywanie albumu o ID: {album_id}...")
    
    try:
        req = urllib.request.Request(url_txt, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            
            # 🟢 POPRAWIONE WYRAŻENIE: Wyciąga z kodu Catbox zarówno pliki .png, jak i .webp!
            linki_plikow = re.findall(r'href="https://files\.catbox\.moe/([a-zA-Z0-9\.]+\.(?:png|webp))"', html)
            
            if not linki_plikow:
                print("❌ Błąd: Album Catbox jest pusty lub nie zawiera obsługiwanych plików (.png / .webp)!")
                return False
                
            print(f"🟩 Wykryto {len(linki_plikow)} kompatybilnych plików w chmurze. Pobieranie masowe...")
            
            for index, nazwa_pliku_zdalna in enumerate(linki_plikow):
                url_bezposredni = f"https://catbox.moe{nazwa_pliku_zdalna}"
                rozszerzenie = os.path.splitext(nazwa_pliku_zdalna)[1].lower()
                
                # Zabezpieczamy nazwy przedmiotów w strukturze Minecrafta
                nazwa_lokalna_czysta = f"custom_item_{index+1}"
                sciezka_zapisu = os.path.join(docelowy_folder, f"{nazwa_lokalna_czysta}{rozszerzenie}")
                
                # Pobieramy pliki binarne na serwer Actions bez żadnego oporu ze strony Catbox
                urllib.request.urlretrieve(url_bezposredni, sciezka_zapisu)
                print(f"  » Pobrano pomyślnie z chmury: {nazwa_lokalna_czysta}{rozszerzenie}")
                
            return True
            
    except Exception as e:
        print(f"❌ Serwery Catbox nie odpowiedziały na zapytanie bota Actions: {e}")
        return False

def main():
    print("====================================================")
    print("   🎛️ SYSTEM MULTI-FORMAT CATBOX AUTOMAT (1.21.4+)   ")
    print("====================================================\n")

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--namespace", default="gui")
    parser.add_argument("-b", "--base", default="red_dye")
    parser.add_argument("-p", "--packname", default="Custom Items Pack")
    parser.add_argument("-o", "--description", default="Zbudowane za pomoca generatora")
    parser.add_argument("--catbox_url", default="")
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

    if not args.catbox_url:
        print("❌ Blad: Brak podanego linku do albumu Catbox!")
        return

    # Uruchomienie zoptymalizowanego skanera dwuformatowego (PNG + WebP)
    if not pobierz_z_catbox_multi_format(args.catbox_url, folder_source):
        return

    # Skanujemy wczytane pliki (na razie traktujemy rozszerzenie elastycznie, dopóki nie wgramy Pillow)
    pliki_sesji = [f for f in os.listdir(folder_source) if f.endswith('.png') or f.endswith('.webp')]
    token_zabezpieczajacy = generuj_losowy_hash()
    print(f"🔒 Klucz ochrony tekstur (Obfuscation): {token_zabezpieczajacy}")

    bedrock_runner = BedrockCompilator(folder_projektu)
    bedrock_runner.kompiluj(args.packname, args.description, token_zabezpieczajacy, folder_source, pliki_sesji)

    java_runner = JavaCompilator(folder_projektu)
    java_runner.kompiluj(args.packname, args.description, token_zabezpieczajacy, folder_source, pliki_sesji, args.namespace, args.base)

    geyser_runner = GeyserCompilator(folder_projektu)
    geyser_runner.kompiluj(token_zabezpieczajacy, pliki_sesji, args.namespace, args.base)

    komendy = []
    gui_items_yml = []
    aktualny_slot = 10

    for plik in pliki_sesji:
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
            f"      - '&7Multi-Format Generator 1.21.4+'"
        )
        aktualny_slot += 1

    with open(os.path.join(folder_projektu, "commands.txt"), "w", encoding="utf-8") as f:
        f.write("=== WYGENEROWANE KOMENDY (Minecraft 1.21.4+) ===\n\n" + "\n\n".join(komendy))

    with open(os.path.join(folder_projektu, "deluxmenus_item_gui.yml"), "w", encoding="utf-8") as f:
        f.write("# ====================================================\n# 🚀 GOTOWA KONFIGURACJA GEYSER/JAVA POD DELUXEMENUS\n# ====================================================\n\nmenu_title: '&8Moje Customowe Przedmioty'\nopen_command: custommenu\nsize: 54\n\nitems:\n" + "\n".join(gui_items_yml))

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
