from random import randint, choice, sample
from config import WIDTH, HEIGHT, FPS
from options import *


class GameControl:
    def __init__(self, city):
        self.city, self.step = city, 0
        self.duration = randint(2, 10) * FPS
        self.start, self.finish = None, None
        self.cost = 0

    def order_generate(self):
        route = list(self.city.route.items())
        self.start, self.finish = sample(route, 2)
        distance = abs(self.start[1] - self.finish[1])
        self.cost = round(distance * (50 / 11000))

    def update(self):
        if self.step == 0:  # Without work
            if self.duration:
                self.duration -= 1
            else:
                self.order_generate()
                print(self.start, self.finish, self.cost)
                self.city.display.set_place(self.start)
                self.step = 1
        elif self.step == 1:  # Accepted order
            if (self.city.place.place == self.start[0]
                    and abs(self.city.taxi.speed) < 1):
                self.city.display.set_place(self.finish)
                self.step = 2
        elif self.step == 2:  # Take the pers
            if (self.city.place.place == self.finish[0]
                    and abs(self.city.taxi.speed) < 1):
                self.city.display.place = pygame.surface.Surface((0, 0))
                self.city.display.meters = pygame.surface.Surface((0, 0))
                self.step = 3
        elif self.step == 3:  # Good job
            self.city.db.money += self.cost
            self.duration = randint(2, 10) * FPS
            self.step = 0


class GameObject(pygame.sprite.Sprite):
    def __init__(self, image, size=None, cords=(0, 0), group=None):
        self.image = load_image(image)
        if size is not None:
            if type(size) is int:
                w, h = self.image.get_size()
                if w > h:
                    size = [size, round(size / w * h)]
                else:
                    size = [round(size / h * w), size]
            alpha = self.image.convert_alpha()
            self.image = pygame.transform.smoothscale(alpha, size)
        self.x = cords[0] + (WIDTH - self.image.get_width()) // 2
        self.y = cords[1] + (HEIGHT - self.image.get_height()) // 2
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.x, self.y
        super().__init__(*[] if group is None else [group])

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self, x):
        self.rect.x = self.x + x


class Collider(pygame.sprite.Sprite):
    def __init__(self, *size):
        super().__init__()
        self.width, self.height = size
        self.rect = pygame.Rect(0, 0, *size)

    def update(self, x, y):
        self.rect.x, self.rect.y = x, y


class Car(GameObject):
    def __init__(self, image, size=None, cords=(0, 0),
                 group=None, right=True, clone=False, **kwargs):
        super().__init__(image, size, cords, group if clone else None)
        self.max_speed = kwargs.get('speed', 4)
        self.speed, self.brake = self.max_speed, 0.1
        self.right, self.rect.x = right, WIDTH
        self.stop, self.braked = False, False
        if not clone:
            self.args = image, size, cords, group
            self.rect.y = HEIGHT
        if not right:
            self.image = pygame.transform.flip(self.image, True, False)
        self.mask = pygame.mask.from_surface(self.image)

    def generate(self, position=None):
        args = list(self.args)
        if position is not None:
            args[2] = position, args[2][1]
        return Car(*args, self.right, True)

    def update(self, position):
        if (self.stop or self.braked) and self.speed > 0:
            self.speed -= self.brake
            if self.speed < 0:
                self.speed = 0
        elif not (self.stop or self.braked) and self.speed < self.max_speed:
            self.speed += self.brake / 2
        self.braked = False
        speed = round(self.rect.x - self.x - position)
        if self.rect.y != HEIGHT:
            self.x += self.speed if self.right else -self.speed
        super().update(position)
        if ((speed <= 0 and self.rect.x > 2 * WIDTH or
                speed >= 0 and self.rect.x < -WIDTH)
                and self.rect.y != HEIGHT):
            self.kill()
            del self


class CarController:
    def __init__(self, right_group, left_group):
        self.right_group = right_group
        self.left_group = left_group
        self.right_models: [Car] = []
        self.left_models: [Car] = []
        self.stopped, self.red = [], False

    def stop(self, cars, zebra):
        for car in cars:
            if car not in self.stopped:
                if (car.right and car.rect.x + car.rect.width - car.max_speed
                        <= zebra.rect.x or not car.right and car.rect.x +
                        car.max_speed >= zebra.rect.x + zebra.rect.width):
                    self.stopped.append(car)
                    car.stop = True

    def drive(self):
        for car in self.stopped:
            car.stop = False
        self.stopped = []

    def add(self, image, size=None, cords=(0, 0)):
        right = Car(image, size, cords, self.right_group, True)
        cords = (cords[0], cords[1] - 80)
        left = Car(image, size, cords, self.left_group, False)
        self.right_models.append(right)
        self.left_models.append(left)

    def generate(self, line, position):
        models = self.right_models if line else self.left_models
        choice(models).generate(position)


