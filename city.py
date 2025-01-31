import pygame.sprite

from objects import *
from music import *
from ui import *


class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        self.sky = load_image("sky.jpg")
        self.black = pygame.Surface((WIDTH, HEIGHT))
        self.black.fill("black"), self.black.set_alpha(90)
        self.taxi = pygame.sprite.Group()
        GameObject("taxi.png", 300, (0, 105), self.taxi)
        self.road, self.position = Road(), 0
        self.intro = pygame.font.Font(font_intro, 200)
        self.small = pygame.font.Font(font_intro, 70)
        self.team = pygame.font.Font(font_intro, 30)
        self.music = Music({"start.mp3": ("", "")})
        self.music.play()

    def render(self):
        self.position -= 1
        self.road.update(self.position)
        self.screen.blit(self.sky, (0, 0))
        self.screen.blit(self.black, (0, 0))
        self.road.draw(self.screen)
        self.taxi.draw(self.screen)
        self.screen.blit(self.black, (0, 0))
        text_render(self.screen, "TAXI", self.intro, "orange", (220, -100))
        text_render(self.screen, "HELL", self.intro, "red", (720, -100))
        text, team = "(Press any key to start)", "©ALYEXPRESS™"
        text_render(self.screen, text, self.small, "white", (320, 220))
        text_render(self.screen, team, self.team, "gray", (10, 730))


