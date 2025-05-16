import pygame
import random
import math
from sys import exit
from tkinter import messagebox

# Константы
SIZE = 10
CELL_SIZE = 40
MARGIN_TOP = 100
MARGIN_SIDES = 80
MARGIN_BOTTOM = 100
SCREEN_WIDTH = MARGIN_SIDES * 2 + CELL_SIZE * SIZE * 2 + 50
SCREEN_HEIGHT = MARGIN_TOP + CELL_SIZE * SIZE + MARGIN_BOTTOM

SEA = '~'
SHIP = '■'
HIT = 'X'
MISS = '○'

# Цвета
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
GREY = (169, 169, 169)
BLACK = (0, 0, 0)
LIGHT_BLUE = (173, 216, 230)
DARK_GREY = (50, 50, 50)

# Инициализация PyGame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Морской Бой")
clock = pygame.time.Clock()

HOVER_ALPHA = 100  # Прозрачность при наведении

# Шрифты
try:
    title_font = pygame.font.Font('assets/fonts/sea_fonts.ttf', 36)
    button_font = pygame.font.Font('assets/fonts/sea_fonts.ttf', 32)
    font = pygame.font.Font('assets/fonts/sea_fonts.ttf', 28)
except:
    title_font = pygame.font.SysFont(None, 36)
    button_font = pygame.font.SysFont(None, 32)
    font = pygame.font.SysFont(None, 28)

# Изображения
ship_img = None
hit_img = None
miss_img = None
sea_img = None

try:
    ship_img = pygame.image.load('assets/images/ship.png')
    hit_img = pygame.image.load('assets/images/explosions/explosion1.png')
    miss_img = pygame.image.load('assets/images/miss.png')
    sea_img = pygame.image.load('assets/images/water.png')

    ship_img = pygame.transform.scale(ship_img, (CELL_SIZE, CELL_SIZE))
    hit_img = pygame.transform.scale(hit_img, (CELL_SIZE, CELL_SIZE))
    miss_img = pygame.transform.scale(miss_img, (CELL_SIZE, CELL_SIZE))
    sea_img = pygame.transform.scale(sea_img, (CELL_SIZE, CELL_SIZE))

except Exception as e:
    print(f"[Ошибка] Не удалось загрузить текстуры: {e}")
    ship_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
    ship_img.fill(GREY)
    hit_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
    hit_img.fill(RED)
    miss_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
    miss_img.fill(WHITE)
    sea_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
    sea_img.fill(BLUE)

# Анимация взрыва
EXPLOSION_FRAMES = []
try:
    for i in range(1, 5):
        frame = pygame.image.load(f'assets/images/explosions/explosion{i}.png')
        frame = pygame.transform.scale(frame, (CELL_SIZE, CELL_SIZE))
        EXPLOSION_FRAMES.append(frame)
except Exception as e:
    print(f"[Ошибка] Не удалось загрузить кадры взрыва: {e}")
    EXPLOSION_FRAMES = [hit_img]

# Звуки
pygame.mixer.init()
sound_hit = pygame.mixer.Sound('assets/sounds/hit.wav')
sound_miss = pygame.mixer.Sound('assets/sounds/miss.wav')
sound_sunk = pygame.mixer.Sound('assets/sounds/sunk.wav')
sound_victory = pygame.mixer.Sound('assets/sounds/victory.wav')
sound_defeat = pygame.mixer.Sound('assets/sounds/defeat.wav')
sound_click = pygame.mixer.Sound('assets/sounds/click.wav')

volume_hit = 0.7
volume_miss = 0.5
volume_sunk = 1.0
volume_music = 0.3
volume_victory = 1.0
volume_defeat = 1.0
volume_click = 0.5
sound_click.set_volume(volume_click)

sound_hit.set_volume(volume_hit)
sound_miss.set_volume(volume_miss)
sound_sunk.set_volume(volume_sunk)
pygame.mixer.music.set_volume(volume_music)
sound_victory.set_volume(volume_victory)
sound_defeat.set_volume(volume_defeat)

# Фоновая музыка
try:
    pygame.mixer.music.load('assets/sounds/background.wav')
    pygame.mixer.music.play(-1)
except Exception as e:
    print(f"[Ошибка] Не удалось загрузить фоновую музыку: {e}")

