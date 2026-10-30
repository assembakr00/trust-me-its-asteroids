import pygame
import random
from logger import log_event
from circleshape import CircleShape
from constants import ASTEROID_MIN_RADIUS

ASTEROID_VISUAL_SCALE = 1.25


class Asteroid(CircleShape):
    sprite_images: dict[str, pygame.Surface] = {}

    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)

        if not Asteroid.sprite_images:
            Asteroid.sprite_images = {
                "large": pygame.image.load(
                    "assets/art/asteroid-large.png"
                ).convert_alpha(),
                "medium": pygame.image.load(
                    "assets/art/Asteroids-medium.png"
                ).convert_alpha(),
                "small": pygame.image.load(
                    "assets/art/asteroid-small.png"
                ).convert_alpha(),
            }

        if radius >= ASTEROID_MIN_RADIUS * 3:
            sprite_name = "large"
        elif radius >= ASTEROID_MIN_RADIUS * 2:
            sprite_name = "medium"
        else:
            sprite_name = "small"

        sprite = Asteroid.sprite_images[sprite_name]
        sprite_scale = 1.5 if sprite_name == "small" else ASTEROID_VISUAL_SCALE
        sprite_diameter = round(self.radius * 2 * sprite_scale)
        sprite_size = (sprite_diameter, sprite_diameter)
        self.image = pygame.transform.scale(sprite, sprite_size)
        self.image = pygame.transform.rotate(self.image, random.randrange(360))

    def draw(self, screen) -> None:
        image_rect = self.image.get_rect(
            center=(round(self.position.x), round(self.position.y))
        )
        screen.blit(self.image, image_rect)

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.wrap_position()

    def split(self, max_children: int = 2) -> None:
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS or max_children <= 0:
            return

        log_event("asteroid_split")
        angle = random.uniform(20, 50)
        new_radius = self.radius - ASTEROID_MIN_RADIUS
        child_velocities = (
            self.velocity.rotate(angle) * 1.2,
            self.velocity.rotate(-angle) * 1.2,
        )

        for velocity in child_velocities[:max_children]:
            child = Asteroid(self.position.x, self.position.y, new_radius)
            child.velocity = velocity
            