class City:
    def __init__(self, screen, db, taxi: Taxi):
        self.screen, self.db, self.taxi = screen, db, taxi
        self.sky = pygame.Surface((1400, 800))
        self.sky.fill("blue")
        self.length = [-5500, 5000]
        self.position = 0
        self.parallax = 3
        self.paused = False
        self.road, self.zebra = Road(), None
        self.on_road = pygame.sprite.Group()
        self.front = pygame.sprite.Group()
        self.background = pygame.sprite.Group()
        self.right_cars = right = pygame.sprite.Group()
        self.left_cars = left = pygame.sprite.Group()
        self.car_control = CarController(right, left)
        self.ending, self.fine = Ending(), Fine()
        # Init UI
        self.place, self.places = Place(self.check_camera), {}
        self.rating, self.counter = Rating(self), Counter(self)
        self.speedometer, self.fuel = Speedometer(), Fuel(self)
        self.display, self.radio = Display(), Radio()
        # Game control
        self.game_control = GameControl(self)
        # Init Music
        self.songs = {
            "central.mp3": ("Владимирский централ", "Михаил Круг"),
            "pobaram.mp3": ("По барам", "ANNA ASTI"),
            "sochi.mp3": ("Город Сочи", "Трофимов Сергей"),
            "nazare.mp3": ("На заре", "Альянс")
        }
        self.music = Music(self.songs)
        self.music.play()
        self.radio.update(*self.music.get())

    def set_position(self, speed):
        # road borders
        if (self.length[0] < self.position < self.length[1]
                and self.taxi.rect.x == self.taxi.center):
            self.position += speed
            if self.position > self.length[1]:
                self.position = self.length[1]
            elif self.position < self.length[0]:
                self.position = self.length[0]
        elif (self.length[0] + speed > self.position and
                self.taxi.rect.x + speed < self.taxi.center) \
                or (self.length[1] + speed < self.position and
                self.taxi.rect.x + speed > self.taxi.center):
            self.taxi.rect.x = self.taxi.center
            self.position += speed
        else:
            self.taxi.rect.x -= speed
        if not self.paused:
            self.game_control.update()
            self.set_ambient_position()
            self.check_fuel()
            self.car_generation()
            self.check_collisions()

    def set_ambient_position(self):
        self.road.update(self.position)
        self.zebra.update(self.position)
        self.background.update(self.position / self.parallax)
        self.on_road.update(self.position)
        self.right_cars.update(self.position)
        self.left_cars.update(self.position)
        self.taxi.update(self.position)
        # UI updating
        self.speedometer.update(self.taxi.speed)
        self.fuel.update(self.taxi.speed)
        self.place.update(self.position, self.places)
        self.display.update(self.position)
        self.counter.update()

    def check_fuel(self):
        if self.db.fuel == 0:
            self.taxi.acceleration = -self.taxi.auto_brake
            if self.taxi.speed == 0 and \
                    self.place.place != "Заправка":
                self.music.game_over(Music.NO_FUEL)
                self.ending.end, self.paused = 4, True
                self.db.clear()
            if abs(self.taxi.speed) < 0.1:
                self.taxi.acceleration = 0
    def car_generation(self):
        count = len(self.left_cars) + len(self.right_cars)
        if abs(self.taxi.speed) > 1 and count < 2:
            line = 1 if len(self.left_cars) > len(self.right_cars) else 0
            position = WIDTH if self.taxi.speed < 0 else -WIDTH
            self.car_control.generate(line, position - self.position)

    def check_collisions(self):
        if type(self.zebra) is Zebra and self.zebra.active is not None:
            person = self.zebra.active
            if (person.line in (1, 2) and
                pygame.sprite.collide_mask(person, self.taxi)):
                if abs(self.taxi.speed) < 3:
                    person.around(self.taxi)
                elif (person.line == 1 and self.taxi.go_backward in (3, 4)
                        or person.line == 2 and
                        self.taxi.go_forward in (3, 4)):
                    if not person_side_collision(person, self.taxi):
                        self.front.remove(person)
                        person.around(self.taxi, self.taxi.speed > 0)
                    elif not person.death:
                        self.music.game_over(Music.CRASH)
                        self.front.add(person)
                        person.speed = -self.taxi.speed * 2
                        self.taxi.speed /= 3
                        self.taxi.acceleration = 0
                        person.death, self.ending.end = True, 1
                        self.db.clear()
        if self.zebra.traffic.queue[self.zebra.traffic.color] != 2:
            args = self.zebra, self.right_cars, self.left_cars
            self.car_control.stop(zebra_collision(*args), self.zebra)
        if self.zebra.traffic.color in (1, 2) and self.car_control.stopped:
            self.car_control.drive()
        group = self.right_cars if self.taxi.right else self.left_cars
        car = pygame.sprite.spritecollideany(self.taxi.collider, group)
        if car is not None:
            car.braked = True
        for group in (self.right_cars, self.left_cars):
            if len(group) > 0:
                car = group.sprites()[0]
                if car.speed == 10:
                    break
                if ((car.right and self.taxi.go_forward in (2, 3, 4) or
                        not car.right and self.taxi.go_backward in (2, 3, 4))
                        and pygame.sprite.collide_mask(car, self.taxi)):
                    car.stop, self.taxi.speed = True, 0
                    if car.right != self.taxi.right:
                        self.music.game_over(Music.CRASH)
                        car.speed, self.ending.end = 0, 2
                        self.paused = True
                        self.db.clear()
                    else:
                        self.car_control.object = car
                        if car in self.car_control.stopped:
                            self.car_control.stopped.remove(car)
                        self.taxi.acceleration = 0
                        self.fine.show = True

    def check_camera(self):
        if abs(self.taxi.speed * 8.9) > 60:
            if self.db.money >= 20:
                self.db.money -= 20
            else:
                self.music.game_over(Music.CRYING)
                self.ending.end = 3
                self.db.clear()
            return True
        return False

    def pay_fine(self):
        self.car_control.object.stop = False
        self.car_control.object.speed = 10
        if self.db.money >= 100:
            self.db.money -= 100
            self.fine.show = False
            self.taxi.acceleration = 4
        else:
            self.music.game_over(Music.CRYING)
            self.ending.end = 3
            self.db.clear()

    def render(self):
        if self.ending.alpha < 255:
            self.screen.blit(self.sky, (0, 0))
            self.set_position(self.taxi.speed)
            self.place.draw(self.screen)
            self.background.draw(self.screen)
            self.road.draw(self.screen)
            self.zebra.draw(self.screen)
            self.on_road.draw(self.screen)
            self.left_cars.draw(self.screen)
            if self.taxi.go_forward == 4:
                self.right_cars.draw(self.screen)
                self.taxi.draw(self.screen)
            elif self.taxi.go_backward == 4:
                self.taxi.draw(self.screen)
                self.right_cars.draw(self.screen)
            self.front.draw(self.screen)
            #DEL
            # s = pygame.Surface((self.taxi.collider.width,
            #                     self.taxi.collider.height))
            # s.fill("green")
            # s.set_alpha(100)
            # self.screen.blit(s, (self.taxi.collider.rect.x,
            #                      self.taxi.collider.rect.y))
            # Render UI
            self.rating.draw(self.screen)
            self.counter.draw(self.screen)
            self.speedometer.draw(self.screen)
            self.fuel.draw(self.screen)
            self.display.draw(self.screen)
            self.radio.draw(self.screen)
            self.fine.draw(self.screen)
        # Ending render
        self.ending.render(self.screen)


