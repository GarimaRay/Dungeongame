ungeon Game (MVC) — tiny micro‑roguelike

A tiny Python micro‑roguelike built with a clean MVC split and two front‑ends:
	•	Console (ASCII map)
	•	GUI (Tkinter) with Start and End screens

Your goal: collect all coins ($) to open the exit gate (E), then step on it to win.
Monsters roam the dungeon using a simple random walk. Collisions and nearby monsters can hurt you—watch your HP!

⸻

Features
	•	Two front‑ends: console + GUI (same game rules).
	•	Exit gate that stays locked until you collect all coins.
	•	Roaming monsters:
	•	Simple random walk each turn.
	•	Immediate collision damage if you step onto a monster.
	•	Random encounter damage if a monster ends up on/next to you after it moves.
	•	Ambient hints (subtle text nudges toward coins/exit).
	•	GUI UX:
	•	Start Game overlay.
	•	YOU WON! / YOU LOST! end overlay showing the final reason (win text or cause of death).

⸻

Quick start

Requires Python 3.10+ (for modern type hints).
GUI requires Tkinter (bundled on Windows/macOS official installers; Linux may need python3-tk).

# Clone
git clone <your-repo-url>
cd <your-repo-name>

# (Optional) Create & activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Run — from the repo root
python DungeonGame/main.py         # Console edition
python DungeonGame/main_gui.py     # GUI edition

If Tkinter is missing (Linux)

sudo apt-get update && sudo apt-get install -y python3-tk

If running headless (SSH/CI/WSL)

Use the console edition (python DungeonGame/main.py) or ensure you have an X display (e.g., WSLg on Win11).

⸻

How to play

Controls

Console
	•	Type: n, s, e, w to move
	•	Other: look, inv, help, quit

GUI
	•	Move: Arrow keys or W/A/S/D
	•	Start with the Start Game button
	•	When the game ends, an overlay shows YOU WON or YOU LOST; click Quit (or press Enter/Esc)

Tiles / Legend
	•	# = wall
	•	. = floor
	•	P = player
	•	$ = coin
	•	M = monster
	•	E = exit gate (red = locked, green = open)

Rules (short)
	•	Collect every coin to open the exit gate.
	•	Step onto E after it’s open to win.
	•	HP starts at 10. If it hits 0 → you lose.
	•	Monsters:
	•	Immediate collision (you step onto a monster): 2 HP damage (no randomness).
	•	Post‑move encounter (monster ends on/adjacent to you): random chance to take damage.
	•	Adjacent: ~35% for 1 HP
	•	Same tile: ~90% for 2 HP

⸻

Project structure

```
DungeonGame/
├── controllers/
│   ├── game_controller.py   # rules/turn logic (shared by both UIs)
│   └── gui_controller.py    # key handling that calls the shared rules
├── models/
│   ├── game_state.py        # GameState dataclass
│   ├── player.py            # Player dataclass (pos, hp, gold, inventory)
│   └── world.py             # Map, coin & monster placement, helpers
├── views/
│   ├── console_view.py      # ASCII rendering
│   └── gui_view.py          # Tkinter rendering + overlays
├── main.py                  # Console entrypoint
└── main_gui.py              # GUI entrypoint (Start + End overlays)
```
Architecture: very small MVC.
	•	Controllers decide what happens (movement, damage, win/lose).
	•	Views only render state.
	•	Models hold data (player, world, state).

⸻

Configuration & tuning

You can quickly change difficulty/feel by editing a few constants.

Number of coins / monsters & map

models/world.py → World.default()
	•	Map: the rows list (walls #, floors .). Default is a friendly 15×9.
	•	Exit: w.exit = (w.width - 2, w.height - 2) (bottom‑right inside the walls).
	•	Placement: w.populate(start=(1, 1), n_coins=5, n_monsters=3)

Encounter probabilities & damage

```
controllers/game_controller.py (top of file):

ENCOUNTER_PROB_ADJ = 0.35  # adjacent monster hit chance
ENCOUNTER_PROB_ON  = 0.90  # same-tile monster hit chance after they move
DAMAGE_ADJ = 1
DAMAGE_ON  = 2
```

Want it harsher? Raise probabilities or damage. Gentler? Lower them.

Player stats

models/player.py

hp = 10      # starting HP
pos = (1, 1) # starting tile (must be floor)

GUI visuals

views/gui_view.py

TILE = 48    # tile pixels
COLORS = {...}


⸻

Troubleshooting

“No module named tkinter”
Install Tk (Linux: sudo apt-get install python3-tk). On macOS/Windows, install Python from python.org.

TclError: no display name and no $DISPLAY
You’re running headless. Use the console version or run with an X server/WSLg.

SyntaxError on | type hints
You’re on Python < 3.10. Upgrade Python or refactor type hints to older typing.Optional/Union style.

Imports fail / module not found
Run from the repo root:

python DungeonGame/main.py
python DungeonGame/main_gui.py

or cd DungeonGame && python main.py. Avoid python -m DungeonGame.main_gui unless you convert imports to package‑relative throughout.

Stale bytecode (changed files not taking effect)

find DungeonGame -name __pycache__ -type d -exec rm -rf {} +


⸻

Design notes
	•	Simplicity > everything: no pathfinding, no complex AI. Monsters random‑walk; encounters are tiny coin‑flip checks.
	•	Single rules engine (GameController.step) used by both UIs → no drift.
	•	Deterministic effects for clarity (e.g., coin pickup, gate checks), with a dash of randomness for monster danger.

⸻

Roadmap (nice‑to‑haves)
	•	Sound effects (console beeps / Tkinter bell) for hits or victory.
	•	Multiple levels or a seed input.
	•	A tiny score screen (coins, turns survived).
	•	Save/load of last run.

⸻

License

Choose a license (e.g., MIT) and drop it here. Until then, this code is “all rights reserved.”

⸻

Credits

Built as a compact teaching/demo project for MVC structure in Python with both console and Tkinter front‑ends.

Happy dungeoneering! 🗝️🪙🐉