#!/usr/bin/env python3
"""Write the four instrumentals this game ships in assets/music/.

They are written here rather than licensed from somebody, so the shop's own
recordings carry no licence at all, which is the whole point of having them: the
game can be handed to anybody. The other four tracks in assets/music are public
domain ragtime recordings downloaded by the game itself (see assets/manifest.txt
and CREDITS.md).

Everything is deterministic: same seed, same notes, same bytes, every run. The
files are mono 16-bit 22050 Hz, which is plenty for a shop's ceiling speakers and
keeps each track about a megabyte.

    python tools/make_music.py

The game only ever reads these by filename, so re-running this after any edit
means the size in the manifest (if you add one) has to be updated too; the
generated tracks are shipped files and are deliberately NOT in the manifest.
"""

import math
import os
import wave

import numpy as np

RATE = 22050
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUSIC_DIR = os.path.join(ROOT, "assets", "music")

NOTE_OFFSETS = {
    "c": 0, "c#": 1, "db": 1, "d": 2, "d#": 3, "eb": 3, "e": 4, "f": 5,
    "f#": 6, "gb": 6, "g": 7, "g#": 8, "ab": 8, "a": 9, "a#": 10, "bb": 10,
    "b": 11,
}


def freq(name):
    """'a4' -> 440.0, 'f#3' -> 185.0, 'eb2' -> 77.8."""
    name = name.strip().lower()
    letter = name[0]
    rest = name[1:]
    if rest[:1] in ("#", "b"):
        letter += rest[0]
        rest = rest[1:]
    octave = int(rest)
    semi = NOTE_OFFSETS[letter] + (octave - 4) * 12
    return 440.0 * (2.0 ** ((semi - 9) / 12.0))


def blank(seconds):
    return np.zeros(int(RATE * seconds), dtype=np.float64)


def add(buf, start_s, sig, gain=1.0):
    """Mix sig into buf at start_s, wrapping anything past the end back to the
    start so the loop has no click and no missing reverb tail."""
    begin = int(start_s * RATE)
    if begin >= len(buf):
        begin %= len(buf)
    for offset in range(0, len(sig), len(buf)):
        part = sig[offset:offset + len(buf)]
        end = begin + len(part)
        if end <= len(buf):
            buf[begin:end] += part * gain
        else:
            first = len(buf) - begin
            buf[begin:] += part[:first] * gain
            buf[:end - len(buf)] += part[first:] * gain
        begin = 0


def env(n, attack=0.01, decay=0.12, sustain=0.7, release=0.25):
    a = max(1, int(attack * RATE))
    d = max(1, int(decay * RATE))
    r = max(1, int(release * RATE))
    s = max(1, n - a - d - r)
    return np.concatenate([
        np.linspace(0.0, 1.0, a),
        np.linspace(1.0, sustain, d),
        np.full(s, sustain),
        np.linspace(sustain, 0.0, r),
    ])[:n]


def tone(name, seconds, kind="sine", detune=0.0, gain=1.0, attack=0.01,
         decay=0.12, sustain=0.7, release=0.25):
    n = int(seconds * RATE)
    t = np.arange(n) / RATE
    f = freq(name)
    sig = np.zeros(n)
    if kind == "sine":
        sig = np.sin(2 * math.pi * f * t)
    elif kind == "warm":
        # a sine with two quiet partners, which reads as an electric piano
        for mult, level in ((1.0, 1.0), (2.0, 0.28), (3.0, 0.09), (4.02, 0.05)):
            sig += level * np.sin(2 * math.pi * f * mult * t)
    elif kind == "saw":
        sig = 2.0 * ((f * t) % 1.0) - 1.0
        sig += 0.5 * np.sin(2 * math.pi * f * 0.5 * t)
    elif kind == "square":
        sig = np.sign(np.sin(2 * math.pi * f * t))
    elif kind == "pluck":
        sig = np.sin(2 * math.pi * f * t) * np.exp(-t * 3.0)
        sig += 0.3 * np.sin(2 * math.pi * f * 2 * t) * np.exp(-t * 6.0)
    if detune:
        sig += 0.5 * np.sin(2 * math.pi * f * (1.0 + detune) * t)
    sig *= env(n, attack, decay, sustain, release)
    return sig * gain


