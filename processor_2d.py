class Item2DProcessor:
    """Zarządza w 100% generowaniem struktur wyłącznie dla przedmiotów płaskich 2D."""
    
    def przetworz(self, nazwa_custom, string_modelu, namespace, przedmiot_bazowy, geyser_definitions):
        # 1. Indywidualny model Java (Plik JSON)
        model_java_json = {
            "parent": "minecraft:item/generated",
            "textures": {
                "layer0": f"minecraft:item/{nazwa_custom}"
            }
        }
        
        # 2. Wpis do zbiorczego selektora Javy 1.21.4+ (Case)
        case_java_wpis = {
            "when": string_modelu,
            "model": {
                "type": "minecraft:model",
                "model": f"minecraft:item/{nazwa_custom}"
            }
        }
        
        # 3. Wpis tekstury bezpośrednio dla Bedrocka (item_texture.json)
        bedrock_texture_wpis = {
            "textures": f"textures/items/{nazwa_custom}"
        }
        
        # 4. Nowy wpis definicji, który dodajemy do listy
        geyser_definitions.append({
            "bedrock_options": {
                "item_model": string_modelu
            },
            "components": {
                "minecraft:icon": nazwa_custom
            },
            "type": "definition"
        })
        
        # 5. GENEROWANIE PEŁNEGO PLIKU GEYSERA bezpośrednio w klasie procesora
        geyser_mappings_json = {
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
        
        return model_java_json, case_java_wpis, bedrock_texture_wpis, geyser_mappings_json