class Taxi(GameObject):
    FORWARD = 2
    BACKWARD = 1

    def __init__(self, image, size=None, cords=(0, 0),
                 group=None, right=True, **kwargs):
        super().__init__(image, size, cords, group)
        self.acceleration = kwargs.get('acceleration', 4)
        self.max_speed = kwargs.get('max_speed', 8.5)
        self.brake = kwargs.get('brake', 11)
        self.auto_brake = kwargs.get('auto_brake', 2)
        self.right, self.speed = right, 0
        self.go_forward, self.go_backward = 0, 3
        self.degree, self.y_offset = 0, 20
        self.img, self.go_turn = self.image.copy(), False
        self.mask = pygame.mask.from_surface(self.img)
        self.flip_img = pygame.transform.flip(self.img, 1, 0)
        self.center = (WIDTH - self.img.get_width()) // 2
        self.collider = Collider(100, 30)

    def get_image(self):
        return self.img if self.right else self.flip_img

    def turn(self):
        if 0 in (self.go_forward, self.go_backward):
            self.right = not self.right
            self.image = self.get_image()
        else:
            self.go_turn = True

    def rotate(self, degree):
        self.degree += degree
        args = self.get_image(), self.degree, 1
        self.image = pygame.transform.rotozoom(*args)

    def change_line(self, line):
        if line == Taxi.FORWARD and self.go_forward == 0:
            self.go_forward = 1
        elif line == Taxi.BACKWARD and self.go_backward == 0:
            self.go_backward = 1

    def move(self, action, time):
        # speed control
        t = time / 1000
        if action == 1:
            if self.right:
                if -self.speed < self.max_speed:
                    self.speed -= self.acceleration * t
            else:
                if self.speed <= 0:
                    self.turn()
                else:
                    self.speed -= self.brake * t
        elif action == -1:
            if not self.right:
                if self.speed < self.max_speed:
                    self.speed += self.acceleration * t
            else:
                if self.speed >= 0:
                    self.turn()
                else:
                    self.speed += self.brake * t
        elif action in (0, -2):
            brake_force = self.brake if action else self.auto_brake
            if self.speed > self.auto_brake * t:
                self.speed -= brake_force * t
            elif self.speed < -self.auto_brake * t:
                self.speed += brake_force * t
            else:
                self.speed = 0

    def update(self, position):
        # update colliders
        offset = -self.collider.width if self.right else self.rect.width
        self.collider.update(self.rect.x + offset, self.rect.y + 30)
        # animations (Forward/Backward)
        deg, y = 1, 2
        if self.go_forward:
            if self.go_forward == 1:
                if (self.right and self.degree > -10 or
                        not self.right and self.degree < 10):
                    self.rotate(-deg if self.right else deg)
                else:
                    self.go_forward = 2
            if self.go_forward == 2:
                if self.y_offset:
                    self.y_offset -= y
                    self.rect.y += 2 * y
                else:
                    self.y_offset, self.go_forward = 20, 3
            if self.go_forward == 3:
                if (self.right and self.degree < 0 or
                        not self.right and self.degree > 0):
                    self.rect.y += 2 * y
                    self.rotate(deg if self.right else -deg)
                else:
                    self.go_forward, self.go_backward = 4, 0
                    if self.go_turn:
                        self.go_turn = False
                        self.turn()
                    self.image = self.get_image()
        if self.go_backward:
            if self.go_backward == 1:
                if (self.right and self.degree < 10 or
                        not self.right and self.degree > -10):
                    self.rect.y -= 2 * y
                    self.rotate(deg if self.right else -deg)
                else:
                    self.go_backward = 2
            if self.go_backward == 2:
                if self.y_offset:
                    self.y_offset -= y
                    self.rect.y -= 2 * y
                else:
                    self.y_offset, self.go_backward = 20, 3
            if self.go_backward == 3:
                if (self.right and self.degree > 0 or
                        not self.right and self.degree < 0):
                    self.rotate(-deg if self.right else deg)
                else:
                    self.go_backward, self.go_forward = 4, 0
                    if self.go_turn:
                        self.go_turn = False
                        self.turn()
                    self.image = self.get_image()


