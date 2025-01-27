import pygame.surface

from config import WIDTH, UI_DIR, FPS
from options import *


def load_scaled_image(filename, size, path=UI_DIR):
    alpha = load_image(filename, path)
    return pygame.transform.smoothscale(alpha, size)


class Rating:
    def __init__(self, city):
        self.star = load_scaled_image('rating/star.png', (55, 55))
        self.background = load_image('rating/background.png', UI_DIR)
        self.background.set_alpha(220)
        self.intro = pygame.font.Font(font_intro, 50)
        self.small = pygame.font.Font(font_intro, 36)
        stars = (sum(city.db.rating) / len(city.db.rating)
                 if city.db.rating else 0.)
        self.text, self.level, self.x = None, None, None
        self.update(stars, city.db.level)

    def update(self, stars, level):
        stars, level = str(round(stars, 1)), f"Level {level + 1}"
        self.text = self.intro.render(stars, True, "#333333")
        self.level = self.small.render(level, True, "#333333")
        self.x = (180 - self.level.get_width()) // 2

    def draw(self, screen):
        screen.blit(self.background, (10, 10))
        screen.blit(self.star, (15, 13))
        screen.blit(self.text, (78, 25))
        screen.blit(self.level, (self.x, 75))


class Speedometer:
    def __init__(self):
        self.scale = load_scaled_image('speedometer/scale.png', (170, 125))
        self.arrow = load_scaled_image('speedometer/arrow.png', (20, 80))
        background = 'speedometer/background.png', (418, 190)
        self.background = load_scaled_image(*background)
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
    def __init__(self, city):
        self.intro = pygame.font.Font(font_intro, 50)
        self.small_intro = pygame.font.Font(font_intro, 40)
        self.db, self.time, self.sec, self.stop = city.db, 0, 0, True
        self.show_money, money = self.db.money, f"${self.db.money}"
        self.timer = self.intro.render("00:00", True, "#333333")
        self.money = self.small_intro.render(money, True, "#009900")
        self.background = load_image('rating/background.png', UI_DIR)
        self.background.set_alpha(200)

    def update_time(self, seconds):
        color = "red" if seconds < 0 else "#333333"
        minute, sec = abs(seconds) // 60, abs(seconds) % 60
        time = f"{'' if minute > 9 else 0}{minute}"
        time += f":{'' if sec > 9 else 0}{sec}"
        self.timer = self.intro.render(time, True, color)

    def update(self):
        if self.sec > 0 and not self.stop:
            self.sec -= 1
        elif not self.stop:
            self.time, self.sec = self.time - 1, FPS
            self.update_time(self.time)
        if self.show_money != self.db.money:
            color = "0099" if self.show_money < self.db.money else "CC00"
            self.show_money += 1 if self.show_money < self.db.money else -1
            args = f"${self.show_money}", True, f"#{color}00"
            self.money = self.small_intro.render(*args)

    def draw(self, screen):
        screen.blit(self.background, (1230, 10))
        screen.blit(self.timer, (1240, 20))
        screen.blit(self.money, (1240, 70))


