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
    parser.add_argument("-l", "--lod", type=int, default=32, help="Dystans optymalizacji LOD")
    args = parser.parse_args()

    folder_source = "obrazy_png"
    folder_output = "wyjscie"
    folder_final = "GEN" # 🟢 TWÓJ NOWY KATALOG DOCELOWY

    os.makedirs(folder_source, exist_ok=True)
    
    pliki_png = [f for f in os.listdir(folder_source) if f.endswith('.png')]
    if not pliki_png:
        print(f"📁 Utworzono pusty folder lokalny '{folder_source}'.")
        print("👉 Wrzuć tam swoje pliki tekstur .png i uruchom skrypt ponownie!")
        return

    token_zabezpieczajacy = generuj_losowy_hash()
    print(f"🔒 Wygenerowano wspólny klucz ochrony plików: {token_zabezpieczajacy}")

    shutil.rmtree(folder_output, ignore_errors=True)

    # 🚀 Uruchomienie kompilatorów
    bedrock_runner = BedrockCompilator(folder_output)
    bedrock_runner.kompiluj(args.packname, args.description, token_zabezpieczajacy, folder_source, pliki_png)

    java_runner = JavaCompilator(folder_output)
    java_runner.kompiluj(args.description, token_zabezpieczajacy, folder_source, pliki_png, args.namespace, args.base)

    geyser_runner = GeyserCompilator(folder_output)
    geyser_runner.kompiluj(token_zabezpieczajacy, pliki_png, args.namespace, args.base)

    # 📝 GENEROWANIE PLIKU COMMANDS.TXT Z LISTĄ KOMEND ZGODNYCH Z HASHEM
    komendy = []
    for plik in pliki_png:
        nazwa_czysta = os.path.splitext(plik)[0]
        string_modelu = f"{args.namespace}:{token_zabezpieczajacy}/{nazwa_czysta}"
        komendy.append(f"🔹 {nazwa_czysta}:\n/give @s {args.base}[item_model=\"{string_modelu}\"]")

    with open(os.path.join(folder_output, "commands.txt"), "w", encoding="utf-8") as f:
        f.write("=== WYGENEROWANE KOMENDY DLA TEJ SESJI (Minecraft 1.21.4+) ===\n\n")
        f.write("\n\n".join(komendy))

    # 💥 PRZENOSZENIE CAŁOŚCI DO FOLDERU GEN
    shutil.rmtree(folder_final, ignore_errors=True)
    shutil.copytree(folder_output, folder_final)
    shutil.rmtree(folder_output, ignore_errors=True)

    print("\n====================================================")
    print("🎉 KOMPILACJA ZAKOŃCZONA SUKCESEM!")
    print(f"📁 Wszystkie gotowe paczki przeszły do folderu: '{folder_final}/'")
    print("====================================================")

if __name__ == "__main__":
    main()
