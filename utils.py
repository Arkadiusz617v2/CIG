import struct

def pobierz_wymiary_png(sciezka_pliku):
    """Odczytuje wymiary obrazka bezpośrednio z binarnego nagłówka pliku PNG."""
    try:
        with open(sciezka_pliku, 'rb') as f:
            dane = f.read(24)
            # Sprawdzamy magiczne bajty formatu PNG oraz blok nagłówka IHDR
            if dane[:8] == b'\x89PNG\r\n\x1a\n' and dane[12:16] == b'IHDR':
                szerokosc, wysokosc = struct.unpack('>ii', dane[16:24])
                return szerokosc, wysokosc
    except Exception:
        pass
    return None, None
