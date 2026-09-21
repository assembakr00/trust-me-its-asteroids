import pygame
from circleshape import CircleShape
from constants import SHOT_RADIUS

class Shot(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, SHOT_RADIUS)


    def draw(self, screen) -> None:
        pygame.draw.circle(
            screen, 
            "red", 
            self.position, 
            self.radius
        )

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt