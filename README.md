# Trust Me, It's Asteroids

A small Asteroids-style game built with Python and Pygame. It has a ship & a buttload number of asteroids

## Introduction

The goal is simple: fly around, shoot asteroids, and avoid becoming part of the rocks!!

This project started as a hands-on exercise in game loops, sprite groups, vectors, collision detection and the particular joy of debugging something that moves in four dimensions when you only asked for two and for crying out loud why do i say this catch phrases damn it

## How To Play

Controls:
 
 Key | Action 

 W to Move forward 
 S to Move backward 
 A to Rotate left 
 D to Rotate right 
 Space to Fire 
 esc the window to Quit or go back

You start with 100hp Colliding with an asteroid costs one diff hp and sends the ship blinks for some time as a varnuable time. Shooting is limited by a short cooldown because holding Space should not turn the ship into an accidental paintball turret(i kinda del that bec i like choas BUT each lvl has a shot and asteroids count limit).


## Upgrades

Ideas for future versions:

- Draw a small heart-based lives display instead of showing lives only through behavior(done)
- Add a short invulnerability period after respawning.(done)
- Add a score and a high-score table.(done)
- Add sound effects and background music.(done)
- Add screen wrapping so objects leaving one edge return from the opposite side.(done)
- Add different weapon types and power-ups.(will do ut added skins and animations)
- Add a browser build for itch.io or GitHub Pages.(made a relaese that has an exe file and itch when adding more things)

## anyways side note

This is a small learning project in active development. The game is playable, but the asteroid field remains committed to making every quiet moment feel temporary.
and i just read what i wrote and damn i may compete with ai for whos readme has an ai look >:[ oh and the wole version stuff is downwards

## Versions
heya
I made the first release 1.4, but 1.0 was just the base game. It had only the core gameplay—no main menu, skin menu, or art—just the basic math and vectors.
Version 1.1 added a main menu with a small title art, asteroids, and a classic plane. I also started adding levels, specifically easy and medium.
Version 1.2 didn't have extra art, but it included two new levels, scoring, and a high score system for each level. I also added an audio mixer and custom damage for each asteroid.
Version 1.3 brought a lot of new art, including background stars and a custom main title. I added a skin page with two skins, and each skin has two thrust animations complete with a preview. I also fixed bugs, such as the enter button issue; because Pygame requires custom mapping for each enter key, the Numpad enter wasn't working, so I fixed that. I added the Escape key to go back or exit, set limits for shots and asteroids in each level, and added custom damage settings for each level.
Version 1.4 introduced even more custom art and details, along with plenty of bug fixes and stress testing. That is all for now!