def kick(seconds=0.28, gain=1.0):
    n = int(seconds * RATE)
    t = np.arange(n) / RATE
    f = 120.0 * np.exp(-t * 26.0) + 42.0
    sig = np.sin(2 * math.pi * np.cumsum(f) / RATE) * np.exp(-t * 11.0)
    return sig * gain


def noise_hit(seconds, gain=1.0, lowpass=0.5, decay=22.0, seed=0):
    rng = np.random.default_rng(seed)
    n = int(seconds * RATE)
    t = np.arange(n) / RATE
    sig = rng.normal(0.0, 1.0, n)
    # one pole low pass, so the noise reads as a hit rather than as hiss
    out = np.zeros(n)
    prev = 0.0
    for i in range(n):
        prev += (sig[i] - prev) * lowpass
        out[i] = prev
    out *= np.exp(-t * decay)
    return out * gain


def soft(buf, amount=0.35):
    """One pole low pass over the whole buffer, to take the edge off."""
    out = np.zeros(len(buf))
    prev = 0.0
    for i in range(len(buf)):
        prev += (buf[i] - prev) * amount
        out[i] = prev
    return out


def reverb(buf, taps=((0.09, 0.28), (0.17, 0.19), (0.27, 0.12), (0.41, 0.07))):
    out = buf.copy()
    for delay_s, level in taps:
        d = int(delay_s * RATE)
        shifted = np.concatenate([np.zeros(d), buf[:len(buf) - d]])
        out += shifted * level
    return out


def normalise(buf, peak=0.85):
    top = np.max(np.abs(buf))
    if top < 1e-9:
        return buf
    return buf * (peak / top)


def write_wav(name, buf):
    os.makedirs(MUSIC_DIR, exist_ok=True)
    path = os.path.join(MUSIC_DIR, name)
    data = np.clip(buf, -1.0, 1.0)
    pcm = (data * 32767.0).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm.tobytes())
    return path, os.path.getsize(path)


def beat(seconds, bpm):
    return seconds * bpm / 60.0


def day_counter_drift():
    """Daytime, shop open, nobody in it yet: a lazy two chord drift."""
    bpm, bars, beats_per_bar = 92.0, 8, 4
    spb = 60.0 / bpm
    total = bars * beats_per_bar * spb
    buf = blank(total)

    chords = [("c3", ["c4", "e4", "g4"]), ("a2", ["a3", "c4", "e4"]),
              ("f2", ["f3", "a3", "c4"]), ("g2", ["g3", "b3", "d4"])]
    for bar in range(bars):
        root, notes = chords[bar % len(chords)]
        at = bar * beats_per_bar * spb
        add(buf, at, tone(root, beats_per_bar * spb, "warm", gain=0.30,
                          attack=0.02, release=spb), 1.0)
        for i, n in enumerate(notes):
            add(buf, at + i * spb * 0.5, tone(n, spb * 2.4, "warm", gain=0.16,
                                              attack=0.03, decay=0.3,
                                              sustain=0.5, release=spb * 1.4), 1.0)
        add(buf, at + spb * 2, noise_hit(0.12, gain=0.07, lowpass=0.7,
                                         decay=40.0, seed=bar), 1.0)
    # a slow melody on top, one note a bar, so it never gets busy
    melody = [(0, "g4"), (1, "e4"), (2, "f4"), (3, "d4"),
              (4, "e4"), (5, "c4"), (6, "d4"), (7, "g3")]
    for bar, note in melody:
        add(buf, bar * beats_per_bar * spb, tone(note, beats_per_bar * spb * 0.9,
                                                 "pluck", gain=0.22), 1.0)
    return "day_counter_drift.wav", reverb(soft(buf))