# Анимация волн
WAVE_COUNT = 3
wave_images = []
try:
    for i in range(1, WAVE_COUNT + 1):
        wave = pygame.image.load(f'assets/images/waves/wave{i}.png')
        wave = pygame.transform.scale(wave, (SCREEN_WIDTH, int(CELL_SIZE * 2)))
        wave_images.append(wave)
except Exception as e:
    wave_images = [pygame.Surface((SCREEN_WIDTH, int(CELL_SIZE * 2)))]
    wave_images[0].fill(BLUE)
    print(f"[Ошибка] Не удалось загрузить волны: {e}")

# Анимация флага
flag_image = None
try:
    flag_image = pygame.image.load('assets/images/flag.png')
    flag_image = pygame.transform.scale(flag_image, (CELL_SIZE * 2, CELL_SIZE * 2))
except Exception as e:
    print(f"[Ошибка] Не удалось загрузить флаг: {e}")
    flag_image = None

# === КНОПКИ ===
def draw_button(text, rect, color=LIGHT_BLUE, text_color=BLACK, mouse_pos=None, sound=None):
    hover = False
    if mouse_pos and rect.collidepoint(mouse_pos):
        hover = True
        # === Тень от кнопки ===
        shadow_rect = pygame.Rect(rect.x + 4, rect.y + 4, rect.width, rect.height)
        shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 30))  # Чёрный с прозрачностью
        screen.blit(shadow_surface, shadow_rect.topleft)

        # === Эффект ховера (белый полупрозрачный слой) ===
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 60))
        screen.blit(overlay, (rect.x, rect.y))

        # === Масштабируем текст при наведении ===
        scaled_font_size = int(button_font.get_height() * 1.1)
        scaled_font = pygame.font.Font('assets/fonts/sea_fonts.ttf', scaled_font_size)
        text_surf = scaled_font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)
    else:
        # === Обычное состояние кнопки ===
        pygame.draw.rect(screen, color, rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, rect, 2, border_radius=10)

        # === Тень под текстом (неподвижная) ===
        shadow_text_surf = button_font.render(text, True, (0, 0, 0, 100))  # Используем RGBA
        shadow_text_rect = shadow_text_surf.get_rect(center=(rect.centerx + 2, rect.centery + 2))
        screen.blit(shadow_text_surf, shadow_text_rect)

        # === Основной текст ===
        text_surf = button_font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

    return hover

def get_cell(pos, offset_x, offset_y):
    x = (pos[1] - offset_y) // CELL_SIZE
    y = (pos[0] - offset_x) // CELL_SIZE
    if 0 <= x < SIZE and 0 <= y < SIZE:
        return x, y
    return None

# === РАССТАНОВКА КОРАБЛЕЙ ===
def create_board(size=SIZE):
    return [[SEA for _ in range(size)] for _ in range(size)]

