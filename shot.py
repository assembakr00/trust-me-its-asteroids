import pygame
from circleshape import CircleShape
from constants import SHOT_LIFETIME_SECONDS, SHOT_RADIUS

class Shot(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, SHOT_RADIUS)
        self.lifetime = SHOT_LIFETIME_SECONDS


    def draw(self, screen) -> None:
        pygame.draw.circle(
            screen, 
            "red", 
            self.position, 
            self.radius
        )

    def update(self, dt: float) -> None:
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return
        self.position += self.velocity * dt
        self.wrap_position()