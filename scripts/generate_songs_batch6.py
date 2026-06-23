"""Generate additional public-domain MusicXML songs (batch 6: 305→350).

Japanese children's songs (童謡), Korean folk, Latin American, Southeast Asian.
Each song is a simple melody + chord progression in a ukulele-friendly key.
Output: samples/public_domain/<filename>.musicxml
"""

from pathlib import Path

import music21

OUT_DIR = Path(__file__).resolve().parent.parent / "samples" / "public_domain"

SONGS = [
    # --- Japanese children's songs (童謡) ---
    ("teru_teru_bouzu", "Teru Teru Bouzu (Japanese children's)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("G", "major", [("E", 4, 2), ("D", 4, 2)]),
    ]),
    ("momotaro", "Momotaro-san (Japanese folk)", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("E", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("zui_zui_zukkorobashi", "Zui Zui Zukkorobashi (Japanese children's)", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 1), ("G", 4, 1), ("E", 4, 2)]),
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("ant_march", "Ari no March (Ant March, Japanese children's)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("obento_obento", "Obento Obento (Japanese children's)", "C", 100, "4/4", [
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 2), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("usagi_usagi", "Usagi Usagi (Rabbit Rabbit, Japanese children's)", "C", 90, "3/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("F", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 1)]),
    ]),
    ("ongaku_no_heyade", "Ongaku no Heya de (In the Music Room)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("haru_ga_kita", "Haru ga Kita (Spring Has Come, Japanese)", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 2), ("G", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("kaeru_no_uta", "Kaeru no Uta (Frog Song, Japanese)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("kirakira_boshi", "Kirakira Boshi (Twinkle Star, Japanese)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("F", 4, 1), ("F", 4, 1), ("E", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    # --- Korean folk & children's songs ---
    ("san_tokki", "San Tokki (Mountain Rabbit, Korean children's)", "C", 100, "3/4", [
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 1)]),
    ]),
    ("gohyang_ui_bom", "Gohyang ui Bom (Spring in My Hometown, Korean)", "C", 90, "3/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 1)]),
    ]),
    ("doraji", "Doraji (Bellflower, Korean folk)", "C", 80, "3/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("F", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 1)]),
    ]),
    ("ganggangsullae", "Ganggangsullae (Korean folk dance)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("E", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("mokpo_sarang", "Mokpo Sarang (Mokpo Love, Korean folk)", "C", 90, "4/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("A", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    # --- Latin American children's songs ---
    ("los_pollitos_dicen", "Los Pollitos Dicen (The Chicks Say, Latin American)", "C", 100, "3/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("F", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 1)]),
    ]),
    ("de_colores", "De Colores (Mexican folk)", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 2), ("G", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("cielito_lindo", "Cielito Lindo (Mexican folk)", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("E", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("estrellita", "Estrellita (Mexican serenade)", "C", 80, "3/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 1)]),
    ]),
    ("burrito_sabanero", "El Burrito Sabanero (Venezuelan Christmas)", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("B", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("C", 5, 1), ("B", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("arroz_con_leche", "Arroz con Leche (Spanish nursery rhyme)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("E", 4, 2)]),
        ("C", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("que_linda_espiga", "Que Linda Espiga (Argentine harvest)", "C", 90, "3/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("B", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 1)]),
    ]),
    ("pescador_de_riveras", "Pescador de Riveras (Chilean folk)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("A", 4, 1), ("G", 4, 1), ("E", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("caminito", "Caminito (Argentine tango standard)", "C", 90, "2/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 1), ("G", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("C", 4, 1)]),
    ]),
    # --- Southeast Asian folk songs ---
    ("burung_kakatua", "Burung Kakatua (Indonesian children's)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 1), ("G", 4, 1), ("E", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("pamulinawen", "Pamulinawen (Filipino folk)", "C", 90, "3/4", [
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 1)]),
    ]),
    ("daulat_tuanku", "Daulat Tuanku (Malay folk)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 2), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("top_leng", "Top Leng (Thai children's)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("singapura_di_sepuluh", "Singapura (Malaysian/Singapore folk)", "C", 110, "4/4", [
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("F", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    # --- More European folk ---
    ("kookaburra", "Kookaburra (Australian children's)", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("waltzing_matilda_alt", "Waltzing Matilda (alt arrangement)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("la_cucaracha_alt", "La Cucaracha (alt arrangement)", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("E", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("guten_morgen", "Guten Morgen (German folk)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("loch_lomond", "Loch Lomond (Scottish folk)", "C", 80, "4/4", [
        ("C", "major", [("G", 4, 2), ("E", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("shenandoah", "Shenandoah (American folk)", "C", 80, "4/4", [
        ("C", "major", [("E", 4, 2), ("G", 4, 2)]),
        ("G", "major", [("A", 4, 1), ("G", 4, 1), ("E", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("simple_gifts_alt", "Simple Gifts (alt arrangement)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 1), ("G", 4, 1), ("E", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("black_sheep_alt", "Baa Baa Black Sheep (alt)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("F", 4, 1), ("F", 4, 1), ("E", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    ("twinkle_alt", "Twinkle Twinkle (alt arrangement)", "C", 90, "4/4", [
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("F", 4, 1), ("F", 4, 1), ("E", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    # --- More African/Latin ---
    ("shosholoza", "Shosholoza (South African folk)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("mbube", "Mbube (Wimoweh, South African)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("A", 4, 1), ("G", 4, 1), ("E", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("samba_lele", "Samba Lele (Brazilian children's)", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("E", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("atirei_o_pau", "Atirei o Pau no Gato (Brazilian children's)", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 1), ("G", 4, 1), ("E", 4, 2)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
]


def generate_musicxml(filename, title, key_str, tempo, time_sig, measures):
    """Generate a single MusicXML file from song data."""
    s = music21.stream.Score()
    p = music21.stream.Part()
    p.partName = "Ukulele"

    s.metadata = music21.metadata.Metadata()
    s.metadata.title = title
    s.metadata.composer = "Public Domain"

    ks = music21.key.Key(key_str)
    ts = music21.meter.TimeSignature(time_sig)
    mm = music21.tempo.MetronomeMark(number=tempo)

    p.append(ks)
    p.append(ts)
    p.append(mm)

    for i, (chord_root, chord_kind, notes) in enumerate(measures):
        m = music21.stream.Measure(number=i + 1)
        h = music21.harmony.ChordSymbol(bass=chord_root, kind=chord_kind)
        m.append(h)
        for step, octave, dur_q in notes:
            n = music21.note.Note(f"{step}{octave}")
            n.quarterLength = dur_q
            m.append(n)
        p.append(m)

    s.append(p)
    out_path = OUT_DIR / f"{filename}.musicxml"
    s.write("musicxml", fp=str(out_path))
    return out_path


def main():
    existing = {f.stem for f in OUT_DIR.glob("*.musicxml")}
    generated = 0
    skipped = 0

    for filename, title, key_str, tempo, time_sig, measures in SONGS:
        if filename in existing:
            print(f"  SKIP {filename} (already exists)")
            skipped += 1
            continue
        out_path = generate_musicxml(filename, title, key_str, tempo, time_sig, measures)
        print(f"  GEN {out_path.name}")
        generated += 1

    print(f"\nDone: {generated} generated, {skipped} skipped")
    print(f"Total .musicxml files: {len(list(OUT_DIR.glob('*.musicxml')))}")


if __name__ == "__main__":
    main()
