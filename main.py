import pygame
from constants import SCREEN_HEIGHT
from constants import SCREEN_WIDTH
from logger import log_state
import player

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
    player.Player.containers = (updatable, drawable)

    player.Player(x=SCREEN_WIDTH / 2, y=SCREEN_HEIGHT / 2)

    while True:
        log_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        updatable.update(dt)
        
        screen.fill("black")
        for obj in drawable:
            obj.draw(screen)

        pygame.display.flip()


        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()