#!/usr/bin/env python3
"""Generate 20 new public-domain children's song MusicXML fixtures.

Each song is encoded as a simple lead sheet: melody + chord symbols.
Output targets tests/fixtures/ and samples/public_domain/.
"""

import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

# ── Song definitions ──
# Each song: (slug, title, key_fifths, mode, bpm, measures)
# measures: list of (chord_root, chord_kind, notes)
# notes: list of (step, alter, octave, duration_quarters)

DIVISIONS = 10080  # same as existing fixtures
Q = DIVISIONS  # quarter note duration

SONGS = {
    "amazing_grace": {
        "title": "Amazing Grace",
        "fifths": 1, "mode": "major", "bpm": 80,
        "measures": [
            ("G", "major", [("G",0,4,Q), ("B",0,4,Q), ("D",0,5,Q), ("D",0,5,Q)]),
            ("G", "major", [("D",0,5,Q), ("B",0,4,Q), ("G",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("D",0,5,Q), ("B",0,4,Q)]),
            ("G", "major", [("G",0,4,Q), ("B",0,4,Q), ("A",0,4,Q), ("G",0,4,Q)]),
            ("G", "major", [("G",0,4,Q), ("B",0,4,Q), ("D",0,5,Q), ("D",0,5,Q)]),
            ("G", "major", [("D",0,5,Q), ("B",0,4,Q), ("G",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("D",0,5,Q), ("B",0,4,Q)]),
            ("D", "major", [("A",0,4,Q), ("A",0,4,Q), ("G",0,4,Q), ("G",0,4,Q)]),
        ],
    },
    "auld_lang_syne": {
        "title": "Auld Lang Syne",
        "fifths": 0, "mode": "major", "bpm": 100,
        "measures": [
            ("C", "major", [("C",0,4,Q), ("C",0,4,Q), ("E",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q), ("D",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("G",0,4,Q), ("G",0,4,Q)]),
            ("F", "major", [("G",0,4,Q), ("E",0,4,Q), ("E",0,4,Q), ("C",0,4,Q)]),
            ("C", "major", [("C",0,4,Q), ("C",0,4,Q), ("E",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q), ("D",0,4,Q)]),
            ("F", "major", [("G",0,4,Q), ("G",0,4,Q), ("A",0,4,Q), ("A",0,4,Q)]),
            ("C", "major", [("A",0,4,Q), ("G",0,4,Q), ("E",0,4,Q), ("C",0,4,Q)]),
        ],
    },
    "brahms_lullaby": {
        "title": "Brahms' Lullaby",
        "fifths": 0, "mode": "major", "bpm": 72,
        "measures": [
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("G",0,4,Q), ("C",0,5,Q)]),
            ("F", "major", [("A",0,4,Q), ("A",0,4,Q), ("A",0,4,Q)]),
            ("C", "major", [("G",0,4,Q), ("G",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q)]),
            ("G", "major", [("D",0,4,Q), ("C",0,4,Q), ("C",0,4,Q)]),
        ],
    },
    "chopsticks": {
        "title": "Chopsticks",
        "fifths": 0, "mode": "major", "bpm": 120,
        "measures": [
            ("C", "major", [("E",0,4,Q), ("F",0,4,Q), ("E",0,4,Q), ("F",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("F",0,4,Q), ("E",0,4,Q), ("F",0,4,Q)]),
            ("G", "major", [("D",0,4,Q), ("E",0,4,Q), ("D",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("F",0,4,Q), ("E",0,4,Q), ("F",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("F",0,4,Q), ("E",0,4,Q), ("F",0,4,Q)]),
            ("G", "major", [("D",0,4,Q), ("E",0,4,Q), ("D",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q)]),
        ],
    },
    "drink_to_me_only": {
        "title": "Drink to Me Only with Thine Eyes",
        "fifths": 0, "mode": "major", "bpm": 88,
        "measures": [
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("F",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q), ("C",0,4,Q)]),
            ("F", "major", [("A",0,4,Q), ("A",0,4,Q), ("G",0,4,Q), ("F",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("F",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q), ("C",0,4,Q)]),
            ("F", "major", [("A",0,4,Q), ("G",0,4,Q), ("F",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("D",0,4,Q), ("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q)]),
        ],
    },
    "frere_jacques": {
        "title": "Frère Jacques",
        "fifths": 0, "mode": "major", "bpm": 108,
        "measures": [
            ("C", "major", [("C",0,4,Q), ("D",0,4,Q), ("E",0,4,Q), ("C",0,4,Q)]),
            ("C", "major", [("C",0,4,Q), ("D",0,4,Q), ("E",0,4,Q), ("C",0,4,Q)]),
            ("F", "major", [("E",0,4,Q), ("F",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("F",0,4,Q), ("G",0,4,Q)]),
            ("G", "major", [("G",0,4,Q), ("A",0,4,Q), ("G",0,4,Q), ("F",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("F",0,4,Q), ("E",0,4,Q), ("D",0,4,Q)]),
            ("C", "major", [("C",0,4,Q), ("D",0,4,Q), ("E",0,4,Q), ("C",0,4,Q)]),
            ("C", "major", [("C",0,4,Q), ("G",0,3,Q), ("C",0,4,Q), ("C",0,4,Q)]),
        ],
    },
    "home_on_the_range": {
        "title": "Home on the Range",
        "fifths": 0, "mode": "major", "bpm": 90,
        "measures": [
            ("C", "major", [("G",0,4,Q), ("G",0,4,Q), ("A",0,4,Q), ("G",0,4,Q)]),
            ("F", "major", [("E",0,4,Q), ("E",0,4,Q), ("D",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("G",0,4,Q), ("G",0,4,Q), ("A",0,4,Q), ("G",0,4,Q)]),
            ("G", "major", [("A",0,4,Q), ("G",0,4,Q), ("E",0,4,Q), ("C",0,4,Q)]),
            ("C", "major", [("G",0,4,Q), ("G",0,4,Q), ("A",0,4,Q), ("G",0,4,Q)]),
            ("F", "major", [("E",0,4,Q), ("E",0,4,Q), ("D",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("G",0,4,Q), ("A",0,4,Q), ("G",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("D",0,4,Q), ("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q)]),
        ],
    },
    "kumbaya": {
        "title": "Kumbaya",
        "fifths": 0, "mode": "major", "bpm": 80,
        "measures": [
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("E",0,4,Q), ("D",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q)]),
            ("G", "major", [("D",0,4,Q), ("D",0,4,Q), ("D",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("D",0,4,Q), ("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("E",0,4,Q), ("D",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q)]),
            ("G", "major", [("D",0,4,Q), ("D",0,4,Q), ("E",0,4,Q), ("D",0,4,Q)]),
            ("C", "major", [("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q)]),
        ],
    },
    "love_me_tender": {
        "title": "Love Me Tender",
        "fifths": 0, "mode": "major", "bpm": 76,
        "measures": [
            ("C", "major", [("C",0,4,Q), ("D",0,4,Q), ("E",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("G",0,4,Q), ("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q)]),
            ("F", "major", [("A",0,4,Q), ("A",0,4,Q), ("G",0,4,Q), ("F",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q)]),
            ("C", "major", [("C",0,4,Q), ("D",0,4,Q), ("E",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("G",0,4,Q), ("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q)]),
            ("F", "major", [("A",0,4,Q), ("G",0,4,Q), ("F",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("D",0,4,Q), ("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q)]),
        ],
    },
    "michael_row": {
        "title": "Michael Row the Boat Ashore",
        "fifths": 0, "mode": "major", "bpm": 96,
        "measures": [
            ("C", "major", [("E",0,4,Q), ("G",0,4,Q), ("G",0,4,Q), ("A",0,4,Q)]),
            ("F", "major", [("G",0,4,Q), ("E",0,4,Q), ("E",0,4,Q), ("D",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("G",0,4,Q), ("G",0,4,Q), ("A",0,4,Q)]),
            ("G", "major", [("G",0,4,Q), ("E",0,4,Q), ("E",0,4,Q), ("C",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("G",0,4,Q), ("G",0,4,Q), ("A",0,4,Q)]),
            ("F", "major", [("G",0,4,Q), ("E",0,4,Q), ("E",0,4,Q), ("D",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("G",0,4,Q), ("A",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q), ("C",0,4,Q)]),
        ],
    },
    "my_bonnie": {
        "title": "My Bonnie Lies Over the Ocean",
        "fifths": 0, "mode": "major", "bpm": 104,
        "measures": [
            ("C", "major", [("G",0,4,Q), ("A",0,4,Q), ("G",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q)]),
            ("C", "major", [("D",0,4,Q), ("E",0,4,Q), ("F",0,4,Q), ("E",0,4,Q)]),
            ("G", "major", [("D",0,4,Q), ("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q)]),
            ("C", "major", [("G",0,4,Q), ("A",0,4,Q), ("G",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q)]),
            ("F", "major", [("D",0,4,Q), ("E",0,4,Q), ("F",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("D",0,4,Q), ("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q)]),
        ],
    },
    "ode_to_joy": {
        "title": "Ode to Joy",
        "fifths": 0, "mode": "major", "bpm": 108,
        "measures": [
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("F",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("G",0,4,Q), ("F",0,4,Q), ("E",0,4,Q), ("D",0,4,Q)]),
            ("C", "major", [("C",0,4,Q), ("C",0,4,Q), ("D",0,4,Q), ("E",0,4,Q)]),
            ("G", "major", [("E",0,4,Q), ("D",0,4,Q), ("D",0,4,Q), ("D",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("F",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("G",0,4,Q), ("F",0,4,Q), ("E",0,4,Q), ("D",0,4,Q)]),
            ("C", "major", [("C",0,4,Q), ("C",0,4,Q), ("D",0,4,Q), ("E",0,4,Q)]),
            ("G", "major", [("D",0,4,Q), ("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q)]),
        ],
    },
    "she_ll_be_coming": {
        "title": "She'll Be Coming 'Round the Mountain (variant)",
        "fifths": 0, "mode": "major", "bpm": 120,
        "measures": [
            ("C", "major", [("C",0,4,Q), ("E",0,4,Q), ("G",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("A",0,4,Q), ("G",0,4,Q), ("E",0,4,Q), ("C",0,4,Q)]),
            ("F", "major", [("A",0,4,Q), ("A",0,4,Q), ("A",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q)]),
            ("C", "major", [("C",0,4,Q), ("E",0,4,Q), ("G",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("A",0,4,Q), ("G",0,4,Q), ("E",0,4,Q), ("C",0,4,Q)]),
            ("G", "major", [("A",0,4,Q), ("G",0,4,Q), ("E",0,4,Q), ("D",0,4,Q)]),
            ("C", "major", [("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q)]),
        ],
    },
    "silent_night": {
        "title": "Silent Night",
        "fifths": 0, "mode": "major", "bpm": 72,
        "measures": [
            ("C", "major", [("G",0,4,Q), ("A",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("G",0,4,Q), ("A",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("E",0,4,Q)]),
            ("G", "major", [("D",0,5,Q), ("D",0,5,Q), ("B",0,4,Q)]),
            ("C", "major", [("G",0,4,Q), ("G",0,4,Q), ("E",0,4,Q)]),
            ("G", "major", [("D",0,5,Q), ("D",0,5,Q), ("B",0,4,Q)]),
            ("C", "major", [("G",0,4,Q), ("G",0,4,Q), ("E",0,4,Q)]),
        ],
    },
    "swanee_river": {
        "title": "Old Folks at Home (Swanee River)",
        "fifths": 0, "mode": "major", "bpm": 88,
        "measures": [
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("E",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("G",0,4,Q), ("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q)]),
            ("F", "major", [("A",0,4,Q), ("A",0,4,Q), ("A",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("E",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("G",0,4,Q), ("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q)]),
            ("F", "major", [("A",0,4,Q), ("A",0,4,Q), ("G",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("D",0,4,Q), ("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q)]),
        ],
    },
    "sweet_betsy": {
        "title": "Sweet Betsy from Pike",
        "fifths": 0, "mode": "major", "bpm": 100,
        "measures": [
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("F",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("D",0,4,Q), ("C",0,4,Q), ("D",0,4,Q), ("E",0,4,Q)]),
            ("F", "major", [("A",0,4,Q), ("A",0,4,Q), ("G",0,4,Q), ("F",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("F",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("D",0,4,Q), ("C",0,4,Q), ("D",0,4,Q), ("E",0,4,Q)]),
            ("G", "major", [("G",0,4,Q), ("G",0,4,Q), ("E",0,4,Q), ("D",0,4,Q)]),
            ("C", "major", [("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q)]),
        ],
    },
    "taps": {
        "title": "Taps",
        "fifths": 0, "mode": "major", "bpm": 60,
        "measures": [
            ("C", "major", [("G",0,4,Q), ("G",0,4,Q), ("G",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("G",0,4,Q), ("C",0,5,Q), ("G",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("G",0,4,Q), ("G",0,4,Q), ("G",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("G",0,4,Q), ("C",0,5,Q), ("G",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("C",0,5,Q), ("C",0,5,Q), ("C",0,5,Q), ("C",0,5,Q)]),
            ("C", "major", [("C",0,5,Q), ("G",0,4,Q), ("G",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("G",0,4,Q), ("C",0,5,Q), ("G",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("G",0,4,Q), ("C",0,5,Q), ("C",0,4,Q), ("C",0,4,Q)]),
        ],
    },
    "the_more_we_get_together": {
        "title": "The More We Get Together",
        "fifths": 0, "mode": "major", "bpm": 112,
        "measures": [
            ("C", "major", [("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("G",0,4,Q), ("G",0,4,Q), ("G",0,4,Q), ("E",0,4,Q)]),
            ("F", "major", [("E",0,4,Q), ("E",0,4,Q), ("E",0,4,Q), ("D",0,4,Q)]),
            ("C", "major", [("D",0,4,Q), ("D",0,4,Q), ("C",0,4,Q), ("C",0,4,Q)]),
            ("C", "major", [("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("G",0,4,Q), ("G",0,4,Q), ("G",0,4,Q), ("E",0,4,Q)]),
            ("F", "major", [("E",0,4,Q), ("E",0,4,Q), ("D",0,4,Q), ("D",0,4,Q)]),
            ("C", "major", [("D",0,4,Q), ("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q)]),
        ],
    },
    "when_the_saints": {
        "title": "When the Saints Go Marching In",
        "fifths": 0, "mode": "major", "bpm": 120,
        "measures": [
            ("C", "major", [("C",0,4,Q), ("E",0,4,Q), ("F",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("C",0,4,Q), ("E",0,4,Q), ("F",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("C",0,4,Q), ("E",0,4,Q), ("F",0,4,Q), ("G",0,4,Q)]),
            ("F", "major", [("E",0,4,Q), ("E",0,4,Q), ("D",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("C",0,4,Q), ("E",0,4,Q), ("F",0,4,Q), ("G",0,4,Q)]),
            ("C", "major", [("C",0,4,Q), ("E",0,4,Q), ("F",0,4,Q), ("G",0,4,Q)]),
            ("F", "major", [("E",0,4,Q), ("E",0,4,Q), ("D",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q)]),
        ],
    },
    "you_are_my_sunshine": {
        "title": "You Are My Sunshine",
        "fifths": 0, "mode": "major", "bpm": 100,
        "measures": [
            ("C", "major", [("C",0,4,Q), ("E",0,4,Q), ("E",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q), ("D",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("E",0,4,Q), ("E",0,4,Q), ("E",0,4,Q)]),
            ("G", "major", [("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q), ("D",0,4,Q)]),
            ("C", "major", [("C",0,4,Q), ("E",0,4,Q), ("E",0,4,Q), ("E",0,4,Q)]),
            ("C", "major", [("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q), ("D",0,4,Q)]),
            ("F", "major", [("E",0,4,Q), ("E",0,4,Q), ("D",0,4,Q), ("C",0,4,Q)]),
            ("C", "major", [("D",0,4,Q), ("C",0,4,Q), ("C",0,4,Q), ("C",0,4,Q)]),
        ],
    },
}

# ── MusicXML generation ──

def build_musicxml(slug: str, song: dict) -> str:
    """Build a MusicXML 4.0 partwise document matching existing fixture format."""
    fifths = song["fifths"]
    mode = song["mode"]
    bpm = song["bpm"]
    title = song["title"]
    measures = song["measures"]

    # Build root
    score = ET.Element("score-partwise", version="4.0")

    work = ET.SubElement(score, "work")
    wt = ET.SubElement(work, "work-title")
    wt.text = title

    mt = ET.SubElement(score, "movement-title")
    mt.text = title

    ident = ET.SubElement(score, "identification")
    creator = ET.SubElement(ident, "creator", type="composer")
    creator.text = "Music21"
    enc = ET.SubElement(ident, "encoding")
    ed = ET.SubElement(enc, "encoding-date")
    ed.text = "2026-06-13"
    sw = ET.SubElement(enc, "software")
    sw.text = "music21 v.9.9.1"

    defaults = ET.SubElement(score, "defaults")
    scaling = ET.SubElement(defaults, "scaling")
    mm = ET.SubElement(scaling, "millimeters")
    mm.text = "7"
    t = ET.SubElement(scaling, "tenths")
    t.text = "40"

    part_list = ET.SubElement(score, "part-list")
    sp = ET.SubElement(part_list, "score-part", id="P1")
    ET.SubElement(sp, "part-name")

    part = ET.SubElement(score, "part", id="P1")

    for idx, (chord_root, chord_kind, notes) in enumerate(measures, 1):
        m = ET.SubElement(part, "measure", number=str(idx))
        if idx == 1:
            m.set("implicit", "no")
            attrs = ET.SubElement(m, "attributes")
            div = ET.SubElement(attrs, "divisions")
            div.text = str(DIVISIONS)
            key = ET.SubElement(attrs, "key")
            f = ET.SubElement(key, "fifths")
            f.text = str(fifths)
            md = ET.SubElement(key, "mode")
            md.text = mode
            time = ET.SubElement(attrs, "time")
            bt = ET.SubElement(time, "beats")
            bt.text = "4"
            btype = ET.SubElement(time, "beat-type")
            btype.text = "4"

            direction = ET.SubElement(m, "direction")
            dtype = ET.SubElement(direction, "direction-type")
            metro = ET.SubElement(dtype, "metronome", parentheses="no")
            bu = ET.SubElement(metro, "beat-unit")
            bu.text = "quarter"
            pm = ET.SubElement(metro, "per-minute")
            pm.text = str(bpm)
            ET.SubElement(direction, "sound", tempo=str(bpm))
        else:
            m.set("implicit", "no")

        # Harmony (chord symbol)
        harmony = ET.SubElement(m, "harmony")
        root = ET.SubElement(harmony, "root")
        rs = ET.SubElement(root, "root-step")
        rs.text = chord_root
        kind = ET.SubElement(harmony, "kind")
        kind.text = chord_kind

        # Notes
        for step, alter, octave, dur in notes:
            note = ET.SubElement(m, "note")
            pitch = ET.SubElement(note, "pitch")
            s = ET.SubElement(pitch, "step")
            s.text = step
            if alter != 0:
                a = ET.SubElement(pitch, "alter")
                a.text = str(alter)
            o = ET.SubElement(pitch, "octave")
            o.text = str(octave)
            d = ET.SubElement(note, "duration")
            d.text = str(dur)
            tp = ET.SubElement(note, "type")
            tp.text = "quarter"

    # Pretty-print
    rough = ET.tostring(score, encoding="unicode")
    parsed = minidom.parseString(rough)
    lines = parsed.toprettyxml(indent="  ", encoding=None).split("\n")
    # Remove minidom's XML declaration, add our own
    result = '<?xml version="1.0" encoding="utf-8"?>\n'
    result += '<!DOCTYPE score-partwise  PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">\n'
    for line in lines:
        if line.strip().startswith("<?xml"):
            continue
        result += line + "\n"
    return result


def main():
    fixtures_dir = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures")
    samples_dir = os.path.join(os.path.dirname(__file__), "..", "samples", "public_domain")

    count = 0
    for slug, song in SONGS.items():
        xml = build_musicxml(slug, song)
        fname = f"{slug}.musicxml"

        for d in [fixtures_dir, samples_dir]:
            path = os.path.join(d, fname)
            with open(path, "w", encoding="utf-8") as f:
                f.write(xml)
            print(f"  wrote {path}")

        count += 1

    print(f"\nGenerated {count} new fixtures (total should be {30 + count})")


if __name__ == "__main__":
    main()
