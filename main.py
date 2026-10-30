import json
from pathlib import Path

import pygame
from constants import (
    ASTEROID_DAMAGE_LARGE,
    ASTEROID_DAMAGE_MEDIUM,
    ASTEROID_DAMAGE_SMALL,
    ASTEROID_MIN_RADIUS,
    ASTEROID_SCORE_LARGE,
    ASTEROID_SCORE_MEDIUM,
    ASTEROID_SCORE_SMALL,
    PLAYER_MAX_HEALTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from logger import log_state, log_event
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot

DIFFICULTY_OPTIONS = (
    ("Easy", 15),
    ("Medium", 20),
    ("Hard", 25),
    ("Hardcore", None),
)
HIGH_SCORE_PATH = Path(__file__).with_name("high_scores.json")


def asteroid_damage(radius: float) -> int:
    if radius >= ASTEROID_MIN_RADIUS * 3:
        return ASTEROID_DAMAGE_LARGE
    if radius >= ASTEROID_MIN_RADIUS * 2:
        return ASTEROID_DAMAGE_MEDIUM
    return ASTEROID_DAMAGE_SMALL


def asteroid_score(radius: float) -> int:
    if radius >= ASTEROID_MIN_RADIUS * 3:
        return ASTEROID_SCORE_LARGE
    if radius >= ASTEROID_MIN_RADIUS * 2:
        return ASTEROID_SCORE_MEDIUM
    return ASTEROID_SCORE_SMALL


def draw_centered_text(
    screen: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    y: int,
    color: str = "white",
) -> None:
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y))
    screen.blit(text_surface, text_rect)


