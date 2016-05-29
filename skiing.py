#!/usr/bin/python2

import sys, random
from pygame import *

# The skier images
skier_images = ['pic/skier_down.png', 'pic/skier_right1.png', 'pic/skier_right2.png',
                'pic/skier_left2.png', 'pic/skier_left1.png']

class SkierClass(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = image.load('pic/skier_down.png')
        self.rect = self.image.get_rect()
        self.rect.center = [320, 100]
        self.angle = 0

    def turn(self, direction):
        # change the angle
        self.angle += direction
        if abs(self.angle) > 2:     # check the boundary
            self.angle -= direction
        # change the skier picture
        center = self.rect.center
        self.image = image.load(skier_images[self.angle])
        self.rect = self.image.get_rect()
        self.rect.center = center

    def move(self):
        # move the skier left and right
        self.rect.centerx += self.angle
        if abs(self.rect.centerx - 320) > 300:    # check the boundary
            self.rect.centerx -= self.angle

class ObstacleClass(sprite.Sprite):
    def __init__(self, img, location, type):
        sprite.Sprite.__init__(self)
        self.image = image.load(img)      # the image of the obstacle, may be a tree or a flag
        self.rect = self.image.get_rect()
        self.rect.center = location
        self.type = type    # the type of the obstacle, either a tree or a flag
        self.passed = False # whether or not the skier passed the obstacle

    def scroll(self, speed):
        self.rect.centery -= speed

# create a 640 x 640 map
# use 'blocks' of 64 x 64 pixels; 10 x 10 blocks in all
def create_map(start, end):
    map = sprite.Group()
    locations = []      # record the existing obstacle locations
    for i in range(10):     # create 10 obstacles in one map
        row = random.randint(start, end)
        col = random.randint(0, 9)
        location = [col * 64 + 20, row * 64 + 20]
        if location not in locations:   # prevent 2 obstacles in the same place
            locations.append(location)
            type = random.choice(('tree', 'flag'))
            if type == 'tree':
                image = 'pic/tree.png'
            elif type == 'flag':
                image = 'pic/flag.png'
            map.add(ObstacleClass(image, location, type))
    return map

def update_obstacles(map_close, map_far):
    obstacles = sprite.Group()
    for ob in map_close:
        obstacles.add(ob)
    for ob in map_far:
        obstacles.add(ob)
    return obstacles

def animate():
    screen.fill((255, 255, 255))
    display.update(obstacles.draw(screen))
    screen.blit(skier.image, skier.rect)
    screen.blit(score_text, (10, 10))
    display.flip()

def pause():
    while True:
        time.wait(50)
        for e in event.get():
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                quit()
                sys.exit()
            if e.type == KEYDOWN and e.key == K_p:
                return

# Initialization
init()
screen = display.set_mode((640, 640))
display.set_caption('Game: Skiing')
clock = time.Clock()
skier = SkierClass()
speed = [0, 6]
points = 0
map = [create_map(10, 19), create_map(20, 29)]
obstacles = update_obstacles(map[0], map[1])
map_shift = -640
robin = 0
font = font.Font(None, 40)

# main game loop
while True:
    # FPS
    clock.tick(80)
    # event handling
    for e in event.get():
        if (e.type == QUIT) or (e.type == KEYDOWN and e.key == K_ESCAPE):   # leave the game
            quit()
            sys.exit()
        elif e.type == KEYDOWN:
            if e.key == K_LEFT:     # turn left
                skier.turn(-1)      # turn the skier sprite
                speed = [skier.angle, 6 - 2 * abs(skier.angle)]     # change the speed
            elif e.key == K_RIGHT:  # turn right
                skier.turn(1)       # turn the skier sprite
                speed = [skier.angle, 6 - 2 * abs(skier.angle)]     # change the speed
            elif e.key == K_p:
                pause()

    # move the skier left or right
    skier.move()
    # scroll up all the obstacles
    for ob in obstacles:
        ob.scroll(speed[1])
    # record how far does the map shift
    map_shift += speed[1]

    # manage maps
    if map_shift >= 640:
        map_shift -= 640
        map[robin] = create_map(10, 19)
        obstacles = update_obstacles(map[robin], map[1-robin])
        robin = 1 - robin

    # check for hitting trees or getting flags
    hit = sprite.spritecollide(skier, obstacles, False)
    if hit:
        if hit[0].type == 'tree' and not hit[0].passed:
            points -= 100
            skier.image = image.load('pic/skier_crash.png')
            animate()
            time.delay(1000)
            skier.image = image.load('pic/skier_down.png')
            skier.angle = 0
            speed = [0, 6]
            hit[0].passed = True
        elif hit[0].type == 'flag' and not hit[0].passed:
            points += 10
            obstacles.remove(hit[0])

    # calculate and render the score
    score_text = font.render('Score: ' + str(points), 1, (10, 10, 10))
    # draw on the screen
    animate()
