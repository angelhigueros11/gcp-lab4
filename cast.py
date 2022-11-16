
import itertools
from math import atan2, cos, pi, sin

import pygame

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
SKY = (50, 100, 200)
BROWN = (200, 200, 100)
TRANSPARENT = (152, 0, 136, 255)

colors = [
    (0, 20, 10),
    (4, 40, 63),
    (0, 91, 82),
    (219, 242, 38),
    (21, 42, 138)
]

walls = {
    "1": pygame.image.load('./wall1.png'),
    "2": pygame.image.load('./wall2.png'),
    "3": pygame.image.load('./wall3.png'),
    "4": pygame.image.load('./wall4.png'),
    "5": pygame.image.load('./wall5.png'),
}

sprites = {
    "1": pygame.image.load('./sprite1.png'),
    "2": pygame.image.load('./sprite2.png'),
    "3": pygame.image.load('./sprite3.png'),
    "4": pygame.image.load('./sprite4.png'),
}

enemies = [
    {
        "x": 150,
        "y": 150,
        "sprite": sprites["1"]
    },
    {
        "x": 300,
        "y": 300,
        "sprite": sprites["2"]
    }
]


class Raycaster(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()
        self.blocksize = 50
        self.map= []
        self.player = {
            "y": int(self.blocksize + self.blocksize / 2),
            "x": int(self.blocksize + self.blocksize / 2),
            "fov": int(pi / 3),
            "a": int(pi / 3)
        }
        self.clearZ()

    def clearZ(self):
        self.zbuffer = [99999 for _ in range(int(self.width / 2))]


    def point(self, x, y, c = WHITE):
        self.screen.set_at((x, y), c)

    def block(self, x, y, wall):
        for i in range(x, x + self.blocksize):
            for j in range(y, y + self.blocksize):
                tx = int(( i - x ) * 128 / self.blocksize)
                ty = int(( j - y ) * 128 / self.blocksize)
                c = wall.get_at((tx, ty))
                self.point(i, j, c)


    def load_map(self, filename):
        with open(filename) as f:
            for line in f:
                self.map.append(list(line))

    def draw_stake(self, x, h, c, tx):
        start_y = int(self.height / 2  - h / 2)
        end_y = int(self.height / 2 + h / 2 )
        height = end_y - start_y

        for y in range(start_y, end_y):
            ty = int((y - start_y) * 128 / height)
            color = walls[c].get_at((tx, ty))
            self.point(x, y, color)

    def draw_map(self):
        for x in range(0, 500, self.blocksize):
            for y in range(0, 500, self.blocksize):

                i = int(x / self.blocksize)
                j = int(y / self.blocksize)


                if self.map[j][i] !=  ' ':
                    self.block(x, y, walls[self.map[j][i]])
            
    
    def draw_player(self):
        self.point(self.player["x"], self.player["y"])

    def draw_enemies(self):
        for enemy in enemies:
            self.point(enemy["x"], enemy["y"], RED)

        for enemy in enemies:
            self.draw_sprite(enemy)

    def draw_sprite(self, sprite):
        sprite_a = atan2(
                sprite["y"] - self.player["y"],
                sprite["x"] - self.player["x"],
            )


        d = (
            (self.player["x"]- sprite["x"]) ** 2 +
            (self.player["y"]- sprite["y"]) ** 2
            ) ** 0.5

        sprite_size = int((500 / d) * (500 / 10))
        sprite_x = int(
            (self.width / 2) + #offser mapa (mostrarlo solo en la segunda mitad)
            (sprite_a - self.player["a"]) *
            (self.width / 2) / self.player["fov"] + 
            sprite_size / 2 # Centrar sprite
        )
        sprite_y = int(self.height / 2 - sprite_size / 2)


        for x, y in itertools.product(range(sprite_x, sprite_x + sprite_size), range(sprite_y, sprite_y + sprite_size)):
            tx = int((x - sprite_x) * 128 / sprite_size)
            ty = int((y - sprite_y) * 128 / sprite_size)
            c= sprite["sprite"].get_at((tx, ty))
            try:
                if c != TRANSPARENT and sprite_x > 500 and self.zbuffer[int(x - self.width / 2)] >= d:
                    self.point(x, y, c)
                    self.zbuffer[int(x - self.width / 2)] = d
            except Exception:
                pass

    def cast_ray(self, a):
        d = 0
        ox = self.player["x"]
        oy = self.player["y"]


        while True:
            x = int(ox + d * cos(a))
            y = int(oy + d * sin(a)) 

            i = int(x / self.blocksize)
            j = int(y / self.blocksize) 

            if self.map[j][i] != ' ':
                hitx = x - i * self.blocksize
                hity = y - j * self.blocksize

                maxhit = hitx if 1 < hitx < self.blocksize - 1 else hity
                tx = int( maxhit * 128 / self.blocksize)
                return d, self.map[j][i], tx

            self.point(x, y)
            d += 3

    def render(self):
        self.draw_map()
        self.draw_player()

        density = 100
        # Minimapa
        for i in range(density):
            a = self.player["a"] - self.player["fov"] / 2 + self.player["fov"] * i / density
            d, c, _ = self.cast_ray(a)

        for i in range(500):
            self.point(499, i)
            self.point(500, i)
            self.point(501, i)
            
        # Draw in 3D
        for i in range(int(self.width / 2)):
            a = self.player["a"] - self.player["fov"] / 2 + self.player["fov"] * i / (self.width / 2)
            d, c, tx = self.cast_ray(a)
            try:
                x = int(self.width / 2 + i)
                h = self.height / (d * cos(a - self.player["a"])) * self.height / 10
            except Exception:
                continue


            if self.zbuffer[i] >= d:
                self.draw_stake(x, h, c, tx)
                self.zbuffer[i] = d
    
        self.draw_enemies()





pygame.init()
screen = pygame.display.set_mode((1000, 500))
r = Raycaster(screen)
r.load_map('./map.txt')

running = True
while running:
    screen.fill(BLACK, (0, 0, r.width / 2, r.height))
    screen.fill(SKY, (r.width / 2, 0, r.width, r.height / 2))
    screen.fill(BROWN, (r.width / 2, r.height / 2, r.width, r.height / 2))
    r.clearZ()
    r.render()

    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_a:
                r.player["a"] -= pi / 25

            if event.key == pygame.K_d:
                r.player["a"] += pi / 25

            if event.key == pygame.K_RIGHT:
                r.player["x"] += 20

            if event.key == pygame.K_LEFT:
                r.player["x"] -= 20

            if event.key == pygame.K_UP:
                r.player["y"] -= 20

            if event.key == pygame.K_DOWN:
                r.player["y"] += 20