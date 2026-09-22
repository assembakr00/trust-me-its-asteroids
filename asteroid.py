import pygame
import random
from logger import log_event
from circleshape import CircleShape
from constants import LINE_WIDTH, ASTEROID_MIN_RADIUS


class Asteroid(CircleShape):
    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)
        self.vertices = []

        for index in range(10):
            angle = index * (360 / 10)
            radius_variation = self.radius * random.uniform(0.8, 1.2)
            point = pygame.Vector2(0, radius_variation).rotate(angle)
            self.vertices.append(point)

    def draw(self, screen) -> None:
        points = [self.position + vertex for vertex in self.vertices]
        pygame.draw.polygon(screen, "black", points)
        pygame.draw.polygon(screen, "white", points, LINE_WIDTH)
        pygame.draw.circle(
            screen, 
            "white", 
            self.position, 
            self.radius, 
            LINE_WIDTH
        )

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt

    def split(self) -> None:
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        else:
            log_event("asteroid_split")
            angle = random.uniform(20, 50)
            new_radius = self.radius - ASTEROID_MIN_RADIUS
            velocity_1 = self.velocity.rotate(angle)
            velocity_2 = self.velocity.rotate(-angle)


            asteroid_1 = Asteroid(self.position.x, self.position.y, new_radius)
            asteroid_2 = Asteroid(self.position.x, self.position.y, new_radius)
            asteroid_1.velocity = velocity_1 * 1.2
            asteroid_2.velocity = velocity_2 * 1.2
            