class Road:
    def __init__(self):
        self.position = 0

    def update(self, position):
        self.position = position

    def draw(self, screen):
        pygame.draw.rect(screen, "#999999", ((0, 490), (WIDTH, 5)))
        pygame.draw.rect(screen, "#333333", ((0, 500), (WIDTH, 400)))
        pygame.draw.rect(screen, "#666666", ((0, 495), (WIDTH, 10)))
        pygame.draw.rect(screen, "#999999", ((0, 640), (WIDTH, 5)))
        pygame.draw.rect(screen, "#666666", ((0, 645), (WIDTH, 10)))
        for i in range(round(self.position) % 100 - 100, WIDTH, 100):
            pygame.draw.line(screen, "#111111", (i, 490), (i - 5, 505), 2)
            pygame.draw.line(screen, "#111111", (i, 640), (i - 5, 655), 2)
            pygame.draw.rect(screen, "#aa5500", ((i - 2, 560), (53, 10)))
            pygame.draw.rect(screen, "orange", ((i, 560), (50, 8)))
        pygame.draw.rect(screen, "#444444", ((0, 660), (WIDTH, 200)))


class Zebra:
    def __init__(self, x, group):
        self.x = x - 2 + WIDTH / 2
        self.cords, self.group = [self.x, 510], group
        self.rect = pygame.Rect(*self.cords, 350, 125)
        self.persons, self.active = [], None
        self.traffic = TrafficLight(50, (x + 150, 15), group)

    def update(self, x):
        self.cords[0] = self.x + x
        self.rect.x = self.cords[0] - 100
        if (self.active is None and self.persons
                and (-350 <= self.cords[0] <= -150 or
                WIDTH <= self.cords[0] <= WIDTH + 200)):
            index = randint(0, len(self.persons) - 1)
            self.active = self.persons[index].generate()

    def draw(self, screen):
        x, y = self.cords
        for i in range(4):
            rect = ((x - 1, y + 33 * i), (155, 27))
            pygame.draw.rect(screen, "gray", rect)
            rect = ((x, y + 33 * i), (153, 25))
            pygame.draw.rect(screen, "white", rect)


class TrafficLight(GameObject):
    def __init__(self, size=None, cords=(0, 0), group=None):
        super().__init__("signs/traffic_lights.png", 905, cords, group)
        self.during, self.queue = [4, 1, 5], [0, 1, 2, 1]
        size, self.time, self.color = (size, size / 285 * 900), 1, 0
        green = self.image.subsurface(((0, 0), (285, 900)))
        orange = self.image.subsurface(((308, 0), (285, 900)))
        red = self.image.subsurface(((619, 0), (285, 900)))
        self.images = [
            pygame.transform.smoothscale(red.convert_alpha(), size),
            pygame.transform.smoothscale(orange.convert_alpha(), size),
            pygame.transform.smoothscale(green.convert_alpha(), size)
        ]
        self.image = self.images[self.color]
        self.x = cords[0] + (WIDTH - self.image.get_width()) // 2
        self.y = cords[1] + (HEIGHT - self.image.get_height()) // 2
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.x, self.y

    def update(self, x):
        super().update(x)
        self.time -= 1
        if self.time == 0:
            self.color = (self.color + 1) % len(self.queue)
            index = self.queue[self.color]
            self.image = self.images[index]
            self.time = self.during[index] * FPS


