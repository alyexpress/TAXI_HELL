from config import WIDTH, UI_DIR
from options import *


class Rating:
    def __init__(self):
        self.intro = pygame.font.Font(font_intro, 50)
        self.text = self.intro.render("5.0", True, "#333333")
        self.text = pygame.transform.rotozoom(self.text, 22, 1)
        alpha = load_image('star.png', UI_DIR).convert_alpha()
        self.star = pygame.transform.smoothscale(alpha, (60, 60))
        self.background = load_image('rating_background.png', UI_DIR)
        self.background.set_alpha(230)

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        screen.blit(self.star, (10, 30))
        screen.blit(self.text, (70, 5))


class Speedometer:
    def __init__(self):
        alpha = load_image('speedometer.png', UI_DIR).convert_alpha()
        self.scale = pygame.transform.smoothscale(alpha, (170, 125))
        alpha = load_image('speed_arrow.png', UI_DIR).convert_alpha()
        self.arrow = pygame.transform.smoothscale(alpha, (20, 80))
        alpha = load_image('speed_background.png', UI_DIR).convert_alpha()
        self.background = pygame.transform.smoothscale(alpha, (418, 190))
        self.degree, self.up = 0, True

    def update(self, speed):
        self.degree = (40 - abs(speed * 9.4)) * 3

    def draw(self, screen):
        screen.blit(self.background, (0, 636))
        screen.blit(self.scale, (40, 668))
        args = self.arrow, self.degree, 1
        arrow = pygame.transform.rotozoom(*args)
        x, y = 116, 735
        if 0 < self.degree < 180:
            x -= arrow.get_width() - 20
        if -90 < self.degree < 90:
            y -= arrow.get_height() - 20
            if -30 < self.degree < 30:
                y -= (30 - abs(self.degree)) * 0.15
        if 60 < abs(self.degree) < 120:
            offset = (30 - abs(abs(self.degree) - 90)) * 0.15
            x -= offset if self.degree > 0 else -offset
        screen.blit(arrow, (x, y))


class Counter:
    def __init__(self):
        self.intro = pygame.font.Font(font_intro, 50)
        self.small_intro = pygame.font.Font(font_intro, 40)
        time = "00:00"
        money = "$200"
        self.timer = self.intro.render(time, True, "#333333")
        self.money = self.small_intro.render(money, True, "#009900")
        self.background = load_image('counter_background.png', UI_DIR)
        self.background.set_alpha(200)

    def draw(self, screen):
        screen.blit(self.background, (1230, 10))
        screen.blit(self.timer, (1240, 20))
        screen.blit(self.money, (1240, 70))


class Fuel:
    def __init__(self):
        red = load_image("fuel_line.png", UI_DIR)
        yellow = load_image("fuel_line.png", UI_DIR)
        green = load_image("fuel_line.png", UI_DIR)
        alpha = load_image("fuel_sign2.png", UI_DIR)
        self.sign = pygame.transform.smoothscale(alpha, (47, 60))
        red.fill("#ff0000", special_flags=pygame.BLEND_RGBA_MIN)
        yellow.fill("#ffaa00", special_flags=pygame.BLEND_RGBA_MIN)
        green.fill("#00cc00", special_flags=pygame.BLEND_RGBA_MIN)
        self.lines = [red, yellow, green]

    def draw(self, screen):
        screen.blit(self.sign, (300, 710))
        for i in range(6):
            screen.blit(self.lines[i // 2], (220, 765 - i * 15))


class Place:
    def __init__(self):
        alpha = load_image('counter_background.png', UI_DIR).convert_alpha()
        self.background = pygame.transform.smoothscale(alpha, (400, 60))
        self.background.set_alpha(220)
        self.place, self.y = "q", -60

    def draw(self, screen):
        if self.place and self.y < 10:
            self.y += 2
        elif not self.place and self.y > -60:
            self.y -= 2
        screen.blit(self.background, (WIDTH // 2 - 200, self.y))
