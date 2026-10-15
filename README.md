# Store Express

An audio game about running a small-town convenience store and gas station. You
are blind to the world and the world is invisible to you: there are no graphics
at all. Everything you know arrives as spoken text, a positional sound cue, or
stereo placement. Put headphones on, walk the aisles by ear, serve whoever is at
the till, keep the shelves full, hire somebody before you collapse, and try not
to get foreclosed on.

Your uncle, twice removed, has died and left you the shop on Main Street: a full
set of shelves, **$2,500** in the till, a back office with the manager computer, a
studio apartment behind the office, and no staff whatsoever. For the first week
or two it is you, the register, and whoever comes in through the front door.

Written in NVGT (NonVisual Gaming Toolkit) AngelScript and run directly from
source.

---

## Running it

```
cd "store express"
nvgt.exe main.nvgt
```

Or run the compiled build, which needs `config.ini` and `assets/` beside it:

```
main.exe
```

The engine must be able to find its own `include` directory, which a normal NVGT
installation does automatically.

`config.ini` is read at startup. Every key has a built-in default, so deleting a
line is safe. Amounts ending in `_cents` are whole cents, so `250000` is
`$2,500.00`. The clock rate lives there too: `minutes_per_real_second=0.25` is
one trading day per real hour, which makes a game hour about four real minutes.

---

## Controls