class Fuel:
    def __init__(self, city):
        self.db, self.place = city.db, city.place
        self.sec = (10 - self.db.level) * 200 + 5000
        red = load_image("speedometer/fuel_line.png", UI_DIR)
        yellow = load_image("speedometer/fuel_line.png", UI_DIR)
        green = load_image("speedometer/fuel_line.png", UI_DIR)
        red.fill("#ff0000", special_flags=pygame.BLEND_RGBA_MIN)
        yellow.fill("#ffaa00", special_flags=pygame.BLEND_RGBA_MIN)
        green.fill("#00cc00", special_flags=pygame.BLEND_RGBA_MIN)
        self.lines, self.fill_time = [red, yellow, green], -1
        self.sign = load_scaled_image("speedometer/fuel_sign.png", (47, 60))

    def refill(self):
        self.db.money -= 5 * (6 - self.db.fuel)
        self.fill_time = FPS

    def update(self, speed):
        if self.fill_time > 0:
            self.fill_time -= 1
            self.sec = (10 - self.db.level) * 200 + 5000
        if self.fill_time == 0:
            if self.place.place == "Заправка":
                self.db.fuel += 1
                if self.db.fuel < 6:
                    self.fill_time = FPS
                else:
                    self.fill_time = -1
            else:
                self.fill_time = -1
        if self.sec - abs(speed) >= 0:
            self.sec -= abs(speed)
        else:
            self.db.fuel -= 1
            self.sec = (10 - self.db.level) * 200 + 5000

    def draw(self, screen):
        screen.blit(self.sign, (300, 710))
        for i in range(self.db.fuel):
            screen.blit(self.lines[i // 2], (220, 765 - i * 15))


class Place:
    def __init__(self, camera_func):
        self.camera_func, self.fine = camera_func, False
        self.intro = pygame.font.Font(font_intro, 60)
        self.text = self.intro.render("", True, "white")
        self.place, self.x, self.y = "", 0, -50

    def update(self, position, place):
        for i, j in place.keys():
            if i < position < j:
                if place[i, j] == "Камера":
                    if not self.fine:
                        self.fine = self.camera_func()
                else:
                    self.fine = False
                    self.x = position - (i + j) // 2
                    self.place = place[i, j]
                    args = self.place, True, "white"
                    self.text = self.intro.render(*args)
                    return
        self.place = ""

    def draw(self, screen):
        if self.place and self.y < 20:
            self.y += 4
        elif not self.place and self.y > -60:
            self.y -= 4
        x = 0.4 * self.x + (WIDTH - self.text.get_width()) // 2
        screen.blit(self.text, (x, self.y))


class Display:
    def __init__(self):
        self.background = load_scaled_image('display/phone.png', (267, 130))
        self.wire = load_scaled_image('display/wire.png', (119, 100))
        self.arrow = load_scaled_image('display/arrow.png', (30, 30))
        self.display = pygame.surface.Surface((220, 110))
        self.display.fill("#111120")
        self.intro = pygame.font.Font(font_intro, 30)
        self.small = pygame.font.Font(font_intro, 25)
        self.place = pygame.surface.Surface((0, 0))
        self.meters = pygame.surface.Surface((0, 0))
        self.x, self.right = 0, False

    def set_place(self, place):
        (place, self.x), size = place, 30
        while True:
            font = pygame.font.Font(font_intro, size)
            text = font.render(place, True, "white")
            if text.get_width() < 185:
                self.place = text
                break
            size -= 1

    def update(self, position):
        if self.place.get_width() == 0:
            return
        meters = round(round((self.x - position) * 0.05, -1))
        if meters > 0 and self.right or meters < 0 and not self.right:
            self.arrow = pygame.transform.flip(self.arrow, True, False)
            self.right = not self.right
        self.meters = self.intro.render(f"{abs(meters)} м", True, "white")

    def draw(self, screen):
        screen.blit(self.wire, (679, 722))
        screen.blit(self.display, (450, 675))
        screen.blit(self.background, (430, 665))
        screen.blit(self.place, (470, 695))
        y = 700 + self.place.get_height()
        if self.place.get_width() > 0:
            screen.blit(self.arrow, (470, y - 2))
        screen.blit(self.meters, (510, y))


class Radio:
    def __init__(self):
        self.font = pygame.font.Font(font_lcd, 30)
        self.play = load_scaled_image('radio/play.png', (40, 45))
        self.pause = load_scaled_image('radio/pause.png', (40, 45))
        self.next = load_scaled_image('radio/next.png', (50, 60))
        background = 'radio/background.png', (570, 130)
        self.background = load_scaled_image(*background)
        self.music = self.font.render("", True, "black")
        self.radio = self.font.render("", True, "black")
        self.music_x, self.radio_x = 0, 0

    def update(self, name, radio):
        self.music = self.font.render(name, True, "black")
        self.radio = self.font.render(radio, True, "black")
        self.music_x = 1027 - self.music.get_width() // 2
        self.radio_x = 1027 - self.radio.get_width() // 2

    def draw(self, screen):
        screen.blit(self.background, (820, 665))
        screen.blit(self.music, (self.music_x, 690))
        screen.blit(self.radio, (self.radio_x, 730))
        screen.blit(self.pause, (1240, 709))
        screen.blit(self.next, (1305, 702))