def night_after_hours():
    """The shop at night, one light on: slow, minor, sparse."""
    bpm, bars, beats_per_bar = 68.0, 8, 4
    spb = 60.0 / bpm
    total = bars * beats_per_bar * spb
    buf = blank(total)
    chords = [("a2", ["a3", "c4", "e4"]), ("f2", ["f3", "a3", "c4"]),
              ("c3", ["c4", "e4", "g4"]), ("e2", ["e3", "g3", "b3"])]
    for bar in range(bars):
        root, notes = chords[bar % len(chords)]
        at = bar * beats_per_bar * spb
        add(buf, at, tone(root, beats_per_bar * spb * 1.1, "sine", gain=0.26,
                          attack=0.6, decay=0.5, sustain=0.8, release=spb * 2.0), 1.0)
        for n in notes:
            add(buf, at, tone(n, beats_per_bar * spb * 1.2, "sine", gain=0.10,
                              attack=0.9, decay=0.7, sustain=0.7,
                              release=spb * 2.4), 1.0)
    bells = [(2, "e5"), (3, "c5"), (6, "a4"), (7, "b4")]
    for bar, note in bells:
        add(buf, bar * beats_per_bar * spb + spb, tone(note, spb * 2.0, "pluck",
                                                       gain=0.16), 1.0)
    return "night_after_hours.wav", reverb(soft(buf, 0.25))


def chase_back_aisle():
    """A shoplifter is running for the forecourt: fast, forward, unstoppable."""
    bpm, bars, beats_per_bar = 152.0, 8, 4
    spb = 60.0 / bpm
    total = bars * beats_per_bar * spb
    buf = blank(total)
    bass = ["a1", "a1", "c2", "c2", "d2", "d2", "e2", "e2"]
    for bar in range(bars):
        at = bar * beats_per_bar * spb
        for step in range(8):
            add(buf, at + step * spb * 0.5,
                tone(bass[bar % len(bass)], spb * 0.42, "saw", gain=0.34,
                     attack=0.004, decay=0.05, sustain=0.6, release=0.05), 1.0)
        for step in range(4):
            add(buf, at + step * spb, kick(0.24, 0.65), 1.0)
            add(buf, at + step * spb + spb * 0.5,
                noise_hit(0.07, gain=0.16, lowpass=0.85, decay=60.0,
                          seed=bar * 10 + step), 1.0)
        for n in ("a4", "e5", "g5", "e5"):
            add(buf, at + random_step(bar) * spb, tone(n, spb * 0.5, "square",
                                                       gain=0.10), 1.0)
    return "chase_back_aisle.wav", soft(buf, 0.5)


def random_step(bar):
    return (bar * 3) % 4


def fight_ruckus():
    """Two drunks, one aisle, no dignity: tense and percussive."""
    bpm, bars, beats_per_bar = 118.0, 8, 4
    spb = 60.0 / bpm
    total = bars * beats_per_bar * spb
    buf = blank(total)
    stabs = ["d2", "eb2", "d2", "f2", "d2", "eb2", "g2", "ab2"]
    for bar in range(bars):
        at = bar * beats_per_bar * spb
        for step in range(4):
            add(buf, at + step * spb, kick(0.3, 0.8), 1.0)
        for step in range(4):
            add(buf, at + step * spb + spb * 0.5,
                noise_hit(0.16, gain=0.30, lowpass=0.6, decay=30.0,
                          seed=bar * 7 + step), 1.0)
        for step in (0, 2):
            add(buf, at + step * spb, tone(stabs[bar % len(stabs)],
                                           spb * 0.9, "saw", gain=0.30,
                                           attack=0.005, decay=0.1,
                                           sustain=0.4, release=0.2), 1.0)
        add(buf, at + spb * 1.5, tone(stabs[(bar + 3) % len(stabs)], spb * 0.6,
                                      "square", gain=0.14), 1.0)
    return "fight_ruckus.wav", soft(buf, 0.45)


TRACKS = (day_counter_drift, night_after_hours, chase_back_aisle, fight_ruckus)


def main():
    for maker in TRACKS:
        name, buf = maker()
        path, size = write_wav(name, normalise(buf))
        length = len(buf) / float(RATE)
        print(f"{name}: {length:6.1f}s  {size:8d} bytes  {os.path.relpath(path, ROOT)}")


if __name__ == "__main__":
    main()
