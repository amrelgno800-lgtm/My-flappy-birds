import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Force full screen mode on Pydroid 3 mobile screen layout
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

clock = pygame.time.Clock()
pygame.display.set_caption('Super Flappy Bird')

# Color Configuration (RGB)
SKY_BLUE = (115, 198, 231)
CLOUD_WHITE = (242, 247, 249)
YELLOW = (250, 215, 60)
WING_YELLOW = (230, 185, 30)
WHITE = (255, 255, 255)
BLACK = (35, 35, 35)
ORANGE = (245, 120, 30)
GREEN = (115, 190, 70)
LIGHT_GREEN = (150, 220, 90)
DARK_GREEN = (70, 140, 40)
GROUND_BROWN = (220, 195, 130)
GROUND_GRASS = (120, 190, 80)
UI_BOX = (50, 50, 50)
BUTTON_GREEN = (50, 200, 80)
BUTTON_RED = (230, 70, 70)
BUTTON_BLUE = (50, 130, 230)
PURPLE = (140, 50, 230)

# Game States: 'MENU', 'PLAYING', 'SHOP', 'GAME_OVER'
game_state = 'MENU'

# Game Parameters
gravity = SCREEN_HEIGHT * 0.00065
bird_movement = 0
bird_jump = -(SCREEN_HEIGHT * 0.0135)  
milestone_active = False  
score = 0
highscore = 0
wins = 0  
current_milestone = 20  

# Speed Variables
base_speed = SCREEN_WIDTH * 0.010       
max_speed = SCREEN_WIDTH * 0.024        
scroll_speed = base_speed

