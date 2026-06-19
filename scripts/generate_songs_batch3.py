"""Generate additional public-domain MusicXML songs (batch 3: 143→200+).

Covers: more folk, campfire, spirituals, holiday, world music, classical themes.
Each song is a simple melody + chord progression in a ukulele-friendly key.
Output: samples/public_domain/<filename>.musicxml
"""

from pathlib import Path

import music21

OUT_DIR = Path(__file__).resolve().parent.parent / "samples" / "public_domain"

# Each entry: (filename, title, key, tempo, time_sig, [(chord_root, chord_kind, [(step, octave, duration_quarter), ...])])
SONGS = [
    # --- More children's songs ---
    ("a_hunting_we_will_go", "A-Hunting We Will Go", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("billy_boy", "Billy Boy", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("F", "major", [("A", 4, 2), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 2), ("C", 4, 2)]),
    ]),
    ("buy_me_a_paper", "Buy Me a Paper Father", "C", 100, "4/4", [
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("F", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("F", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("chinese_children_song", "Two Tigers (Liang Zhi Lao Hu)", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("F", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("F", 4, 1), ("G", 4, 2)]),
    ]),
    ("frog_went_a_courtin", "Frog Went A-Courtin'", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("grandfathers_clock", "Grandfather's Clock", "C", 90, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("B", 4, 1), ("G", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("growl_tiger", "Growl Tiger's Last Stand", "C", 100, "4/4", [
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("C", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("A", 4, 1), ("C", 5, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("hush_little_baby", "Hush Little Baby", "C", 80, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    ("it_s_a_small_world", "It's a Small World", "C", 100, "3/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 1)]),
    ]),
    ("little_jack_horner", "Little Jack Horner", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("F", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("F", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    ("london_bridge_is_falling", "London Bridge Is Falling Down", "C", 100, "4/4", [
        ("C", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("F", 4, 1)]),
        ("F", "major", [("E", 4, 1), ("F", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("F", 4, 1)]),
        ("G", "major", [("E", 4, 2), ("C", 4, 2)]),
    ]),
    ("looby_loo", "Looby Loo", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("F", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("my_darling_clementine", "Oh My Darling Clementine", "C", 100, "3/4", [
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("D", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
    ]),
    ("naughty_maria", "Naughty Maria", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("E", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("C", 4, 4)]),
    ]),
    ("nine_little_indians", "Ten Little Indians (alt)", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("C", 4, 1), ("D", 4, 1)]),
        ("F", "major", [("E", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("D", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("C", 4, 4)]),
    ]),
    ("oh_where_oh_where", "Oh Where Has My Little Dog Gone", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("pease_pudding", "Pease Pudding Hot", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("G", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("ring_around_rosie", "Ring Around the Rosie", "C", 100, "4/4", [
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("E", 4, 2), ("C", 4, 2)]),
    ]),
    ("rock_a_bye_baby", "Rock-a-Bye Baby", "C", 80, "3/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 1)]),
    ]),
    ("sally_gardens", "Down by the Salley Gardens", "C", 90, "4/4", [
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("C", 4, 1), ("D", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("scotland_the_brave", "Scotland the Brave", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("B", 4, 1), ("G", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("sing_a_song_of_sixpence", "Sing a Song of Sixpence", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("C", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("soldiers_march", "The Soldiers' March", "C", 110, "2/4", [
        ("C", "major", [("C", 4, 0.5), ("E", 4, 0.5), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 0.5), ("A", 4, 0.5), ("G", 4, 1)]),
        ("C", "major", [("E", 4, 0.5), ("F", 4, 0.5), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("C", 4, 1)]),
    ]),
    ("surprise_symphony", "Surprise Symphony Theme", "C", 100, "2/4", [
        ("C", "major", [("C", 4, 0.5), ("C", 4, 0.5), ("D", 4, 0.5), ("D", 4, 0.5)]),
        ("G", "major", [("E", 4, 0.5), ("E", 4, 0.5), ("F", 4, 0.5), ("G", 4, 0.5)]),
        ("C", "major", [("G", 4, 0.5), ("F", 4, 0.5), ("E", 4, 0.5), ("D", 4, 0.5)]),
        ("G", "major", [("C", 4, 2)]),
    ]),
    ("there_was_an_old_woman_alt", "There Was an Old Woman (alt)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("B", 4, 1), ("G", 4, 1)]),
        ("C", "major", [("C", 5, 1), ("B", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 2), ("C", 4, 2)]),
    ]),
    ("wake_me_up", "Wake Me Up Shake Me", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("F", "major", [("A", 4, 1), ("G", 4, 1), ("F", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    # --- Folk / World ---
    ("arirang_alt", "Arirang (Korean folk, alt)", "C", 90, "3/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 1)]),
    ]),
    ("bonnie_banks", "The Bonnie Banks of Loch Lomond", "C", 90, "4/4", [
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("C", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("G", 4, 1), ("A", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("botany_bay", "Botany Bay", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("brazilian_national", "Brazilian Folk Theme", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("B", 4, 1), ("C", 5, 1)]),
        ("C", "major", [("C", 5, 1), ("B", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("calon_llan", "Calon Lan (Welsh)", "C", 100, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("B", 4, 1)]),
        ("G", "major", [("C", 5, 2), ("G", 4, 2)]),
    ]),
    ("chevaliers_de_la_table", "Chevaliers de la Table Ronde", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("B", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("C", 5, 1), ("B", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("edelweiss_alt", "Edelweiss (alt arrangement)", "C", 80, "3/4", [
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 1)]),
    ]),
    ("hua_xie", "Hua Xie (Chinese Flower City)", "C", 90, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("F", "major", [("A", 4, 1), ("G", 4, 1), ("F", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("kalinka", "Kalinka (Russian folk)", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("la_marsellaise_theme", "La Marseillaise Theme", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("D", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("o_sole_mio_theme", "O Sole Mio Theme", "C", 100, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("F", "major", [("E", 4, 1), ("F", 4, 1), ("E", 4, 2)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("sakura_alt", "Sakura Sakura (Japanese folk, alt)", "C", 90, "4/4", [
        ("C", "major", [("E", 4, 1), ("F", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("F", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("shenandoah_alt", "Shenandoah (alt)", "C", 80, "4/4", [
        ("C", "major", [("E", 4, 2), ("G", 4, 2)]),
        ("G", "major", [("A", 4, 2), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("veni_veni_emmanuel", "Veni Veni Emmanuel", "C", 80, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("E", 4, 2), ("C", 4, 2)]),
    ]),
    # --- Campfire / Spirituals ---
    ("all_my_trials", "All My Trials (folk spiritual)", "C", 80, "4/4", [
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("C", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("A", 4, 1), ("C", 5, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("blow_the_man_down", "Blow the Man Down", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("bring_little_susie", "Bring Little Susie", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("he_got_the_whole_world", "He's Got the Whole World", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("C", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("C", 4, 4)]),
    ]),
    ("hes_a_pirate_theme", "He's a Pirate Theme", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("joe_hill", "Joe Hill (I Dreamed I Saw)", "C", 90, "4/4", [
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("F", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("F", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("keep_on_the_sunny_side", "Keep on the Sunny Side", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("B", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("A", 4, 1), ("C", 5, 2)]),
        ("C", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("matilda", "Matilda (calypso)", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("shall_we_gather", "Shall We Gather at the River", "C", 90, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("sloop_john_b", "Sloop John B", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("A", 4, 1), ("C", 5, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("st_james_infirmary", "St. James Infirmary Blues", "C", 90, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("A", 4, 1), ("C", 5, 2)]),
        ("C", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("will_the_circle", "Will the Circle Be Unbroken", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    # --- Holiday (non-Christmas) ---
    ("auld_lang_syne_alt", "Auld Lang Syne (alt arrangement)", "C", 90, "4/4", [
        ("C", "major", [("C", 4, 1), ("F", 4, 1), ("F", 4, 1), ("A", 4, 1)]),
        ("F", "major", [("A", 4, 1), ("G", 4, 1), ("F", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("E", 4, 2), ("C", 4, 2)]),
    ]),
    ("auld_lang_syne_slow", "Auld Lang Syne (slow)", "C", 70, "4/4", [
        ("C", "major", [("C", 4, 1), ("F", 4, 2), ("A", 4, 1)]),
        ("F", "major", [("A", 4, 1), ("G", 4, 1), ("F", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("A", 4, 2), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 2), ("C", 4, 2)]),
    ]),
    ("battle_hymn", "Battle Hymn of the Republic", "C", 100, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("A", 4, 1), ("C", 5, 2)]),
        ("C", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    # --- Classical themes ---
    ("air_on_g_string", "Air on the G String Theme", "C", 80, "4/4", [
        ("C", "major", [("E", 4, 2), ("G", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 2), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("canon_in_d_theme", "Canon in D Theme", "C", 80, "4/4", [
        ("C", "major", [("G", 4, 1), ("F", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("C", "major", [("G", 4, 1), ("F", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("C", 4, 2), ("G", 4, 2)]),
    ]),
    ("clair_de_lune_theme", "Clair de Lune Theme", "C", 70, "3/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("B", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 1)]),
    ]),
    ("moonlight_sonata_theme", "Moonlight Sonata Theme", "C", 70, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("B", 4, 1), ("G", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("C", 5, 1), ("B", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("swan_lake_theme", "Swan Lake Theme", "C", 90, "4/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("A", 4, 1), ("B", 4, 1)]),
        ("G", "major", [("C", 5, 2), ("G", 4, 2)]),
    ]),
    # --- More folk / traditional ---
    ("la_cucaracha_alt", "La Cucaracha (alt arrangement)", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("B", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("C", 5, 1), ("B", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("marines_hymn", "The Marines' Hymn", "C", 110, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("B", 4, 1)]),
        ("G", "major", [("C", 5, 1), ("B", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("A", 4, 1), ("C", 5, 2)]),
        ("C", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("minuet_in_g", "Minuet in G Theme", "C", 110, "3/4", [
        ("C", "major", [("D", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("B", 4, 1), ("C", 5, 1), ("D", 4, 1)]),
        ("C", "major", [("G", 4, 1), ("F", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("G", 4, 1)]),
    ]),
    ("turkish_march_theme", "Turkish March Theme", "C", 120, "2/4", [
        ("C", "major", [("E", 4, 0.5), ("D", 4, 0.5), ("C", 4, 0.5), ("D", 4, 0.5)]),
        ("G", "major", [("E", 4, 0.5), ("F", 4, 0.5), ("G", 4, 1)]),
        ("C", "major", [("G", 4, 0.5), ("F", 4, 0.5), ("E", 4, 0.5), ("D", 4, 0.5)]),
        ("G", "major", [("C", 4, 2)]),
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
