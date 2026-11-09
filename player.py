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
    PLAYER_THRUST_FRAME_SECONDS,
    PLAYER_TURN_SPEED,
    SHOT_RADIUS,
    ART_DIR,
    resource_path,
)
from shot import Shot

PLAYER_SPRITE_SCALE = 1.5


class Player(CircleShape):
    containers: tuple[pygame.sprite.Group, ...]

    def __init__(
        self,
        x: float,
        y: float,
        shots: pygame.sprite.Group | None = None,
        shot_limit: int | None = None,
        skin: str = "white",
        thrust_animation: int = 0,
    ):
        super().__init__(x, y, PLAYER_RADIUS)
        self.shots = shots
        self.shot_limit = shot_limit
        self.skin = skin
        self.thrust_animation = thrust_animation
        self.rotation = 0.0
        self.shoot_cooldown = 0.0
        self.invulnerable_timer = 0.0
        self.health = PLAYER_MAX_HEALTH
        self.health_regen_timer = 0.0
        self.visual_radius = self.radius * PLAYER_SPRITE_SCALE
        sprite_size = (round(self.visual_radius * 2), round(self.visual_radius * 2))
        skin_assets = {
            "white": (
                "plane.png",
                (
                    (
                        "plane-thrust-white.png",
                        "plane-thrust-white-2.png",
                        "plane-thrust-white-3.png",
                    ),
                    (
                        "plane-thrust-white-version2-1.png",
                        "plane-thrust-white-version2-2.png",
                        "plane-thrust-white-version2-3.png",
                    ),
                ),
            ),
            "red": (
                "plane-red.png",
                (
                    (
                        "plane-thrust-red.png",
                        "plane-thrust-red2.png",
                        "plane-thrust-red3.png",
                    ),
                    (
                        "plane-thrust-red-version-2-1.png",
                        "plane-thrust-red-version-2-2.png",
                        "plane-thrust-red-version-2-3.png",
                    ),
                ),
            ),
        }
        idle_name, thrust_names = skin_assets[skin]
        thrust_names = thrust_names[thrust_animation]
        self.ship_image = pygame.transform.scale(
            pygame.image.load(ART_DIR / idle_name).convert_alpha(),
            sprite_size,
        )
        self.thrust_images = [
            pygame.transform.scale(
                pygame.image.load(ART_DIR / image_name).convert_alpha(),
                sprite_size,
            )
            for image_name in thrust_names
        ]
        self.thrust_frame_index = 0
        self.thrust_frame_timer = 0.0
        self.fire_sound = None
        self.thrust_sound = None
        if pygame.mixer.get_init():
            self.fire_sound = pygame.mixer.Sound(
                resource_path("assets/music/fire/fire.wav")
            )
            self.fire_sound.set_volume(0.35)
            self.thrust_sound = pygame.mixer.Sound(
                resource_path("assets/music/thrust/thrust.wav")
            )
            self.thrust_sound.set_volume(0.25)
        self.thrust_channel = None
        self.thrusting = False

    def draw(self, screen) -> None:
        if self.invulnerable_timer > 0:
            if int(self.invulnerable_timer * 10) % 2 == 0:
                return

        image = (
            self.thrust_images[self.thrust_frame_index]
            if self.thrusting
            else self.ship_image
        )
        rotated_image = pygame.transform.rotate(image, 180 - self.rotation)
        image_rect = rotated_image.get_rect(
            center=(round(self.position.x), round(self.position.y))
        )
        screen.blit(rotated_image, image_rect)

    def rotate(self, dt: float):
        self.rotation += PLAYER_TURN_SPEED * dt

    def set_thrusting(self, is_thrusting: bool) -> None:
        self.thrusting = is_thrusting
        if self.thrust_sound is None:
            return
        if is_thrusting:
            if self.thrust_channel is None or not self.thrust_channel.get_busy():
                self.thrust_channel = self.thrust_sound.play(loops=-1)
        elif self.thrust_channel is not None:
            self.thrust_channel.stop()
            self.thrust_channel = None

    def shoot(self) -> None:
        if self.shoot_cooldown > 0:
            return
        if (
            self.shot_limit is not None
            and self.shots is not None
            and len(self.shots) >= self.shot_limit
        ):
            return

        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        shot_pos = self.position + forward * (self.visual_radius + SHOT_RADIUS)
        shot = Shot(shot_pos.x, shot_pos.y)
        shot.velocity = forward * PLAYER_SHOOT_SPEED
        if self.fire_sound is not None:
            self.fire_sound.play()
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
        self.set_thrusting(keys[pygame.K_w])
        if self.thrusting:
            self.thrust_frame_timer += dt
            while self.thrust_frame_timer >= PLAYER_THRUST_FRAME_SECONDS:
                self.thrust_frame_timer -= PLAYER_THRUST_FRAME_SECONDS
                self.thrust_frame_index = (
                    self.thrust_frame_index + 1
                ) % len(self.thrust_images)
        else:
            self.thrust_frame_index = 0
            self.thrust_frame_timer = 0.0

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