# Bird Dimensions
bird_size = int(SCREEN_WIDTH * 0.11)
bird_rect = pygame.Rect(int(SCREEN_WIDTH * 0.22), int(SCREEN_HEIGHT // 2), bird_size, bird_size)

# Obstacle Setup
pipe_list = []
SPAWNPIPE = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWNPIPE, 1800)  
pipe_width = int(SCREEN_WIDTH * 0.20)
ground_height = int(SCREEN_HEIGHT * 0.1)

# Smooth Flow Generation Variables
last_pipe_center_y = SCREEN_HEIGHT // 2
max_vertical_shift = int(SCREEN_HEIGHT * 0.20) 

# Scenery Setup
clouds = [[random.randint(0, SCREEN_WIDTH), random.randint(int(SCREEN_HEIGHT * 0.05), int(SCREEN_HEIGHT * 0.25)), random.randint(30, 55)] for _ in range(3)]

# Scaled Fonts System
font = pygame.font.Font(None, int(SCREEN_WIDTH * 0.09))
game_over_font = pygame.font.Font(None, int(SCREEN_WIDTH * 0.13))
ui_font = pygame.font.Font(None, int(SCREEN_WIDTH * 0.07))
small_ui_font = pygame.font.Font(None, int(SCREEN_WIDTH * 0.05))

# Shop Items Setup
shop_hats = [
    {'name': 'Top Hat', 'cost': 15, 'color': (10, 10, 10), 'purchased': False},
    {'name': 'Red Cap', 'cost': 45, 'color': (240, 30, 30), 'purchased': False},
    {'name': 'Crown', 'cost': 120, 'color': (255, 215, 0), 'purchased': False}
]
selected_hat = -1 

# Code Entry System Configuration
typing_mode = False
typed_password = ""
status_message = "Tap box to enter code"
status_color = WHITE

# Visual interactive box rect to activate typing & mobile keyboard
input_box_rect = pygame.Rect((SCREEN_WIDTH - int(SCREEN_WIDTH * 0.65)) // 2, int(SCREEN_HEIGHT * 0.25), int(SCREEN_WIDTH * 0.65), int(SCREEN_HEIGHT * 0.06))

# Interactive UI Rectangles
start_btn = pygame.Rect(0, 0, 0, 0)
shop_btn = pygame.Rect(0, 0, 0, 0)
back_btn = pygame.Rect(0, 0, 0, 0)
stop_btn = pygame.Rect(0, 0, 0, 0)
cont_btn = pygame.Rect(0, 0, 0, 0)
replay_btn = pygame.Rect(0, 0, 0, 0)
quit_btn = pygame.Rect(0, 0, 0, 0)
hat_rects = []

def create_pipe():
    global last_pipe_center_y
    dynamic_gap = random.randint(int(SCREEN_HEIGHT * 0.24), int(SCREEN_HEIGHT * 0.29)) 
    min_y = int(SCREEN_HEIGHT * 0.2)
    max_y = int(SCREEN_HEIGHT * 0.6)
    target_min = max(min_y, last_pipe_center_y - max_vertical_shift)
    target_max = min(max_y, last_pipe_center_y + max_vertical_shift)
    
    random_pipe_pos = random.randint(target_min, target_max)
    last_pipe_center_y = random_pipe_pos 
    
    bottom_pipe = pygame.Rect(SCREEN_WIDTH + 40, random_pipe_pos + (dynamic_gap // 2), pipe_width, SCREEN_HEIGHT)
    top_pipe = pygame.Rect(SCREEN_WIDTH + 40, 0, pipe_width, random_pipe_pos - (dynamic_gap // 2))
    
    return [bottom_pipe, top_pipe, False]

def move_pipes(pipes):
    for pipe_pair in pipes:
        pipe_pair[0].x -= int(scroll_speed)
        pipe_pair[1].x -= int(scroll_speed)
    return [p for p in pipes if p[0].right > -50]

def draw_pipes(pipes):
    for pipe_pair in pipes:
        bot_rect, top_rect = pipe_pair[0], pipe_pair[1]
        pygame.draw.rect(screen, GREEN, bot_rect)
        pygame.draw.rect(screen, LIGHT_GREEN, [bot_rect.x, bot_rect.y, int(pipe_width * 0.13), bot_rect.height])
        pygame.draw.rect(screen, DARK_GREEN, bot_rect, 3)
        
        pygame.draw.rect(screen, GREEN, top_rect)
        pygame.draw.rect(screen, LIGHT_GREEN, [top_rect.x, top_rect.y, int(pipe_width * 0.13), top_rect.height])
        pygame.draw.rect(screen, DARK_GREEN, top_rect, 3)

        lip_height = int(SCREEN_HEIGHT * 0.035)
        lip_padding = int(pipe_width * 0.06)
        
        bot_lip = pygame.Rect(bot_rect.x - lip_padding, bot_rect.y, bot_rect.width + (lip_padding * 2), lip_height)
        pygame.draw.rect(screen, GREEN, bot_lip)
        pygame.draw.rect(screen, LIGHT_GREEN, [bot_lip.x, bot_lip.y, int(pipe_width * 0.13), lip_height])
        pygame.draw.rect(screen, DARK_GREEN, bot_lip, 3)
        
        top_lip = pygame.Rect(top_rect.x - lip_padding, top_rect.bottom - lip_height, top_rect.width + (lip_padding * 2), lip_height)
        pygame.draw.rect(screen, GREEN, top_lip)
        pygame.draw.rect(screen, LIGHT_GREEN, [top_lip.x, top_lip.y, int(pipe_width * 0.13), lip_height])
        pygame.draw.rect(screen, DARK_GREEN, top_lip, 3)

def check_collision(pipes):
    for pipe_pair in pipes:
        if bird_rect.colliderect(pipe_pair[0]) or bird_rect.colliderect(pipe_pair[1]):
            return False
    if bird_rect.top <= 0 or bird_rect.bottom >= SCREEN_HEIGHT - ground_height:
        return False
    return True

def draw_bird():
    pygame.draw.ellipse(screen, YELLOW, bird_rect)
    pygame.draw.ellipse(screen, BLACK, bird_rect, 3)
    
    if selected_hat != -1:
        hat_color = shop_hats[selected_hat]['color']
        if selected_hat == 0:  
            pygame.draw.rect(screen, hat_color, [bird_rect.x + int(bird_size * 0.1), bird_rect.y - int(bird_size * 0.35), int(bird_size * 0.6), int(bird_size * 0.4)])
            pygame.draw.rect(screen, hat_color, [bird_rect.x - int(bird_size * 0.1), bird_rect.y - int(bird_size * 0.05), int(bird_size * 0.9), int(bird_size * 0.1)])
        elif selected_hat == 1:  
            pygame.draw.ellipse(screen, hat_color, [bird_rect.x + int(bird_size * 0.05), bird_rect.y - int(bird_size * 0.15), int(bird_size * 0.7), int(bird_size * 0.35)])
            pygame.draw.rect(screen, hat_color, [bird_rect.x + int(bird_size * 0.4), bird_rect.y - int(bird_size * 0.02), int(bird_size * 0.65), int(bird_size * 0.1)])
        elif selected_hat == 2:  
            points = [
                (bird_rect.x, bird_rect.y + int(bird_size * 0.05)),
                (bird_rect.x + int(bird_size * 0.1), bird_rect.y - int(bird_size * 0.25)),
                (bird_rect.x + int(bird_size * 0.35), bird_rect.y - int(bird_size * 0.05)),
                (bird_rect.x + int(bird_size * 0.6), bird_rect.y - int(bird_size * 0.25)),
                (bird_rect.x + int(bird_size * 0.7), bird_rect.y + int(bird_size * 0.05))
            ]
            pygame.draw.polygon(screen, hat_color, points)
            pygame.draw.polygon(screen, BLACK, points, 2)

    eye_size = int(bird_size * 0.3)
    eye_rect = pygame.Rect(bird_rect.x + int(bird_size * 0.5), bird_rect.y + int(bird_size * 0.12), eye_size, eye_size)
    pygame.draw.ellipse(screen, WHITE, eye_rect)
    pygame.draw.ellipse(screen, BLACK, [eye_rect.x + int(eye_size * 0.4), eye_rect.y + int(eye_size * 0.2), int(eye_size * 0.4), int(eye_size * 0.4)])
    
    pygame.draw.polygon(screen, ORANGE, [
        (bird_rect.x + int(bird_size * 0.8), bird_rect.y + int(bird_size * 0.35)),
        (bird_rect.x + int(bird_size * 1.1), bird_rect.y + int(bird_size * 0.5)),
        (bird_rect.x + int(bird_size * 0.8), bird_rect.y + int(bird_size * 0.6))
    ])
    pygame.draw.polygon(screen, BLACK, [
        (bird_rect.x + int(bird_size * 0.8), bird_rect.y + int(bird_size * 0.35)),
        (bird_rect.x + int(bird_size * 1.1), bird_rect.y + int(bird_size * 0.5)),
        (bird_rect.x + int(bird_size * 0.8), bird_rect.y + int(bird_size * 0.6))
    ], 3)
    
    wing_offset = int(math.sin(pygame.time.get_ticks() * 0.025) * (bird_size * 0.12)) if bird_movement < 2 else int(bird_size * 0.1)
    wing_rect = pygame.Rect(bird_rect.x + int(bird_size * 0.08), bird_rect.y + int(bird_size * 0.35) + wing_offset, int(bird_size * 0.4), int(bird_size * 0.3))
    pygame.draw.ellipse(screen, WING_YELLOW, wing_rect)
    pygame.draw.ellipse(screen, BLACK, wing_rect, 3)

def draw_scenery():
    for cloud in clouds:
        cloud[0] -= (scroll_speed * 0.1)
        if cloud[0] < -120:
            cloud[0] = SCREEN_WIDTH + random.randint(20, 100)
            cloud[1] = random.randint(int(SCREEN_HEIGHT * 0.05), int(SCREEN_HEIGHT * 0.25))
        pygame.draw.circle(screen, CLOUD_WHITE, (int(cloud[0]), cloud[1]), cloud[2])
        pygame.draw.circle(screen, CLOUD_WHITE, (int(cloud[0] + (cloud[2] * 0.5)), cloud[1] + 4), int(cloud[2] * 0.8))
        pygame.draw.circle(screen, CLOUD_WHITE, (int(cloud[0] - (cloud[2] * 0.5)), cloud[1] + 4), int(cloud[2] * 0.8))

    pygame.draw.rect(screen, GROUND_BROWN, [0, SCREEN_HEIGHT - ground_height, SCREEN_WIDTH, ground_height])
    pygame.draw.rect(screen, GROUND_GRASS, [0, SCREEN_HEIGHT - ground_height, SCREEN_WIDTH, int(ground_height * 0.25)])
    pygame.draw.line(screen, DARK_GREEN, (0, SCREEN_HEIGHT - ground_height), (SCREEN_WIDTH, SCREEN_HEIGHT - ground_height), 3)

def get_win_reward(milestone):
    step = milestone // 20
    return step * step

def draw_milestone_popup():
    global stop_btn, cont_btn
    box_w, box_h = int(SCREEN_WIDTH * 0.85), int(SCREEN_HEIGHT * 0.38)
    box_x = (SCREEN_WIDTH - box_w) // 2
    box_y = (SCREEN_HEIGHT - box_h) // 2
    
    pygame.draw.rect(screen, UI_BOX, [box_x, box_y, box_w, box_h], 0, 15)
    pygame.draw.rect(screen, WHITE, [box_x, box_y, box_w, box_h], 4, 15)
    
    txt1 = ui_font.render(f"Reached Score {current_milestone}!", True, WHITE)
    reward = get_win_reward(current_milestone)
    txt2 = ui_font.render(f"Stop for +{reward} Wins?", True, YELLOW)
    
    screen.blit(txt1, txt1.get_rect(center=(SCREEN_WIDTH // 2, box_y + int(box_h * 0.2))))
    screen.blit(txt2, txt2.get_rect(center=(SCREEN_WIDTH // 2, box_y + int(box_h * 0.45))))
    
    btn_w, btn_h = int(box_w * 0.4), int(box_h * 0.25)
    stop_btn = pygame.Rect(box_x + int(box_w * 0.07), box_y + int(box_h * 0.65), btn_w, btn_h)
    cont_btn = pygame.Rect(box_x + int(box_w * 0.53), box_y + int(box_h * 0.65), btn_w, btn_h)
    
    pygame.draw.rect(screen, BUTTON_RED, stop_btn, 0, 8)
    pygame.draw.rect(screen, BUTTON_GREEN, cont_btn, 0, 8)
    
    lbl_stop = ui_font.render("STOP", True, WHITE)
    lbl_cont = ui_font.render("GO ON", True, WHITE)
    screen.blit(lbl_stop, lbl_stop.get_rect(center=stop_btn.center))
    screen.blit(lbl_cont, lbl_cont.get_rect(center=cont_btn.center))

def draw_menu():
    global start_btn, shop_btn
    title = game_over_font.render("FLAPPY BIRD", True, WHITE)
    shadow = game_over_font.render("FLAPPY BIRD", True, BLACK)
    screen.blit(shadow, shadow.get_rect(center=(SCREEN_WIDTH // 2 + 4, SCREEN_HEIGHT * 0.22)))
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.2)))
    
    hs_txt = ui_font.render(f"HIGHSCORE: {highscore}", True, YELLOW)
    screen.blit(hs_txt, hs_txt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.32)))
    
    wins_txt = ui_font.render(f"Wins: {wins}", True, WHITE)
    screen.blit(wins_txt, wins_txt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.4)))

    start_btn = pygame.Rect((SCREEN_WIDTH - int(SCREEN_WIDTH * 0.6)) // 2, int(SCREEN_HEIGHT * 0.52), int(SCREEN_WIDTH * 0.6), int(SCREEN_HEIGHT * 0.1))
    shop_btn = pygame.Rect((SCREEN_WIDTH - int(SCREEN_WIDTH * 0.6)) // 2, int(SCREEN_HEIGHT * 0.66), int(SCREEN_WIDTH * 0.6), int(SCREEN_HEIGHT * 0.1))
    
    pygame.draw.rect(screen, BUTTON_GREEN, start_btn, 0, 12)
    pygame.draw.rect(screen, BLACK, start_btn, 3, 12)
    pygame.draw.rect(screen, BUTTON_BLUE, shop_btn, 0, 12)
    pygame.draw.rect(screen, BLACK, shop_btn, 3, 12)
    
    lbl_start = ui_font.render("PLAY GAME", True, WHITE)
    lbl_shop = ui_font.render("HAT SHOP", True, WHITE)
    screen.blit(lbl_start, lbl_start.get_rect(center=start_btn.center))
    screen.blit(lbl_shop, lbl_shop.get_rect(center=shop_btn.center))

def draw_shop():
    global back_btn, hat_rects, typed_password, typing_mode, status_message, status_color
    title = game_over_font.render("HAT SHOP", True, YELLOW)
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.09)))
    
    wins_txt = ui_font.render(f"Your Wins: {wins}", True, WHITE)
    screen.blit(wins_txt, wins_txt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.18)))
    
    # Draw Visual Typing Input Box Container
    box_bg = (30, 45, 60) if typing_mode else UI_BOX
    box_border = YELLOW if typing_mode else WHITE
    pygame.draw.rect(screen, box_bg, input_box_rect, 0, 8)
    pygame.draw.rect(screen, box_border, input_box_rect, 2, 8)
    
    # Handle text display inside or above the text input field
    if typing_mode:
        lbl_show = small_ui_font.render(f"Code: {typed_password}|", True, WHITE)
    else:
        lbl_show = small_ui_font.render(status_message, True, status_color)
        
    screen.blit(lbl_show, lbl_show.get_rect(center=input_box_rect.center))

    hat_rects = []
    start_y = int(SCREEN_HEIGHT * 0.34)
    row_h = int(SCREEN_HEIGHT * 0.13)
    
    for i, hat in enumerate(shop_hats):
        row_rect = pygame.Rect(int(SCREEN_WIDTH * 0.05), start_y + (i * row_h), int(SCREEN_WIDTH * 0.9), int(SCREEN_HEIGHT * 0.11))
        pygame.draw.rect(screen, UI_BOX, row_rect, 0, 10)
        
        p_box = pygame.Rect(row_rect.x + 15, row_rect.y + 15, int(row_rect.height*0.6), int(row_rect.height*0.6))
        pygame.draw.rect(screen, hat['color'], p_box, 0, 5)
        pygame.draw.rect(screen, WHITE, p_box, 2, 5)
        
        name_lbl = ui_font.render(hat['name'], True, WHITE)
        screen.blit(name_lbl, (row_rect.x + int(row_rect.height * 0.9), row_rect.y + 10))
        
        btn = pygame.Rect(row_rect.right - int(SCREEN_WIDTH * 0.32), row_rect.y + 15, int(SCREEN_WIDTH * 0.28), int(row_rect.height * 0.6))
        hat_rects.append(btn)
        
        if hat['purchased']:
            if selected_hat == i:
                pygame.draw.rect(screen, PURPLE, btn, 0, 6)
                txt = small_ui_font.render("ACTIVE", True, WHITE)
            else:
                pygame.draw.rect(screen, BLACK, btn, 0, 6)
                txt = small_ui_font.render("EQUIP", True, WHITE)
        else:
            pygame.draw.rect(screen, BUTTON_GREEN, btn, 0, 6)
            txt = small_ui_font.render(f"{hat['cost']} W", True, WHITE)
            
        screen.blit(txt, txt.get_rect(center=btn.center))
        
    back_btn = pygame.Rect((SCREEN_WIDTH - int(SCREEN_WIDTH * 0.5)) // 2, int(SCREEN_HEIGHT * 0.82), int(SCREEN_WIDTH * 0.5), int(SCREEN_HEIGHT * 0.09))
    pygame.draw.rect(screen, BUTTON_RED, back_btn, 0, 10)
    lbl_back = ui_font.render("BACK", True, WHITE)
    screen.blit(lbl_back, lbl_back.get_rect(center=back_btn.center))

def draw_game_over():
    global replay_btn, quit_btn
    go_surface = game_over_font.render('GAME OVER', True, BLACK)
    go_rect = go_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.2))
    screen.blit(go_surface, go_rect)
    
    score_surface = font.render(f'Score: {score}', True, WHITE)
    score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.33))
    screen.blit(score_surface, score_rect)
    
    hs_surface = font.render(f'Highscore: {highscore}', True, YELLOW)
    hs_rect = hs_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.43))
    screen.blit(hs_surface, hs_rect)
    
    replay_btn = pygame.Rect((SCREEN_WIDTH - int(SCREEN_WIDTH * 0.6)) // 2, int(SCREEN_HEIGHT * 0.56), int(SCREEN_WIDTH * 0.6), int(SCREEN_HEIGHT * 0.09))
    quit_btn = pygame.Rect((SCREEN_WIDTH - int(SCREEN_WIDTH * 0.6)) // 2, int(SCREEN_HEIGHT * 0.69), int(SCREEN_WIDTH * 0.6), int(SCREEN_HEIGHT * 0.09))
    
    pygame.draw.rect(screen, BUTTON_GREEN, replay_btn, 0, 10)
    pygame.draw.rect(screen, BLACK, replay_btn, 2, 10)
    pygame.draw.rect(screen, BUTTON_RED, quit_btn, 0, 10)
    pygame.draw.rect(screen, BLACK, quit_btn, 2, 10)
    
    lbl_replay = ui_font.render("REPLAY", True, WHITE)
    lbl_quit = ui_font.render("QUIT TO MENU", True, WHITE)
    screen.blit(lbl_replay, lbl_replay.get_rect(center=replay_btn.center))
    screen.blit(lbl_quit, lbl_quit.get_rect(center=quit_btn.center))

def reset_game_data():
    global game_active, pipe_list, bird_movement, score, current_milestone, scroll_speed, last_pipe_center_y
    game_active = True
    pipe_list.clear()
    bird_rect.center = (int(SCREEN_WIDTH * 0.22), SCREEN_HEIGHT // 2)
    bird_movement = 0
    score = 0
    current_milestone = 20
    scroll_speed = base_speed
    last_pipe_center_y = SCREEN_HEIGHT // 2

# Execution Engine Thread
while True:
    pos = (0, 0)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        # Pydroid Mobile Mobile-Friendly Input Handler via TEXTINPUT Layer
        if game_state == 'SHOP' and typing_mode:
            if event.type == pygame.TEXTINPUT:
                if len(typed_password) < 14:
                    typed_password += event.text
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    typed_password = typed_password[:-1]
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    pygame.key.stop_text_input()
                    typing_mode = False
                    if typed_password.lower() == "banana":
                        wins += 500
                        status_message = "ACCEPTED! +500 WINS"
                        status_color = BUTTON_GREEN
                    else:
                        status_message = "fih."
                        status_color = BUTTON_RED
                    typed_password = ""

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            
            if game_state == 'MENU':
                if start_btn.collidepoint(pos):
                    game_state = 'PLAYING'
                    reset_game_data()
                elif shop_btn.collidepoint(pos):
                    game_state = 'SHOP'
                    status_message = "Tap box to enter code"
                    status_color = WHITE
                    typing_mode = False
                    typed_password = ""
                    
            elif game_state == 'SHOP':
                if back_btn.collidepoint(pos):
                    pygame.key.stop_text_input()
                    game_state = 'MENU'
                
                # Active Tap Detector on the Input Area
                if input_box_rect.collidepoint(pos):
                    typing_mode = True
                    typed_password = ""
                    pygame.key.start_text_input()  # Forces hardware/software visual keyboard engine initialization
                
                if not typing_mode:
                    for i, btn in enumerate(hat_rects):
                        if btn.collidepoint(pos):
                            hat = shop_hats[i]
                            if hat['purchased']:
                                selected_hat = -1 if selected_hat == i else i
                            elif wins >= hat['cost']:
                                wins -= hat['cost']
                                hat['purchased'] = True
                                selected_hat = i
                            
            elif game_state == 'PLAYING':
                if milestone_active:
                    if stop_btn.collidepoint(pos):
                        wins += get_win_reward(current_milestone)
                        if score > highscore:
                            highscore = score
                        game_state = 'MENU'
                        milestone_active = False
                    elif cont_btn.collidepoint(pos):
                        current_milestone += 20  
                        milestone_active = False
                else:
                    if game_active:
                        bird_movement = bird_jump
                        
            elif game_state == 'GAME_OVER':
                if replay_btn.collidepoint(pos):
                    game_state = 'PLAYING'
                    reset_game_data()
                elif quit_btn.collidepoint(pos):
                    game_state = 'MENU'

        if event.type == SPAWNPIPE and game_state == 'PLAYING' and game_active and not milestone_active:
            pipe_list.append(create_pipe())

    screen.fill(SKY_BLUE)
    draw_scenery()

    if game_state == 'MENU':
        draw_menu()
    elif game_state == 'SHOP':
        draw_shop()
    elif game_state == 'GAME_OVER':
        draw_game_over()
    elif game_state == 'PLAYING':
        if game_active:
            if not milestone_active:
                bird_movement += gravity
                bird_rect.y += int(bird_movement)
                pipe_list = move_pipes(pipe_list)
                
                if not check_collision(pipe_list):
                    game_active = False
                    if score > highscore:
                        highscore = score
                    game_state = 'GAME_OVER'  
                
                for pipe_pair in pipe_list:
                    if not pipe_pair[2] and pipe_pair[0].centerx < bird_rect.centerx:
                        pipe_pair[2] = True
                        score += 1
                        
                        new_speed = scroll_speed + (SCREEN_WIDTH * 0.0008)
                        if new_speed <= max_speed:
                            scroll_speed = new_speed
                        else:
                            scroll_speed = max_speed
                        
                        if score == current_milestone:
                            milestone_active = True
            
            draw_bird()
            draw_pipes(pipe_list)
            
            score_surface = font.render(f"Score: {score}", True, WHITE)
            score_rect = score_surface.get_rect(topleft=(int(SCREEN_WIDTH * 0.05), int(SCREEN_HEIGHT * 0.04)))
            screen.blit(score_surface, score_rect)
            
            wins_surface = font.render(f"Wins: {wins}", True, YELLOW)
            wins_rect = wins_surface.get_rect(topright=(int(SCREEN_WIDTH * 0.95), int(SCREEN_HEIGHT * 0.04)))
            screen.blit(wins_surface, wins_rect)
            
            if milestone_active:
                draw_milestone_popup()

    pygame.display.flip()
    clock.tick(60)