| Key | Action |
| --- | --- |
| Arrow keys | Walk, **relative to the way you are facing**. Hold to keep walking, hold Shift as well to run. |
| `Q` / `E` | Turn a quarter turn left or right. |
| `G` | Go-to: a list of every place in the room, spoken with its direction and distance. |
| `Enter` | Use whatever you are standing next to. |
| `Space` | Swing the fly swatter at a shoplifter, three tiles ahead of you. |
| `P` | Press the portable panic button. |
| `Shift+P` | Your phone. `\` does the same. |
| `T` | The time and the day. |
| `M` | The money: till, week, orders, next bill. |
| `C` | Where you are. |
| `B` | Who is in the shop: who is shopping, who is at the counter and who is behind them, who is about to settle the queue, and everybody else placed by direction, distance and what they are doing. Then what is around you. |
| `Z` | Lift your ears to the ceiling as an overhead camera, and back down. `Page Up` / `Page Down` change its height. |
| `Ctrl` + `,` / `.` | The previous and next track on the shop's speakers, wherever you are in the shop. |
| `Ctrl` + `[` / `]` | The music five percent quieter or louder through the shop's speakers. |
| `Escape` | The pause menu. Your store saves itself when you open it. |
| `F1` | The whole control list, read out. |

Inside any menu: `Up`/`Down` move, `Enter` or `Space` selects, `Escape` goes back
one page and then closes the menu.

Debug keys, in every build: `F7` / `F8` step the clock an hour back or forward,
`Shift+F7` and `Shift+F8` jump to six in the morning or ten at night, `F11` sends
in a shoplifter, `Ctrl+Shift+R` toggles diagnostics into `logs/speech.log`, and
`Ctrl+F1` writes a full state snapshot to it. The snapshot is the first thing to
send when something goes wrong.

The listener always faces the way you are facing, so turning your body turns the
whole stereo image with it. That keeps what you hear and what a direction word
tells you in exact agreement.

---

## The six rooms

| Room | Contents |
| --- | --- |
| Main shop floor | Till, ten aisles (twenty shelf faces), entry doors, the door to the office. |
| Cooler | Walk-in chiller. |
| Freezer | Walk-in freezer. |
| Fuel forecourt | Four pumps, the tank under them, the road. Cars pull up and the engines idle. |
| Back office | Manager terminal, the secure back door. |
| Studio apartment | Bed, television, kitchen fridge. Behind the office, not the shop. |

Five doorways join them, each a two-way pair of thresholds, so ten portals exist
in all. Adjacency is not symmetric: the apartment sits *behind* the office, so
from the shop floor the apartment is silent, while standing in the office you can
just hear it through the wall.

### Multi-room audio isolation

Enforced in `audio.nvgt`:

* **Same room** — the cue is fully spatialised: pan from `x`, distance from `y`,
  elevation from `z`, through `sound_pool`'s 3D positioning.
* **Adjacent room** — muffled bleed only, at `muffle_gain_db` (default `-22 dB`).
  You can tell something is happening through the wall; you cannot locate it.
* **Anything further away** — completely silent.

Press `B` and the scan will tell you which of those three worlds you are hearing.

---

## The clock

Internal game time, not real-world time. It tracks `current_minute`,
`current_hour`, `current_day_of_week` (Monday brings the delivery truck) and
`current_week` (bills, wages and satisfaction are settled weekly). It advances
only while the player is on a live room grid, and **stops completely** while a
blocking screen is open: the pause menu, the phone, the issue reporter. The
register and the identification prompt are in-world actions, so time keeps
moving there — and so does the patience of a customer you are ignoring.

The manager terminal is **not** one of those screens any more. Reading the
reports, working out an order or watching a machine install its own speech chip
does not stop the day: the shop keeps trading behind you, the queue keeps
forming and the closing time still comes. That is what makes the terminal part of
the store rather than a screen sitting outside it.

---

## Your first day

Nobody is employed and nothing is on the rota, so you are the till, the shelf
stacker and the janitor at once. The loop is:

1. Somebody walks in, hears the door chime and the aisle rustle, and fills a
   basket at one of the twenty faces.
2. They walk to the queue and wait. Patience is per archetype and is only frozen
   while you are actually serving that person, so a queue you ignore with your
   back turned empties itself and your reputation goes with it.
3. You ring them through at the register, take the money, and the takings land in
   the till.
4. At the end of the week the bills, the wages and the loan come out of that
   till. If they cannot, you start climbing the arrears ladder.

---

## The register

At the till you can fetch anything behind the counter, scan a line or the rest of
the basket, ask for identification, run a card, take the exact money, take a
round note and count change back, or step away mid-sale.

* **Scanning** builds the total one line at a time, or all at once.
* **Alcohol, tobacco and vapes** need an identification scan. Around five
  customers in six have their licence on them; the rest have nothing to show you
  and those lines go back under the counter.
* **Cards** can be declined, and a declined card usually turns into cash.
* **Stepping away** without counting out the change short-changes the customer,
  and they will say so in a review. Counting it out puts the note in the drawer
  and the change back out of it, so the drawer is up by the sale.

Every restricted sale is recorded on the till log, scanned or not, and the
alcohol board reads that log.

---

## Stock, aisles and the Monday truck

A catalogue of **128 products** is spread across **twenty shelf faces**, two per
aisle, so every aisle has a west side and an east side and you can hear which one
is running out. Faces hold stock, stock sells down, and an empty face is a sale
you did not make: customers walk past a gap and buy less.

The office computer takes orders. Fill a face, fill the whole draft, or add lines
by hand; the draft has a total and a count of what is on order, and `M` reports
both from anywhere. Deliveries arrive on **Monday**, and the truck is audible
before it matters. An order that has not arrived is still a bill.

---

## Prices and the market

The catalogue has a fair price per line, worked back from its cost. You can set a
price by line, take a line back to fair, or move every line on a face up or down
by a percentage. Pricing over fair sells for more and moves less; under cost is a
warning the computer will repeat to you. Prices drift on their own over time, so
a shop left alone slowly loses its margin.

---

## Fuel on the forecourt

The pumps sell what the tank under the forecourt holds: **unleaded, measured in
litres, priced on the sign**. It is the one thing in the shop that is ordered by
the tanker load and sold by the litre, and it trades inside out compared with the
shelves:

1. A driver pulls up at a pump - you hear the engine idling out on the
   forecourt, muffled through the wall if you are inside - and comes in to the
   till. They name their litres and their pump: "eighteen litres on pump three".
2. You ring it up like any other sale. The bill is the litres times the sign,
   and the register offers the card, the exact money, a round note or what their
   wallet actually covers.
3. Money changes hands **before any fuel moves**, so a drive-off cannot happen.
   The tank gives up the litres when the sale closes, and the driver walks back
   out to the car.
4. The pump starts where they left it - the nozzle cue, then the pump running
   on its own island, for as long as the litres take - and when it finishes the
   engine catches and the car goes. From inside the shop it is all through the
   wall, which is exactly how a real forecourt behind a shop sounds.

The tank holds **2,000 litres** and starts part full. When it runs low, order a
load by the tanker on the manager terminal (200, 500 or 1000 litres at
wholesale); it is paid for when you order it and arrives with **Monday's truck**.
Order more than the tank holds and the excess goes back - the terminal tells you
what fits before you commit. With the tank dry no driver comes at all, so the
forecourt earns nothing until you order.

**The sign is yours to set** on the terminal's Prices page, next to the shelf
faces. Fuel's wholesale cost moves with the same weekly market as everything
else, quoted by name on the market report, so a refinery story in the news is
your chance to order before the cost lands. The fair price is cost plus sixty
cents. The forecourt report (Reports on the terminal, or the phone) gives the
tank level, the cost, the sign and the margin; `M` from anywhere reports any
tanker load on its way.

---

## Staff: cashiers, drink servers and janitors

Three roles, and each one is a job you are otherwise doing yourself.

* You open a position, and **five applicants** turn up the next morning with a
  star rating, an asking wage and a name. Five stars ask more than one star.
* A hired worker gets a **rota** of shifts across the week, and wages accrue while
  they are on duty. A **cashier** on the rota rings the queue through while you are
  somewhere else, quickly if they are good, and a crooked one skips identification
  scans that the board will later find in the till log. A **janitor** on shift mops
  a patch a minute, worst mess first. A **drink server** can be hired, rostered and
  paid, but pouring drinks unattended is not wired in yet, so serve those yourself.
  If nobody is on the till, the queue is entirely yours.
* **Satisfaction** moves with pay and rota, and staff make requests — a shift
  change, a raise — with a deadline attached. Grant or refuse them.
* Underpaid staff do not turn up: a worker with low satisfaction has a chance of
  no-showing, which is how a bad week turns into a bad bill.

---

## Mess and damage

The floor collects mess: spills that dry into sticky patches, and worse. Stand in
it and press `Enter` and you clean it up, and a **janitor** on the rota does the
same round without you, worst patch first. Shelves and displays can be knocked
over, and a knocked-over shelf face dumps everything that was on it. Damaged
fixtures stay down until you book a repair, with a bill attached.

---

## Trouble: shoplifters, drunks, fights and the police

* **Shoplifters** rustle at the shelf, which is the only warning you get. The fly
  swatter reaches three tiles straight ahead; hit them and they drop it, hit a
  customer instead and they remember.
* **Drunks** wander, knock over displays, and start things.
* **Fights** break out between customers and run themselves out over a few
  second-by-second blows.
* **The panic button** (`P`) calls the police. What the officers do depends on
  what you tell them and what they find: turning in a shoplifter you already
  hit is an offence, and so is wasting their time.

---

## Bills, the bank and money

Once a week, on bill day, the money moves:

* Rent, utilities, wages and the insurance premium come out of the till.
* **Arrears** start a ladder: missed, then a notice, then an emergency, and then
  the shop is gone. That is the foreclosure, and it is the ordinary way to lose.
* **Loans** are available, including an emergency one at a punitive rate, and can
  be paid off early.
* **Insurance** comes in four tiers — none, the building, the building and half
  the stock, the building and all of it — and a claim is held until bill day. No
  cover means a shoplifter is your loss.
* **Income tax** is filed on the terminal. You choose what to declare; declaring
  less leaves more in the till this week and is checked against the books later.

`M` reads the whole position back to you: the till, the week's sales, stock and
wages, the profit, and what the next bill is likely to be.

---

## The riskier side

Two older systems are still in the build. They are the ones to decide about if
this is to be a store management game and nothing else:

* The **alcohol board** reads the till log. Every restricted sale with no recorded
  scan is a fine, and a third bad inspection suspends the licence.
* **Income tax** can be under-declared, and is checked against the books later.
  Being caught seizes the shop, which ends the run.

A sentence in **jail** fast-forwards whole days while your staff, your stock and
your takings quietly leak.

### The back door is empty

There used to be a **person** at the office back door. A courier knocked, in the
world, from the office, and wanted cash for a box of stock you could not insure;
he left the boxes behind the counter, and only then could a customer ask for
something stronger over it. That whole chain has been removed, on the grounds
that the shop makes its money over the counter:

* Nothing knocks. The office back door is still a **place** you can stand next to
  and use, and using it describes a door bolted from the inside onto an empty
  alley. It opens no screen and no trade menu.
* There is no cut-price offer on the phone, and no supplier email.
* `config.ini` has no `courier_offer_gap_ms` and no `courier_window_ms` any more,
  so there is nothing to tune and no visitor to schedule. A save written by an
  older build loads: its `boxes=` line is simply one more key the reader no
  longer asks for.

---

## Customers: wallets, receipts and memory

Everyone who comes in is a person with a name, a voice of their own, a basket
drawn off the shelves and — new — a wallet that may not cover it.

**Everybody walks in with a wallet, and some wallets are thinner than the
basket.** Teenagers and drunks are the worst for it, truckers and big spenders
the least. When the money in their hand does not cover the bill, the till says
how short it is and offers what is actually possible:

* **Take what they have**, and the rest is yours to write off. They know it, and
  they remember it.
* **Sell what their money covers.** The dearest line comes off the bill a unit at
  a time, so three of something becomes two rather than nothing at all, and
  whatever comes off goes back on the shelf with the shelf's own sales counters
  following it back.
* **Give them the drink for nothing**, if it is a coffee or a fountain drink that
  has already been poured. It cannot go back on the shelf, so it does not.
* **Refuse the sale**, and they leave with nothing.

**A receipt prints after every sale, and about half of the customers wave it
away.** It matters to the ones who come back about their change, which is the
whole reason the short-change book exists.

**Regulars remember how you treated them last time** — a quick service, a long
wait, a bare shelf, a price hike, short change, being carded — and they say so at
the counter before they buy anything. That memory is written down when they leave
and saved with the store, so it survives quitting and coming back.

---

## Customers: the body in the aisle

Everyone in the shop is a **body in the room** before they are a basket: something
that coughs, sighs, huffs at the price of a sandwich, takes a phone call in aisle
four, or walks into somebody coming the other way.

**Every noise a body makes is one of ten real recordings**, downloaded on first
run with everything else the shop plays: a cough, a sneeze, three sighs, a yawn,
laughter, a throat being cleared, an annoyed huff, a hiccup, a belch, and a phone
ringing. Who the person is decides which of them they make — a trucker coughs, a
teenager laughs at her phone, the night shift yawns, a complainer huffs — and
somebody who has had a drink gets the hiccups and the belching instead. Each one
is heard **where that person is**, so a cough two aisles over arrives from there,
is muffled through a wall, and is silent from another room, like every other sound
in the building. A few of them are worth saying out loud as well as playing
(a huff, a belch, a yawn), because they are the shop telling you something about
the next two minutes; a cough in the distance is only texture.

**Walking into each other is an event with two halves.** Somebody bumps into
somebody else, the person walked into says something about it in their own voice,
and the other one answers in theirs — so a trucker and a complainer do not collide
the same way, and neither of them uses a template. Both lose a little patience,
and it goes into the review in the order it happened. There is deliberately **no
thud**: this shop's audio is real recordings, and there is no recording of two
people walking into each other in it, so the collision is the two sentences and
the footsteps that were already happening.

**Some of them arrive with people.** Two in five big spenders bring a small crowd
(one to four, who shop the way their host does), and between them they **clear a
third of a shelf face** rather than taking one of anything. One big spender in
four also **settles every basket in the queue in front of them** on the way out,
at their own expense — the queue is delighted, and their review says so.

**A complainer escalates on a ladder.** First a tut, then a demand to speak to
whoever is in charge of this shop, then an announcement to the whole queue that
she is never shopping here again. Each step is heard, each step is written into
her review, and at the top of the ladder she **stops running out of patience**,
which is what makes her worth dealing with rather than waiting out.

**A drunk arrives drunk and gets drunker.** There is a level on it, and it is the
level that everything else reads from: from two they start going over in the
aisle, and while they are on the floor they think about staying there. Every drink
is another level of slur in their own voice — a word repeated, then a word with
its vowels pulled long, then a hiccup in front of the sentence and an assurance
that they are fine, twice — and the whole line drops in pitch as the level climbs.
A drunk who has had one at the door turns round and starts again, which is how a
visit becomes an evening.

**The `B` key is the answer to "who just made that noise".** It names who is in
the shop, how many of them are shopping, who is at the counter and how many are
waiting behind them, which of them is about to settle the queue, and places
everybody else by direction, distance and what they are doing.

---

## Reputation and reviews

Going well, or badly, produces reviews. A customer who leaves happy scores four
or five stars and lifts your reputation; a short-changed, swatted or long-waited
customer does the opposite. Reputation is the dial that decides who walks through
that door and how many of them, so it is the number to watch when the week looks
fine and the takings do not.

**A review is a small story, not a score.** Up to **three** of the things that
happened during the visit are told, **in the order they happened** — the empty
shelf first, then the stranger who paid for their shopping — and they are phrased
in the register that reviewer actually talks in, so the same visit reads
differently in a trucker's voice and a teenager's. A five star review with one bad
thing in it says so, and a one star review with one good thing does the same the
other way round. Nineteen different things can end up in one, from being carded
without a fuss to walking into somebody in an aisle.

---

## Saving, quitting and starting over

Fifteen slots. `Escape` saves and opens the menu, with Save and quit, Save and
return to the main menu, and Exit. The slot list reads each save's name and till
so you know what you are overwriting, and overwriting an occupied slot takes two
presses, because starting over cannot be undone. Saves live in `saves/slotNN.txt`
and the previous save is kept beside it as a `.bak`.

---

## The floors and the walls

The world is heard, so the ground under you and the walls around you are sounds
rather than scenery. **Every floor has a recording of its own, and three recorded
steps of it**, because one step repeated under every foot is the sound of a
machine walking:

| Floor | Rooms | Recordings | The three steps, and how they are played |
| --- | --- | --- | --- |
| vinyl tile | the shop floor | `step_tile.mp3` | 7.02 s, 10.26 s and 13.26 s, cut to 450 ms |
| carpet | the office and your apartment | `step_carpet.mp3` | 3.60 s, 8.10 s and 14.10 s, cut to 450 ms |
| bare concrete | the cooler and the freezer | `step_concrete.mp3`, `step_concrete2.mp3` | one whole step, then 3.90 s and 7.96 s |
| gravel | the forecourt | `footstep.mp3`, `step_asphalt.mp3` | one whole step, then 4.42 s and 6.72 s |

The three are taken in turn, so two strides in a row are never the same
recording. Where a file is half a minute of somebody walking - a minute, in the
forecourt's case - a step is **played from the moment it actually starts and cut a
moment later**: from the top, a footstep would begin with silence, because the
first tile step is seven seconds into its file. Each variant's gain is measured so
that every step of a floor lands at the same heard level, so a walk never jumps in
volume from one foot to the next - and no cue is ever played with a positive gain,
which is why concrete and the forecourt sit a few dB below the tile. Carpet is
levelled **with** the tile rather than with the quiet ones: the soft socks-on-
carpet recording it used to carry was the one floor nobody could hear at all, and
it is now a close-miked walk of shoes on carpet at the tile's own heard level.
Every offset, peak and gain is written into `assets/manifest.txt` with the numbers
`ffmpeg` gave, so they can be re-checked rather than trusted.

**Walls have their own sound too.** Walk into one and it answers where it is
rather than in your own head: a plasterboard thud in the shop, the office and
your apartment, and a sheet metal clang in the cooler and the freezer, each
placed at the tile you tried to walk into, so the sound says which side you hit
as well as that you hit one. The words "A wall." still follow it, because a wall
is worth naming.

A cue played from an offset needs its bundled tone to be **silent up to that
offset**, or a failed download is silence where the step should be. Each of these
has one, and a file the game seeks to several times - the tile steps, say - is
silent up to the smallest offset it seeks to and tone from there past the largest
one plus the cut, so every variant lands on the beep offline. See
`assets/placeholder/`, and the recipe above those cues in `assets/manifest.txt`.

## Music, and the shop's speakers

The shop has a speaker system in the ceiling, and the music is **off when a
store starts**. Switch it on from the office computer, under **Music**, which
also has the volume, the subwoofers, shuffle, skip and what is playing.

Music is not played straight out of the machine. It is a **sound source in room
space**, up in the ceiling of the shop floor, so the same room isolation table
that muffles the coolers decides what you hear:

* Standing in the shop, it plays at the shop's own volume.
* Through the wall, in the office, it is still there and muffled, exactly like
  everything else next door.
* In the cooler, the freezer or your apartment, it is gone. Walking into another
  area takes the music with you, the way walking away from a shop's speakers
  does. Walking back in resumes the same track where it was.
* Announcements duck the music rather than talking over it.
* A shoplifter making a run for it takes the speakers over with the **Back Aisle
  Dash**, and two drunks going at it take them with the **Closing Time
  Argument**. Both play even with the shop's own music switched off, and when the
  trouble is over the speakers go back to whatever was playing.

### Tracks

| Where | What |
| --- | --- |
| `sounds/music/` next to the game | Your own. Drop `.mp3`, `.ogg`, `.wav`, `.flac`, `.m4a` or `.wma` files in and use **Look for new tracks** on the computer. Scanned first, so your tracks come first in the playlist. |
| `assets/music/` | What the shop ships: four public domain ragtime recordings downloaded on first run (Joplin's *The Entertainer*, *Palm Leaf Rag* and *The Nonpareil*, and the United States Marine Band playing *Sunflower Slow Drag*), plus four instrumentals written for this project. |

Those four written for the project are generated, not licensed from anybody:
`tools/make_music.py` writes a daytime loop, one for after hours, the chase and
the fight as deterministic mono 16-bit WAVs. Re-run it and the same bytes come
back. The other four are fetched from Wikimedia Commons with the rest of the
audio; see [CREDITS.md](CREDITS.md).

The shop floor's own background bed changed too. It used to be a recording of a
Berlin shopping centre, and then of an Asian market whose own description says a
TV and a radio were playing music in it — which is why a radio could be heard in
a convenience store. It is now a supermarket checkout counter with, in the words
of the person who recorded it, "no music, light humming of fridges".

---

## The speech layer

Everything the game says comes out of one of **two channels**, and which one it
is is the design rather than an accident:

* **The player's own channel** is the screen reader that is already running —
  NVDA, JAWS, whatever it is — at the player's own speed, in the player's own
  voice. The menus, the prompts, the reports and everything else the game says
  *to* the player come out here, because it is the voice the player is already
  listening with. With no screen reader running it is a Windows voice instead
  (`screen_reader_preferred=0` asks for that voice even when a reader is
  running). Nothing is ever borrowed from the pool to read a menu line: with no
  screen reader and no voice of its own this machine drops the line and says why
  in `logs/speech.log`, because a menu read out in a customer's voice is a worse
  failure than a menu that says nothing.
* **The people's channel** is the voice pool: every customer and every member of
  staff is given a voice of their own, so a shop full of people does not sound
  like one man. Nothing the player's channel says goes through the pool, and
  nobody in the building is ever read out by the screen reader.

The pool is the rest of this section.

One voice for every person in the shop is the wrong sound, so it is
a **pool**: three keyless server families, each expanded into the voices it really
offers, plus this computer's own installed voices.

Every server is probed at startup rather than stopping at the first success, and
every one that answers contributes its voices:

1. `https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=en&q=`
2. `https://translate.googleapis.com/translate_tts?ie=UTF-8&client=gtx&tl=en&q=`
3. `https://code.responsivevoice.org/getvoice.php?tl=en&sv=g1&pitch=0.5&rate=0.5&vol=1&t=`

