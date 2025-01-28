import pygame

from config import WIDTH, HEIGHT, WINDOW_TITLE, \
                    ICON, UI_DIR, DATABASE_NAME, FPS
from city import StartScreen, FirstCity, Taxi, load_image
from database import Database


if __name__ == '__main__':
    pygame.init()
    size = WIDTH, HEIGHT
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption(WINDOW_TITLE)
    pygame.display.set_icon(load_image(ICON, UI_DIR))
    db = Database(DATABASE_NAME)
    clock = pygame.time.Clock()
    # city = FirstCity(screen, db)
    city = StartScreen(screen)
    MUSIC_END = pygame.USEREVENT
    pygame.mixer.music.set_endevent(MUSIC_END)
    action, running = 0, True
    actions = {pygame.K_a: -1, pygame.K_d: 1, pygame.K_SPACE: -2}
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if type(city) == FirstCity:
                    if city.ending.end and city.ending.alpha > 255:
                        if event.key in (pygame.K_SPACE, pygame.K_KP_ENTER):
                            city = StartScreen(screen)
                    else:
                        if city.taxi.acceleration >= 0:
                            if event.key == pygame.K_s:
                                city.taxi.change_line(Taxi.FORWARD)
                            if event.key == pygame.K_w:
                                city.taxi.change_line(Taxi.BACKWARD)
                        if event.key in actions.keys():
                            action = actions[event.key]
                        if event.key == pygame.K_e:
                            if city.place.place == "Заправка":
                                city.fuel.refill()
                        if event.key == pygame.K_q:
                            city.music.dialog()
                elif type(city) == StartScreen:
                    city.music.stop()
                    city = FirstCity(screen, db)
            if event.type == pygame.MOUSEBUTTONDOWN \
                    and event.button in (1, 3):
                if type(city) == StartScreen:
                    city.music.stop()
                    city = FirstCity(screen, db)
                elif type(city) == FirstCity:
                    if city.ending.end:
                        city.music.stop()
                        city = StartScreen(screen)
                    else:
                        if 1240 < event.pos[0] < 1280 and \
                                710 < event.pos[1] < 755:
                            city.music.pause()
                            city.radio.paused = city.music.paused
                        elif 1300 < event.pos[0] < 1355 and \
                                715 < event.pos[1] < 750:
                            city.music.next()
                            city.radio.update(*city.music.get())
            if type(city) == FirstCity and event.type == pygame.KEYUP:
                if (event.key == pygame.K_a and action == -1 or
                        event.key == pygame.K_d and action == 1
                        or event.key == pygame.K_SPACE):
                    action = 0
            if event.type == MUSIC_END and not city.music.stopped:
                city.music.next()
                if type(city) == FirstCity:
                    city.radio.update(*city.music.get())
            if event.type == pygame.QUIT:
                city.music.stop()
                db.save()
                running = False
        time = clock.tick(FPS)
        if type(city) == FirstCity and not city.paused:
            city.taxi.move(action, time)
        city.render()
        pygame.display.flip()
    pygame.quit()