def can_place(board, x, y, size, orientation):
    if orientation == 'h':
        if y + size > SIZE:
            return False
        for i in range(size):
            if board[x][y + i] != SEA:
                return False
            for dx in [-1, 0, 1]:
                for dy in range(-1, size + 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < SIZE and 0 <= ny < SIZE:
                        if board[nx][ny] != SEA:
                            return False
    else:
        if x + size > SIZE:
            return False
        for i in range(size):
            if board[x + i][y] != SEA:
                return False
            for dy in [-1, 0, 1]:
                for dx in range(-1, size + 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < SIZE and 0 <= ny < SIZE:
                        if board[nx][ny] != SEA:
                            return False
    return True

def place_ship(board, x, y, size, orientation):
    for i in range(size):
        if orientation == 'h':
            board[x][y + i] = SHIP
        else:
            board[x + i][y] = SHIP

def place_ships(board, ship_sizes=[4, 3, 3, 2, 2, 2, 1, 1, 1, 1]):
    placed = 0
    attempts = 0
    while placed < len(ship_sizes) and attempts < 1000:
        size = ship_sizes[placed]
        orientation = random.choice(['h', 'v'])
        x = random.randint(0, SIZE - 1)
        y = random.randint(0, SIZE - 1)
        if can_place(board, x, y, size, orientation):
            place_ship(board, x, y, size, orientation)
            placed += 1
        attempts += 1

# Проверка выстрела
def shoot(board, x, y):
    if board[x][y] == SEA:
        board[x][y] = MISS
        return False, "Промах!"
    elif board[x][y] == SHIP:
        board[x][y] = HIT
        return True, "Попал!"
    return None, "Уже стреляли!"

def find_ship(board, x, y):
    if board[x][y] not in [HIT, SHIP]:
        return []
    ship = [(x, y)]
    queue = [(x, y)]
    visited = set(queue)
    while queue:
        cx, cy = queue.pop(0)
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < SIZE and 0 <= ny < SIZE and (nx, ny) not in visited:
                visited.add((nx, ny))
                if board[nx][ny] in [HIT, SHIP]:
                    ship.append((nx, ny))
                    queue.append((nx, ny))
    return list(set(ship))

def is_sunk(board, x, y):
    print(f"\n[DEBUG] Проверка: уничтожен ли корабль в ({x}, {y})?")

    # Находим все части текущего корабля
    ship_coords = find_ship(board, x, y)
    print("Координаты корабля:", ship_coords)

    # Убеждаемся, что все палубы подбиты
    for sx, sy in ship_coords:
        if board[sx][sy] == SHIP:
            print("Ещё есть непопаданная палуба!")
            return False

    # Теперь проверяем клетки вокруг каждой палубы
    for sx, sy in ship_coords:
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < SIZE and 0 <= ny < SIZE:
                    if board[nx][ny] == SHIP or board[nx][ny] == HIT:
                        # Если эта палуба не принадлежит текущему кораблю → это другой корабль
                        if (nx, ny) not in ship_coords:
                            print(f"Возможно, это часть другого корабля: ({nx}, {ny})")
                            return False

    print("Корабль полностью уничтожен!")
    return True


def open_area_around_ship(board, x, y):
    ship_coords = find_ship(board, x, y)
    for sx, sy in ship_coords:
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < SIZE and 0 <= ny < SIZE:
                    if board[nx][ny] == SEA:
                        board[nx][ny] = MISS

def has_ships(board):
    for row in board:
        if SHIP in row:
            return True
    return False

# ==== ДОСКА ====
def draw_board(board, offset_x, offset_y, is_computer=True):
    for i in range(SIZE):
        label = font.render(str(i+1), True, BLACK)
        screen.blit(label, (offset_x + i * CELL_SIZE + 15, offset_y - 20))
        screen.blit(label, (offset_x - 20, offset_y + i * CELL_SIZE + 15))

    for x in range(SIZE):
        for y in range(SIZE):
            rect = pygame.Rect(offset_x + y * CELL_SIZE, offset_y + x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if board[x][y] == SEA:
                screen.blit(sea_img, rect.topleft)
            elif board[x][y] == SHIP and not is_computer:
                screen.blit(ship_img, rect.topleft)
            elif board[x][y] == HIT:
                screen.blit(hit_img, rect.topleft)
            elif board[x][y] == MISS:
                screen.blit(miss_img, rect.topleft)
            else:
                screen.blit(sea_img, rect.topleft)
            pygame.draw.rect(screen, BLACK, rect, 1)

    # Анимация взрыва
    current_time = pygame.time.get_ticks()
    for exp in explosions.copy():
        x_exp, y_exp, start_time = exp
        elapsed = (current_time - start_time) // 100
        if elapsed < len(EXPLOSION_FRAMES):
            screen.blit(EXPLOSION_FRAMES[elapsed], (offset_x + y_exp * CELL_SIZE, offset_y + x_exp * CELL_SIZE))
        else:
            explosions.remove(exp)

# ==== ИИ ====
class SmartAI:
    def __init__(self, size=SIZE, difficulty='legend'):
        self.size = size
        self.difficulty = difficulty
        self.shots = set()
        self.last_hits = []
        self.directions = [(0,1), (1,0), (0,-1), (-1,0)]
        self.remaining_ship_sizes = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        self.board = None  # Поле игрока
        self.priority_queue = []  # Приоритетная очередь после попадания
        self.search_pattern = [(x, y) for x in range(size) for y in range(size)]
        random.shuffle(self.search_pattern)
        self.probability_map = [[0 for _ in range(size)] for _ in range(size)]

    def calculate_probabilities(self):
        """Рассчитываем карту вероятностей"""
        if self.board is None:
            return

        self.probability_map = [[0 for _ in range(self.size)] for _ in range(self.size)]

        for ship_size in self.remaining_ship_sizes:
            for x in range(self.size):
                for y in range(self.size):
                    if (x, y) in self.shots or self.board[x][y] == HIT or self.board[x][y] == MISS:
                        continue

                    # Горизонтальная ориентация
                    if y + ship_size <= self.size:
                        valid = True
                        for i in range(ship_size):
                            if (x, y + i) in self.shots or self.board[x][y + i] == MISS:
                                valid = False
                                break
                        if valid:
                            for i in range(ship_size):
                                self.probability_map[x][y + i] += 1

                    # Вертикальная ориентация
                    if x + ship_size <= self.size:
                        valid = True
                        for i in range(ship_size):
                            if (x + i, y) in self.shots or self.board[x + i][y] == MISS:
                                valid = False
                                break
                        if valid:
                            for i in range(ship_size):
                                self.probability_map[x + i][y] += 1

        # Нормализуем
        max_p = max(max(row) for row in self.probability_map)
        if max_p > 0:
            for x in range(self.size):
                for y in range(self.size):
                    self.probability_map[x][y] /= max_p

    def make_move(self):
        # 1. Если есть попадание → ищем продолжение
        if self.last_hits:
            cx, cy = self.last_hits[-1]
            for dx, dy in self.directions:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.size and 0 <= ny < self.size and (nx, ny) not in self.shots:
                    return nx, ny

        # 2. Легендарный режим: выбираем по карте вероятностей
        if self.difficulty == 'legend':
            self.calculate_probabilities()
            best_moves = []
            max_score = -1

            for x in range(self.size):
                for y in range(self.size):
                    score = self.probability_map[x][y]
                    if score > max_score and (x, y) not in self.shots:
                        max_score = score
                        best_moves = [(x, y)]
                    elif score == max_score and (x, y) not in self.shots:
                        best_moves.append((x, y))
            if best_moves:
                return random.choice(best_moves)

        # 3. Hard: шахматный паттерн
        if self.difficulty in ['hard', 'god']:
            hunt_coords = [
                (x, y) for x in range(self.size) for y in range(self.size)
                if (x + y) % 2 == 0 and (x, y) not in self.shots
            ]
            if hunt_coords:
                return random.choice(hunt_coords)

        # 4. Normal: по порядку
        if self.difficulty == 'normal':
            for move in self.search_pattern:
                if move not in self.shots:
                    return move[0], move[1]

        # 5. Easy: случайно
        attempts = 0
        while attempts < 1000:
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            if (x, y) not in self.shots:
                return x, y
            attempts += 1

        # 6. Резервный поиск
        for x in range(self.size):
            for y in range(self.size):
                if (x, y) not in self.shots:
                    return x, y

        return random.randint(0, self.size - 1), random.randint(0, self.size - 1)

    def report_result(self, x, y, hit):
        self.shots.add((x, y))
        if hit:
            self.last_hits.append((x, y))
        else:
            if (x, y) in self.last_hits:
                self.last_hits.remove((x, y))

    def check_sunk(self):
        self.last_hits.clear()

def draw_probability_map(screen, ai, offset_x, offset_y):
    for x in range(ai.size):
        for y in range(ai.size):
            prob = ai.probability_map[x][y]
            color = (int(255 * prob), int(255 * prob), int(255 * (1 - prob)))
            rect = pygame.Rect(offset_x + y * CELL_SIZE, offset_y + x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect, border_radius=3)
            pygame.draw.rect(screen, BLACK, rect, 1)
        
# ==== НАСТРОЙКИ ====
def settings_menu():
    global volume_hit, volume_miss, volume_sunk, volume_music

    running = True
    back_button = pygame.Rect(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT - 80, 120, 40)

    while running:
        screen.fill(WHITE)
        draw_slider("Попадание", 150, volume_hit, 'hit')
        draw_slider("Промах", 220, volume_miss, 'miss')
        draw_slider("Уничтожение корабля", 290, volume_sunk, 'sunk')
        draw_slider("Громкость музыки", 360, volume_music, 'music')
        mouse_pos = pygame.mouse.get_pos()
        draw_button("Назад", back_button, (255, 100, 100), BLACK, mouse_pos)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if back_button.collidepoint(pos):
                    sound_click.play()
                    running = False
                handle_slider(pos, 150, 'hit')
                handle_slider(pos, 220, 'miss')
                handle_slider(pos, 290, 'sunk')
                handle_slider(pos, 360, 'music')

        pygame.display.flip()
        clock.tick(60)

def draw_slider(label_text, y, volume, sound_type):
    label = font.render(label_text, True, BLACK)
    screen.blit(label, (SCREEN_WIDTH // 2 - 200, y))
    slider_rect = pygame.Rect(SCREEN_WIDTH // 2 + 50, y + 10, 200, 10)
    pygame.draw.rect(screen, BLACK, slider_rect, 2)
    handle_x = slider_rect.x + int((slider_rect.width - 10) * volume)
    handle_rect = pygame.Rect(handle_x, slider_rect.y - 5, 20, 20)
    pygame.draw.rect(screen, LIGHT_BLUE, handle_rect)
    return handle_rect

def handle_slider(pos, slider_y, sound_type):
    global volume_hit, volume_miss, volume_sunk, volume_music

    slider_rect = pygame.Rect(SCREEN_WIDTH // 2 + 50, slider_y + 10, 200, 10)
    if slider_rect.collidepoint(pos):
        rel_x = pos[0] - slider_rect.x
        new_volume = max(0.0, min(1.0, rel_x / slider_rect.width))

        if sound_type == 'hit':
            volume_hit = new_volume
            sound_hit.set_volume(volume_hit)
        elif sound_type == 'miss':
            volume_miss = new_volume
            sound_miss.set_volume(volume_miss)
        elif sound_type == 'sunk':
            volume_sunk = new_volume
            sound_sunk.set_volume(volume_sunk)
        elif sound_type == 'music':
            volume_music = new_volume
            pygame.mixer.music.set_volume(volume_music)

# ==== МЕНЮ ====
def main_menu():
    menu_running = True
    selected_difficulty = 'god'
    stats = {'win': 0, 'lose': 0}
    play_button = pygame.Rect(SCREEN_WIDTH//2 - 100, 200, 200, 50)
    diff_button = pygame.Rect(SCREEN_WIDTH//2 - 150, 270, 300, 50)
    stats_button = pygame.Rect(SCREEN_WIDTH//2 - 290, 340, 600, 50)
    settings_button = pygame.Rect(SCREEN_WIDTH//2 - 100, 410, 200, 50)
    quit_button = pygame.Rect(SCREEN_WIDTH//2 - 100, 480, 200, 50)

    wave_offset = 0

    while menu_running:
        if menu_background:
            screen.blit(menu_background, (0, 0))
        else:
            screen.fill(DARK_GREY)

        wave_y = SCREEN_HEIGHT - CELL_SIZE * 2
        for i in range(-1, 2):
            offset = (wave_offset + i * SCREEN_WIDTH) % SCREEN_WIDTH
            for idx in range(len(wave_images)):
                screen.blit(wave_images[idx], (i * SCREEN_WIDTH - offset, wave_y))

        # Кнопки
        mouse_pos = pygame.mouse.get_pos()
        hover_play = draw_button("Новая игра", play_button, (30, 144, 255), BLACK, mouse_pos, sound=sound_click)
        hover_diff = draw_button(f"Сложность: {selected_difficulty.capitalize()}", diff_button, (100, 149, 237), BLACK, mouse_pos, sound=sound_click)
        hover_stats = draw_button(f"Статистика: Побед - {stats['win']}, Поражений - {stats['lose']}", stats_button, (135, 206, 230), BLACK, mouse_pos, sound=sound_click)
        hover_settings = draw_button("Настройки", settings_button, (173, 216, 230), BLACK, mouse_pos, sound=sound_click)
        hover_quit = draw_button("Выход", quit_button, (255, 99, 71), BLACK, mouse_pos, sound=sound_click)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos

                if play_button.collidepoint(pos):
                    sound_click.play()
                    result = game_loop(selected_difficulty)
                    if result == 'win':
                        stats['win'] += 1
                    elif result == 'lose':
                        stats['lose'] += 1

                elif diff_button.collidepoint(pos):
                    sound_click.play()
                    difficulties = ['easy', 'normal', 'hard', 'god', 'legend']
                    idx = difficulties.index(selected_difficulty)
                    selected_difficulty = difficulties[(idx + 1) % len(difficulties)]

                elif settings_button.collidepoint(pos):
                    sound_click.play()
                    settings_menu()

                elif quit_button.collidepoint(pos):
                    sound_click.play()
                    pygame.quit()
                    exit()

        wave_offset += 1
        if wave_offset > SCREEN_WIDTH:
            wave_offset = 0

        pygame.display.flip()
        clock.tick(60)

# ==== ОСНОВНАЯ ИГРА ====
def game_loop(difficulty):
    global explosions  # Добавь это, если будешь использовать explosions глобально
    explosions = []  # ← ОБЯЗАТЕЛЬНО добавь эту строку!
    player_board = create_board()
    computer_board = create_board()
    place_ships(player_board)
    place_ships(computer_board)

    ai = SmartAI(difficulty=difficulty)
    ai.board = player_board  # <<< ПЕРЕДАЁМ ССЫЛКУ НА ПОЛЕ ИГРОКА
    status_text = "Ваш ход"
    new_game_button = pygame.Rect(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT - 80, 120, 40)

    explosions = []

    flag_wave_offset = 0.0

    running = True
    while running:
        screen.fill(WHITE)

        total_width = MARGIN_SIDES * 2 + CELL_SIZE * SIZE * 2 - 90
        start_x = (SCREEN_WIDTH - total_width) // 2
        player_offset = (start_x, MARGIN_TOP)
        computer_offset = (start_x + MARGIN_SIDES + CELL_SIZE * SIZE, MARGIN_TOP)

        # Рисуем поля
        draw_board(player_board, *player_offset, is_computer=False)
        draw_board(computer_board, *computer_offset, is_computer=True)

        # Анимация флага
        if flag_image:
            flag_wave_offset += 0.05
            sway = math.sin(flag_wave_offset) * 3
            tilt = math.sin(flag_wave_offset * 0.5) * 2
            flag_x = computer_offset[0] + CELL_SIZE * SIZE // 2 - CELL_SIZE // 2
            flag_y = computer_offset[1] - CELL_SIZE * 2.5 + int(sway)
            rotated_flag = pygame.transform.rotate(flag_image, tilt)
            flag_rect = rotated_flag.get_rect(center=(flag_x + CELL_SIZE, flag_y + CELL_SIZE))
            screen.blit(rotated_flag, flag_rect.topleft)

        # Статус
        status = font.render(f"Статус: {status_text}", True, BLACK)
        screen.blit(status, (MARGIN_SIDES, SCREEN_HEIGHT - 100))

        # Кнопка новой игры
        draw_button("Новая игра", new_game_button, (255, 223, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                if new_game_button.collidepoint(pos):
                    return 'restart'

                cell = get_cell(pos, *computer_offset)
                if cell:
                    x, y = cell
                    if computer_board[x][y] in [HIT, MISS]:
                        continue

                    hit, msg = shoot(computer_board, x, y)
                    if hit:
                        status_text = "Попадание! Ваш ход"
                        explosions.append((x, y, pygame.time.get_ticks()))
                        if is_sunk(computer_board, x, y):
                            sound_sunk.play()
                            open_area_around_ship(computer_board, x, y)
                    else:
                        status_text = "Ход компьютера"
                        sound_miss.play()

                    if not has_ships(computer_board):
                        sound_victory.play()
                        messagebox.showinfo("Победа!", "Вы победили!")
                        return 'win'

                    # Ход компьютера
                    if not hit:
                        computer_hit = True
                        while computer_hit:
                            cx, cy = ai.make_move()
                            chit, cmsg = shoot(player_board, cx, cy)
                            
                            ai.report_result(cx, cy, chit)

                            if chit:
                                computer_hit = True
                                status_text = "Компьютер попал! Его ход"
                                explosions.append((cx, cy, pygame.time.get_ticks()))
                                if is_sunk(player_board, cx, cy):
                                    sound_sunk.play()
                                    open_area_around_ship(player_board, cx, cy)
                                    ai.check_sunk()
                            else:
                                computer_hit = False
                                status_text = "Ваш ход"

                    if not has_ships(player_board):
                        sound_defeat.play()
                        messagebox.showinfo("Проигрыш", "Все ваши корабли уничтожены.")
                        return 'lose'

        pygame.display.flip()
        clock.tick(60)

# ==== ЗАГРУЖАЕМ ЛОГОТИП МЕНЮ ====
menu_background = None
try:
    menu_background = pygame.image.load('assets/images/menu/background_sea.png')
    menu_background = pygame.transform.scale(menu_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
except Exception as e:
    print(f"[Ошибка] Не удалось загрузить фоновое изображение главного меню: {e}")

# ==== ЗАПУСК ==== #
explosions = []
main_menu()
