import pygame
import sys

pygame.init()

# Setup Display
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("The Growing Entity")
clock = pygame.time.Clock()

# Exposition/intro
GAME_FONT = pygame.freetype.SysFont("Times New Roman", 28)

lines = [
    "It was just another average Tuesday evening in my hometown…",
    "Nothing seemed amiss, until I suddenly heard a scream from outside my window.",
    "As I ran outside, I saw an ominous purple fog seep soundlessly into town, growing as it consumed the town.",
    "The screaming died down as quick as it started; anyone who made contact with the mysterious entity seemed to collapse immediately.",
    "I didn’t think, I just ran.",
    "As The Entity continued to grow, it covered more and more ground.",
    "I realized…",
    "The only way out, was up."
]

TEXT_COLOR = (255, 255, 255)
BG_COLOR = (0, 0, 0)
MARGIN_X = 80
LINE_SPACING = 8

# INTRO loop
show_intro = True
index = 0

def wrap_text(font, text, max_width, color):
    words = text.split(" ")
    cur_line = ""
    out = []
    for word in words:
        test = cur_line + ("" if cur_line == "" else " ") + word
        surf, rect = font.render(test, color)
        if rect.width <= max_width:
            cur_line = test
        else:
            if cur_line == "":
                out.append(font.render(test, color))
                cur_line = ""
            else:
                out.append(font.render(cur_line, color))
                cur_line = word
    if cur_line:
        out.append(font.render(cur_line, color))
    return out

# Intro loop
while show_intro:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_SPACE:
                index += 1
                if index >= len(lines):
                    show_intro = False

    screen.fill(BG_COLOR)

    if index < len(lines):
        max_w = SCREEN_WIDTH - 2 * MARGIN_X
        rendered = wrap_text(GAME_FONT, lines[index], max_w, TEXT_COLOR)

        total_h = sum(rect.height for surf, rect in rendered) + LINE_SPACING * (len(rendered) - 1)
        start_y = (SCREEN_HEIGHT - total_h) // 2

        y = start_y
        for surf, rect in rendered:
            x = (SCREEN_WIDTH - rect.width) // 2
            screen.blit(surf, (x, y))
            y += rect.height + LINE_SPACING

        hint = "Press SPACE to continue"
        hint_surf, hint_rect = GAME_FONT.render(hint, (180, 180, 180))
        hint_x = (SCREEN_WIDTH - hint_rect.width) // 2
        hint_y = SCREEN_HEIGHT - 40
        screen.blit(hint_surf, (hint_x, hint_y))

    pygame.display.flip()
    clock.tick(60)

# Assets
background_img = pygame.image.load("sky.jpg").convert()
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

ground_img = pygame.image.load("grass.png").convert_alpha()
ground_img = pygame.transform.scale(ground_img, (SCREEN_WIDTH, 20))

branch_img_left = pygame.image.load("branch.png").convert_alpha()
branch_img_left = pygame.transform.scale(branch_img_left, (370, 60))
branch_img_right = pygame.transform.flip(branch_img_left, True, False)

player_img_right = pygame.image.load("avatar.png").convert_alpha()
player_img_right = pygame.transform.scale(player_img_right, (60, 80))
player_img_left = pygame.transform.flip(player_img_right, True, False)
current_player_img = player_img_right

fog_image = pygame.image.load("the_entity_but_bigger.png").convert_alpha()

# Constants and game state
FPS = 60
GRAVITY = 0.6
JUMP_POWER = -20
scroll_y = 0.0

player_rect = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, 60, 80)
y_speed = 0.0
platforms = [pygame.Rect(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20)]

# Fog variables
fog_list = []
fog_speed = 1.2
fog_spawn_rate = 60
frame_count = 0

def spawn_branch(last_y, side):
    width = 370
    height = 20
    y = last_y - 180
    if side == "left":
        x = 0
    else:
        x = SCREEN_WIDTH - width
    return pygame.Rect(x, y, width, height)

current_side = "left"
for i in range(15):
    new_plat = spawn_branch(platforms[-1].y, current_side)
    platforms.append(new_plat)
    current_side = "right" if current_side == "left" else "left"

# Main loop
run = True
while run:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_rect.left > 0:
        player_rect.x -= 8
        current_player_img = player_img_left
    if keys[pygame.K_RIGHT] and player_rect.right < SCREEN_WIDTH:
        player_rect.x += 8
        current_player_img = player_img_right

    # Gravity
    y_speed += GRAVITY
    player_rect.y += y_speed

    # Reset/Fall logic
    if player_rect.top > SCREEN_HEIGHT + 1000:
        target_plat = platforms[0]
        player_rect.bottom = target_plat.top
        player_rect.centerx = SCREEN_WIDTH // 2
        y_speed = 0

    # Scrolling upwards
    if player_rect.y < SCREEN_HEIGHT // 2:
        diff = SCREEN_HEIGHT // 2 - player_rect.y
        player_rect.y = SCREEN_HEIGHT // 2
        scroll_y += diff
        for p in platforms:
            p.y += diff

    # Collision with platforms
    on_ground = False
    for p in platforms:
        if player_rect.colliderect(p) and y_speed > 0:
            if player_rect.bottom - y_speed <= p.top:
                player_rect.bottom = p.top
                y_speed = 0
                on_ground = True

    # Jumping
    if keys[pygame.K_SPACE] and on_ground:
        y_speed = JUMP_POWER

    # Cleanup and spawn platforms
    platforms = [p for p in platforms if p.y < SCREEN_HEIGHT + 1000]
    while len(platforms) < 20:
        new_plat = spawn_branch(platforms[-1].y, current_side)
        platforms.append(new_plat)
        current_side = "right" if current_side == "left" else "left"

    # Fog spawning
    if frame_count % fog_spawn_rate == 0:
        fog_height = 300
        new_fog_world_y = scroll_y + SCREEN_HEIGHT + 600  # spawn below screen in world coords
        fog_scaled = pygame.transform.smoothscale(fog_image, (SCREEN_WIDTH, fog_height))
        fog_list.append({
            "world_y": float(new_fog_world_y),
            "height": fog_height,
            "image": fog_scaled,
            "rect": pygame.Rect(0, int(new_fog_world_y - scroll_y), SCREEN_WIDTH, fog_height)
        })

    # Move fog and collision
    new_fog_list = []
    for fog in fog_list:
        fog["world_y"] -= fog_speed
        fog_screen_y = fog["world_y"] - scroll_y
        fog["rect"].y = int(fog_screen_y)

        if player_rect.colliderect(fog["rect"]):
            print("The Entity consumed you!")
            run = False
            break

        # keep fog while it's not too far above the screen
        if fog_screen_y + fog["height"] >= -500:
            new_fog_list.append(fog)

    fog_list = new_fog_list

    # Limit fog count
    if len(fog_list) > 10:
        fog_list = fog_list[-10:]

    # DRAW
    screen.blit(background_img, (0, 0))

    # Draw Platforms
    for i, p in enumerate(platforms):
        if i == 0 and p.width == SCREEN_WIDTH:
            screen.blit(ground_img, (p.x, p.y))
        else:
            if p.x > 0:
                screen.blit(branch_img_right, p)
            else:
                screen.blit(branch_img_left, p)

    # Draw Fog
    for fog in fog_list:
        screen.blit(fog["image"], (fog["rect"].x, fog["rect"].y))

    # Draw Player
    screen.blit(current_player_img, (player_rect.x, player_rect.y))

    frame_count += 1
    pygame.display.flip()

pygame.quit()
sys.exit()
