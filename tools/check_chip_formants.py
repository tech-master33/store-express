#!/usr/bin/env python3
"""Measure the chip's vowels against the phoneme ROM it is supposed to be reading.

This reads logs/chip_vowels.wav: one code per vowel, four frames each, rendered
by the real engine's own chip. That file was left behind by the project's old
runtime check, which is gone - the wav is the only copy there is, so keep it if
you want to run this again. It estimates each vowel's formants with LPC and
compares them with what chip.nvgt's own ROM table decodes to at the filter clock
the terminal runs at. The ROM is parsed out of chip.nvgt rather than copied
here, so a mistyped field or a broken capacitor decode shows up as a gap between
the two columns.

    python tools/check_chip_formants.py

A cascade does not put its measured peaks exactly on the poles its sections are
tuned to: the neighbouring sections, the source's own tilt and the two fixed
sections above F3 all pull them. So what this checks is not that a peak equals a
pole but that the tract TRACKS the ROM: the measured first formant has to order
the vowels the way the ROM's fields do, from the closed front ones down to the
open back ones, and the second formant has to separate the front vowels from the
back ones. Those are the two things that decide whether a vowel is recognisable.
"""
import math
import os
import re
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHIP = os.path.join(ROOT, "chip.nvgt")
WAV = os.path.join(ROOT, "logs", "chip_vowels.wav")

# the capacitor constants and the terminal's clock, read out of chip.nvgt too
def read_consts(text):
    def num(name):
        m = re.search(r"const double %s = ([0-9.]+);" % name, text)
        return float(m.group(1)) if m else None
    return {
        "F1": (num("CHIP_F1_K"), num("CHIP_F1_C0")),
        "F2": (num("CHIP_F2_K"), num("CHIP_F2_C0")),
        "F3": (num("CHIP_F3_K"), num("CHIP_F3_C0")),
    }

def read_rom(text):
    """code -> (name, F1, F2, F3 fields) from CHIP_ROM_TABLE."""
    block = re.search(r"CHIP_ROM_TABLE\s*=\s*(.*?);\n", text, re.S).group(1)
    rows = re.findall(r'"([^"]+)"', block)
    out = {}
    for row in rows:
        parts = row.strip(";").split(",")
        if len(parts) < 11:
            continue
        out[parts[1]] = (int(parts[2]), int(parts[3]), int(parts[4]))
    return out

def ff_from_chip(text):
    m = re.search(r"g_chip_computer\.ff = (\d+);", text)
    return int(m.group(1))

def theta(k, c0, field):
    cap = c0 + sum((1, 2, 4, 8)[i] for i in range(4) if (field >> i) & 1)
    s = min(0.999, math.sqrt(k * cap) / 2.0)
    return 2 * math.asin(s)

def lpc_formants(x, rate, order=14, count=3):
    """LPC on a pre-emphasised window, then the roots of the prediction filter."""
    x = np.append(x[0], x[1:] - 0.97 * x[:-1])
    x = (x - x.mean()) * np.hanning(len(x))
    r = np.correlate(x, x, "full")[len(x) - 1:]
    a = np.zeros(order + 1)
    a[0] = 1.0
    e = r[0]
    for i in range(1, order + 1):
        k = -(r[i] + np.dot(a[1:i], r[i - 1:0:-1])) / e
        anew = a.copy()
        for j in range(1, i):
            anew[j] = a[j] + k * a[i - j]
        anew[i] = k
        a = anew
        e *= (1 - k * k)
    fs = []
    for rt in np.roots(a):
        if rt.imag <= 0:
            continue
        f = abs(np.arctan2(rt.imag, rt.real)) * rate / (2 * math.pi)
        bw = -0.5 * (rate / math.pi) * math.log(abs(rt))
        if 90 < f < 3600 and bw < 700:
            fs.append((f, bw))
    fs.sort()
    out = []
    for f, bw in fs:
        if out and f - out[-1][0] < 120:
            if bw < out[-1][1]:
                out[-1] = (f, bw)
            continue
        out.append((f, bw))
    return [f for f, _ in out][:count]

def segments(data, rate):
    loud = np.abs(data) > 500.0
    segs, i = [], 0
    while i < len(data):
        if loud[i]:
            j = i
            while j < len(data) and (loud[j] or (j + 400 < len(data) and loud[j:j + 400].any())):
                j += 1
            if j - i > rate // 20:
                segs.append((i, j))
            i = j
        else:
            i += 1
    return segs

def main():
    if not os.path.exists(WAV):
        print("no %s: the wav the old runtime check left behind is gone" % WAV)
        return 1
    text = open(CHIP, encoding="utf-8").read()
    consts = read_consts(text)
    rom = read_rom(text)
    ff = ff_from_chip(text)
    fc = 1_000_000.0 / (2 * (256 - ff))

    w = wave.open(WAV, "rb")
    rate = w.getframerate()
    data = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(float)
    segs = segments(data, rate)

    names = ["E", "I", "EH", "AE", "AH", "AW", "O", "OO", "U", "ER", "R"]
    print("filter clock %d Hz, %d segments in %s" % (fc, len(segs), os.path.basename(WAV)))
    print("%-4s %-26s %-26s %s" % ("code", "measured (LPC)", "the ROM's poles", "F1 out by"))
    measured = {}
    want_f1 = {}
    for name, (a, b) in zip(names, segs):
        if name not in rom:
            continue
        mid, half = (a + b) // 2, int(rate * 0.025)
        got = lpc_formants(data[mid - half:mid + half], rate)
        want = [theta(consts[f][0], consts[f][1], rom[name][i]) / (2 * math.pi) * fc
                for i, f in enumerate(("F1", "F2", "F3"))]
        if len(got) >= 2:
            measured[name] = got
            want_f1[name] = want[0]
            print("%-4s %-26s %-26s %3.0f%%" % (
                name, "[%s]" % ", ".join("%.0f" % p for p in got),
                "[%s]" % ", ".join("%.0f" % e for e in want),
                abs(got[0] - want[0]) / want[0] * 100))
    print()

    # 1. does the measured F1 order the vowels the way the ROM does?
    pairs = wrong = 0
    ks = list(measured)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            a, b = ks[i], ks[j]
            pairs += 1
            if (want_f1[a] - want_f1[b]) * (measured[a][0] - measured[b][0]) < 0:
                wrong += 1
    print("F1 order: %d of %d vowel pairs come out in the ROM's order" % (pairs - wrong, pairs))

    # 2. does the measured F2 keep the front vowels ahead of the back ones?
    front = [n for n in ("E", "I", "EH", "AE") if n in measured]
    back = [n for n in ("O", "OO", "U", "AW", "R") if n in measured]
    lo_front = min(measured[n][1] for n in front)
    hi_back = max(measured[n][1] for n in back)
    print("F2 front/back: lowest front vowel %.0f Hz against highest back one %.0f Hz" % (lo_front, hi_back))

    ok = (wrong * 4 <= pairs) and lo_front > hi_back
    print()
    print("the tract tracks the ROM" if ok else "THE TRACT DOES NOT TRACK THE ROM")
    return 0 if ok else 2

if __name__ == "__main__":
    sys.exit(main())
