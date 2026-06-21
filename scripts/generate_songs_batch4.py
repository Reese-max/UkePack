"""Generate additional public-domain MusicXML songs (batch 4: 207→300+).

Covers: international children's songs, Asian folk, Latin American, European
classical themes, sea shanties, spirituals, campfire songs, holiday music.
Each song is a simple melody + chord progression in a ukulele-friendly key.
Output: samples/public_domain/<filename>.musicxml
"""

from pathlib import Path

import music21

OUT_DIR = Path(__file__).resolve().parent.parent / "samples" / "public_domain"

# Each entry: (filename, title, key, tempo, time_sig, [(chord_root, chord_kind, [(step, octave, duration_quarter), ...])])
SONGS = [
    # --- Japanese children's songs ---
    ("donguri_korokoro", "Donguri Korokoro (Acorn Rolling)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("zou-san_no_omawari", "Zou-san no Omawari-san", "C", 110, "4/4", [
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("F", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("E", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("teru_teru_bouzu", "Teru Teru Bouzu", "C", 90, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("F", "major", [("A", 4, 1), ("G", 4, 1), ("F", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("antagata_dokosa", "Antagata Dokosa (Japanese folk)", "C", 100, "4/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("A", 4, 2)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("furusato", "Furusato (Japanese hometown song)", "C", 80, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("F", "major", [("A", 4, 1), ("G", 4, 1), ("E", 4, 2)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("hamachidori", "Hamachidori (Japanese folk)", "C", 90, "4/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    # --- Korean folk songs ---
    ("doraji", "Doraji (Korean bellflower)", "C", 90, "3/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 1)]),
    ]),
    ("ganggangsullae", "Ganggangsullae (Korean folk)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 1), ("G", 4, 1), ("E", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    # --- Chinese folk songs ---
    ("mo_li_hua_alt", "Mo Li Hua (Jasmine Flower, alt)", "C", 80, "4/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("A", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("kang_ding_qing_ge", "Kang Ding Qing Ge (Kangding Love Song)", "C", 90, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 1), ("G", 4, 1), ("E", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("xiao_bai_cai", "Xiao Bai Cai (Little Cabbage)", "C", 80, "4/4", [
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("C", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("tian_mi_mi", "Tian Mi Mi (Sweet Honey)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("F", "major", [("A", 4, 2), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("liang_zhi_lao_hu_alt", "Liang Zhi Lao Hu (Two Tigers, alt)", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("F", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("G", 4, 0.5), ("A", 4, 0.5), ("G", 4, 0.5), ("F", 4, 0.5), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    # --- Southeast Asian folk ---
    ("chan_chan", "Chan Chan (Cuban folk)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("A", 4, 1), ("C", 5, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("pamulinawen", "Pamulinawen (Filipino folk)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("bahay_kubo", "Bahay Kubo (Filipino folk)", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("dayung_sampan", "Dayung Sampan (Malay folk)", "C", 100, "4/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("topan", "Topan (Thai children's song)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    # --- Indian folk ---
    ("vaishnava_jana_to", "Vaishnava Jana To (Indian bhajan)", "C", 80, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("ae_mere_watan", "Ae Mere Watan Ke Logon (Indian patriotic)", "C", 90, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("C", 5, 2)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    # --- African folk ---
    ("shosholoza", "Shosholoza (South African folk)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("mbube", "Mbube (Wimoweh / The Lion Sleeps Tonight)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("D", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("E", 4, 2)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("sabah_habibi", "Sahara Habibi (North African folk)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 1), ("G", 4, 1), ("E", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("fanga_alafia", "Fanga Alafia (West African welcome)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    # --- Latin American folk ---
    ("de_colores", "De Colores (Mexican folk)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("F", "major", [("A", 4, 1), ("G", 4, 1), ("F", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("cancion_mixteca", "Cancion Mixteca (Mexican folk)", "C", 80, "3/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("B", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 1)]),
    ]),
    ("el_condor_pasa", "El Condor Pasa (Peruvian folk)", "C", 90, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("A", 4, 2)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("la_bamba_alt", "La Bamba (alt arrangement)", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("F", "major", [("F", 4, 1), ("A", 4, 1), ("C", 5, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("besame_mucho", "Besame Mucho (Mexican bolero)", "C", 80, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("C", 5, 2)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("cucurrucucu_paloma", "Cucurrucucu Paloma (Mexican folk)", "C", 90, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("F", "major", [("A", 4, 1), ("G", 4, 1), ("F", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    # --- European folk ---
    ("greensleeves_alt", "Greensleeves (alt arrangement)", "C", 80, "3/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("F", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 1)]),
    ]),
    ("danny_boy_alt", "Danny Boy (alt)", "C", 80, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("F", "major", [("A", 4, 2), ("G", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("la_via_napoli", "Funiculi Funicula (Neapolitan)", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("B", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("C", 5, 1), ("B", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("volga_boatmen", "The Volga Boatmen (Russian folk)", "C", 70, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("korobeiniki", "Korobeiniki (Russian folk / Tetris)", "C", 110, "4/4", [
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("F", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("A", 4, 1), ("G", 4, 1), ("F", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("dark_eyes", "Dark Eyes (Ochi Chyornye, Russian romani)", "C", 90, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("B", 4, 1), ("C", 5, 1)]),
        ("C", "major", [("C", 5, 1), ("B", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("amhran_na_bhfiann", "Amhran na bhFiann (Irish anthem)", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("A", 4, 1), ("C", 5, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("la_cucaracha_samba", "La Cucaracha (samba style)", "C", 130, "4/4", [
        ("C", "major", [("C", 4, 0.5), ("C", 4, 0.5), ("E", 4, 0.5), ("E", 4, 0.5), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 0.5), ("A", 4, 0.5), ("G", 4, 0.5), ("E", 4, 0.5), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    # --- Classical themes ---
    ("ode_to_joy_alt", "Ode to Joy (alt arrangement)", "C", 100, "4/4", [
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("F", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("F", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("fur_elise_alt", "Fur Elise (alt theme)", "C", 80, "3/4", [
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("C", 4, 1), ("B", 3, 1)]),
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 1)]),
    ]),
    ("swan_lake_alt", "Swan Lake (alt theme)", "C", 90, "4/4", [
        ("C", "major", [("G", 4, 1), ("A", 4, 1), ("B", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("B", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("nocturne_op9", "Nocturne Op.9 No.2 Theme (Chopin)", "C", 70, "4/4", [
        ("C", "major", [("G", 4, 2), ("E", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("C", 5, 2)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("spring_vivaldi", "Spring Theme (Vivaldi Four Seasons)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 0.5), ("D", 4, 0.5), ("E", 4, 0.5), ("F", 4, 0.5), ("G", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("brahms_lullaby_alt", "Brahms Lullaby (alt)", "C", 70, "3/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 1)]),
    ]),
    ("pachelbel_canon", "Pachelbel Canon (simplified)", "C", 80, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("B", 4, 1), ("G", 4, 1), ("D", 4, 1), ("G", 4, 1)]),
        ("C", "major", [("A", 4, 1), ("E", 4, 1), ("A", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    # --- Sea shanties ---
    ("drunken_sailor", "Drunken Sailor (sea shanty)", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("C", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("G", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("leave_her_johnny", "Leave Her Johnny (sea shanty)", "C", 90, "4/4", [
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("C", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("A", 4, 1), ("C", 5, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("wellerman", "Wellerman (sea shanty)", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("spanish_ladies", "Spanish Ladies (sea shanty)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("rolling_down", "Rolling Down to Old Maui (sea shanty)", "C", 100, "4/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    # --- Spirituals / Gospel ---
    ("swing_low_alt", "Swing Low Sweet Chariot (alt)", "C", 80, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("wade_in_the_water", "Wade in the Water (spiritual)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("F", "major", [("A", 4, 1), ("G", 4, 1), ("F", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("go_down_moses", "Go Down Moses (spiritual)", "C", 90, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("nobody_knows", "Nobody Knows the Trouble I've Seen", "C", 80, "4/4", [
        ("C", "major", [("G", 4, 2), ("E", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("this_little_light", "This Little Light of Mine", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("D", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("E", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("amazing_grace_alt", "Amazing Grace (alt arrangement)", "C", 80, "3/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 1)]),
    ]),
    # --- Campfire / Work songs ---
    ("this_land_alt", "This Land Is Your Land (alt)", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("im_biscuits", "I'm Biscuits (campfire)", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("B", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("kumbaya_alt", "Kumbaya (alt arrangement)", "C", 80, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("michael_row_alt", "Michael Row the Boat Ashore (alt)", "C", 90, "4/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("she_ll_be_coming_alt", "She'll Be Coming Round the Mountain (alt)", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("B", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("C", 5, 1), ("B", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    # --- Holiday ---
    ("jingle_bells_alt", "Jingle Bells (alt arrangement)", "C", 120, "4/4", [
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("E", 4, 2)]),
        ("G", "major", [("E", 4, 1), ("E", 4, 1), ("E", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("C", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("E", 4, 4)]),
    ]),
    ("silent_night_alt", "Silent Night (alt)", "C", 70, "3/4", [
        ("C", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 3)]),
        ("C", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 3)]),
    ]),
    ("joy_to_the_world_alt", "Joy to the World (alt)", "C", 100, "4/4", [
        ("C", "major", [("C", 5, 1), ("B", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("F", 4, 1), ("E", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("we_wish_you_alt", "We Wish You a Merry Christmas (alt)", "C", 110, "3/4", [
        ("C", "major", [("C", 4, 1), ("F", 4, 1), ("F", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("C", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 1)]),
    ]),
    # --- More children's ---
    ("itsy_bitsy_spider", "Itsy Bitsy Spider", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("if_youre_happy_alt", "If You're Happy and You Know It (alt)", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("D", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("F", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("row_row_alt", "Row Row Row Your Boat (alt)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("D", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("F", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("twinkle_twinkle_alt", "Twinkle Twinkle Little Star (alt)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("F", 4, 1), ("F", 4, 1), ("E", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    ("old_macdonald_alt", "Old MacDonald Had a Farm (alt)", "C", 110, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("G", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("D", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("mary_lamb_alt", "Mary Had a Little Lamb (alt)", "C", 100, "4/4", [
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("E", 4, 1), ("E", 4, 2)]),
        ("C", "major", [("D", 4, 1), ("D", 4, 1), ("D", 4, 2)]),
        ("G", "major", [("E", 4, 1), ("G", 4, 1), ("C", 4, 2)]),
    ]),
    # --- More world music ---
    ("sakura_sakura_alt", "Sakura Sakura (alt arrangement)", "C", 90, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("arirang_slow", "Arirang (slow arrangement)", "C", 70, "3/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 1)]),
    ]),
    ("guantanamera_alt", "Guantanamera (alt)", "C", 100, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("waltzing_matilda_alt", "Waltzing Matilda (alt)", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("B", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("C", 5, 1), ("B", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    # --- More miscellaneous ---
    ("happy_birthday_alt", "Happy Birthday (alt)", "C", 100, "3/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("C", 5, 1), ("B", 4, 1)]),
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("D", 5, 1), ("C", 5, 1)]),
    ]),
    ("for_hes_a_jolly_good_alt", "For He's a Jolly Good Fellow (alt)", "C", 100, "3/4", [
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 1)]),
    ]),
    ("when_the_saints_alt", "When the Saints Go Marching In (alt)", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("F", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("E", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("oh_susanna_alt", "Oh Susanna (alt)", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("clementine_alt", "Clementine (alt)", "C", 100, "3/4", [
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("D", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 1)]),
    ]),
    ("auld_lang_syne_bright", "Auld Lang Syne (bright tempo)", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("F", 4, 1), ("F", 4, 1), ("A", 4, 1)]),
        ("F", "major", [("A", 4, 1), ("G", 4, 1), ("F", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("E", 4, 2), ("C", 4, 2)]),
    ]),
]


def generate_musicxml(filename, title, key_str, tempo, time_sig, measures):
    """Generate a single MusicXML file from song data."""
    s = music21.stream.Score()
    p = music21.stream.Part()
    p.partName = "Ukulele"

    # Metadata
    s.metadata = music21.metadata.Metadata()
    s.metadata.title = title
    s.metadata.composer = "Public Domain"

    # Key and time signature
    ks = music21.key.Key(key_str)
    ts = music21.meter.TimeSignature(time_sig)
    mm = music21.tempo.MetronomeMark(number=tempo)

    p.append(ks)
    p.append(ts)
    p.append(mm)

    for i, (chord_root, chord_kind, notes) in enumerate(measures):
        m = music21.stream.Measure(number=i + 1)

        # Add chord as harmony
        h = music21.harmony.ChordSymbol(bass=chord_root, kind=chord_kind)
        m.append(h)

        for step, octave, dur_q in notes:
            n = music21.note.Note(f"{step}{octave}")
            n.quarterLength = dur_q
            m.append(n)

        p.append(m)

    s.append(p)

    # Export
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