A Google server is expanded into one voice per dialect in `voice_google_dialects`
(`en`, `en-gb`, `en-au`, `en-in`, `en-ie`, `en-za`, `en-ca`), and ResponsiveVoice
into one per locale in `voice_responsive_locales` crossed with the engines in
`voice_responsive_engines`. Every one of those was checked: the dialects return
genuinely different recordings, not the same voice relabelled. A browser-like
`User-Agent` is sent, because these endpoints answer a bare client with 401.

Each person is then given a slot, so the queue does not all sound like one
man. Speech is **fetched in the background and played when it arrives**: the clip
for a line is requested through the engine's asynchronous http object, and the
same frame loop that draws the window collects it, decodes it with `load_memory`
and plays it. Nothing about speaking can stall the game. A line longer than
`voice_chunk_chars` is fetched as several pieces, played back to back, because
Google's endpoint answers **HTTP 400** above about 200 characters — and this
game's own sentences are longer than that. A server that has not answered within
`voice_fetch_timeout_ms` has its slot dropped, the people on it are moved to a
voice that still works, and the dead one is never handed out again:

> The voice server did not answer, so the shop is using this computer's voices for this session.

**This computer's own voices are part of the pool too**, `local_voices=1` is the
default, and the engine asked for is **SAPI5** (`local_voice_engines=sapi5`) —
the standard Windows voice set, including any commercial voices bought for it.
That is the answer to "Google is not enough": this machine has **617 installed
SAPI5 voices**, and the shop casts from the English ones the moment they are
ready. They work with no network at all, so a session with the servers down still
has a crowd in it. **The two are not a preference order.** The server voices and
this computer's own voices are in the one pool at the same time and are handed
out from the same cursor; the only thing that ever takes a voice out of the pool
is that voice failing, at which point the person it was speaking for is given
another one from the same pool. Online and offline work together here, which is
where this project parts company with a design that treats the offline voice as
the thing you drop back to.

