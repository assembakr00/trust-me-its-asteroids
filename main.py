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
    
    lives = 3

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
            for player_obj in players:
                if player_obj.invulnerable_timer > 0:
                    continue

                if asteroid_obj.collides_with(player_obj):
                    lives -= 1
                    player_obj.invulnerable_timer = 2.0
                    log_event("player_hit")

                    if lives <= 0:
                        print("Game over!")
                        sys.exit()

                    player_obj.position = pygame.Vector2(
                        SCREEN_WIDTH / 2,
                        SCREEN_HEIGHT / 2,
                    )
                    break

            for shot_obj in shots:
                if asteroid_obj.collides_with(shot_obj):
                    log_event("asteroid_shot")
                    asteroid_obj.split()
                    shot_obj.kill()

        screen.fill("black")

        # draw all game sprites
        for obj in drawable:
            obj.draw(screen)

        # HUD box in top-left
        hud_rect = pygame.Rect(12, 12, 170, 60)
        pygame.draw.rect(screen, (35, 35, 35), hud_rect, border_radius=10)
        pygame.draw.rect(screen, (180, 180, 180), hud_rect, 2, border_radius=10)

        heart_count = lives
        heart_start_x = hud_rect.x + (hud_rect.width - heart_count * 28) // 2
        heart_y = hud_rect.y + 18

        for i in range(lives):
            x = heart_start_x + i * 28
            pygame.draw.polygon(
                screen,
                (255, 90, 90),
                [
                    (x, heart_y + 8),
                    (x - 8, heart_y),
                    (x - 14, heart_y + 8),
                    (x - 6, heart_y + 20),
                    (x, heart_y + 28),
                    (x + 6, heart_y + 20),
                    (x + 14, heart_y + 8),
                    (x + 8, heart_y),
                ],
            )

        pygame.display.flip()

        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()