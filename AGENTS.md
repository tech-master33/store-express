# Store Express — standing instructions for every session

These are the rules for working in this project. They are here so the NVGT
skill does not have to be loaded by hand: enabling **Settings → General →
Agent instructions → Include AGENTS.md** puts this file in front of every
message. The full skill, with its scripts and the whole engine reference, is
still at `C:\Users\aj918\.agents\skills\nvgt-dev` (`SKILL.md`, `scripts/`,
`references/`); invoke `/nvgt-dev` when you want the long form of it.

## 1. Read the local engine before the web

Everything about this engine is already on this machine. In order:

1. `C:\Users\aj918\.agents\skills\nvgt-dev\references\nvgt_src\` — the real C++
   source. Priority for exact signatures, property semantics and behaviour.
   The script API is registered in `src/*.cpp` (for audio: `src/sound.cpp`).
2. `C:\nvgt\include\` — the shipped includes this project already uses
   (`sound_pool.nvgt`, `speech.nvgt`, `ini.nvgt`, `settings.nvgt`...).
3. `C:\nvgt\nvgt.chm` — the 900 page reference. If it needs reading offline:
   `cmd //c "hh.exe -decompile <outdir> C:\nvgt\nvgt.chm"`, then grep the HTML.
4. `C:\Users\aj918\.agents\skills\nvgt-dev\references\*.md` and
   `references/example_game/` — tutorials and worked projects.
5. Only after all of that, the web.

The skill's own tools: `python scripts/nvgt_researcher.py --source <file>` and
`python scripts/asset_manager.py --download <url>` (run from the skill
directory).

## 2. Never hand over NVGT code that has not been compiled

The engine is `C:\nvgt\nvgt.exe`. Work is finished only when this has run, from
this project folder, and passed:

```bash
/c/nvgt/nvgt.exe -c -q main.nvgt         # release build; must exit 0 and write main.zip
```

Fix every error and warning before reporting back, and repeat until clean. The
`-q` is quiet, so when something looks wrong run it without `-q` and read the
warnings.

**Do not write or run a test harness, and do not run the game yourself.** The
player tests the store by playing it. A script that drives the game opens a
window, takes the keyboard and interrupts whatever the player is doing, and it
has been removed from this project for that reason. Compiling is the only
automatic check there is, and a clean compile proves the script parses and
nothing more: do not report behaviour you have not seen, and do not claim a
behaviour is verified because a build succeeded. If you need a state to look at,
use the debug keys (`F7`/`F8` the clock, `F11` a shoplifter, `Ctrl+Shift+R`
diagnostics, `Ctrl+F1` a snapshot) and read `logs/speech.log`.

**Never leave a test script behind.** A one-off script written to look at
something gets deleted in the same turn it was made, and so does anything it
wrote into the project folder.

**The compiled product SHADOWS the script.** This build of NVGT packages a
release build as `<script>.zip` (`Success!: ... saved to ...\main.zip`), and a
compiled product sitting beside a script of the same basename is what runs —
`main.zip` or `main.exe` next to `main.nvgt` is loaded instead of the source, so
a stale one makes every edit look like it did nothing. That is the first thing to
suspect when a fix "does not work". Compile to check, then DELETE `main.zip` and
`main.exe` before finishing, so the next run is the source you just wrote.

Every main-thread loop keeps its frame pump: `main.nvgt`'s `process_frame()`
calls `wait(5)`, which is NVGT's window/event pump and is not optional.

## 3. Audio conventions — read this before touching anything audible

* **Volumes are decibels here, on purpose.** The engine is created with
  `audio_engine::PERCENTAGE_ATTRIBUTES`, and with those flags
  `sound::set_volume()` converts its argument from dB to linear
  (`src/sound.cpp`). So 0 is full scale and -96 is silence, and every gain in
  this project is already in dB. Do not "modernise" these to 0.0–1.0: that
  would make the whole game silent or deafening.
* **Two speech channels, and they are not interchangeable.** The player's own
  channel is the screen reader they are already listening with, at their own
  speed, or a Windows voice when they have none: the menus, the prompts, the
  reports and everything else the game says *to* the player. The people's
  channel is the voice pool: every customer and every member of staff has a
  voice of their own. It is one pool: the voices the servers answered with and
  the voices this computer already has sit in it together, on the network and
  off it, never one behind the other, so a server going quiet costs the shop
  variety and not its crowd. `say()` routes on whether a character voice is
  set, `say_player()` is the player's channel and `say_as()` is a person's.
  Nobody in the building is ever read out by the screen reader, and no menu is
  ever read out by a customer: the channels do not borrow from each other in
  either direction, not even when one of them has nothing to speak with. The
  machines are a third thing again: they have chips of their own.
* **No pitch for elevation or distance.** The world is spatial: position
  everything with the sound pool's 3D calls (`play_extended_3d`) and let
  `rooms.nvgt` decide what is muffled through a wall.
* **Surfaces are recordings, not effects.** A step is one of three measured
  variants of the room's floor (`footsteps_init()` in `rooms.nvgt`), played in
  turn, so two steps in a row are never the same recording; a wall is one of two
  (`wall_sound()`): plasterboard in the shop, the office and the apartment,
  sheet metal in the walk ins, placed at the wall you walked into rather than at
  the listener. A variant is an offset into a file plus a short cut, and its gain
  is what puts every step of that floor at the same heard level - a walk must not
  jump in volume from one foot to the next - and no cue is ever played with a
  positive gain. Each file's bundled tone must be silent up to the SMALLEST
  offset the game seeks to in it, or a failed download is silent where the step
  should be. Offsets, cuts, peaks and gains are measured values with the `ffmpeg`
  numbers written into `assets/manifest.txt`: do not retune them by ear, and do
  not add a floor or a fourth variant without a recording to go with it.
* **Device choice.** `get_sound_output_devices()` lists the machine's output
  devices and `sound_output_device` (a global property, -1 = system default) is
  the index the engine takes. `sound_output_device` is read at startup from
  `config.ini`, changed in the main menu under Options, sound output, and
  written back in place. An unconfirmed device must never be the one that gets
  written, and the player's own choice must be the only thing that switches one:
  `g_audio_switch_allowed` is the guard for exactly that, and a run killed
  mid-switch leaves the player pointed at the wrong box.
* **Menu movement is one sound.** Every menu tick goes through `sfx_tick()` in
  `audio.nvgt`, which cuts `scanner.ogg` to `SFX_MENU_TICK_MS`. Never call
  `sfx_ui(A("scanner.ogg"), ...)` without a cut: the recording is twenty nine
  seconds of supermarket checkout, and playing it whole on every arrow key is
  what made the device list unusable.
* **A machine's speech speed and pitch are set on the machine, and saved with
  the store.** `chip_speed_*` and `chip_pitch_*` in `chip.nvgt` give each chip a
  speed in per cent of the chip's own rate (40–100, default and **normal** 65)
  and a pitch in per cent of its own `pitch_hz` (30–200, default 100), because
  the chip's own `R2` cannot reach far enough for a player who cannot follow the
  voice and `pitch_hz` is where the note the whole voice hangs on is set. 65 is
  this machine's normal on purpose: the words are built around it, and a chip at
  100 sounds faster than it is meant to. The speed is a host clock over the frame,
  never a resampling: stretching the frame is what slows the phonemes, the
  transitions and the pauses and leaves the pitch and the formants where they
  were, and the pitch period was measured at both speeds to prove it. The
  controls are a `Speech speed:` line and a `Pitch:` line on the terminal's own
  home page and on the phone's, not lines in Options — that is where the player
  who needs them is — and the chip answering a line is the chip being changed.
  **Enter on one of those lines opens a page listing every setting** rather than
  stepping the value in place (`chip_setting_page()` in `mechanics.nvgt`), and
  choosing one applies it, saves it, has the machine say it and returns to the
  home page with the cursor on the line. Both live in the save, not `config.ini`
  (`chip_*_speed_pct`, `chip_*_pitch_pct`), because they belong to a store's
  machines and loading another slot must put that slot's settings back;
  `mechanics.nvgt` writes them into the slot in place, one line at a time, when
  the player chooses one.
* **Changing a machine's speed or pitch never cuts it off.** `chip_speed_apply()`
  and `chip_pitch_apply()` set the profile and say nothing, and the render state
  keeps the speed the line was started at (`chip_render_state.speed_pct`, used by
  `chip_frame_seconds_at()`), so choosing a setting while the machine is mid
  sentence lets it finish as it began. Never put `chip_silence()` or a cache
  clear back into a setting change; the cache key carries both the speed and the
  pitch, so a stale line can never be played back.
* **A machine's cursor move does cut the last line off.** A chip line is queued,
  where the player's own voice interrupts, so `menu_speak_current()` and
  `menu_select()` call `machine_chip_cut()` (`chip_stop_device()` in `chip.nvgt`)
  before a new line is spoken: the line the cursor left stops the moment the new
  one is asked for, and only that device is touched. Without it a machine reads
  out every line the player has already moved past.
* **Each machine has a startup and a shutdown sound, and they are ours.**
  `machine_power_sound()` in `mechanics.nvgt` plays one of four shipped files when
  a machine's screen opens and when it closes or logs off
  (`tech_terminal_on/off.wav`, `tech_phone_on/off.wav`). They were written once
  for this project and are in `assets/`; there is no generator in the repository,
  deliberately not in `assets/manifest.txt`, and no placeholder tone either,
  because silence is what a missing chime should sound like. Change one by
  replacing the file, and only if there is a reason to.
* **The machines do not use the screen reader.** The people speak through the
  voice pool and the menus through the player's own voice, both via `say()` in
  `audio.nvgt`. The hardware in the building speaks through
  `chip.nvgt`: an emulated Silicon Systems SSI-263 with its own phoneme ROM, its
  own registers (`config.ini`, `chip_*` keys) and its own samples, which is what
  makes those lines pannable and impossible to fail. When adding a line for a
  device, put it through the chip and keep the store clock running while it
  speaks. Nothing repeats a chip line in the player's voice: `chip_mirror_lines`
  is 0 by default and is an accessibility crutch, not the intended way to play.
  The terminal's own screens and readouts are chip lines too — they arrive as
  `say()` calls that `terminal_capture_begin()`/`terminal_action_spoken()` hold
  and hand to the chip. **While a machine owns the screen, every line of it is
  the machine's**, the line the cursor is on included: `menu_speak_current()`
  goes through `menu_line_spoken()`, which asks `machine_for_modal()` and sends
  the line to that machine's chip. Only the screens the player's own voice owns
  (the register, the pause menu, the issue reporter) use `say()`.

## 4. The shape of the project

Include order is one way only:
`audio.nvgt <- core.nvgt <- chip.nvgt <- rooms.nvgt <- money.nvgt <- shop.nvgt
<- staff.nvgt <- people.nvgt <- trouble.nvgt <- hardware.nvgt <- mechanics.nvgt
<- main.nvgt`. Nothing calls upward; state a lower file cannot own is passed up
with a flag and acted on by the higher one (see `g_hw_need_save`).

| File | What belongs in it |
| --- | --- |
| `audio.nvgt` | The sound pool, the room isolation table, the voice and speech queue, the machine's own audio devices, `say()`, logging. |
| `core.nvgt` | Leaf helpers and the clock's state: `money()`, `plural()`, modal ids. |
| `chip.nvgt` | The emulated SSI-263: the phoneme ROM, the registers, the renderer, the line cache. |
| `rooms.nvgt` | The map, tiles, things, portals, ambience; every position in the game. |
| `mechanics.nvgt` | The frame's own logic, the menus and their pages, the save file, the clock's ticks. |
| `hardware.nvgt` | The speech devices in the building and their first-run install routines. |
| `main.nvgt` | Window, key map, main loop, main menu and Options. |
| `tools/make_music.py` | Writes the shipped music. Not run by the game. |

The front end has one shop of its own: the **attract mode** (`demo_shop_*`,
section 18 of `mechanics.nvgt`), a scripted recording of a shop heard from the main
menu, turned off by a switch in Options. It never touches a save.

Small facts worth not rediscovering: money is always whole cents and never a
float; a save is `saves/slotNN.txt` with a `.bak`; the hardware flags are
`computer_init` and `phone_init`; `config.ini` is documented and the game is
allowed to rewrite a single key in place, preserving the file's own line
endings (it is CRLF); the machines' speech speed and pitch are NOT in
`config.ini` - they are saved with the store as `chip_*_speed_pct` and
`chip_*_pitch_pct` in `saves/slotNN.txt`, one pair per machine, and the player
changes them on the machine's own screen rather than in a menu.

Two more that are cheap to get wrong and expensive to find:

* **The office back door has nobody at it.** The courier, the boxes behind the
  counter and the under-the-counter sale were removed on purpose, as was the
  supplier offer on the phone, so the back door is a place you can stand next to
  and use and nothing more, and `config.ini` carries no key for a visitor. Do
  not put a person back at it without being asked.
* **A cue the game seeks into needs a fallback tone that is silent up to that
  seek.** The ten body sounds in `people.nvgt` are played from an offset into
  their recording, so their tones in `assets/placeholder/` are that offset of
  silence followed by the usual quiet tone. A plain four second beep made the
  sigh, which seeks to 10.4 s, completely silent offline, and the cough clipped.
  The recipe is above those sounds in `assets/manifest.txt`.

Three engine facts that have already cost a day each, so do not relearn them:

* **`&out` parameters do not arrive with their value.** A function that is
  handed a string as `string &out` cannot read what was in it: an accumulator
  that appends to an `&out` parameter silently keeps only the last piece, and a
  cursor passed as `int &out` never moves, which is an endless loop. Return the
  new value instead. `&inout` is not used anywhere in this project; keep it that
  way and the trap cannot come back.
* **A phoneme token that is not a name on the ROM is dropped where it stands.**
  There is no SH on the die (/sh/ is its SCH), and the dictionary was quietly
  losing the middle of CALIBRATION for it, which is why every token in every
  table has to be checked against the ROM by hand before it is added.
* **The chip's front end is not a word list any more.** A word goes through the
  dictionary, then the spelling rules in `chip.nvgt` (asked longest first), and
  only a word with no vowel in it, or a known acronym, is spelled out; prices,
  numbers, clock readings and percents have words of their own. The phone's
  vowels have to stay in the speech band: it is a device the player reads a
  screen through, so cheap sounding is fine and unintelligible is not.

## 5. How to talk about the work

State what was verified and what was not, name the command and its result, and
do not claim audio quality or a speedup that was not measured. If a check could
not run, say so instead of implying it passed. Keep the prose short: the user
reads it in a terminal.
