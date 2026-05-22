class Item3DProcessor:
    """Zarządza w 100% generowaniem struktur wyłącznie dla przedmiotów przestrzennych 3D."""
    
    def przetworz(self, nazwa_custom, string_modelu, dystans_lod, namespace, przedmiot_bazowy, geyser_definitions):
        # 1. Wpis Java z wbudowaną optymalizacją odległości (LOD)
        case_java_wpis = {
            "when": string_modelu,
            "model": {
                "type": "minecraft:range_dispatch",
                "property": "minecraft:view_distance",
                "entries": [
                    {
                        "threshold": 0,
                        "model": {
                            "type": "minecraft:model",
                            "model": f"minecraft:item/{nazwa_custom}_3d"
                        }
                    },
                    {
                        "threshold": dystans_lod,
                        "model": {
                            "type": "minecraft:model",
                            "model": f"minecraft:item/{nazwa_custom}"
                        }
                    }
                ]
            }
        }
        
        # 2. Wpis tekstury dla Bedrocka (item_texture.json)
        bedrock_texture_wpis = {
            "textures": f"textures/items/{nazwa_custom}"
        }
        
        # 3. Nowy wpis definicji, który dodajemy do listy
        geyser_definitions.append({
            "bedrock_options": {
                "item_model": string_modelu
            },
            "components": {
                "minecraft:icon": nazwa_custom
            },
            "type": "definition"
        })
        
        # 4. GENEROWANIE PEŁNEGO PLIKU GEYSERA bezpośrednio w klasie procesora
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
        
        return case_java_wpis, bedrock_texture_wpis, geyser_mappings_json
