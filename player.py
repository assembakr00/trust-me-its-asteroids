import pygame
from circleshape import CircleShape
from constants import (PLAYER_RADIUS, LINE_WIDTH, PLAYER_TURN_SPEED, 
                       PLAYER_SPEED, PLAYER_SHOOT_COOLDOWN_SECONDS, 
                       PLAYER_SHOOT_SPEED, SHOT_RADIUS)
from shot import Shot


class Player(CircleShape):
    containers: tuple[pygame.sprite.Group, ...]

    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0.0
        self.shoot_cooldown = 0.0
        self.invulnerable_timer = 0.0
    # in the Player class
    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        shot_pos = self.position + forward * (self.radius +  SHOT_RADIUS)
        shot = Shot(shot_pos.x, shot_pos.y)
        shot.velocity = self.velocity + forward * PLAYER_SHOOT_SPEED
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right

        return [a, b, c]
    def draw(self, screen) -> None:
        if self.invulnerable_timer > 0:
            if int(self.invulnerable_timer * 10) % 2 == 0:
                return
        pygame.draw.polygon(screen, "white", self.triangle(), LINE_WIDTH)

    def rotate(self, dt: float):
        self.rotation += PLAYER_TURN_SPEED * dt

    def shoot(self) -> None:
        if self.shoot_cooldown > 0:
            return
        shot = Shot(self.position.x, self.position.y)
        vector = pygame.Vector2(0, 1).rotate(self.rotation)
        shot.velocity = vector * PLAYER_SHOOT_SPEED
        self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS
            

    def move(self, dt: float) -> None:
        move_vector = pygame.Vector2(0, 1)

        moved_direction = move_vector.rotate(self.rotation)

        self.position += moved_direction * dt * PLAYER_SPEED
        self.wrap_position()


    def update(self, dt: float) -> None:
        self.shoot_cooldown = max(0.0, self.shoot_cooldown - dt)
        self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)
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