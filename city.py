import pygame.sprite

from objects import *
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
        text = "(Press any key to start)"
        text_render(self.screen, text, self.small, "white", (320, 220))
        team = "©ALYEXRESS™"
        text_render(self.screen, team, self.team, "gray", (10, 730))


class City:
    def __init__(self, screen, taxi: Taxi):
        self.screen = screen
        self.taxi = taxi
        self.sky = pygame.Surface((1400, 800))
        self.sky.fill("blue")
        self.length = [-6000, 5000]
        self.position = 0
        self.parallax = 3
        self.paused = False
        self.places = {}
        self.road, self.zebra = Road(), None
        self.on_road = pygame.sprite.Group()
        self.front = pygame.sprite.Group()
        self.background = pygame.sprite.Group()
        right = self.right_cars = pygame.sprite.Group()
        left = self.left_cars = pygame.sprite.Group()
        self.car_control = CarController(right, left)
        self.ending = Ending()
        # Init UI
        self.rating = Rating()
        self.counter = Counter()
        self.speedometer = Speedometer()
        self.fuel = Fuel()
        self.place = Place()

        #DEL
        self.info = None

    def set_position(self, speed):
        # road borders
        if (self.length[0] <= self.position + speed <= self.length[1]
                and self.taxi.rect.x == self.taxi.center):
            self.position += speed
        elif (self.length[0] + speed > self.position and
                self.taxi.rect.x + speed < self.taxi.center) \
                or (self.length[1] + speed < self.position and
                self.taxi.rect.x + speed > self.taxi.center):
            self.taxi.rect.x = self.taxi.center
        else:
            self.taxi.rect.x -= speed
        if not self.paused:
            self.set_ambient_position()
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
        self.place.update(self.position, self.places)

    def car_generation(self):
        count = len(self.left_cars) + len(self.right_cars)
        if abs(self.taxi.speed) > 1 and count < 2:
            line = 1 if len(self.left_cars) > len(self.right_cars) else 0
            position = WIDTH if self.taxi.speed < 0 else -WIDTH
            # self.car_control.generate(line, position - self.position)

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
                        self.front.add(person)
                        person.speed = -self.taxi.speed * 2
                        self.taxi.speed /= 3
                        self.taxi.acceleration = 0
                        person.death, self.ending.end = True, 1
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
                if ((car.right and self.taxi.go_forward in (2, 3, 4) or
                        not car.right and self.taxi.go_backward in (2, 3, 4))
                        and pygame.sprite.collide_mask(car, self.taxi)):
                    car.stop, self.taxi.speed = True, 0
                    if car.right != self.taxi.right:
                        car.speed, self.ending.end = 0, 2
                        self.paused = True

    def render(self):
        self.screen.blit(self.sky, (0, 0))
        self.set_position(self.taxi.speed)
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
        self.place.draw(self.screen)
        # Ending render
        self.ending.render(self.screen)


class FirstCity(City):
    def __init__(self, screen: pygame.surface.Surface):
        super().__init__(screen, Taxi("taxi.png", 300, (0, 105)))
        self.sky = load_image("sky.jpg")
        # Ambient setting
        self.places[400, 1000] = "Бизнес центр"
        GameObject("business.png", 600, (-250, -100), self.background)
        self.places[-1100, -400] = "Заправка"
        GameObject("gas.png", 500, (250, -15), self.background)
        GameObject("stop.png", 150, (-5550, 15), self.on_road)
        # Camera setting
        GameObject("camera.png", 200, (2800, -10), self.on_road)
        GameObject("sixty.png", 150, (2000, 15), self.on_road)
        GameObject("sixty.png", 150, (4000, 15), self.on_road)
        # Zebra setting
        zebra = self.zebra = Zebra(-1000, self.on_road)
        Person("cartman.png", 80, (35, 56), self.front, zebra)
        Person("kyle.png", 75, (50, 56), self.front, zebra, speed=0.6)
        Person("stan.png", 80, (50, 55), self.front, zebra, speed=0.6)
        Person("kenny2.png", 75, (50, 56), self.front, zebra, speed=0.7)
        GameObject("person_sign.png", 150, (-350, 17), self.on_road)
        GameObject("person_sign.png", 150, (-1500, 17), self.on_road)
        # Cars setting
        self.car_control.add("red_car.png", 290, (-300, 180))
        self.car_control.add("white_car.png", 280, (-300, 185))
        self.car_control.add("blue_car.png", 290, (-300, 180))
        self.car_control.add("black_car.png", 290, (-300, 180))
        self.car_control.add("gray_car.png", 300, (-300, 180))
        # Car setting (for testing)
        # car = Car("red_car.png", 290, (-300, 180),
        #           self.right_cars, clone=True)
        # car.rect.x, car.speed = WIDTH / 2, 0

    def render(self):
        super().render()
        info = self.info
        # info = self.info
        if info is not None:
            font = pygame.font.Font(None, 50)
            text = font.render(str(info), True, (255, 255, 255))
            self.screen.blit(text, (1200, 700))
