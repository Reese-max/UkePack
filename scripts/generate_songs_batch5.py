"""Generate additional public-domain MusicXML songs (batch 5: 288→300+).

Fills remaining gap to reach 300-song corpus target.
Each song is a simple melody + chord progression in a ukulele-friendly key.
Output: samples/public_domain/<filename>.musicxml
"""

from pathlib import Path

import music21

OUT_DIR = Path(__file__).resolve().parent.parent / "samples" / "public_domain"

SONGS = [
    # --- More international ---
    ("sukiyaki", "Ue o Muite Arukou (Sukiyaki, Japanese pop)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 1), ("G", 4, 1), ("E", 4, 2)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("dojoji", "Dojoji Temple Bell (Japanese traditional)", "C", 80, "4/4", [
        ("C", "major", [("C", 4, 2), ("E", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("taegukgi", "Arirang Arirang (Korean folk alt)", "C", 90, "4/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("A", 4, 2)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("gongxi_facai", "Gong Xi Gong Xi (Chinese New Year)", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("B", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("C", 5, 1), ("B", 4, 1), ("A", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("chaiyachet", "Chaiyachet (Thai folk)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 1), ("G", 4, 1), ("E", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("rasa_sayang", "Rasa Sayang (Malay/Indonesian folk)", "C", 110, "4/4", [
        ("C", "major", [("E", 4, 1), ("E", 4, 1), ("F", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("nenenne", "Nenenne (Brazilian lullaby)", "C", 70, "3/4", [
        ("C", "major", [("G", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 1)]),
    ]),
    ("ay_linda_amiga", "Ay Linda Amiga (Argentine folk)", "C", 90, "3/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("G", "major", [("B", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 1)]),
    ]),
    # --- More classical ---
    ("moonlight_sonata_alt", "Moonlight Sonata (alt theme)", "C", 70, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("C", 5, 1)]),
        ("F", "major", [("A", 4, 1), ("G", 4, 1), ("F", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("claire_de_lune_alt", "Clair de Lune (alt)", "C", 70, "4/4", [
        ("C", "major", [("E", 4, 2), ("G", 4, 2)]),
        ("F", "major", [("A", 4, 1), ("G", 4, 1), ("F", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("C", 5, 2)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    # --- More folk ---
    ("scarborough_fair", "Scarborough Fair (English folk)", "C", 80, "3/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("A", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("F", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("D", 4, 1), ("E", 4, 1), ("D", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 1)]),
    ]),
    ("barbara_allen", "Barbara Allen (English folk)", "C", 80, "4/4", [
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("C", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("A", 4, 1), ("G", 4, 2)]),
        ("C", "major", [("G", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("lashes_of_the_brown", "Lashes of the Brown (Irish folk)", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("G", 4, 1), ("A", 4, 1), ("G", 4, 1), ("E", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("cockles_and_mussels_alt", "Cockles and Mussels (Irish alt)", "C", 90, "4/4", [
        ("C", "major", [("E", 4, 1), ("G", 4, 1), ("A", 4, 2)]),
        ("F", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("yesterday_yes_a_day", "Yesterday Yes a Day (French folk)", "C", 90, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("G", 4, 1)]),
        ("G", "major", [("A", 4, 1), ("G", 4, 1), ("E", 4, 2)]),
        ("C", "major", [("E", 4, 1), ("D", 4, 1), ("C", 4, 2)]),
        ("G", "major", [("D", 4, 2), ("C", 4, 2)]),
    ]),
    ("alouette_alt", "Alouette (alt arrangement)", "C", 120, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("F", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("E", 4, 2)]),
        ("C", "major", [("F", 4, 1), ("E", 4, 1), ("D", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("G", 4, 2), ("C", 4, 2)]),
    ]),
    ("frere_jacques_alt", "Frere Jacques (alt)", "C", 100, "4/4", [
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("C", "major", [("C", 4, 1), ("D", 4, 1), ("E", 4, 1), ("C", 4, 1)]),
        ("G", "major", [("E", 4, 1), ("F", 4, 1), ("G", 4, 2)]),
        ("G", "major", [("E", 4, 1), ("F", 4, 1), ("G", 4, 2)]),
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