class Person(GameObject):
    def __init__(self, image, size=None, cords=(0, 0),
                 front=None, zebra=None, **kwargs):
        super().__init__(image, size, cords, zebra.group)
        self.x = zebra.x + cords[0]
        self.args = image, size, cords
        self.zebra, self.front = zebra, front
        self.img, self.rect.y = self.image.copy(), HEIGHT
        self.mask = pygame.mask.from_surface(self.img)
        self.speed = kwargs.get('speed', 0.5)
        self.during = kwargs.get('during', 50)
        self.degree, self.right, self.death = 0, True, False
        self.bottom, self.line = self.y + 162, 0
        self.zebra.persons.append(self)

    def generate(self):
        clone = Person(*self.args, self.front, self.zebra)
        clone.speed = float(self.speed)
        clone.during = float(self.during)
        clone.rect.y = clone.y
        return clone

    def rotate(self, degree):
        self.degree += degree
        args = self.img, self.degree, 1
        self.image = pygame.transform.rotozoom(*args)

    def going(self):
        self.rotate(0.5 if self.right else -0.5)
        if abs(self.degree) >= 3:
            self.right = not self.right

    def around(self, car, right=None):
        if right is None:
            center = self.rect.x + self.rect.width // 2
            car_center = car.rect.x + car.rect.width // 2
            speed = 2 if person_side_collision(self, car) else 1
            self.x += speed if center > car_center else -speed
        else:
            self.x += self.speed if right else -self.speed
        self.y -= self.speed

    def update(self, x):
        self.rect.x = self.x + x
        if self.rect.y == HEIGHT:
            return
        if self.death:
            if abs(self.speed) > 0.2:
                self.x += self.speed
                self.rect.y += self.rect.height // 50
                self.rotate(-self.speed / 4)
                self.speed += 0.2 if self.speed < 0 else -0.2
            else:
                self.speed = 0
            return
        if self.line == 3:
            self.x += self.speed
            self.going()
        elif self.zebra.traffic.queue[self.zebra.traffic.color] == 0:
            if self.during > 0:
                self.during -= 1
            elif self.y >= self.bottom:
                self.line = 3
                self.front.add(self)
            else:
                if self.zebra.traffic.time == 1:
                    self.zebra.traffic.time += 1
                    self.y += 0.5
                self.y += self.speed
                self.rect.y = self.y
                self.going()
                if self.line == 0:
                    self.line = 1
                elif self.line == 1 and self.y > self.bottom - 81:
                    self.line = 2
                    self.front.add(self)
        if (not -self.image.get_width() <= self.rect.x <= WIDTH
                and self.line == 3):
            self.zebra.active = None
            self.kill()
            del self


class Ending:
    def __init__(self):
        self.end, self.alpha = 0, 0
        self.intro = pygame.font.Font(font_intro, 60)
        self.small_intro = pygame.font.Font(font_intro, 42)
        self.prisoner = GameObject('end/prisoner.png')
        self.grid = GameObject('end/grid.png')
        self.tombstone = GameObject('end/tombstone.png')
        self.prisoner.rect.x = 100
        self.grid.rect.y, self.grid.rect.x = -500, 110
        self.tombstone.rect.x, self.tombstone.rect.y = 50, -300

    def render(self, screen):
        header, text, position = "", "", 650
        if self.end != 0:  # Black screen
            self.alpha += 8 if self.alpha < 255 * 2 else 0
            surface = pygame.Surface((WIDTH, HEIGHT))
            surface.fill("black")
            surface.set_alpha(self.alpha if self.alpha < 255 else 255)
            screen.blit(surface, (0, 0))
            if self.alpha > 255:
                if self.end == 1:  # Person death
                    self.prisoner.image.set_alpha(self.alpha - 255)
                    self.prisoner.draw(screen)
                    self.grid.image.set_alpha(self.alpha - 255)
                    if self.grid.rect.y < 105:
                        self.grid.rect.y += 16
                    self.grid.draw(screen)
                    header = "ВЫ СБИЛИ ЧЕЛОВЕКА!"
                    text = """Пешеход скончался на месте.
На суде выяснилось, что вы\nсильно превысили скорость
и проехали на красный свет.\nРебёнка, которого вы сбили,
ждали дома родные, а он так\nи не вернулся... Суд приговорил
вас к 10 годам лишения свободы."""
                elif self.end == 2:  # Driver death
                    self.tombstone.image.set_alpha(self.alpha - 255)
                    self.tombstone.draw(screen)
                    if self.tombstone.rect.y < 105:
                        self.tombstone.rect.y += 14
                    position -= 110
                    header = "ВЫ РАЗБИЛСЬ НАСМЕРТЬ!"
                position1 = position + (255 * 2 - self.alpha) * 0.7
                position2 = position + (255 * 2 - self.alpha)
                text_render(screen, header, self.intro,
                            "red", (position1, 60), self.alpha - 255)
                text_render(screen, text, self.small_intro, "white",
                            (position2, 150), self.alpha - 255)