def load_high_scores() -> dict[str, int]:
    try:
        saved_scores = json.loads(HIGH_SCORE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        saved_scores = {}

    if not isinstance(saved_scores, dict):
        saved_scores = {}

    return {
        name: value if isinstance(value, int) and value >= 0 else 0
        for name, _ in DIFFICULTY_OPTIONS
        for value in (saved_scores.get(name, 0),)
    }


def save_high_scores(scores: dict[str, int]) -> None:
    try:
        HIGH_SCORE_PATH.write_text(
            json.dumps(scores, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as error:
        print(f"Could not save high scores: {error}")


def record_high_score(scores: dict[str, int], difficulty: str, score: int) -> None:
    if score > scores[difficulty]:
        scores[difficulty] = score
        save_high_scores(scores)


def main() -> None:
    pygame.init()
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    dt = 0.0

    drawable = pygame.sprite.Group()
    updatable = pygame.sprite.Group()
    players = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    Player.containers = (updatable, drawable, players)
    Asteroid.containers = (updatable, drawable, asteroids)
    AsteroidField.containers = updatable
    Shot.containers = (updatable, drawable, shots)

    title_font = pygame.font.Font(None, 72)
    body_font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    plaque_font = pygame.font.Font(None, 58)
    subtitle_font = pygame.font.Font(None, 32)
    title_image = pygame.image.load("assets/art/main-title.png").convert_alpha()
    title_image = pygame.transform.scale(title_image, (512, 256))
    game_state = "menu"
    difficulty_index = 0
    difficulty_name = DIFFICULTY_OPTIONS[difficulty_index][0]
    level = 1
    score = 0
    asteroid_field = None
    high_scores = load_high_scores()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state == "menu":
                        return
                    if game_state == "playing":
                        record_high_score(high_scores, difficulty_name, score)
                    for group in (drawable, updatable, players, asteroids, shots):
                        group.empty()
                    game_state = "menu"
                    score = 0
                    level = 1
                    asteroid_field = None
                    continue
                if game_state == "menu" and event.key in (
                    pygame.K_LEFT,
                    pygame.K_RIGHT,
                ):
                    direction = 1 if event.key == pygame.K_RIGHT else -1
                    difficulty_index = (
                        difficulty_index + direction
                    ) % len(DIFFICULTY_OPTIONS)
                if game_state in ("menu", "game_over") and event.key == pygame.K_RETURN:
                    for group in (drawable, updatable, players, asteroids, shots):
                        group.empty()
                    level = 1
                    difficulty_name, max_active = DIFFICULTY_OPTIONS[difficulty_index]
                    Player(x=SCREEN_WIDTH / 2, y=SCREEN_HEIGHT / 2)
                    asteroid_field = AsteroidField(asteroids, max_active, level)
                    score = 0
                    game_state = "playing"

        if game_state == "playing":
            log_state()
            updatable.update(dt)

            for asteroid_obj in asteroids.sprites():
                for player_obj in players:
                    if player_obj.invulnerable_timer > 0:
                        continue

                    if asteroid_obj.collides_with(player_obj):
                        player_obj.take_damage(asteroid_damage(asteroid_obj.radius))
                        log_event("player_hit")
                        if player_obj.health <= 0:
                            game_state = "game_over"
                            record_high_score(high_scores, difficulty_name, score)
                        else:
                            player_obj.position = pygame.Vector2(
                                SCREEN_WIDTH / 2,
                                SCREEN_HEIGHT / 2,
                            )
                        break

                if game_state != "playing":
                    break

                for shot_obj in shots.sprites():
                    if asteroid_obj.collides_with(shot_obj):
                        score += asteroid_score(asteroid_obj.radius)
                        log_event("asteroid_shot")
                        if asteroid_field.max_active is None:
                            max_children = 2
                        else:
                            free_slots = asteroid_field.max_active - len(asteroids) + 1
                            max_children = max(0, min(2, free_slots))
                        asteroid_obj.split(max_children=max_children)
                        shot_obj.kill()
                        break

            if (
                game_state == "playing"
                and asteroid_field.remaining_to_spawn == 0
                and not asteroids
            ):
                level += 1
                asteroid_field.start_level(level)

        screen.fill("black")

        if game_state == "menu":
            screen.blit(title_image, title_image.get_rect(center=(SCREEN_WIDTH // 2, 200)))
            draw_centered_text(screen, subtitle_font, "TRUST ME, IT'S", 158, "black")
            draw_centered_text(screen, plaque_font, "ASTEROIDS", 215, "black")
            draw_centered_text(screen, body_font, "W / S: thrust and reverse", 380)
            draw_centered_text(screen, body_font, "A / D: turn    SPACE: fire", 420)
            difficulty_name, asteroid_limit = DIFFICULTY_OPTIONS[difficulty_index]
            limit_text = (
                "unlimited asteroids"
                if asteroid_limit is None
                else f"{asteroid_limit} asteroids at once"
            )
            draw_centered_text(
                screen,
                body_font,
                f"Difficulty: {difficulty_name} ({limit_text})",
                490,
            )
            draw_centered_text(
                screen, body_font, "LEFT / RIGHT: choose difficulty", 535
            )
            draw_centered_text(screen, body_font, "Press ENTER to start", 580)
            draw_centered_text(
                screen,
                body_font,
                f"HIGH SCORE: {high_scores[difficulty_name]}",
                635,
            )
        elif game_state == "playing":
            for obj in drawable:
                obj.draw(screen)

            player_obj = next(iter(players), None)
            if player_obj is not None:
                health_bar = pygame.Rect(24, 24, 260, 24)
                pygame.draw.rect(screen, (45, 45, 45), health_bar)
                health_width = round(
                    health_bar.width * player_obj.health / PLAYER_MAX_HEALTH
                )
                if health_width > 0:
                    if player_obj.health > 50:
                        health_color = (70, 210, 120)
                    elif player_obj.health > 25:
                        health_color = (240, 190, 65)
                    else:
                        health_color = (235, 75, 75)
                    pygame.draw.rect(
                        screen,
                        health_color,
                        (health_bar.x, health_bar.y, health_width, health_bar.height),
                    )
                pygame.draw.rect(screen, (220, 220, 220), health_bar, 2)
                health_text = body_font.render(
                    f"HP: {player_obj.health}/{PLAYER_MAX_HEALTH}", True, "white"
                )
                screen.blit(health_text, (24, 58))

            score_text = body_font.render(f"SCORE: {score}", True, "white")
            screen.blit(
                score_text,
                score_text.get_rect(topright=(SCREEN_WIDTH - 24, 24)),
            )
            level_text = body_font.render(
                f"LEVEL: {level} | {difficulty_name.upper()}", True, "white"
            )
            screen.blit(
                level_text,
                level_text.get_rect(midtop=(SCREEN_WIDTH // 2, 24)),
            )
            abort_text = small_font.render("ESC: abort to menu", True, "white")
            screen.blit(abort_text, (24, SCREEN_HEIGHT - 32))
        else:
            draw_centered_text(screen, title_font, "GAME OVER", 260)
            draw_centered_text(screen, body_font, f"SCORE: {score}", 340)
            draw_centered_text(screen, body_font, f"LEVEL: {level}", 385)
            draw_centered_text(
                screen,
                body_font,
                f"{difficulty_name} HIGH SCORE: {high_scores[difficulty_name]}",
                430,
            )
            draw_centered_text(screen, body_font, "Press ENTER to play again", 475)

        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()