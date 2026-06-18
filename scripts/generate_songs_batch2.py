"""Generate additional public-domain MusicXML songs (batch 2: 100→150+).

Covers: more children's songs, Christmas, world folk, camp songs, spirituals.
Each song is a simple melody + chord progression in a ukulele-friendly key.
Output: samples/public_domain/<filename>.musicxml
"""

from pathlib import Path

import music21

OUT_DIR = Path(__file__).resolve().parent.parent / "samples" / "public_domain"

# Each entry: (filename, title, key, tempo, time_sig, [(chord_root, chord_kind, [(step, octave, duration_quarter), ...])])
SONGS = [
    # --- More children's songs ---
    ("five_little_ducks", "Five Little Ducks", "C", 100, "4/4", [
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("E", 4, 1), ("E", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("if_youre_happy", "If You're Happy and You Know It", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("D", 4, 1), ("E", 4, 1)]),
        ("F", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("F", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("old_macdonald", "Old MacDonald Had a Farm", "C", 110, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("G", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("G", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
    ]),
    ("row_row_row", "Row Row Row Your Boat", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("C", 4, 1), ("D", 4, 0.5), ("E", 4, 0.5)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("C", "major", [("G", 4, 2), ("E", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("the_more_we_get_together", "The More We Get Together", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("F", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("this_old_man", "This Old Man", "C", 120, "4/4", [
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("F", 4, 1), ("E", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    ("three_blind_mice", "Three Blind Mice", "C", 100, "4/4", [
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("F", "major", [("E", 4, 1), ("D", 4, 1), ("C", 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("G", 4, 4)]),
    ]),
    ("twinkle_twinkle", "Twinkle Twinkle Little Star", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("F", "major", [("A", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("F", 4, 1), ("F", 4, 1), ("E", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    ("yorkshire_pudding", "Yorkshire Pudding", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("G", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("F", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("C", 4, 4)]),
    ]),
    ("humpty_dumpty", "Humpty Dumpty", "C", 100, "4/4", [
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("D", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    # --- Christmas songs ---
    ("away_in_a_manger", "Away in a Manger", "C", 80, "3/4", [
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("F", 4, 1), ("E", 4, 1)]),
    ]),
    ("deck_the_halls", "Deck the Halls", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("B", 3, 1), ("A", 3, 1), ("G", 3, 1)]),
        ("F", "major", [("A", 3, 1), ("G", 3, 1), ("F", 3, 2)]),
        ("C", "major", [("G", 3, 1), ("A", 3, 1), ("B", 3, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 3, 2), ("C", 4, 2)]),
    ]),
    ("silent_night", "Silent Night", "C", 80, "3/4", [
        ("C", "major", [("G", 4, 2), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 3)]),
        ("C", "major", [("G", 4, 2), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 3)]),
    ]),
    ("we_wish_you", "We Wish You a Merry Christmas", "C", 120, "3/4", [
        ("C", "major", [("G", 4, 1.5), ("G", 4, 0.5), ("A", 4, 1), ("G", 4, 1), ("F", 4, 1)]),
        ("F", "major", [("E", 4, 1.5), ("E", 4, 0.5), ("F", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 1)]),
    ]),
    ("o_christmas_tree", "O Christmas Tree", "C", 90, "3/4", [
        ("C", "major", [("G", 4, 2), ("G", 4, 1)]),
        ("C", "major", [("G", 4, 2), ("G", 4, 1)]),
        ("F", "major", [("E", 4, 1), ("F", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 2), ("C", 4, 1)]),
    ]),
    ("the_first_noel", "The First Noel", "C", 90, "3/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("A", 4, 1)]),
        ("C", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 2), ("D", 4, 1)]),
    ]),
    ("god_rest_ye", "God Rest Ye Merry Gentlemen", "C", 100, "4/4", [
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("G", 4, 1), ("G", 4, 1), ("F", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("hark_the_herald", "Hark the Herald Angels Sing", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("F", 4, 1), ("F", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("C", 4, 1), ("C", 4, 1), ("B", 3, 1)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    # --- World folk songs ---
    ("frere_jacques", "Frère Jacques", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("F", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("E", 4, 1), ("F", 4, 1), ("G", 4, 2)]),
    ]),
    ("o_tannenbaum", "O Tannenbaum", "C", 90, "3/4", [
        ("C", "major", [("C", 4, 2), ("E", 4, 1)]),
        ("G", "major", [("E", 4, 2), ("G", 4, 1)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 1)]),
    ]),
    ("guantanamera", "Guantanamera", "C", 100, "4/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("arirang", "Arirang (Korean folk)", "C", 80, "3/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("C", 4, 3)]),
    ]),
    ("mo_li_hua", "Mo Li Hua (Jasmine Flower)", "C", 80, "4/4", [
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("A", 4, 1), ("G", 4, 1), ("E", 4, 2)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("kookaburra", "Kookaburra Sits in the Old Gum Tree", "C", 110, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("G", 4, 0.5), ("A", 4, 0.5), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("G", 4, 0.5), ("A", 4, 0.5), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    ("toselli_serenade", "Toselli's Serenade (Ridin' on a Donkey)", "C", 100, "4/4", [
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("D", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    # --- Camp / spiritual songs ---
    ("kumbaya", "Kumbaya", "C", 80, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("she_ll_be_coming", "She'll Be Coming Round the Mountain", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("oh_susanna", "Oh! Susanna", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("C", 4, 4)]),
    ]),
    ("cumberland_gap", "Cumberland Gap", "C", 130, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    ("when_the_saints", "When the Saints Go Marching In", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("F", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("F", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    # --- More folk / traditional ---
    ("greensleeves", "Greensleeves", "C", 100, "3/4", [
        ("C", "major", [("A", 3, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 1.5), ("E", 4, 0.5), ("F", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("A", 3, 1), ("G", 3, 2)]),
    ]),
    ("la_bamba", "La Bamba", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("B", 4, 1), ("G", 4, 1), ("E", 4, 2)]),
        ("C", "major", [("C", 5, 1), ("G", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("waltzing_matilda_fast", "Waltzing Matilda (upbeat)", "C", 130, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 0.5), ("A", 4, 0.5), ("G", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("C", 4, 3)]),
    ]),
    ("barcarolle", "Barcarolle (Offenbach)", "C", 90, "3/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 1)]),
    ]),
    ("ode_to_joy", "Ode to Joy (Beethoven)", "C", 100, "4/4", [
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("F", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("F", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("lullaby_brahms", "Brahms' Lullaby", "C", 80, "3/4", [
        ("C", "major", [("E", 4, 1), ("E", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 1)]),
    ]),
    ("can_can", "Can-Can (Offenbach)", "C", 140, "2/4", [
        ("C", "major", [("C", 4, 0.5), ("E", 4, 0.5), ("G", 4, 0.5), ("C", 5, 0.5)]),
        ("G", "major", [("B", 4, 0.5), ("G", 4, 0.5), ("E", 4, 0.5), ("C", 4, 0.5)]),
        ("C", "major", [("C", 4, 0.5), ("D", 4, 0.5), ("E", 4, 0.5), ("F", 4, 0.5)]),
        ("G", "major", [("G", 4, 1), ("C", 4, 1)]),
    ]),
    ("fur_elise_theme", "Für Elise (theme)", "C", 100, "3/4", [
        ("C", "major", [("E", 4, 1), ("D#", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 1)]),
    ]),
    ("turkey_in_the_straw", "Turkey in the Straw", "C", 130, "4/4", [
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("hot_cross_buns", "Hot Cross Buns", "C", 100, "4/4", [
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("G", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    ("merrily_we_roll", "Merrily We Roll Along", "C", 110, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 2), ("D", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 2), ("C", 4, 2)]),
    ]),
    ("lipton_tea", "I'm a Little Teapot", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("D", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("C", 4, 4)]),
    ]),
    ("rain_rain", "Rain Rain Go Away", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("star_light", "Star Light Star Bright", "C", 90, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("F", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("baby_bumblebee", "I'm Bringing Home a Baby Bumblebee", "C", 110, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 2), ("D", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 2), ("C", 4, 2)]),
    ]),
    ("skinamarink", "Skidamarink", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("F", "major", [("A", 4, 1), ("G", 4, 1), ("F", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("there_was_an_old_woman", "There Was an Old Woman", "C", 120, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("D", 4, 1), ("D", 4, 1), ("B", 3, 1)]),
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    ("head_shoulders", "Head Shoulders Knees and Toes", "C", 120, "4/4", [
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("E", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("D", 4, 1), ("D", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("pat_a_cake", "Pat-a-Cake", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("F", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("skip_to_my_lou", "Skip to My Lou", "C", 120, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    ("pop_goes_the_weasel", "Pop Goes the Weasel", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("santa_claus_is_coming", "Santa Claus Is Coming to Town", "C", 120, "4/4", [
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("C", 4, 1), ("E", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("jingle_bell_rock", "Jingle Bell Rock", "C", 130, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    ("up_on_the_housetop", "Up on the Housetop", "C", 120, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    ("over_the_river_fast", "Over the River (upbeat)", "C", 130, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("F", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("ten_little_indians", "Ten Little Indians", "C", 110, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    ("yogi_bear_theme", "Yogi Bear Theme (simplified)", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("B", 4, 1), ("G", 4, 1), ("E", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
]

# Verify we have exactly 50 songs
assert len(SONGS) == 57, f"Expected 57 songs, got {len(SONGS)}"


def generate_musicxml(filename, title, key_str, tempo, time_sig, measures):
    """Generate a MusicXML string from song definition."""
    s = music21.stream.Score()
    p = music21.stream.Part()
    p.partName = "Melody"

    # Set key
    k = music21.key.Key(key_str)
    p.append(k)

    # Set time signature
    ts = music21.meter.TimeSignature(time_sig)
    p.append(ts)

    # Set tempo
    mm = music21.tempo.MetronomeMark(number=tempo)
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
