import pygame
from pygame import *
import random
import os


pygame.init()
pygame.mixer.init()

win_width = 800
win_height = 600
window = display.set_mode((win_width, win_height))
display.set_caption('Super Mario Adventure')
clock = time.Clock()
FPS = 60


backgrounds = ['mario_background.jpg', 'mario_background_2.jpg']
current_bg_idx = 0
bg_change_timer = pygame.time.get_ticks()
BG_CHANGE_INTERVAL = 5000


jump_sound = mixer.Sound('maro-jump-sound-effect_1.wav')
coin_sound = mixer.Sound('super-mario-coin-sound.wav')


def load_image(filename):
    return image.load(os.path.join("pythonProject6", filename))



class GameSprite(pygame.sprite.Sprite):
    def __init__(self, player_image, x, y, speed=0):
        super().__init__()
        self.image = load_image(player_image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed

    def draw(self):
        window.blit(self.image, self.rect)



class Player(GameSprite):
    def __init__(self, x, y):
        super().__init__('pngwing.com (5).png', x, y)
        self.is_jumping = False
        self.jump_count = 10

    def update(self):
        keys = pygame.key.get_pressed()

        if not self.is_jumping:
            if keys[K_SPACE]:
                self.is_jumping = True
                jump_sound.play()

        else:
            if self.jump_count >= -10:
                neg = 1
                if self.jump_count < 0:
                    neg = -1
                self.rect.y -= (self.jump_count ** 2) * 0.5 * neg
                self.jump_count -= 1
            else:
                self.is_jumping = False
                self.jump_count = 10

        if keys[K_LEFT] and self.rect.x > 0:
            self.rect.x -= 5
        elif keys[K_RIGHT] and self.rect.x < win_width - self.rect.width:
            self.rect.x += 5


class Enemy(GameSprite):
    def __init__(self, x, y, speed, move_area=(0, win_width)):
        super().__init__('pngwing.com (3).png', x, y, speed)
        self.move_area = move_area

    def update(self):
        self.rect.x += self.speed
        if self.rect.x <= self.move_area[0] or self.rect.x + self.rect.width >= self.move_area[1]:
            self.speed *= -1


class Coin(GameSprite):
    def __init__(self, x, y):
        super().__init__('pngwing.com (4).png', x, y)
        self.angle = 0

    def update(self):
        self.angle += 5
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        window.blit(rotated_image, new_rect)



class Menu():
    def __init__(self):
        self.menu_font = pygame.font.SysFont(None, 60)
        self.start_text = self.menu_font.render("START GAME", True, (255, 255, 255))
        self.exit_text = self.menu_font.render("EXIT", True, (255, 255, 255))

    def render_menu(self):
        menu_pos_start = ((win_width // 2) - (self.start_text.get_width() // 2), 200)
        menu_pos_exit = ((win_width // 2) - (self.exit_text.get_width() // 2), 300)
        window.fill((0, 0, 0))
        window.blit(self.start_text, menu_pos_start)
        window.blit(self.exit_text, menu_pos_exit)

    def check_click(self, pos):
        start_button_rect = Rect(menu_pos_start[0], menu_pos_start[1],
                                 self.start_text.get_width(), self.start_text.get_height())
        exit_button_rect = Rect(menu_pos_exit[0], menu_pos_exit[1],
                                self.exit_text.get_width(), self.exit_text.get_height())

        if start_button_rect.collidepoint(pos):
            return "start"
        elif exit_button_rect.collidepoint(pos):
            return "exit"
        return None



player = Player(win_width // 2, win_height - 100)
enemies = []
for _ in range(3):
    enemy = Enemy(random.randint(0, win_width), random.randint(0, win_height), random.choice([-3, 3]))
    enemies.append(enemy)

coins = []
for _ in range(5):
    coin = Coin(random.randint(0, win_width), random.randint(0, win_height))
    coins.append(coin)

menu = Menu()
game_over_font = pygame.font.SysFont(None, 80)

running = True
in_game = False
game_over = False

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN and not in_game:
            click_result = menu.check_click(event.pos)
            if click_result == "start":
                in_game = True
            elif click_result == "exit":
                running = False
        elif event.type == KEYDOWN and game_over:
            if event.key == K_RETURN:
                game_over = False
                in_game = True
                player.rect.x = win_width // 2
                player.rect.y = win_height - 100
                enemies.clear()
                coins.clear()
                for _ in range(3):
                    enemy = Enemy(random.randint(0, win_width), random.randint(0, win_height), random.choice([-3, 3]))
                    enemies.append(enemy)
                for _ in range(5):
                    coin = Coin(random.randint(0, win_width), random.randint(0, win_height))
                    coins.append(coin)

    current_time = pygame.time.get_ticks()
    if current_time - bg_change_timer > BG_CHANGE_INTERVAL:
        current_bg_idx = (current_bg_idx + 1) % len(backgrounds)
        background = load_image(backgrounds[current_bg_idx])
        bg_change_timer = current_time

    if in_game:
        window.blit(background, (0, 0))
        player.update()
        player.draw()

        for e in enemies:
            e.update()
            e.draw()
            if pygame.sprite.collide_rect(player, e):
                game_over = True
                break

        for c in coins:
            c.update()
            if pygame.sprite.collide_rect(player, c):
                coins.remove(c)
                coin_sound.play()

        if not coins:
            game_over = True
            victory_text = game_over_font.render("YOU WIN!", True, (255, 255, 255))
            window.blit(victory_text, (win_width // 2 - victory_text.get_width() // 2,
                                       win_height // 2 - victory_text.get_height() // 2))
        elif game_over:
            defeat_text = game_over_font.render("GAME OVER! Press Enter to restart.", True, (255, 255, 255))
            window.blit(defeat_text, (win_width // 2 - defeat_text.get_width() // 2,
                                      win_height // 2 - defeat_text.get_height() // 2))

    else:
        menu.render_menu()

    clock.tick(FPS)
    display.flip()

pygame.quit()