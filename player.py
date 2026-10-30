import pygame
from circleshape import CircleShape
from constants import (
    PLAYER_HEALTH_REGEN_INTERVAL_SECONDS,
    PLAYER_INVULNERABILITY_SECONDS,
    PLAYER_MAX_HEALTH,
    PLAYER_RADIUS,
    PLAYER_SHOOT_COOLDOWN_SECONDS,
    PLAYER_SHOOT_SPEED,
    PLAYER_SPEED,
    PLAYER_TURN_SPEED,
    SHOT_RADIUS,
)
from shot import Shot

PLAYER_SPRITE_SCALE = 1.5


class Player(CircleShape):
    containers: tuple[pygame.sprite.Group, ...]

    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0.0
        self.shoot_cooldown = 0.0
        self.invulnerable_timer = 0.0
        self.health = PLAYER_MAX_HEALTH
        self.health_regen_timer = 0.0
        self.visual_radius = self.radius * PLAYER_SPRITE_SCALE
        sprite_size = (round(self.visual_radius * 2), round(self.visual_radius * 2))
        self.ship_image = pygame.transform.scale(
            pygame.image.load("assets/art/plane.png").convert_alpha(),
            sprite_size,
        )
        self.thrust_image = pygame.transform.scale(
            pygame.image.load("assets/art/plane-fire.png").convert_alpha(),
            sprite_size,
        )
        self.thrusting = False

    def draw(self, screen) -> None:
        if self.invulnerable_timer > 0:
            if int(self.invulnerable_timer * 10) % 2 == 0:
                return

        image = self.thrust_image if self.thrusting else self.ship_image
        rotated_image = pygame.transform.rotate(image, 180 - self.rotation)
        image_rect = rotated_image.get_rect(
            center=(round(self.position.x), round(self.position.y))
        )
        screen.blit(rotated_image, image_rect)

    def rotate(self, dt: float):
        self.rotation += PLAYER_TURN_SPEED * dt

    def shoot(self) -> None:
        if self.shoot_cooldown > 0:
            return

        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        shot_pos = self.position + forward * (self.visual_radius + SHOT_RADIUS)
        shot = Shot(shot_pos.x, shot_pos.y)
        shot.velocity = forward * PLAYER_SHOOT_SPEED
        self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS

    def take_damage(self, amount: int) -> None:
        self.health = max(0, self.health - amount)
        self.invulnerable_timer = PLAYER_INVULNERABILITY_SECONDS
        self.health_regen_timer = 0.0
            

    def move(self, dt: float) -> None:
        move_vector = pygame.Vector2(0, 1)

        moved_direction = move_vector.rotate(self.rotation)

        self.position += moved_direction * dt * PLAYER_SPEED
        self.wrap_position()


    def update(self, dt: float) -> None:
        self.shoot_cooldown = max(0.0, self.shoot_cooldown - dt)
        self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)
        if self.health < PLAYER_MAX_HEALTH:
            self.health_regen_timer += dt
            while (
                self.health_regen_timer >= PLAYER_HEALTH_REGEN_INTERVAL_SECONDS
                and self.health < PLAYER_MAX_HEALTH
            ):
                self.health += 1
                self.health_regen_timer -= PLAYER_HEALTH_REGEN_INTERVAL_SECONDS
        else:
            self.health_regen_timer = 0.0

        keys = pygame.key.get_pressed()
        self.thrusting = keys[pygame.K_w]

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