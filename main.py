import os
import sys

import pygame
from math import sin, cos, radians

pygame.init()
size = WIDTH, HEIGHT = 800, 600
FPS = 60
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
car_sprites = pygame.sprite.Group()
checkpoints_sprites = pygame.sprite.Group()
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
    def __init__(self, image_name, start_pos, checkpoints=None):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(load_image(image_name), (3200, 3200))
        self.start_pos = start_pos
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        pygame.mask.Mask.invert(self.mask)
        if checkpoints:
            for checkpoint_pos in checkpoints:
                checkpoints_sprites.add(CheckPoint(checkpoint_pos))



class Car(pygame.sprite.Sprite):
    image = load_image('car.png')

    def __init__(self, pos, acceleration=30, turnability=3, weight=1000, max_speed=15):
        #  pos is place where car will be spawn
        #  accelearation is number of pixels that car vector increases for every second if UP or DOWN key pressed
        #  turnability is number of degrees that car vector rotates every tick if LEFT or RIGHT key pressed
        #  max_speed is max length of car vector
        super().__init__(all_sprites, car_sprites)
        self.vec = Vector(0, 90)
        self.acceleration = acceleration
        self.turnability = turnability
        self.weight = weight
        self.inertion = weight // 50
        self.max_speed = max_speed
        self.image = pygame.transform.rotate(Car.image, self.vec.angle)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(*pos)

    def update(self, keys):
        if keys[pygame.K_UP] and self.vec.length > -self.max_speed:
            self.vec += -self.acceleration / FPS
        if keys[pygame.K_DOWN] and self.vec.length < self.max_speed:
            self.vec += self.acceleration / FPS
        if keys[pygame.K_LEFT]:
            self.vec.rotate(self.turnability)
            self.image = pygame.transform.rotate(Car.image, self.vec.angle)
        if keys[pygame.K_RIGHT]:
            self.vec.rotate(-self.turnability)
            self.image = pygame.transform.rotate(Car.image, self.vec.angle)
        if self.vec.length < 0:
            self.vec += self.inertion / FPS
        if self.vec.length > 0:
            self.vec += -self.inertion / FPS
        self.rect = self.image.get_rect(center=self.rect.center).move((self.vec.x, self.vec.y))

class CheckPoint(pygame.sprite.Sprite):
    image = load_image('checkpoint.png')
    def __init__(self, pos):
        super().__init__(all_sprites, checkpoints_sprites)
        self.image = CheckPoint.image
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=pos)



class Camera:
    # set camera shift
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # move obj for camera shift
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # positioning camera at target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)

def show_text(screen, text, font, color, size, center_pos):
    font = pygame.font.Font('data/' + font, size)
    rendered_text = font.render(text, True, color)
    text_rect = rendered_text.get_rect()
    text_rect.center = center_pos
    screen.blit(rendered_text, text_rect)



def start_screen():
    grass = OutTrack()
    track = Track('tr.png', (1900, 460), ((1230, 540), (1000, 1610), (620, 470), (450, 1860), (1400, 2730), 
                                          (1950, 1860), (2525, 2720), (2720, 1525), (1610, 1280), (2770, 760)))
    car = Car(track.start_pos)
    camera = Camera()

    while True:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        for car in car_sprites:
            for group in (all_sprites, checkpoints_sprites):
                group.remove(pygame.sprite.spritecollideany(car, checkpoints_sprites))

        if pygame.sprite.collide_mask(car, grass):
            car.vec += -car.max_speed * (car.vec.length // abs(car.vec.length))
        if pygame.sprite.collide_mask(car, track):
            car.vec *= 0.9

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
