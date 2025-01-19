import pygame
import sys
import os

pygame.init()

size = width, height = 1400, 800
screen = pygame.display.set_mode((width, height))


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# звезда
star = pygame.image.load('data/star.png')
star = pygame.transform.scale(star, (50, 50))

# топливо
fuel = pygame.image.load('data/fuel.png')
fuel = pygame.transform.scale(fuel, (300, 200))

point = pygame.image.load('data/point.png')
point = pygame.transform.scale(point, (150, 150))

arrow = pygame.image.load('data/arrow.png')
arrow = pygame.transform.scale(arrow, (250, 250))

# радио

radio_screen = pygame.image.load('data/background.png')
radio_screen = pygame.transform.scale(radio_screen, (600, 200))


def rating(message):
    font = pygame.font.Font(None, 50)
    text = font.render(message, True, "black")
    screen.blit(text, (70, 25))


def speedometer(speed):
    font = pygame.font.Font(None, 200)
    text = font.render(speed, True, "black")
    screen.blit(text, (10, 650))


def balance(summa):
    font = pygame.font.Font(None, 50)
    text = font.render(summa, True, "white")
    screen.blit(text, (1280, 10))


def radio(channel, song):
    font = pygame.font.Font(None, 50)
    text = font.render(channel, True, "black")
    text = pygame.transform.scale(text, (370, 40))
    screen.blit(text, (965, 620))

    font = pygame.font.Font(None, 40)
    text = font.render(song, True, "black")
    screen.blit(text, (1025, 660))


def places(place):
    font = pygame.font.Font(None, 70)
    text = font.render(place, True, "black")
    screen.blit(text, (500, 650))


running = True
if __name__ == '__main__':
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))

        pygame.draw.polygon(screen, (250, 250, 220), [(0, 0), (300, 0), (0, 120)])
        pygame.draw.rect(screen, (250, 250, 220), (0, 600, 1400, 800))

        # картинки
        screen.blit(star, (10, 10))

        screen.blit(fuel, (220, 600))
        screen.blit(arrow, (225, 535))
        screen.blit(point, (295, 595))

        screen.blit(radio_screen, (845, 600))

        # ф-ции
        rating("| 5.0")
        speedometer('50')
        balance('2000$')
        radio('Название радио', 'Название песни')
        places('Название места')

        font = pygame.font.Font(None, 70)
        text = font.render('км', True, "black")
        screen.blit(text, (180, 650))

        font = pygame.font.Font(None, 70)
        text = font.render('_', True, "black")
        text = pygame.transform.scale(text, (60, 50))
        screen.blit(text, (180, 650))

        font = pygame.font.Font(None, 70)
        text = font.render('ч', True, "black")
        screen.blit(text, (195, 700))

        pygame.display.flip()
    pygame.quit()
