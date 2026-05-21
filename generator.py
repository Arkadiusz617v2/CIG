import os
import json
import uuid
import struct
import tkinter as tk
from tkinter import messagebox, filedialog, ttk

def pobierz_wymiary_png(sciezka_pliku):
    """Odczytuje wymiary obrazka PNG, aby sprawdzić czy ma format 32x32."""
    try:
        with open(sciezka_pliku, 'rb') as f:
            dane = f.read(24)
            if dane[:8] == b'\x89PNG\r\n\x1a\n' and dane[12:16] == b'IHDR':
                szerokosc, wysokosc = struct.unpack('>ii', dane[16:24])
                return szerokosc, wysokosc
    except Exception:
        pass
    return None, None

class GeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft 1.21.4+ Pack Creator (Vanilla)")
        self.root.geometry("520x480")
        self.root.resizable(False, False)
        
        self.ikona_path = tk.StringVar()
        self.item_bazowy = tk.StringVar(value="red_dye")
        
        # --- UKŁAD GRAFICZNY (GUI) ---
        tk.Label(root, text="Nazwa paczki zasobów:", font=("Arial", 10, "bold")).place(x=20, y=20)
        self.entry_nazwa = tk.Entry(root, width=50)
        self.entry_nazwa.insert(0, "Custom Items Pack")
        self.entry_nazwa.place(x=20, y=40)
        
        tk.Label(root, text="Opis paczki zasobów:", font=("Arial", 10, "bold")).place(x=20, y=75)
        self.entry_opis = tk.Entry(root, width=50)
        self.entry_opis.insert(0, "Wygenerowane przez Custom Creator")
        self.entry_opis.place(x=20, y=95)
        
        tk.Label(root, text="Ikona paczki (Opcjonalnie, plik .png):", font=("Arial", 10, "bold")).place(x=20, y=130)
        self.entry_ikona = tk.Entry(root, textvariable=self.ikona_path, width=38)
        self.entry_ikona.place(x=20, y=150)
        tk.Button(root, text="Przeglądaj...", command=self.wybierz_ikone).place(x=400, y=146)
        
        tk.Label(root, text="Wybierz przedmiot bazowy (Vanilla):", font=("Arial", 10, "bold")).place(x=20, y=190)
        items_lista = ["red_dye", "grey_stained_glass", "iron_nugget", "paper", "stick"]
        self.combo_item = ttk.Combobox(root, textvariable=self.item_bazowy, values=items_lista, width=47, state="readonly")
        self.combo_item.place(x=20, y=210)
        
        tk.Label(root, text="Regulator odległości 3D -> 2D (Bloki):", font=("Arial", 10, "bold")).place(x=20, y=250)
        self.suwak_lod = tk.Scale(root, from_=8, to=128, orient=tk.HORIZONTAL, length=470)
        self.suwak_lod.set(32)
        self.suwak_lod.place(x=20, y=270)
        
        # Sekcja informacyjna skanowania obrazków
        self.info_label = tk.Label(root, text="Status: Czekam na pliki PNG w folderze 'obrazy_png'...", font=("Arial", 9, "italic"), fg="#7f8c8d")
        self.info_label.place(x=20, y=320)
        
        self.btn_generuj = tk.Button(root, text="🚀 GENERUJ WSZYSTKIE PACZKI", font=("Arial", 12, "bold"), bg="#2ecc71", fg="white", height=2, width=42, command=self.uruchom_generowanie)
        self.btn_generuj.place(x=20, y=370)
        
        # Sprawdzamy foldery na starcie aplikacji
        self.sprawdz_pliki_wejsciowe()

    def wybierz_ikone(self):
        sciezka = filedialog.askopenfilename(filetypes=[("Obrazki PNG", "*.png")])
        if sciezka:
            self.ikona_path.set(sciezka)
            
    def sprawdz_pliki_wejsciowe(self):
        FOLDER_OBRAZOW = "obrazy_png"
        os.makedirs(FOLDER_OBRAZOW, exist_ok=True)
        pliki = [f for f in os.listdir(FOLDER_OBRAZOW) if f.endswith('.png')]
        
        if pliki:
            info_tekst = f"Wykryto {len(pliki)} plików PNG. "
            format_32 = False
            for p in pliki:
                w, h = pobierz_wymiary_png(os.path.join(FOLDER_OBRAZOW, p))
                if w == 32 and h == 32:
                    format_32 = True
            if format_32:
                info_tekst += "Wymiary 32x32 wykryte - rozmiar jest jak najbardziej git!"
            self.info_label.config(text=info_tekst, fg="#27ae60")
        else:
            self.info_label.config(text="⚠️ Folder 'obrazy_png' jest pusty! Wrzuć tam grafiki przedmiotów.", fg="#e74c3c")

    def uruchom_generowanie(self):
        FOLDER_OBRAZOW = "obrazy_png"
        pliki_png = [f for f in os.listdir(FOLDER_OBRAZOW) if f.endswith('.png')]
        
        if not pliki_png:
            messagebox.showerror("Błąd", f"Folder '{FOLDER_OBRAZOW}' jest pusty!\nWrzuć tam grafiki .png swoich przedmiotów przed generowaniem.")
            return

        nazwa_paczki = self.entry_nazwa.get().strip() or "Custom Items Pack"
        opis_paczki = self.entry_opis.get().strip() or "Wygenerowane przez Custom Creator"
        ikona_sciezka = self.ikona_path.get()
        przedmiot_bazowy = self.item_bazowy.get()
        dystans_lod = self.suwak_lod.get()
        namespace = "gui"
        nazwa_bez_spacji = nazwa_paczki.toLowerCase().replace(" ", "_") if hasattr(str, 'toLowerCase') else nazwa_paczki.lower().replace(" ", "_")

        # Ścieżki docelowe
        WYJSCIE_JAVA_MODELE = os.path.join("wyjscie", "paczka_java", "assets", "minecraft", "models", "item")
        WYJSCIE_JAVA_ITEMS = os.path.join("wyjscie", "paczka_java", "assets", "minecraft", "items")
        WYJSCIE_JAVA_TEXTURES = os.path.join("wyjscie", "paczka_java", "assets", "minecraft", "textures", "item")
        WYJSCIE_BEDROCK_TEXTURES = os.path.join("wyjscie", "paczka_bedrock", "textures", "items")
        WYJSCIE_BEDROCK_ROOT = os.path.join("wyjscie", "paczka_bedrock")
        WYJSCIE_GEYSER = os.path.join("wyjscie", "geyser")

        os.makedirs(WYJSCIE_JAVA_MODELE, exist_ok=True)
        os.makedirs(WYJSCIE_JAVA_ITEMS, exist_ok=True)
        os.makedirs(WYJSCIE_JAVA_TEXTURES, exist_ok=True)
        os.makedirs(WYJSCIE_BEDROCK_TEXTURES, exist_ok=True)
        os.makedirs(WYJSCIE_GEYSER, exist_ok=True)

        # Kopiowanie ikony pack.png / pack_icon.png
        if ikona_sciezka and os.path.exists(ikona_sciezka):
            with open(ikona_sciezka, 'rb') as src:
                img_data = src.read()
            with open(os.path.join("wyjscie", "paczka_java", "pack.png"), 'wb') as dst:
                dst.write(img_data)
            with open(os.path.join(WYJSCIE_BEDROCK_ROOT, "pack_icon.png"), 'wb') as dst:
                dst.write(img_data)

        java_cases = []
        geyser_definitions = []
        texture_data_bedrock = {}

        # Przetwarzanie obrazków z folderu wejściowego
        for plik in pliki_png:
            nazwa_czysta = os.path.splitext(plik)[0]
            string_modelu = f"{namespace}:custom/{nazwa_czysta}"
            
            # Przerzucanie obrazków do paczek
            with open(os.path.join(FOLDER_OBRAZOW, plik), 'rb') as src:
                obraz_bajt = src.read()
            with open(os.path.join(WYJSCIE_JAVA_TEXTURES, plik), 'wb') as dst:
                dst.write(obraz_bajt)
            with open(os.path.join(WYJSCIE_BEDROCK_TEXTURES, plik), 'wb') as dst:
                dst.write(obraz_bajt)

            # 1. GENEROWANIE PLIKÓW DLA JAVY (Format 1.21.4+ z regulatorem LOD)
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

            # 2. GENEROWANIE PACZKI BEDROCK
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

        # Zapis plików zbiorczych projektu dla Java Edition
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

        # Zapis plików zbiorczych projektu dla Bedrock Edition
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

        # Zapis pliku geyser_mappings.json dla serwera
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

        messagebox.showinfo("Sukces", "🎉 Wszystkie paczki i mapowania dla Geysera zostały wygenerowane w folderze 'wyjscie'!")
        self.sprawdz_pliki_wejsciowe()

if __name__ == "__main__":
    root = tk.Tk()
    app = GeneratorApp(root)
    root.mainloop()
