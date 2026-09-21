import pygame
import sys
from constants import (SCREEN_HEIGHT, 
                       SCREEN_WIDTH, 
                       ASTEROID_KINDS,
                       ASTEROID_SPAWN_RATE_SECONDS,
                       ASTEROID_MAX_RADIUS, 
                       ASTEROID_MIN_RADIUS,
                       PLAYER_RADIUS,
                       PLAYER_SPEED,
                       PLAYER_TURN_SPEED,
                       PLAYER_SHOOT_SPEED)
from logger import log_state, log_event
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot



def main():
    pygame.init()
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    clock = pygame.time.Clock()
    dt = 0.0

    drawable = pygame.sprite.Group()
    updatable = pygame.sprite.Group()
    players = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    Player.containers = (updatable, drawable, players)
    Asteroid.containers = (updatable, drawable, asteroids)
    AsteroidField.containers = (updatable)
    Shot.containers = (updatable, drawable, shots)

    Player(x=SCREEN_WIDTH / 2, y=SCREEN_HEIGHT / 2)
    AsteroidField()

    while True:
        log_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        updatable.update(dt)

        for asteroid_obj in asteroids:
            if any(asteroid_obj.collides_with(player) for player in players):
                log_event("player_hit")
                print("Game over!")
                sys.exit()
            for shot_obj in shots:
                if asteroid_obj.collides_with(shot_obj):
                    log_event("asteroid_shot")
                    asteroid_obj.split()
                    shot_obj.kill()

        screen.fill("black")
        for obj in drawable:
            obj.draw(screen)

        pygame.display.flip()


        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()