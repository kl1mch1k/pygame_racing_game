import os
import sys

import pygame
from math import sin, cos, radians

pygame.init()
size = WIDTH, HEIGHT = 1600, 900
FPS = 60
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
car_sprites = pygame.sprite.Group()
clock = pygame.time.Clock()


class Vector:
    def __init__(self, length, angle):
        self.x = sin(radians(angle)) * length
        self.y = cos(radians(angle)) * length
        self.length = length
        self.angle = angle

    def rotate(self, angle):
        self.__init__(self.length, self.angle + angle)

    def __iadd__(self, other):
        return Vector(self.length + other, self.angle)

    def __imul__(self, other):
        return Vector(self.length * other, self.angle)



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


def terminate():
    pygame.quit()
    sys.exit()

class OutTrack(pygame.sprite.Sprite):
    image = load_image("grass.png")

    def __init__(self):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(OutTrack.image, (3200, 3200))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        pygame.mask.Mask.invert(self.mask)

class Track(pygame.sprite.Sprite):
    def __init__(self, image_name, start_pos):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(load_image(image_name), (3200, 3200))
        self.start_pos = start_pos
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        pygame.mask.Mask.invert(self.mask)


class Car(pygame.sprite.Sprite):
    image = load_image('car.png')

    def __init__(self, pos, acceleration = 1, turnability = 3, max_speed = 20, inertion = 0.5):
        super().__init__(all_sprites, car_sprites)
        self.vec = Vector(0, 90)
        self.acceleration = acceleration
        self.inertion = inertion
        self.turnability = turnability
        self.max_speed = max_speed
        self.image = pygame.transform.rotate(Car.image, self.vec.angle)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(*pos)

    def update(self, args):
        if args:
            if args[pygame.K_UP] and self.vec.length > -self.max_speed:
                self.vec += -self.acceleration
            if args[pygame.K_DOWN] and self.vec.length < self.max_speed:
                self.vec += self.acceleration
            if args[pygame.K_LEFT]:
                self.vec.rotate(self.turnability)
                self.image = pygame.transform.rotate(Car.image, self.vec.angle)
            if args[pygame.K_RIGHT]:
                self.vec.rotate(-self.turnability)
                self.image = pygame.transform.rotate(Car.image, self.vec.angle)
            self.rect = self.image.get_rect(center=self.rect.center).move((self.vec.x, self.vec.y))
            if self.vec.length < 0:
                self.vec += self.inertion
            if self.vec.length > 0:
                self.vec += -self.inertion


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


def start_screen():
    grass = OutTrack()
    track = Track('tr.png', (1600, 300))
    borders = pygame.sprite.Group()
    borders.add()
    car = Car(track.start_pos, max_speed=15)
    camera = Camera()

    while True:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        if pygame.sprite.collide_mask(car, grass):
            car.vec += -car.max_speed * (car.vec.length // abs(car.vec.length))
        if pygame.sprite.collide_mask(car, track):
            car.vec *= 0.5

        car.update(pygame.key.get_pressed())

        camera.update(car)
        for sprite in all_sprites:
            camera.apply(sprite)

        all_sprites.draw(screen)

        # debug info showing
        for sprite in car_sprites:
            screen.fill((255, 255, 0), (sprite.rect.centerx - 2, sprite.rect.centery - 2, 4, 4))
            pygame.draw.rect(screen, (255, 0, 0), sprite.rect, width=1)
        pygame.draw.line(screen, (255, 0, 0), (50, 50), (50 + car.vec.x * 1.5, 50 + car.vec.y * 1.5), width=2)
        font1 = pygame.font.Font(None, 25)
        text1 = font1.render(str(track.rect.center), True, (255, 0, 0))
        textRect1 = text1.get_rect()
        textRect1.center = (50, 500)
        screen.blit(text1, textRect1)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    start_screen()
