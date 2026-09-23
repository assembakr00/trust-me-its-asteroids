# Trust Me, It's Asteroids

A small Asteroids-style game built with Python and Pygame. It has a ship, a suspicious number of asteroids, and enough momentum to make a tiny mistake feel very educational.

## Introduction

The goal is simple: fly around, shoot asteroids, and avoid becoming part of the scenery.

This project started as a hands-on exercise in game loops, sprite groups, vectors, collision detection, and the particular joy of debugging something that moves in four dimensions when you only asked for two.

## How It Works

The game runs a Pygame loop that:

1. Reads window events and keyboard input.
2. Updates the player, shots, asteroid field, and asteroids using frame time (`dt`).
3. Checks collisions between the player, shots, and asteroids.
4. Draws the current frame.
5. Displays the frame and repeats.

Game objects inherit from `CircleShape`, which provides a position, velocity, radius, and circle-based collision detection. Asteroids are drawn with irregular polygon points, so they are technically more lumpy than circles while still using simple circular collision rules.

Large asteroids split into two smaller, faster asteroids when hit. Small asteroids disappear instead. This is a classic arcade solution: when in doubt, make the problem smaller and give it friends.

## How To Play

Run the game with:

```bash
uv run main.py
```

Controls:

| Key | Action |
| --- | --- |
| `W` | Move forward |
| `S` | Move backward |
| `A` | Rotate left |
| `D` | Rotate right |
| `Space` | Fire |
| Close the window | Quit |

You start with three lives. Colliding with an asteroid costs one life and sends the ship back to the center. Shooting is limited by a short cooldown, because holding Space should not turn the ship into an accidental paintball turret.

## Running Checks

Compile the main modules with:

```bash
python3 -m py_compile main.py player.py asteroid.py asteroidfield.py shot.py circleshape.py
```

The game also writes runtime events and state snapshots to JSON Lines files. These files are useful for local debugging and are ignored by Git.

## Upgrades

Ideas for future versions:

- Draw a small heart-based lives display instead of showing lives only through behavior.
- Add a short invulnerability period after respawning.
- Add a score and a high-score table.
- Add sound effects and background music.
- Add a start screen, pause screen, and game-over screen.
- Add screen wrapping so objects leaving one edge return from the opposite side.
- Add particle effects when asteroids split.
- Add different weapon types and power-ups.
- Add a browser build for itch.io or GitHub Pages.

## Project Status

This is a small learning project in active development. The game is playable, but the asteroid field remains committed to making every quiet moment feel temporary.
