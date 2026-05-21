import os
import json
import uuid
import struct
import tkinter as tk
from tkinter import messagebox, filedialog, ttk

def pobierz_wymiary_png(sciezka_pliku):
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
        self.root.title("Minecraft 1.21.4+ Pack Creator")
        self.root.geometry("520x450")
        self.root.resizable(False, False)
        
        # Zmienne przechowujące dane z okienka
        self.ikona_path = tk.StringVar()
        self.item_bazowy = tk.StringVar(value="red_dye")
        
        # --- Interfejs Graficzny ---
        # 1. Nazwa i opis paczki
        tk.Label(root, text="Nazwa paczki zasobów:", font=("Arial", 10, "bold")).place(x=20, y=20)
        self.entry_nazwa = tk.Entry(root, width=50)
        self.entry_nazwa.insert(0, "Custom Items Pack")
        self.entry_nazwa.place(x=20, y=40)
        
        tk.Label(root, text="Opis paczki zasobów:", font=("Arial", 10, "bold")).place(x=20, y=75)
        self.entry_opis = tk.Entry(root, width=50)
        self.entry_opis.insert(0, "Wygenerowane przez Custom Creator")
        self.entry_opis.place(x=20, y=95)
        
        # 2. Wybór ikony paczki
        tk.Label(root, text="Ikona paczki (Opcjonalnie, plik .png):", font=("Arial", 10, "bold")).place(x=20, y=130)
        self.entry_ikona = tk.Entry(root, textvariable=self.ikona_path, width=38)
        self.entry_ikona.place(x=20, y=150)
        tk.Button(root, text="Przeglądaj...", command=self.wybierz_ikone).place(x=400, y=146)
        
        # 3. Wybór przedmiotu bazowego (Menu rozwijane)
        tk.Label(root, text="Wybierz przedmiot bazowy (Vanilla):", font=("Arial", 10, "bold")).place(x=20, y=190)
        items_lista = ["red_dye", "grey_stained_glass", "iron_nugget", "paper", "stick"]
        self.combo_item = ttk.Combobox(root, textvariable=self.item_bazowy, values=items_lista, width=47, state="readonly")
        self.combo_item.place(x=20, y=210)
        
        # 4. Suwak optymalizacji odległości (LOD)
        tk.Label(root, text="Regulator odległości 3D -> 2D (Bloki):", font=("Arial", 10, "bold")).place(x=20, y=250)
        self.suwak_lod = tk.Scale(root, from_=8, to=128, orient=tk.HORIZONTAL, length=470)
        self.suwak_lod.set(32)
        self.suwak_lod.place(x=20, y=270)
        
        # 5. Główny przycisk startu
        self.btn_generuj = tk.Button(root, text="🚀 GENERUJ WSZYSTKIE PACZKI", font=("Arial", 12, "bold"), bg="#2ecc71", fg="white", height=2, width=42, command=self.uruchom_generowanie)
        self.btn_generuj.place(x=20, y=350)
        
    def wybierz_ikone(self):
        sciezka = filedialog.askopenfilename(filetypes=[("Obrazki PNG", "*.png")])
        if sciezka:
            self.ikona_path.set(sciezka)
            
    def uruchom_generowanie(self):
        FOLDER_OBRAZOW = "obrazy_png"
        if not os.path.exists(FOLDER_OBRAZOW) or not [f for f in os.listdir(FOLDER_OBRAZOW) if f.endswith('.png')]:
            os.makedirs(FOLDER_OBRAZOW, exist_ok=True)
            messagebox.showerror("Błąd", f"Folder '{FOLDER_OBRAZOW}' jest pusty!\nWrzuć tam grafiki .png swoich przedmiotów przed kliknięciem.")
            return

        nazwa_paczki = self.entry_nazwa.get().strip() or "Custom Pack"
        opis_paczki = self.entry_opis.get().strip() or "Custom Description"
        ikona_sciezka = self.ikona_path.get()
        przedmiot_bazowy = self.item_bazowy.get()
        dystans_lod = self.suwak_lod.get()
        namespace = "gui"
        
        # Budowanie folderów wyjściowych
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

        # Kopiowanie ikony paczki
        if ikona_sciezka and os.path.exists(ikona_sciezka):
            with open(ikona_sciezka, 'rb') as src:
                img_data = src.read()
            with open(os.path.join("wyjscie", "paczka_java", "pack.png"), 'wb') as dst:
                dst.write(img_data)
            with open(os.path.join(WYJSCIE_BEDROCK_ROOT, "pack_icon.png"), 'wb') as dst:
                dst.write(img_data)

        pliki_png = [f for f in os.listdir(FOLDER_OBRAZOW) if f.endswith('.png')]
        java_cases = []
        geyser_definitions = []
        texture_data_bedrock = {}

        for plik in pliki_png:
            nazwa_czysta = os.path.splitext(plik)[0]
            string_modelu = f"{namespace}:custom/{nazwa_czysta}"
            
            with open(os.path.join(FOLDER_OBRAZOW, plik), 'rb') as src:
                obraz_bajt = src.read()
            with open(os.path.join(WYJSCIE_JAVA_TEXTURES, plik), 'wb') as dst:
                dst.write(obraz_bajt)
            with open(os.path.join(WYJSCIE_BEDROCK_TEXTURES, plik), 'wb') as dst:
                dst.write(obraz_bajt)

            # Generowanie plików dla Javy z uwzględnieniem suwaka dystansu LOD
            model_2d_java = {"parent": "minecraft:item/generated", "textures": {"layer0": f"minecraft:item/{nazwa_czysta}"}}
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

            texture_data_bedrock[nazwa_czysta] = {"textures": f"textures/items/{nazwa_czysta}"}

            geyser_wpis = {
                "bedrock_options": {"item_model": string_modelu},
                "components": {"minecraft:icon": nazwa_czysta},
                "type": "definition"
            }
            geyser_definitions.append(geyser_wpis)

        # Zapis plików zbiorczych (mcmeta, items, item_texture, manifest, geyser)
        glowny_item_java = {"model": {"type": "minecraft:select", "property": "minecraft:item_model", "cases": java_cases, "fallback": {"type": "minecraft:model", "model": f"minecraft:item/{przedmiot_bazowy}"}}}
        with open(os.path.join(WYJSCIE_JAVA_ITEMS, f"{przedmiot_bazowy}.json"), "w", encoding="utf-8") as f:
            json.dump(glowny_item_java, f, indent=2)

        with open(os.path.join("wyjscie", "paczka_java", "pack.mcmeta"), "w", encoding="utf-8") as f:
            json.dump({"pack": {"pack_format": 46, "description": opis_paczki}}, f, indent=2)

        os.makedirs(os.path.join(WYJSCIE_BEDROCK_ROOT, "textures"), exist_ok=True)
        with open(os.path.join(WYJSCIE_BEDROCK_ROOT, "textures", "item_texture.json"), "w", encoding="utf-8") as f:
            json.dump({"resource_pack_name": nazwa_paczki.lower().replace(" ", "_"), "texture_name": "atlas.items", "texture_data": texture_data_bedrock}, f, indent=2)

        manifest_json = {"format_version": 2, "header": {"description": opis_paczki, "name": nazwa_paczki, "uuid": str(uuid.uuid4()), "version": [1, 0, 0], "min_engine_version": [1, 21, 40]}, "modules": [{"description": opis_paczki, "type": "resources", "uuid": str(uuid.uuid4()), "version": [1, 0, 0]}]}
        with open(os.path.join(WYJSCIE_BEDROCK_ROOT, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest_json, f, indent=2)

        with open(os.path.join(WYJSCIE_GEYSER, "geyser_mappings.json"), "w", encoding="utf-8") as f:
            json.dump({"format_version": 2, "items": {f"minecraft:{przedmiot_bazowy}": [{"bedrock_identifier": f"{namespace}:{przedmiot_bazowy}", "model": "minecraft:geometry.item_2d", "definitions": geyser_definitions}]}}, f, indent=2)

        messagebox.showinfo("Sukces", "🎉 Wszystkie paczki i mapowania Geysera zostały pomyślnie wygenerowane w folderze 'wyjscie'!")

if __name__ == "__main__":
    root = tk.Tk()
    app = GeneratorApp(root)
    root.mainloop()