class FirstCity(City):
    def __init__(self, screen: pygame.surface.Surface, db):
        super().__init__(screen, db, Taxi("taxi.png", 300, (0, 105)))
        self.sky = load_image("sky.jpg")
        # Places setting
        self.places = {(4700, 5001): "Личный Дом",
                       (3350, 4150): "Колледж",
                       (2000, 2800): "Магазин",
                       (125, 1325): "Бизнес центр",
                       (-2050, -900): "Заправка",
                       (-3300, -2850): "Камера",
                       (-4500, -3300): "Станция",
                       (-5501, -5490): "Ферма"}
        self.route = {v: sum(k) // 2 for k, v in self.places.items()
                      if v not in ("Заправка", "Камера")}
        # Ambient setting
        GameObject("signs/stop.png", 150, (-5550, 15), self.on_road)
        GameObject("build/college.png", 400, (-1250, -15), self.background)
        GameObject("build/home.png", 700, (-1800, -60), self.background)
        GameObject("build/shop.png", 400, (-850, -15), self.background)
        GameObject("build/business.png", 750, (-250, -100), self.background)
        GameObject("build/gas.png", 750, (550, -55), self.background)
        GameObject("build/station.png", 800, (1300, -80), self.background)
        GameObject("build/farm.png", 600, (2050, 0), self.background)
        self.position = 4700
        # Camera setting
        GameObject("signs/camera.png", 200, (2800, -10), self.on_road)
        GameObject("signs/sixty.png", 150, (2000, 15), self.on_road)
        GameObject("signs/sixty.png", 150, (4000, 15), self.on_road)
        # Zebra setting
        zebra = self.zebra = Zebra(-1500, self.on_road)
        Person("pers/cartman.png", 80, (35, 56), self.front, zebra)
        Person("pers/kyle.png", 75, (50, 56), self.front, zebra, speed=0.6)
        Person("pers/stan.png", 80, (50, 55), self.front, zebra, speed=0.6)
        Person("pers/kenny.png", 75, (50, 56), self.front, zebra, speed=0.7)
        GameObject("signs/person.png", 150, (-850, 17), self.on_road)
        GameObject("signs/person.png", 150, (-2000, 17), self.on_road)
        # Cars setting
        self.car_control.add("cars/red_car.png", 290, (-300, 180))
        self.car_control.add("cars/white_car.png", 280, (-300, 185))
        self.car_control.add("cars/blue_car.png", 290, (-300, 180))
        self.car_control.add("cars/black_car.png", 290, (-300, 180))
        self.car_control.add("cars/gray_car.png", 300, (-300, 180))
        # Car setting (for testing)
        # car = Car("cars/red_car.png", 290, (-300, 180),
        #           self.right_cars, clone=True)
        # car.rect.x, car.speed = WIDTH / 2, 0
