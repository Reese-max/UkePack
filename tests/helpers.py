from __future__ import annotations

import io

import mido


def build_test_midi_bytes(*, bpm: int = 100, numerator: int = 4, denominator: int = 4) -> bytes:
    mid = mido.MidiFile(type=1)
    meta = mido.MidiTrack()
    notes = mido.MidiTrack()
    mid.tracks.extend([meta, notes])

    meta.append(
        mido.MetaMessage("time_signature", numerator=numerator, denominator=denominator, time=0)
    )
    meta.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
    meta.append(mido.MetaMessage("end_of_track", time=0))

    notes.append(mido.Message("program_change", program=0, time=0))
    notes.append(mido.Message("note_on", note=60, velocity=84, time=0))
    notes.append(mido.Message("note_off", note=60, velocity=0, time=mid.ticks_per_beat))
    notes.append(mido.Message("note_on", note=64, velocity=72, time=0))
    notes.append(mido.Message("note_off", note=64, velocity=0, time=mid.ticks_per_beat))
    notes.append(mido.MetaMessage("end_of_track", time=0))

    buffer = io.BytesIO()
    mid.save(file=buffer)
    return buffer.getvalue()