SAPI5 used to be off by default for one measured reason: asking NVGT for the
installed voices enumerates every one of them, and on this machine that costs
**52 to 59 seconds**, with no way to cache it. It is now built **on a worker
thread while the shop is already open**: measured on a real launch, the menu was
up in 2.3 seconds, the frame loop kept running for the whole minute, and at
1:01 the worker landed and logged `local voice worker built the engine in
58714ms: 617 installed, 24 taking part in the shop`, after which the pool went
from 19 voices to 43 mid-session and said so out loud. `local_voices_max` caps
how many join (24 by default), and `local_voices_english_only=1` keeps the rest
of the world's voices out of a small-town shop.

One trap found while wiring this up, and worth repeating: **a local voice must
carry its index in the engine's own list, not its place in the filtered list.**
The pool hands that index straight back to `set_voice()`, so filtering the names
without carrying the index along — which is exactly what the obvious loop does —
makes every character after the first dropped voice speak with somebody else's
voice. A list whose indices are not contiguous (0, 8, 16) is the case to look at
if this is ever tested again.

The **menus and the reports are not in any of this**. They are the player's own
channel: the running screen reader, NVDA or JAWS or whatever it is, with the
braille mirror, falling back to a SAPI voice only when no screen reader is
running. The pool above is for the people in the building, and a customer is
never read out by the screen reader: **the pool is for what the people say and
for nothing else**, so the two channels do not borrow from each other in either
direction, not even when one of them has nothing to speak with. These endpoints rate-limit rapid requests,
so a session announcing the switch and then running on local voices is the
designed behaviour, not a failure. Set `voice_endpoints=` (empty) to skip the
probe entirely, and `screen_reader_preferred=0` to have the interface read by a
Windows voice even when a screen reader is running.

