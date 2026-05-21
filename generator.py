import os
import json
import uuid
import struct

def pobierz_wymiary_png(sciezka_pliku):
    """Odczytuje wymiary obrazka PNG bezpośrednio z nagłówka pliku."""
    try:
        with open(sciezka_pliku, 'rb') as f:
            dane = f.read(24)
            if dane[:8] == b'\x89PNG\r\n\x1a\n' and dane[12:16] == b'IHDR':
                szerokosc, wysokosc = struct.unpack('>ii', dane[16:24])
                return szerokosc, wysokosc
    except Exception:
        pass
    return None, None

def generuj():
    print("====================================================")
    print("     KREATOR PACZEK MINECRAFT 1.21.4+ (VANILLA)     ")
    print("====================================================\n")

    FOLDER_OBRAZOW = "obrazy_png"
    if not os.path.exists(FOLDER_OBRAZOW):
        os.makedirs(FOLDER_OBRAZOW)
        print(f"📁 Utworzono pusty folder '{FOLDER_OBRAZOW}'.")
        print("👉 Wrzuć tam swoje pliki .png dla przedmiotów i uruchom program ponownie.")
        return

    # Pobieramy pliki .png z folderu wejściowego
    pliki_png = [f for f in os.listdir(FOLDER_OBRAZOW) if f.endswith('.png')]
    if not pliki_png:
        print(f"❌ Brak plików .png w folderze '{FOLDER_OBRAZOW}'. Wrzuć tam grafiki!")
        return

    # KROK 1: Analiza obrazków i wyświetlenie informacji o 32x32
    print("🔍 Skanowanie plików graficznych...")
    for plik in pliki_png:
        sciezka = os.path.join(FOLDER_OBRAZOW, plik)
        w, h = pobierz_wymiary_png(sciezka)
        if w == 32 and h == 32:
            print(f"  » {plik}: Wykryto format 32x32 - rozmiar jest jak najbardziej git!")
        elif w is not None:
            print(f"  » {plik}: Wykryto rozmiar {w}x{h}.")
        else:
            print(f"  » {plik}: Wczytano plik graficzny.")

    print("\n----------------------------------------------------")
    print("📝 PARAMETRY PACZKI (Interaktywna konfiguracja)")
    print("----------------------------------------------------")
    
    nazwa_paczki = input("1. Podaj NAZWĘ dla swojej paczki zasobów: ").strip() or "Custom Items Pack"
    opis_paczki = input("2. Podaj OPIS dla swojej paczki: ").strip() or "Wygenerowane przez Custom Creator"
    ikona_sciezka = input("3. Podaj ścieżkę do ikony paczki (np. ikona.png) [Opcjonalnie - Enter]: ").strip()
    
    print("\nDostępne popularne przedmioty bazowe (Vanilla):")
    print("  red_dye (Czerwony barwnik)")
    print("  grey_stained_glass (Szare szkło)")
    print("  iron_nugget (Samorodek żelaza)")
    wybor = input("4. Wybierz przedmiot bazowy [Wpisz 1, 2, 3 lub podaj własne ID przedmiotu]: ").strip()
    
    if wybor == "1":
        przedmiot_bazowy = "red_dye"
    elif wybor == "2":
        przedmiot_bazowy = "grey_stained_glass"
    elif wybor == "3":
        przedmiot_bazowy = "iron_nugget"
    elif wybor:
        przedmiot_bazowy = wybor
    else:
        przedmiot_bazowy = "red_dye"

    # Suwak LOD w wersji tekstowej
    try:
        lod_input = input("5. Podaj dystans optymalizacji LOD 3D -> 2D w blokach [Domyślnie: 32]: ").strip()
        dystans_lod = int(lod_input) if lod_input else 32
    except ValueError:
        dystans_lod = 32

    namespace = "gui"
    nazwa_bez_spacji = nazwa_paczki.lower().replace(" ", "_")

    # Definiowanie ścieżek wyjściowych
    WYJSCIE_JAVA_MODELE = os.path.join("wyjscie", "paczka_java", "assets", "minecraft", "models", "item")
    WYJSCIE_JAVA_ITEMS = os.path.join("wyjscie", "paczka_java", "assets", "minecraft", "items")
    WYJSCIE_JAVA_TEXTURES = os.path.join("wyjscie", "paczka_java", "assets", "minecraft", "textures", "item")
    WYJSCIE_BEDROCK_TEXTURES = os.path.join("wyjscie", "paczka_bedrock", "textures", "items")
    WYJSCIE_BEDROCK_ROOT = os.path.join("wyjscie", "paczka_bedrock")
    WYJSCIE_GEYSER = os.path.join("wyjscie", "geyser")

    # Tworzenie kompletnej struktury katalogów
    os.makedirs(WYJSCIE_JAVA_MODELE, exist_ok=True)
    os.makedirs(WYJSCIE_JAVA_ITEMS, exist_ok=True)
    os.makedirs(WYJSCIE_JAVA_TEXTURES, exist_ok=True)
    os.makedirs(WYJSCIE_BEDROCK_TEXTURES, exist_ok=True)
    os.makedirs(WYJSCIE_GEYSER, exist_ok=True)

    # Kopiowanie ikony paczki
    if ikona_sciezka and os.path.exists(ikona_sciezka):
        try:
            with open(ikona_sciezka, 'rb') as src:
                img_data = src.read()
            with open(os.path.join("wyjscie", "paczka_java", "pack.png"), 'wb') as dst:
                dst.write(img_data)
            with open(os.path.join(WYJSCIE_BEDROCK_ROOT, "pack_icon.png"), 'wb') as dst:
                dst.write(img_data)
            print("🎨 Pomyślnie dodano ikonę do paczek Java i Bedrock.")
        except Exception as e:
            print(f"⚠️ Nie udało się skopiować ikony: {e}")

    java_cases = []
    geyser_definitions = []
    texture_data_bedrock = {}

    print("\n----------------------------------------------------")
    print("⚙️ PROCES GENEROWANIA PLIKÓW...")
    print("----------------------------------------------------")

    for plik in pliki_png:
        nazwa_czysta = os.path.splitext(plik)[0]
        string_modelu = f"{namespace}:custom/{nazwa_czysta}"
        
        # Przerzucanie plików graficznych
        sciezka_oryginalna = os.path.join(FOLDER_OBRAZOW, plik)
        with open(sciezka_oryginalna, 'rb') as src:
            obraz_bajt = src.read()
            
        with open(os.path.join(WYJSCIE_JAVA_TEXTURES, plik), 'wb') as dst:
            dst.write(obraz_bajt)
        with open(os.path.join(WYJSCIE_BEDROCK_TEXTURES, plik), 'wb') as dst:
            dst.write(obraz_bajt)

        # 1. JAVA EDITION (Format 1.21.4+)
        model_2d_java = {
            "parent": "minecraft:item/generated",
            "textures": {
                "layer0": f"minecraft:item/{nazwa_czysta}"
            }
        }
        with open(os.path.join(WYJSCIE_JAVA_MODELE, f"{nazwa_czysta}.json"), "w", encoding="utf-8") as f:
            json.dump(model_2d_java, f, indent=2)

        case_wpis = {
            "when": string_modelu,
            "model": {
                "type": "minecraft:range_dispatch",
                "property": "minecraft:view_distance",
                "entries": [
                    {"threshold": 0, "model": {"type": "minecraft:model", "model": f"minecraft:item/{nazwa_czysta}_3d"}},
                    {"threshold": dystans_lod, "model": {"type": "minecraft:model", "model": f"minecraft:item/{nazwa_czysta}"}}
                ]
            }
        }
        java_cases.append(case_wpis)

        # 2. BEDROCK EDITION
        texture_data_bedrock[nazwa_czysta] = {
            "textures": f"textures/items/{nazwa_czysta}"
        }

        # 3. GEYSER MAPPINGS
        geyser_wpis = {
            "bedrock_options": {
                "item_model": string_modelu
            },
            "components": {
                "minecraft:icon": nazwa_czysta
            },
            "type": "definition"
        }
        geyser_definitions.append(geyser_wpis)
        print(f"✔️ Przetworzono przedmiot: {nazwa_czysta}")

    # ZAPIS PLIKÓW ZBIORCZYCH

    # Java Selector
    glowny_item_java = {
        "model": {
            "type": "minecraft:select",
            "property": "minecraft:item_model",
            "cases": java_cases,
            "fallback": {
                "type": "minecraft:model",
                "model": f"minecraft:item/{przedmiot_bazowy}"
            }
        }
    }
    with open(os.path.join(WYJSCIE_JAVA_ITEMS, f"{przedmiot_bazowy}.json"), "w", encoding="utf-8") as f:
        json.dump(glowny_item_java, f, indent=2)

    with open(os.path.join("wyjscie", "paczka_java", "pack.mcmeta"), "w", encoding="utf-8") as f:
        json.dump({"pack": {"pack_format": 46, "description": opis_paczki}}, f, indent=2)

    # Bedrock Tekstury i Manifest
    os.makedirs(os.path.join(WYJSCIE_BEDROCK_ROOT, "textures"), exist_ok=True)
    with open(os.path.join(WYJSCIE_BEDROCK_ROOT, "textures", "item_texture.json"), "w", encoding="utf-8") as f:
        json.dump({"resource_pack_name": nazwa_bez_spacji, "texture_name": "atlas.items", "texture_data": texture_data_bedrock}, f, indent=2)

    manifest_json = {
        "format_version": 2,
        "header": {
            "description": opis_paczki,
            "name": nazwa_paczki,
            "uuid": str(uuid.uuid4()),
            "version": [1, 0, 0],
            "min_engine_version": [1, 21, 40]
        },
        "modules": [
            {
                "description": opis_paczki,
                "type": "resources",
                "uuid": str(uuid.uuid4()),
                "version": [1, 0, 0]
            }
        ]
    }
    with open(os.path.join(WYJSCIE_BEDROCK_ROOT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest_json, f, indent=2)

    # Geyser Mappings
    geyser_mappings = {
        "format_version": 2,
        "items": {
            f"minecraft:{przedmiot_bazowy}": [
                {
                    "bedrock_identifier": f"{namespace}:{przedmiot_bazowy}",
                    "model": "minecraft:geometry.item_2d",
                    "definitions": geyser_definitions
                }
            ]
        }
    }
    with open(os.path.join(WYJSCIE_GEYSER, "geyser_mappings.json"), "w", encoding="utf-8") as f:
        json.dump(geyser_mappings, f, indent=2)

    print("\n====================================================")
    print("🚀 SUKCES! WSZYSTKIE PACZKI ZOSTAŁY WYGENEROWANE!")
    print("====================================================")

if __name__ == "__main__":
    generuj()
