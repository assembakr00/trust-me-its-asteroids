import pygame
from circleshape import CircleShape
from constants import PLAYER_RADIUS, LINE_WIDTH, PLAYER_TURN_SPEED, PLAYER_SPEED, PLAYER_SHOOT_COOLDOWN_SECONDS
from shot import Shot


class Player(CircleShape):
    containers: tuple[pygame.sprite.Group, ...]

    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0.0
        self.shoot_cooldown = 0.0

    # in the Player class
    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]
    def draw(self, screen) -> None:
        pygame.draw.polygon(screen, "white", self.triangle(), LINE_WIDTH)

    def rotate(self, dt: float):
        self.rotation += PLAYER_TURN_SPEED * dt

    def shoot(self) -> None:
        if self.shoot_cooldown > 0:
            return
        shot = Shot(self.position.x, self.position.y)
        vector = pygame.Vector2(0, 1).rotate(self.rotation)
        shot.velocity = vector * PLAYER_SPEED
        self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS
            

    def move(self, dt: float) -> None:
        move_vector = pygame.Vector2(0, 1)

        moved_direction = move_vector.rotate(self.rotation)

        self.position += moved_direction * dt * PLAYER_SPEED


    def update(self, dt: float) -> None:
        self.shoot_cooldown = max(0.0, self.shoot_cooldown - dt)
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.rotate(-dt)


        if keys[pygame.K_d]:
            self.rotate(dt)

        if keys[pygame.K_w]:
            self.move(dt)

        if keys[pygame.K_s]:
            self.move(-dt)

        if keys[pygame.K_SPACE]:
            self.shoot()