---

## The hardware speech chips

Everything above is about the *people* in the building and the *player's own
channel*. The machines in the building are a different thing altogether. The back office terminal and the
phone do not speak through the screen reader, do not use a SAPI voice and do not
touch the network. Each one has a speech chip of its own, and that chip is
synthesized by the game itself in [chip.nvgt](chip.nvgt). It is not an invented
voice: it is an emulated **Silicon Systems SSI-263** (the Votrax SC-02 part),
written from the chip's own data and not from a hardware recording — the game
implements the registers that matter, then a converter that throws most of the
detail away. There is no recording and no voice server anywhere in it.

The port comes from [tgeczy/ssi263-speech](https://github.com/tgeczy/ssi263-speech),
a register-level model of the part whose phoneme ROM was read off the die. Its
three pieces are all reproduced here:

* **The phoneme table.** The chip's speech ROM, 64 phonemes wide: for each code,
the filter's frequencies and bandwidths for the first and second half of the
frame, the voiced/unvoiced source routes, and whether the frame holds or moves.
The game carries its own transcribed copy in [chip.nvgt](chip.nvgt), with the
same layout the reference decoder produces, and every frequency in it is checked
against that model.
* **The registers.** `R2` sets the speech rate, `R3` the articulation and the
four bit amplitude, `R4` the filter clock the whole tract is scaled from, `R1`
the inflection glide — and `R0`, bit 0, asks the chip for the next frame.
* **The chip's clock.** A frame lasts `4096 (16 - rate)` cycles and a half frame
`2048 (16 - rate)`; the filter sections run at `1 MHz / (2 (256 - FF))`. That
ratio is why the chip has a voice at all, and holding it means the port is in
the same key as the part.

That is a deliberate choice, and two things only work because of it:

* **The chip can be panned.** A screen reader voice and a SAPI voice belong to
the operating system and always come out of the centre; the engine cannot move
them. Samples this game made are an ordinary sound, so the hardware setup can
speak its count hard left and hard right and genuinely prove both channels.
* **The chip cannot fail.** No endpoint to answer, no voice to enumerate, so it
costs nothing at startup and cannot go quiet because somebody else's server is
down.

The computer is a clean machine that was good in its day: the filter clock its ROM
was checked against (a low `filter_clock` makes a small, squawky voice), moderate
articulation, no converter damage, no dropouts. The phone is a cheap handset: a
clock a little lower, so its tract is smaller and brighter; five bits of
converter; a higher pitch; and a few blocks of audio that simply fall on the
floor. It is meant to sound cheap, **not to be unlistenable**: it used to run at a
9 kHz clock with a 3 bit converter, which put every formant below half where it
belongs and made whole words unrecognisable, and that is no good in the one
device the player has to read a screen through. Every number is a register knob in
`config.ini` under *hardware speech chips*, so turning `chip_phone_filter_clock`
down and `chip_phone_bits` to 3 is all it takes to make the phone unintelligible
again.

### Slowing a machine down, and moving its note

A chip's own speech rate register cannot reach far enough to help. At `R2` zero a
frame lasts 65 ms against the terminal's 41, so the chip's slowest setting is less
than one and a half times slower than its own default — and handing the machine
over to the screen reader is not a fair price for a player who simply needs the
words further apart. So each machine has a **speech speed** and a **pitch** of its
own, set on its own screen: a `Speech speed:` line and a `Pitch:` line on the
manager terminal's home page and on the phone's home page. **Enter on either line
opens a page of settings** rather than stepping the value where it stands — every
setting the machine offers is listed, the one it is on now is named — and the
line the cursor lands on is read out by the machine, so the whole list can be
walked before anything is chosen. Picking one applies it, makes the machine say
what it now sounds like in its own voice, and leaves the player back on the home
page with the cursor on the line that changed.

The speed page is **normal, faster, fastest, slower, very slow**, and this
machine's normal is 65 per cent of the chip's own rate, not the die's own
maximum: a chip left at 100 is faster than it is meant to sound, so 65 is the
number the words are built around and the number a new store starts at. The pitch
page is **higher, a little higher, normal, a little lower, lower**, in per cent
of that machine's own pitch — the terminal and the handset are two different
voices, and "lower" has to mean the same thing on both. Both settings are kept
**in the save**, not in `config.ini`: they are facts about this store's machines,
so loading a slot puts that slot's speed and pitch back on the machines.

A setting change does not cut off what the machine is already saying: the line in
flight finishes at the speed and pitch it started with, and the line cache is
keyed by both, so a machine can never answer at a setting the player has left.
What *does* stop it is a **move**: the line the cursor leaves is dropped the
moment the cursor lands on the next one, the way the player's own voice has
always interrupted itself, so a machine is never still reading the line you are
no longer on.

The speed is a host clock laid over the chip rather than a register: every frame
the tract counts in is stretched by one factor, so the phonemes, the transitions
between them and the pauses between the words all take longer, while the pitch of
the machine stays where the player put it, and the formants and the machine's own
voice stay exactly where they were. Slowing a
machine down is not the same as playing it back slowly, and the difference was
measured rather than trusted: the same vowel was rendered at both speeds to show
that the phonemes really do take twice as long (6412 samples to 11831
at half speed, with the 90 ms the tract rings out at the end of a line the part
that does not stretch) and that the pitch period in samples has not moved at all
(111 Hz against 111 Hz). Note that this is the speed only: the pitch line beside
it is exact, not approximate, because it moves the one number the chip is told.

### Switching a machine on and off

Each of the two machines has a **startup and a shutdown sound** of its own,
played when its screen opens and when it closes or it logs off: the terminal in
two low notes, up to switch on and down to switch off, and the phone in three
quick blips up and two down, because a handset is smaller and brighter than a
desk. They were written for this project and ship as files in `assets/`, at
−12 dBFS and played another −4 dB down, so a chime sits
under the machine's own voice rather than over it. Nothing is fetched and there
is no placeholder tone: silence is what a missing startup chime should sound
like.

### The first time you use the terminal

A terminal that has never been set up in this store does not show its pages. It
installs its chip first, and the routine is a state machine ticked from the frame
loop rather than a loop of its own, which means **the store does not stop for
it** — customers still walk in, the clock still runs, and the room's own ambience
still plays while the chip counts:

1. **Stereo calibration.** The chip counts one to five, hard left on the odd
   numbers and hard right on the even ones, with a blip on the same side ahead of
   each number. The player has to press `Space` to say they heard both sides, and
   `Space` does nothing until the whole sweep has been spoken, because a player
   who confirms halfway through has confirmed nothing.
2. **Voice chip activation.** The chip reads its own diagnostic out in its own
   voice, which is what proves the chip is the thing doing the talking.
3. **Write.** `is_computer_initialized` becomes true and the save is written, so
   every later visit to the terminal goes straight to its ordinary pages.

`Escape` does not get you out of it: a half-installed machine is a half-installed
machine. `H` repeats whatever the routine is asking for in the reading voice.
Because the clock genuinely does not stop, the one thing that can interrupt the
routine is the day ending; the step it had reached is remembered, and the next
visit to the terminal picks up there.

### What the terminal sounds like once it is installed

The terminal keeps speaking through its own chip for the rest of the game. Every
screen it opens is announced by the back office chip, in the machine's voice, and
everything the player does on it — an order placed, a price changed, a readout
asked for — is read out by the chip too, because the result belongs to the
machine. **The line the cursor is on is the machine's as well**: while a machine
owns the screen, every line of it goes to that machine's chip, so a page can
never end up half read by the machine and half by the screen reader. The screens
the player's own voice owns — the register, the pause menu, the issue reporter —
are the ones that speak through the screen reader.

The split is implemented in one place rather than at a hundred call sites.
`mechanics.nvgt`'s `menu_line_spoken()` asks `machine_for_modal()` which voice
owns the screen, and the terminal's own readouts arrive as `say()` calls that
`terminal_capture_begin()` holds for a moment and hands to the chip after the
action has run. Nothing outside that moment is touched, so the time key, the help
list, the money report and a customer walking in are all still spoken in the
player's voice with the terminal open.

Two honest notes about it. A chip line is **rendered a slice at a time** while
the shop carries on, so the first thing a chip says can be a beat behind the
moment the game asks for it; a line the chip has already said once is played from
a cache instead.
And because a chip is a synthesizer rather than a voice actor, `chip_mirror_lines=1`
reads each chip line out again half a second later in the reading voice. That is
off by default on purpose: a machine that is read back by the screen reader is a
machine with no chip in it, and the point of these devices is that they speak for
themselves. The knob is there for a player who cannot follow a chip voice at all,
and nothing else about a device changes either way.

---

## Audio assets

The game ships no third-party recordings. `assets/manifest.txt` lists **28
recordings**: 34 cues and the four music tracks, and the game resolves them in
three steps:

1. **Check first, download second.** The bootstrap counts only the recordings that
   are missing or that sit on disk at the wrong size. If that count is zero it
   does not start at all, logs one line, and the menu is up immediately. Fetching
   runs beside the game in a frame-driven state machine, so the window never
   freezes and **never takes the keyboard away** while it works.
2. **Fall back** to the matching locally generated tone in `assets/placeholder/`
   for anything that cannot be fetched after its retries.
3. **Skip**: `Escape` during the download uses the bundled tones immediately.

**All 34 cues now have real recordings.** Twenty-four come from Wikimedia Commons
and ten from Freesound's public preview CDN: an engine idling on the forecourt, a
television muffled through the flat's wall, a wet step, crockery hitting the
floor, a fly swatter, a punch, a delivery truck starting up, the shop floor
trading, the street outside, a shoplifter rustling at a shelf, and the ten noises
a customer's body makes. Each was picked for the cue it serves, not by name match
alone, and the last placeholder tones were the first thing to go. Nothing
third-party is in the repository: the bootstrap fetches all of it from the URLs in
`assets/manifest.txt`.

**The ten body sounds are the only cues the game seeks into.** They are whole
sessions rather than single cues — the cough file is twenty-one seconds of
somebody coughing with long gaps, and its first half second is silence — so each
one carries the point in the recording where the sound actually is. That made
their **fallback tones** a case of their own: the bundled tone used when a
download cannot be reached is the cue's own offset of silence followed by the same
quiet tone as every other placeholder, so the seek lands on the beep at the moment
the cue happens rather than seconds after it or, for a sigh, past the end of a four
second beep, which was silence. The offset and the cut are recorded per cue in
`people_emote_offset()` and `people_emote_cut_ms()`, and each fallback tone in
`assets/placeholder/` is built to be at least as long as the two of them
together.

Four of those exist because the sound they replaced was wrong in a way worth
recording. The shop floor's ambience **and** the road outside were both the same
recording of a Berlin shopping centre, so a piano played indoors in a convenience
store and a mall stood in for a street. The replacement for the shop floor was
then wrong in a subtler way: it was an Asian market whose own description says
"there's a TV tuned to Japanese programming behind the counter; in a nearby
aisle, a radio plays pop music" — which is music in the room with no way to
switch it off. It is now a supermarket checkout counter described as having **no
music** and light humming of fridges. The road is real city traffic. And the
shoplifter's rustle used the shop ambience as its one-shot, which meant **a whole
minute of room noise for one rustle**, because a one-shot plays its file to the
end — it has a four second cue of its own now.

Two more of that shape, both found by ear rather than by reading.
**`scanner.ogg` is twenty nine seconds of supermarket checkout**, and every menu
in the game was playing it from the top on every arrow key, over itself, on top
of the line the player was trying to hear — which is why the sound output list
could be opened but not walked through. A menu tick is now one function,
`sfx_tick()`, and it is 140 ms of that recording (`SFX_MENU_TICK_MS`). And
**`chime.ogg` is a twenty two second bell**; it is the shop's door and nothing
else, cut to the ring (`DOOR_CHIME_CUT_MS`, 1.5 s), so a customer walking in does
not ring a bell for the next twenty seconds.

The four music tracks are the one exception to "nothing is baked in": they are
fetched like everything else, and the four the project writes itself live in
`assets/music/` as shipped files.

The downloader paces itself because `upload.wikimedia.org` answers bursts with
**HTTP 429**, retries with exponential backoff, and compares every body against
the server's own `Content-Length` — never against a guess. Anything short is
thrown away and refetched, and the body is staged as `name.part` and renamed into
place, so a half-written file never wears the real name.

Each manifest line ends with the file's exact verified size. That column makes a
damaged file self-healing: the bootstrap otherwise skips anything already on disk,
so a download interrupted months ago would stay truncated forever, playing
clipped and looking perfectly normal. With the size recorded, a file of the wrong
length is deleted and fetched again. Two codec notes, both learned the hard way:

* **Ogg Opus is not decodable here, only Ogg Vorbis.** The forecourt pump was
  silent for its whole life because its source was an `.ogg` that held Opus — a
  valid file the engine simply could not open, with no error to show for it. It is
  now an MP3 from Freesound. Check the codec, not just the extension.
* **The extension must match the container.** Files are written byte for byte as
  downloaded and loaded by the manifest's name, so the seven recordings arrive as
  `.mp3` and one as `.wav`. Code that names an asset in `A("...")` has to agree.

To re-download, delete the files in `assets/` but keep `assets/placeholder/` and
`assets/manifest.txt`. See [CREDITS.md](CREDITS.md) for every source and licence.

---

## Architecture

[main.nvgt](main.nvgt) includes eleven modules in dependency order, and then
drives them:

| File | Responsibility |
| --- | --- |
| [audio.nvgt](audio.nvgt) | Config, diagnostics logging, the speech layer, the asset bootstrap, the spatial audio field with multi-room isolation. |
| [core.nvgt](core.nvgt) | Money and clock helpers, the clock globals and its rate, the screen state. |
| [chip.nvgt](chip.nvgt) | The hardware speech chips: the phoneme and word tables, the formant synthesizer, the two voice profiles, the pannable players and the render queue. |
| [rooms.nvgt](rooms.nvgt) | Room grids, materials, the mess overlay, facing, portals, movement, the camera, scanning. |
| [money.nvgt](money.nvgt) | Till, weekly bill day, arrears ladder, loans, insurance, income tax. |
| [shop.nvgt](shop.nvgt) | The catalogue, twenty faces, stock, ordering, the Monday truck, pricing, the market. |
| [staff.nvgt](staff.nvgt) | Roles, applicants, rotas, wages, satisfaction, staff requests. |
| [people.nvgt](people.nvgt) | Customers, baskets, the queue, patience, reviews, reputation, footfall. |
| [trouble.nvgt](trouble.nvgt) | Mess, shoplifters, the swatter, drunks, fights, the panic button, the police. |
| [hardware.nvgt](hardware.nvgt) | The devices in the building, the per-save install flags, and the non-blocking routine that installs the terminal's chip. |
| [mechanics.nvgt](mechanics.nvgt) | The till and the serving flow, the frame tick, day events, the office computer, the phone, the pause menu, save and load, key dispatch tables. |
| [main.nvgt](main.nvgt) | Window, module build order, menu, frame loop, clean shutdown. |

### Traps, and what each one cost

**The frame-driven downloader must never own the frame loop.** The bootstrap runs
at startup, and it used to take over the whole loop while it worked: no menu, no
keys, nothing but Escape. A launch with recordings to fetch therefore ignored
every press for up to two and a half minutes and looked exactly like a hang, while
the music carried on playing. Downloading now happens alongside the menu and the
world, and a launch with everything present does not even enter that state.

**`http::response_body` drains on read, so the last chunk arrives late.** The
final 64 KiB or less of a body can land in the instant *after* `complete` flips
true. A downloader that reads the body once and writes it there and then saves a
truncated file: on this project a 356,430 byte recording was written as 327,680
bytes, exactly five 64 KiB chunks, with the transfer reported complete and not a
word of complaint. A clipped WAV or MP3 still plays, so nothing else in the game
could ever notice. Read the body again over the next couple of frames, compare the
total against the server's `Content-Length`, and the file is whole.

**`sound::stream_url()` blocks the calling thread and has no timeout.** Playing
an utterance straight off a speech URL looks tidy and is a trap: when an endpoint
went quiet mid-request the call simply never returned, so the window froze and
stopped taking keys while nothing at all reached the log — the freeze was
invisible precisely because it was silent. The fix is not a smaller timeout, since
there is no timeout to set: speech is fetched with the asynchronous `http` object
and played from memory when it arrives. **Anything that talks to the network from
the frame loop must be asynchronous**, which the asset bootstrap already knew and
the speech layer did not.

**Speech endpoints have a character limit, and it is shorter than this game's
sentences.** Google's translate_tts answers **HTTP 400** above about 200
characters, so the new game greeting — 225 characters — was refused every single
time, and a refused line used to cost the voice that tried it. Long lines are now
split at word boundaries and the pieces are played back to back.

**A one-shot cue plays its file to the end, so a loop recording must never be used
as one.** The shoplifter's rustle pointed at the shop ambience file, which meant a
full minute of room noise for a rustle at a shelf. Short cues need short files.

**The extension and the codec both matter, and they are different things.** Files
are written byte for byte as downloaded, and the engine decodes Vorbis, MP3 and
WAV but not Ogg Opus. A valid `.ogg` holding Opus loads as nothing at all, with no
error — which is why the forecourt pump was silent for its whole life.

### Two constraints worth knowing before you edit anything

**AngelScript has no function prototypes at the top level**, so a bare signature
such as `float rooms_are_adjacent(int a, int b);` is parsed as a *global variable*.
Keep functions above their first caller. `mechanics.nvgt` is ordered strictly
bottom-up; if you move a function, move it up, not down.

**Assigning one object handle to another needs the `@`.**

```
thing@ best = null;
best = t;      // compiles, then dies: this is a VALUE copy via opAssign,
               // which dereferences a null handle
@ best = t;    // this is the handle assignment you meant
```

The `=` form is only correct in a declaration (`thing@ best = t;`), on an array
element (`g_things[i] = t;`, which goes through `opIndex`), and on `= null` it
does not compile at all. This one costs an afternoon every time it is forgotten,
because the compiler is silent and the crash points at the assignment line.

### The frame pump

The design brief asked for `process_game_window()` each frame. **That function
does not exist in NVGT** — it is absent from the 918-page reference, the engine
binary and every shipped include.

The real equivalent, and what the documentation mandates for every main loop, is
`wait(5)`: on the main thread it pumps window and input events, performs
incremental garbage collection, refreshes the window and yields the CPU.
`main.nvgt` wraps it in one named directive:

```
void process_frame() {
	wait(5);
}
```

so every loop calls the same pump and none can forget it.

---

## Verification

**There is no test harness in this project, and the game is not checked by a
script.** It is checked by compiling it and by playing it.

**Compile it.** This is the bar nothing gets past:

```
nvgt.exe -c -q main.nvgt
```

It must exit 0 and write `main.zip`. A clean compile proves the script parses,
every symbol it names exists and the include order is right — and nothing else.
Compiling is not playing: do not report behaviour nobody has heard.

**Then play it.** The store is the test. `F1` reads every key aloud, and the debug
keys get you to a state quickly: `F7` and `F8` step the clock an hour back or
forward, `F11` sends in a shoplifter, `Ctrl+Shift+R` turns diagnostic logging into
`logs/speech.log`, and `Ctrl+F1` writes a full state snapshot to it. When
something behaves oddly the log is the first place to look, and the snapshot is
the first thing to send.

**Delete the product when you are done with it.** `nvgt.exe -c main.nvgt` writes
`main.zip` beside the source, and **that bundle shadows `main.nvgt`**, so the next
run loads the stale build and your edits appear to have done nothing. See the note
under the traps below.

Verified by actually running it: the project compiles clean, and the compiled
`main.exe` creates its window, builds all six rooms with 128 products across 20
faces, probes the voice server, builds its speech chips, loads its assets and runs
its frame loop.

Verified on the audio specifically, by running the real thing rather than reading
it: the packaged build was started with `assets/` emptied and downloaded **all the
recordings from scratch, every one byte-identical to what its URL serves** (SHA-1,
not just the byte count) with no placeholder fallbacks. Each was then loaded *and
played* through the NVGT engine, and the seven cues with new sources were
downloaded a second time from a clean `assets/` to prove their manifest lines.

The speech fix was measured rather than assumed, by driving the real code path
against the live endpoints: the 225-character greeting is cut into two pieces,
both are fetched and played, **0 of 19 voices are dropped**, and the longest
single `speech_update()` call was **53 ms**. The old path blocked forever. A file
was then truncated to 327,680 bytes on purpose and the next launch logged `is
327680 bytes, expected 356430; refetching` and repaired it inside ten seconds.

The chip renderer was tuned the same way, with the cost written down rather than
guessed. The first version reached through two object handles and an array for
every sample and measured **267 ms of work per second of speech**; hoisting the
state into locals and moving from 22050 Hz to 11025 Hz took it to **64 ms per
second**, which is the figure the chip logs when it renders. A slice is 700
samples, so the largest single frame of the twenty second routine wrote 2100
samples — about two milliseconds of work — and the routine itself was spread over
104 frames instead of stalling one.

**Not verified:** the game has been played by exactly one human, briefly, and that
session is where the input lock and the leaking music were found — but it was not
a full playthrough. No cue has been *listened* to in its place in the world, the
spatial placement of the beacons is still hearsay, and most of the key bindings in
`main.nvgt` have never been pressed. **Nobody has heard a speech chip yet**, which
for this feature is the one that matters: the phoneme tables are ordinary
formant-synthesis figures, and the samples have been measured to be real, loud,
the right length and panned to the right side, but whether the chip sounds like a
1980s appliance or like a broken modem is a judgement only an ear can make. If it
is not intelligible, `chip_computer_bits` and `chip_computer_pitch_hz` are the two
register knobs to move first, and the machine's own `Speech speed:` and `Pitch:`
lines change its voice a step at a time without editing anything by hand — though
whether the slow or the lowered setting is *better* is, again, an ear's judgement
and not a measurement's.

### Two more traps, already paid for

* Compiling with `nvgt.exe -c main.nvgt` writes `main.zip` next to the source, and
  **that bundle then shadows `main.nvgt`** — the engine runs the stale build and
  your edits appear to do nothing. Delete it, or build from elsewhere. The bundle
  is a zip containing `main.exe` and `lib/`; extract it to distribute.
* Constructing a `tts_voice` measured **51 seconds** on the development machine,
  because it enumerates every SAPI voice. It is created lazily on first use and
  never at all when a screen reader is talking, which took startup from 52 seconds
  to 0.6. See the note above `g_tts` in `audio.nvgt` before changing it.

* **`out` is a reserved word** in AngelScript, so `file out;` will not compile.
  The bootstrap's staging handle is called `outf` for that reason, and the same
  trap will bite any new code that reaches for the obvious name.

* **A local voice must keep its engine index.** The pool stores the index it will
  hand back to `set_voice()`, so numbering the voices by their place in a filtered
  list makes every character after the first filtered-out voice speak with
  somebody else's voice, silently. Carry the index with the name, always. A
  non-contiguous list (0, 8, 16) is the case that exposes it.

* **A worker thread can build a `tts_voice` and the main thread can use it.** This
  was measured rather than assumed: the worker takes 52-59 seconds for 617 SAPI
  voices while the frame loop keeps running, and afterwards `set_voice()` and
  `speak()` from the main thread both answer yes. That is what makes SAPI5
affordable at all. The pool is only ever written from the main thread: the worker
  fills plain arrays and sets a ready flag last, and `voice_local_update()` does
  the insertion.

* **Interpolate decibels from silence, not from zero.** The subwoofer fade was
  written as a multiplication, which turned the *quietest* setting (-60 dB to mean
  no sub bass) into the loudest one, because multiplying a decibel figure by a
  fade factor is meaningless. It fades from -60 dB instead.

* **Action constants are a shared namespace.** Two features cannot pick the same
  number: `ACT_MUSIC_PREV` and `ACT_RENAME` both landed on 130, and the engine
  says only `Duplicate switch case`, pointing at the switch rather than at the
  constants. Check the list before adding one.

* **`save_game()` writes nothing unless a game is running** — it returns at once
  when `g_game_mode` is false. A test or a menu that saves without setting that
  flag gets silence and a stale file, with no error.

* **A shelf holds what its capacity says, and no more.** `shop_unsell()` clamps
  to capacity, so stock set above capacity in a test comes back clamped to zero
  and the goods appear never to return. Set stock inside capacity in any new test.

---

## Output files

| Path | Written when |
| --- | --- |
| `logs/speech.log` | Every utterance, cue and module message, when diagnostics are on. |
| `saves/slotNN.txt` | On `Escape`, on clean exit, and the moment a machine finishes installing itself; also, one line at a time, the moment a machine's `Speech speed:` or `Pitch:` line is pressed. The previous save is kept as `.bak`. Carries `computer_init` and `phone_init`, the per-store hardware flags, and the two machines' `chip_computer_*`/`chip_phone_*` speech speed and pitch. |
| `assets/` | Fetched on first run; the tone fallbacks live in `assets/placeholder/`. |
| `assets/music/` | The eight tracks the shop's speakers can play. Four are fetched, four ship with the game. |
| `sounds/music/` | Yours, if you make one. Scanned first, so your tracks come first. |
