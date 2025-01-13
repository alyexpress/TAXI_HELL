import pygame

from config import WIDTH, HEIGHT, WINDOW_TITLE, FPS
from database import Database
from city import FirstCity, Taxi
# db = Database(DATABASE_NAME)

if __name__ == '__main__':
    pygame.init()
    size = WIDTH, HEIGHT
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()
    city = FirstCity(screen)
    action = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
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
            if event.type == pygame.KEYUP:
                if (event.key == pygame.K_a and action == -1 or
                        event.key == pygame.K_d and action == 1
                        or event.key == pygame.K_SPACE):
                    action = 0
            if event.type == pygame.QUIT:
                # db.close()
                running = False
        time = clock.tick(FPS)
        if not city.paused:
            city.taxi.move(action, time)
        city.render()
        pygame.display.flip()
    pygame.quit()
