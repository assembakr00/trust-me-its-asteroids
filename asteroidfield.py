import random
from collections.abc import Callable

import pygame
from asteroid import Asteroid
from constants import (
    ASTEROID_KINDS,
    ASTEROID_MIN_RADIUS,
    ASTEROID_SPAWN_RATE_SECONDS,
    ASTEROIDS_PER_LEVEL,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)

Edge = tuple[pygame.Vector2, Callable[[float], pygame.Vector2]]


class AsteroidField(pygame.sprite.Sprite):
    containers: pygame.sprite.Group

    edges: list[Edge] = [
        (
            pygame.Vector2(1, 0),
            lambda y: pygame.Vector2(0, y * SCREEN_HEIGHT),
        ),
        (
            pygame.Vector2(-1, 0),
            lambda y: pygame.Vector2(
                SCREEN_WIDTH, y * SCREEN_HEIGHT
            ),
        ),
        (
            pygame.Vector2(0, 1),
            lambda x: pygame.Vector2(x * SCREEN_WIDTH, 0),
        ),
        (
            pygame.Vector2(0, -1),
            lambda x: pygame.Vector2(
                x * SCREEN_WIDTH, SCREEN_HEIGHT
            ),
        ),
    ]

    def __init__(
        self,
        asteroids: pygame.sprite.Group,
        max_active: int | None,
        level: int,
    ) -> None:
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.asteroids = asteroids
        self.max_active = max_active
        self.spawn_timer = 0.0
        self.start_level(level)

    def start_level(self, level: int) -> None:
        self.level = level
        self.remaining_to_spawn = ASTEROIDS_PER_LEVEL * level
        self.spawn_timer = 0.0

    def spawn(
        self, radius: float, position: pygame.Vector2, velocity: pygame.Vector2
    ) -> None:
        asteroid = Asteroid(position.x, position.y, radius)
        asteroid.velocity = velocity

    def update(self, dt: float) -> None:
        if self.remaining_to_spawn <= 0:
            return
        if self.max_active is not None and len(self.asteroids) >= self.max_active:
            return

        self.spawn_timer += dt
        if self.spawn_timer >= ASTEROID_SPAWN_RATE_SECONDS:
            self.spawn_timer -= ASTEROID_SPAWN_RATE_SECONDS

            # spawn a new asteroid at a random edge
            edge = random.choice(self.edges)
            speed = random.randint(40, 100)
            velocity = edge[0] * speed
            velocity = velocity.rotate(random.randint(-30, 30))
            position = edge[1](random.uniform(0, 1))
            kind = random.randint(1, ASTEROID_KINDS)
            self.spawn(ASTEROID_MIN_RADIUS * kind, position, velocity)
            self.remaining_to_spawn -= 1