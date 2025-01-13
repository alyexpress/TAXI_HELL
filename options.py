from config import SPRITES_DIR, SYSTEM_DIR

import pygame
import os


font_intro = os.path.join(SYSTEM_DIR, "Intro.ttf")


def load_image(filename, path=SPRITES_DIR):
    fullname = os.path.join(path, filename)
    if not os.path.isfile(fullname):
        raise FileExistsError(fullname)
    return pygame.image.load(fullname)


def person_side_collision(person, car):
    car_x, person_x = car.rect.x, person.rect.x
    if car.right:
        return car_x + car.rect.width <= person_x + 30
    else:
        return car_x >= person_x + person.rect.width - 30


def zebra_collision(zebra, right, left):
    right = pygame.sprite.spritecollideany(zebra, right)
    left = pygame.sprite.spritecollideany(zebra, left)
    return [car for car in (right, left) if car is not None]


def text_render(screen, text, font, color, cords, alpha=255):
    x, y = cords
    for line in text.split('\n'):
        text = font.render(line, True, color)
        text.set_alpha(alpha)
        y += font.get_height() + 5
        screen.blit(text, (x, y))