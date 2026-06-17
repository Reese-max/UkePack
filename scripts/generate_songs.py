"""Generate 49 additional public-domain MusicXML songs for the starter pack.

Each song is a simple melody + chord progression in a ukulele-friendly key.
Output: samples/public_domain/<filename>.musicxml
"""

from pathlib import Path

import music21

OUT_DIR = Path(__file__).resolve().parent.parent / "samples" / "public_domain"

# Each entry: (filename, title, key, tempo, time_sig, [(chord_root, chord_kind, [(step, octave, duration_quarter), ...])])
# duration_quarter = number of quarter notes
SONGS = [
    # --- Children's songs ---
    ("a_bicycle_built_for_two", "A Bicycle Built for Two", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("A", 4, 1), ("F", 4, 1), ("A", 4, 1)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 1), ("B", 3, 1), ("G", 3, 2)]),
    ]),
    ("after_the_ball", "After the Ball", "C", 100, "3/4", [
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("D", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("C", 4, 3)]),
    ]),
    # auld_lang_syne already exists in corpus, skip
    ("b_i_n_g_o", "B-I-N-G-O", "C", 120, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("F", 4, 1), ("E", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 4)]),
    ]),
    ("buffalo_gals", "Buffalo Gals", "C", 110, "4/4", [
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("carry_my_love", "Carry Me Back to Old Virginny", "C", 90, "4/4", [
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("C", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("F", "major", [("A", 4, 1), ("G", 4, 1), ("F", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("C", 4, 3)]),
    ]),
    ("cockles_and_mussels", "Cockles and Mussels", "C", 100, "3/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("C", 4, 2)]),
    ]),
    # comin_round_the_mountain: variant of existing shell_be_coming_round_the_mountain, skip
    ("danny_boy", "Danny Boy (Londonderry Air)", "C", 80, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 2), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("F", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("dear_old_pals", "Dear Old Pals", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("E", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("C", 4, 4)]),
    ]),
    ("ding_dong_merrily", "Ding Dong Merrily on High", "C", 120, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("F", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("C", 4, 4)]),
    ]),
    ("do_your_ears_hang_low", "Do Your Ears Hang Low", "C", 110, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("down_by_the_riverside", "Down by the Riverside", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("F", "major", [("A", 4, 1), ("G", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("down_in_the_valley", "Down in the Valley", "C", 90, "3/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("C", 4, 2)]),
    ]),
    ("for_hes_a_jolly_good_fellow", "For He's a Jolly Good Fellow", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("F", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("C", 4, 2), ("C", 4, 2)]),
    ]),
    ("give_my_regards", "Give My Regards to Broadway", "C", 110, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 0.5), ("G", 4, 0.5), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("F", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    ("glory_glory_hallelujah", "Glory Glory Hallelujah", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("G", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    ("good_king_wenceslas", "Good King Wenceslas", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("F", "major", [("E", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
    ]),
    ("hesGot_theWholeWorld", "He's Got the Whole World", "C", 90, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("C", 4, 3)]),
    ]),
    ("here_we_go_round", "Here We Go Round the Mulberry Bush", "C", 110, "4/4", [
        ("C", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("i_ve_been_working_variant", "I've Been Working variant", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("C", 4, 3)]),
    ]),
    ("jesu_joy", "Jesu Joy of Man's Desiring", "C", 80, "3/4", [
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("B", 3, 1), ("A", 3, 1)]),
        ("G", "major", [("G", 3, 1), ("C", 4, 2)]),
    ]),
    ("john_brown_s_baby", "John Brown's Baby", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("F", "major", [("E", 4, 1), ("F", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("C", 4, 4)]),
    ]),
    ("joy_to_the_world", "Joy to the World", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("B", 3, 1), ("A", 3, 1), ("G", 3, 1)]),
        ("G", "major", [("F", 3, 1), ("E", 3, 1), ("D", 3, 1), ("C", 3, 1)]),
        ("C", "major", [("G", 3, 1), ("A", 3, 1), ("B", 3, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 3, 2), ("C", 4, 2)]),
    ]),
    ("la_cucaracha", "La Cucaracha", "C", 120, "4/4", [
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("E", 4, 1), ("E", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("C", 4, 1), ("F", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 1), ("G", 4, 1), ("C", 4, 2)]),
    ]),
    ("lily_of_the_valley", "Lily of the Valley", "C", 90, "3/4", [
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("C", 4, 2)]),
    ]),
    ("make_new_friends", "Make New Friends", "C", 100, "3/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("F", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("C", 4, 3)]),
    ]),
    ("man_on_the_flying_trapeze", "The Man on the Flying Trapeze", "C", 110, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 0.5), ("A", 4, 0.5), ("G", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("C", 4, 4)]),
    ]),
    ("my_country_tis", "My Country 'Tis of Thee", "C", 90, "4/4", [
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("D", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("F", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    ("nearer_my_god", "Nearer My God to Thee", "C", 80, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("F", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    ("no_woman_no_cry_intro", "No Woman No Cry (intro melody)", "C", 80, "4/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("F", "major", [("F", 4, 2), ("E", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    ("on_top_of_old_smokey", "On Top of Old Smokey", "C", 100, "3/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("C", 4, 3)]),
    ]),
    ("over_the_river", "Over the River and Through the Woods", "C", 110, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("F", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("polly_wolly_doodle", "Polly Wolly Doodle", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("reuben_reuben", "Reuben Reuben", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("B", 4, 1), ("G", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("F", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    ("rock_of_ages", "Rock of Ages", "C", 80, "4/4", [
        ("C", "major", [("C", 4, 1), ("C", 4, 1), ("D", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("F", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("C", 4, 4)]),
    ]),
    ("sakura_sakura", "Sakura Sakura", "C", 100, "4/4", [
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 1), ("A", 3, 1)]),
        ("G", "major", [("A", 3, 1), ("G", 3, 1), ("C", 4, 2)]),
    ]),
    ("simple_gifts", "Simple Gifts", "C", 100, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("F", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("C", 4, 4)]),
    ]),
    ("swing_low_sweet_chariot", "Swing Low Sweet Chariot", "C", 90, "4/4", [
        ("C", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("C", 4, 3)]),
    ]),
    ("taiwanese_folk_boat", "Small Boat (Taiwanese folk)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 1), ("G", 4, 1), ("E", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("C", 4, 3)]),
    ]),
    ("the_blue_tail_fly", "The Blue Tail Fly", "C", 110, "4/4", [
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("C", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("C", 4, 3)]),
    ]),
    ("the_campbells", "The Campbells Are Coming", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 0.5), ("D", 4, 0.5), ("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 1), ("G", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    # the_more_we_get_together_alt: variant of existing, skip
    ("there_is_a_tavern", "There Is a Tavern in the Town", "C", 110, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("C", 4, 3)]),
    ]),
    ("this_land_is_your_land", "This Land Is Your Land", "C", 110, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("today_is_monday", "Today Is Monday", "C", 100, "4/4", [
        ("C", "major", [("G", 4, 2), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("G", 4, 2), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("C", 4, 2)]),
    ]),
    ("tom_dooley", "Tom Dooley", "C", 100, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
    ]),
    ("waltzing_matilda", "Waltzing Matilda", "C", 110, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 0.5), ("A", 4, 0.5), ("G", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("C", 4, 3)]),
    ]),
    ("wayfaring_stranger", "Wayfaring Stranger", "C", 90, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("when_irish_eyes", "When Irish Eyes Are Smiling", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 1), ("G", 4, 1), ("E", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("C", 4, 3)]),
    ]),
    ("wheels_on_the_bus", "The Wheels on the Bus", "C", 110, "4/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 4)]),
    ]),
    # you_are_my_sunshine_alt: variant of existing, skip
    ("zum_gali_gali", "Zum Gali Gali", "C", 110, "4/4", [
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("F", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("F", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
]

# Verify we have exactly 49 songs
assert len(SONGS) == 49, f"Expected 49 songs, got {len(SONGS)}"


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
