import pygame

from config import WIDTH, HEIGHT, DATABASE_NAME, WINDOW_TITLE, FPS
from city import StartScreen, FirstCity, Taxi
from database import Database


if __name__ == '__main__':
    pygame.init()
    size = WIDTH, HEIGHT
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption(WINDOW_TITLE)
    db = Database(DATABASE_NAME)
    clock = pygame.time.Clock()
    city = FirstCity(screen, db)
    # city = StartScreen(screen)
    action, running = 0, True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if type(city) == FirstCity:
                    if city.ending.end and city.ending.alpha > 255:
                        if event.key in (pygame.K_SPACE, pygame.K_KP_ENTER):
                            city = StartScreen(screen)
                    else:
                        if event.key == pygame.K_s:
                            city.taxi.change_line(Taxi.FORWARD)
                        if event.key == pygame.K_w:
                            city.taxi.change_line(Taxi.BACKWARD)
                        if event.key == pygame.K_a:
                            action = -1
                        if event.key == pygame.K_d:
                            action = 1
                        if event.key == pygame.K_SPACE:
                            action = -2
                        if event.key == pygame.K_q:
                            print(city.position)
                elif type(city) == StartScreen:
                    city = FirstCity(screen, db)
            if event.type == pygame.MOUSEBUTTONDOWN \
                    and event.button in (1, 3):
                if type(city) == StartScreen:
                    city = FirstCity(screen, db)
                elif type(city) == FirstCity and city.ending.end:
                    city = StartScreen(screen)
            if type(city) == FirstCity and event.type == pygame.KEYUP:
                if (event.key == pygame.K_a and action == -1 or
                        event.key == pygame.K_d and action == 1
                        or event.key == pygame.K_SPACE):
                    action = 0
            if event.type == pygame.QUIT:
                db.save()
                running = False
        time = clock.tick(FPS)
        if type(city) == FirstCity and not city.paused:
            city.taxi.move(action, time)
        city.render()
        pygame.display.flip()
    pygame.quit()
