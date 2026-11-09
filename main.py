import json
import random
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
    ART_DIR,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from logger import log_state, log_event
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot

DIFFICULTY_OPTIONS = (
    ("Easy", 15, None),
    ("Medium", 20, 30),
    ("Hard", 25, 20),
    ("Hardcore", None, 10),
)
SKIN_OPTIONS = ("white", "red")
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


def audio_slider_rect(index: int) -> pygame.Rect:
    return pygame.Rect(SCREEN_WIDTH // 2 - 210, 310 + index * 120, 420, 12)


def build_star_background(star_tile: pygame.Surface) -> pygame.Surface:
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.fill("black")
    small_star = pygame.transform.scale(star_tile, (8, 8))
    randomizer = random.Random(42)
    for _ in range(90):
        position = (
            randomizer.randrange(0, SCREEN_WIDTH - 8),
            randomizer.randrange(0, SCREEN_HEIGHT - 8),
        )
        background.blit(small_star, position)
    return background


def load_high_scores() -> dict[str, list[int]]:
    try:
        saved_scores = json.loads(HIGH_SCORE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        saved_scores = {}

    if not isinstance(saved_scores, dict):
        saved_scores = {}

    high_scores = {}
    for name, _, _ in DIFFICULTY_OPTIONS:
        saved_values = saved_scores.get(name, [])
        if isinstance(saved_values, int):
            saved_values = [saved_values]
        if not isinstance(saved_values, list):
            saved_values = []
        valid_scores = [
            value
            for value in saved_values
            if isinstance(value, int) and not isinstance(value, bool) and value > 0
        ]
        high_scores[name] = sorted(valid_scores, reverse=True)[:5]
    return high_scores


def save_high_scores(scores: dict[str, list[int]]) -> None:
    try:
        HIGH_SCORE_PATH.write_text(
            json.dumps(scores, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as error:
        print(f"Could not save high scores: {error}")


def record_high_score(
    scores: dict[str, list[int]], difficulty: str, score: int
) -> None:
    if score > 0:
        scores[difficulty].append(score)
        scores[difficulty] = sorted(scores[difficulty], reverse=True)[:5]
        save_high_scores(scores)


def main() -> None:
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error as error:
        print(f"Audio unavailable; continuing without sound: {error}")

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
    title_image = pygame.image.load(ART_DIR / "main-title.png").convert_alpha()
    title_image = pygame.transform.scale(title_image, (384, 192))
    star_tile = pygame.image.load(ART_DIR / "star-bg.png").convert_alpha()
    star_background = build_star_background(star_tile)
    heart_image = pygame.transform.scale(
        pygame.image.load(ART_DIR / "heart.png").convert_alpha(),
        (28, 28),
    )
    audio_enabled = pygame.mixer.get_init() is not None
    asteroid_sounds = {}
    music_enabled = False
    if audio_enabled:
        pygame.mixer.music.load(
            Path(__file__).parent / "assets" / "music" / "bg.mp3"
        )
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)
        music_enabled = True
        asteroid_sounds = {
            "small": pygame.mixer.Sound("assets/music/bangsmall/bangSmall.wav"),
            "medium": pygame.mixer.Sound("assets/music/bangmedium/bangMedium.wav"),
            "large": pygame.mixer.Sound("assets/music/banglarge/bangLarge.wav"),
        }
        for sound in asteroid_sounds.values():
            sound.set_volume(0.4)
    audio_levels = {"Master": 1.0, "Effects": 1.0}
    skin_preview_images = {
        "white": pygame.transform.scale(
            pygame.image.load(ART_DIR / "plane.png").convert_alpha(), (96, 96)
        ),
        "red": pygame.transform.scale(
            pygame.image.load(ART_DIR / "plane-red.png").convert_alpha(), (96, 96)
        ),
    }
    skin_preview_frames = {
        "white": [
            [
                pygame.transform.scale(
                    pygame.image.load(ART_DIR / filename).convert_alpha(), (96, 96)
                )
                for filename in (
                    "plane-thrust-white.png",
                    "plane-thrust-white-2.png",
                    "plane-thrust-white-3.png",
                )
            ],
            [
                pygame.transform.scale(
                    pygame.image.load(ART_DIR / filename).convert_alpha(), (96, 96)
                )
                for filename in (
                    "plane-thrust-white-version2-1.png",
                    "plane-thrust-white-version2-2.png",
                    "plane-thrust-white-version2-3.png",
                )
            ],
        ],
        "red": [
            [
                pygame.transform.scale(
                    pygame.image.load(ART_DIR / filename).convert_alpha(), (96, 96)
                )
                for filename in (
                    "plane-thrust-red.png",
                    "plane-thrust-red2.png",
                    "plane-thrust-red3.png",
                )
            ],
            [
                pygame.transform.scale(
                    pygame.image.load(ART_DIR / filename).convert_alpha(), (96, 96)
                )
                for filename in (
                    "plane-thrust-red-version-2-1.png",
                    "plane-thrust-red-version-2-2.png",
                    "plane-thrust-red-version-2-3.png",
                )
            ],
        ],
    }

    def apply_audio_levels() -> None:
        combined_volume = audio_levels["Master"] * audio_levels["Effects"]
        if music_enabled:
            pygame.mixer.music.set_volume(0.2 * audio_levels["Master"])
        for player_obj in players:
            if player_obj.fire_sound is not None:
                player_obj.fire_sound.set_volume(0.35 * combined_volume)
            if player_obj.thrust_sound is not None:
                player_obj.thrust_sound.set_volume(0.25 * combined_volume)
        for sound in asteroid_sounds.values():
            sound.set_volume(0.4 * combined_volume)

    def set_audio_slider(index: int, mouse_x: int) -> None:
        slider = audio_slider_rect(index)
        audio_levels["Master" if index == 0 else "Effects"] = max(
            0.0,
            min(1.0, (mouse_x - slider.x) / slider.width),
        )
        apply_audio_levels()

    game_state = "menu"
    difficulty_index = 0
    skin_index = 0
    skin_name = SKIN_OPTIONS[skin_index]
    thrust_animation_index = 0
    difficulty_name = DIFFICULTY_OPTIONS[difficulty_index][0]
    level = 1
    level_notice_timer = 0.0
    score = 0
    asteroid_field = None
    high_scores = load_high_scores()
    selected_audio_slider = 0
    dragging_audio_slider = None
    preview_frame = 0
    preview_timer = 0.0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if audio_enabled:
                    pygame.mixer.music.stop()
                return
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_audio_slider = None
            if game_state == "audio_settings" and audio_enabled:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for index in range(2):
                        if audio_slider_rect(index).inflate(20, 36).collidepoint(
                            event.pos
                        ):
                            selected_audio_slider = index
                            dragging_audio_slider = index
                            set_audio_slider(index, event.pos[0])
                elif (
                    event.type == pygame.MOUSEMOTION
                    and dragging_audio_slider is not None
                ):
                    set_audio_slider(dragging_audio_slider, event.pos[0])
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state == "menu":
                        if audio_enabled:
                            pygame.mixer.music.stop()
                        return
                    if game_state == "audio_settings":
                        game_state = "menu"
                        continue
                    if game_state == "playing":
                        record_high_score(high_scores, difficulty_name, score)
                    for player_obj in players:
                        player_obj.set_thrusting(False)
                    for group in (drawable, updatable, players, asteroids, shots):
                        group.empty()
                    game_state = "menu"
                    score = 0
                    level = 1
                    asteroid_field = None
                    continue
                if event.key == pygame.K_m:
                    if game_state == "menu":
                        game_state = "audio_settings"
                    elif game_state == "audio_settings":
                        game_state = "menu"
                    continue
                if event.key == pygame.K_TAB:
                    if game_state == "menu":
                        game_state = "skin_menu"
                    elif game_state == "skin_menu":
                        game_state = "menu"
                    continue
                if game_state == "skin_menu":
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        direction = 1 if event.key == pygame.K_RIGHT else -1
                        skin_index = (skin_index + direction) % len(SKIN_OPTIONS)
                        skin_name = SKIN_OPTIONS[skin_index]
                    elif event.key in (pygame.K_UP, pygame.K_DOWN):
                        direction = 1 if event.key == pygame.K_DOWN else -1
                        thrust_animation_index = (
                            thrust_animation_index + direction
                        ) % 2
                        preview_frame = 0
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        game_state = "menu"
                    continue
                if game_state == "audio_settings":
                    if not audio_enabled:
                        continue
                    if event.key in (pygame.K_UP, pygame.K_DOWN):
                        selected_audio_slider = 1 - selected_audio_slider
                    elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        slider_name = "Master" if selected_audio_slider == 0 else "Effects"
                        direction = 1 if event.key == pygame.K_RIGHT else -1
                        audio_levels[slider_name] = max(
                            0.0,
                            min(1.0, audio_levels[slider_name] + direction * 0.05),
                        )
                        apply_audio_levels()
                    continue
                if event.key == pygame.K_p:
                    if game_state == "playing":
                        for player_obj in players:
                            player_obj.set_thrusting(False)
                        game_state = "paused"
                    elif game_state == "paused":
                        game_state = "playing"
                    continue
                if game_state == "menu" and event.key in (
                    pygame.K_LEFT,
                    pygame.K_RIGHT,
                ):
                    direction = 1 if event.key == pygame.K_RIGHT else -1
                    difficulty_index = (
                        difficulty_index + direction
                    ) % len(DIFFICULTY_OPTIONS)
                if game_state in ("menu", "game_over") and event.key in (
                    pygame.K_RETURN,
                    pygame.K_KP_ENTER,
                ):
                    for group in (drawable, updatable, players, asteroids, shots):
                        group.empty()
                    level = 1
                    level_notice_timer = 0.0
                    difficulty_name, max_active, shot_limit = DIFFICULTY_OPTIONS[
                        difficulty_index
                    ]
                    player_obj = Player(
                        x=SCREEN_WIDTH / 2,
                        y=SCREEN_HEIGHT / 2,
                        shots=shots,
                        shot_limit=shot_limit,
                        skin=skin_name,
                        thrust_animation=thrust_animation_index,
                    )
                    if player_obj.fire_sound is not None:
                        player_obj.fire_sound.set_volume(
                            0.35 * audio_levels["Master"] * audio_levels["Effects"]
                        )
                    if player_obj.thrust_sound is not None:
                        player_obj.thrust_sound.set_volume(
                            0.25 * audio_levels["Master"] * audio_levels["Effects"]
                        )
                    asteroid_field = AsteroidField(asteroids, max_active, level)
                    score = 0
                    game_state = "playing"

        if game_state == "playing":
            log_state()
            updatable.update(dt)
            level_notice_timer = max(0.0, level_notice_timer - dt)

            for asteroid_obj in asteroids.sprites():
                for player_obj in players:
                    if player_obj.invulnerable_timer > 0:
                        continue

                    if asteroid_obj.collides_with(player_obj):
                        player_obj.take_damage(asteroid_damage(asteroid_obj.radius))
                        log_event("player_hit")
                        if player_obj.health <= 0:
                            player_obj.set_thrusting(False)
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
                        if asteroid_sounds:
                            if asteroid_obj.radius >= ASTEROID_MIN_RADIUS * 3:
                                asteroid_sounds["large"].play()
                            elif asteroid_obj.radius >= ASTEROID_MIN_RADIUS * 2:
                                asteroid_sounds["medium"].play()
                            else:
                                asteroid_sounds["small"].play()
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
                level_notice_timer = 2.5

        if game_state == "skin_menu":
            preview_timer += dt
            while preview_timer >= 0.1:
                preview_timer -= 0.1
                preview_frame = (preview_frame + 1) % len(
                    skin_preview_frames[skin_name][thrust_animation_index]
                )

        screen.blit(star_background, (0, 0))

        if game_state == "skin_menu":
            draw_centered_text(screen, title_font, "CHOOSE YOUR SHIP", 110)
            draw_centered_text(
                screen,
                small_font,
                "LEFT / RIGHT: skin    UP / DOWN: thrust style    ENTER: confirm",
                165,
            )
            for index, name in enumerate(SKIN_OPTIONS):
                center_x = SCREEN_WIDTH // 2 - 180 + index * 360
                panel = pygame.Rect(center_x - 135, 220, 270, 300)
                panel_color = (35, 75, 85) if index == skin_index else (25, 25, 35)
                pygame.draw.rect(screen, panel_color, panel, border_radius=8)
                pygame.draw.rect(
                    screen,
                    (100, 220, 200) if index == skin_index else (80, 80, 90),
                    panel,
                    3,
                    border_radius=8,
                )
                idle_image = skin_preview_images[name]
                idle_rect = idle_image.get_rect(center=(center_x, 330))
                screen.blit(idle_image, idle_rect)
                thrust_image = skin_preview_frames[name][thrust_animation_index][
                    preview_frame
                ]
                thrust_rect = thrust_image.get_rect(center=(center_x, 430))
                screen.blit(thrust_image, thrust_rect)
                skin_label = body_font.render(name.upper(), True, "white")
                screen.blit(
                    skin_label,
                    skin_label.get_rect(center=(center_x, 480)),
                )
            draw_centered_text(
                screen,
                small_font,
                f"THRUST STYLE {thrust_animation_index + 1}    TAB / ESC: menu",
                570,
            )
        elif game_state == "audio_settings" and not audio_enabled:
            draw_centered_text(screen, title_font, "AUDIO MIXER", 190)
            draw_centered_text(screen, body_font, "Audio output unavailable", 310)
            draw_centered_text(
                screen, small_font, "The game will continue without sound", 355
            )
            draw_centered_text(screen, small_font, "M or ESC: return to menu", 575)
        elif game_state == "audio_settings":
            draw_centered_text(screen, title_font, "AUDIO MIXER", 190)
            draw_centered_text(screen, body_font, "Master", 270)
            draw_centered_text(screen, body_font, "Effects", 390)
            for index, name in enumerate(("Master", "Effects")):
                slider = audio_slider_rect(index)
                value = audio_levels[name]
                pygame.draw.rect(screen, (55, 55, 55), slider, border_radius=6)
                fill_rect = pygame.Rect(
                    slider.x,
                    slider.y,
                    round(slider.width * value),
                    slider.height,
                )
                if fill_rect.width > 0:
                    pygame.draw.rect(
                        screen, (80, 205, 190), fill_rect, border_radius=6
                    )
                knob_x = round(slider.x + slider.width * value)
                knob_color = "white" if index == selected_audio_slider else (180, 180, 180)
                pygame.draw.circle(screen, knob_color, (knob_x, slider.centery), 12)
                value_text = small_font.render(f"{round(value * 100)}%", True, "white")
                screen.blit(value_text, value_text.get_rect(center=(SCREEN_WIDTH // 2, slider.y + 35)))
            draw_centered_text(
                screen, small_font, "Click and drag, or use arrows to adjust", 535
            )
            draw_centered_text(
                screen, small_font, "M or ESC: return to menu", 575
            )
        elif game_state == "menu":
            screen.blit(title_image, title_image.get_rect(center=(SCREEN_WIDTH // 2, 125)))
            draw_centered_text(
                screen, small_font, "W / S: thrust and reverse    A / D: turn    SPACE: fire", 245
            )
            pygame.draw.line(screen, (70, 70, 70), (160, 280), (SCREEN_WIDTH - 160, 280), 2)
            difficulty_name, asteroid_limit, shot_limit = DIFFICULTY_OPTIONS[
                difficulty_index
            ]
            limit_text = (
                "unlimited asteroids"
                if asteroid_limit is None
                else f"{asteroid_limit} asteroids at once"
            )
            shot_limit_text = (
                "unlimited shots"
                if shot_limit is None
                else f"{shot_limit} shots at once"
            )
            draw_centered_text(
                screen,
                body_font,
                f"<  {difficulty_name.upper()}  >",
                330,
            )
            draw_centered_text(
                screen,
                small_font,
                f"LEFT / RIGHT to change  |  {limit_text}  |  {shot_limit_text}",
                365,
            )
            draw_centered_text(screen, body_font, "ENTER: start", 430)
            pygame.draw.line(screen, (70, 70, 70), (160, 480), (SCREEN_WIDTH - 160, 480), 2)
            draw_centered_text(screen, body_font, "HIGH SCORES", 510)
            for column, (name, _, _) in enumerate(DIFFICULTY_OPTIONS):
                column_x = round(SCREEN_WIDTH * (column + 0.5) / len(DIFFICULTY_OPTIONS))
                heading = small_font.render(name.upper(), True, "white")
                screen.blit(heading, heading.get_rect(center=(column_x, 545)))
                for rank in range(3):
                    scores = high_scores[name]
                    score_label = str(scores[rank]) if rank < len(scores) else "-"
                    score_surface = small_font.render(
                        f"{rank + 1}. {score_label}", True, "white"
                    )
                    screen.blit(
                        score_surface,
                        score_surface.get_rect(center=(column_x, 570 + rank * 25)),
                    )
            draw_centered_text(
                screen, small_font, "TAB: skins    M: audio mixer    |    ESC: quit", 675
            )
        elif game_state in ("playing", "paused"):
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
                heart_count = (player_obj.health + 19) // 20
                for heart_index in range(5):
                    heart = heart_image.copy()
                    if heart_index >= heart_count:
                        heart.set_alpha(55)
                    screen.blit(heart, (24 + heart_index * 32, 90))

            score_text = body_font.render(f"SCORE: {score}", True, "white")
            screen.blit(
                score_text,
                score_text.get_rect(topright=(SCREEN_WIDTH - 24, 24)),
            )
            shot_limit = next(iter(players)).shot_limit
            shot_label = (
                f"SHOTS: {len(shots)} / {shot_limit}"
                if shot_limit is not None
                else f"SHOTS: {len(shots)} / unlimited"
            )
            shot_text = small_font.render(shot_label, True, "white")
            screen.blit(
                shot_text,
                shot_text.get_rect(topright=(SCREEN_WIDTH - 24, 58)),
            )
            level_text = body_font.render(
                f"LEVEL: {level} | {difficulty_name.upper()}", True, "white"
            )
            screen.blit(
                level_text,
                level_text.get_rect(midtop=(SCREEN_WIDTH // 2, 24)),
            )
            if level_notice_timer > 0:
                draw_centered_text(
                    screen,
                    title_font,
                    f"LEVEL {level}",
                    SCREEN_HEIGHT // 2,
                )
            abort_text = small_font.render("ESC: abort to menu", True, "white")
            screen.blit(abort_text, (24, SCREEN_HEIGHT - 32))
            if game_state == "paused":
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 170))
                screen.blit(overlay, (0, 0))
                draw_centered_text(screen, title_font, "PAUSED", 300)
                draw_centered_text(screen, body_font, "Press P to resume", 370)
                draw_centered_text(screen, body_font, "Press ESC for menu", 415)
        else:
            draw_centered_text(screen, title_font, "GAME OVER", 260)
            draw_centered_text(screen, body_font, f"SCORE: {score}", 340)
            draw_centered_text(screen, body_font, f"LEVEL: {level}", 385)
            best_scores = high_scores[difficulty_name][:3]
            best_scores_text = "BEST: " + (
                " | ".join(str(value) for value in best_scores)
                if best_scores
                else "-"
            )
            draw_centered_text(
                screen,
                body_font,
                f"{difficulty_name} {best_scores_text}",
                430,
            )
            draw_centered_text(screen, body_font, "Press ENTER to play again", 475)

        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()