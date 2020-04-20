#!/usr/bin/env python
""" pygame.examples.neil_tuts_field

This game has stuff you can buy and characters.
"""
import os
import pygame as pg

main_dir = os.path.split(os.path.abspath(__file__))[0]

class Player:
    ground = 530
    sky = 100

    def __init__(self, standing, walking_left, walking_right, climbing, climb_speed, fall_speed, camera):
        self.image_standing = load_image(standing, 100, 150)
        self.image_walking_left = load_image(walking_left, 100, 150)
        self.image_walking_right = load_image(walking_right, 100, 150)
        self.image_climbing = load_image(climbing, 120, 150)
        self.climb_speed = climb_speed
        self.fall_speed = fall_speed
        self.camera = camera
        self.pos = self.image_standing.get_rect().move(200, Player.ground - 150)
        self.total_fall = 0

    def draw(self, direction, on_ladder, screen):
        if direction < 0:
            screen.blit(self.image_walking_left, self.pos)
        elif direction > 0:
            screen.blit(self.image_walking_right, self.pos)
        elif on_ladder:
            screen.blit(self.image_climbing, self.pos)
        else:
            screen.blit(self.image_standing, self.pos)

    def climb(self, direction):
        self.pos = self.pos.move(0, self.climb_speed * direction)
        # make sure we don't go beneath the ground or above the sky
        if self.pos.bottom > Player.ground:
            self.pos.bottom = Player.ground
        elif self.pos.top < Player.sky:
            self.pos.top = Player.sky

    def fall(self, platform):
        self.pos = self.pos.move(0, self.fall_speed)
        self.total_fall += self.fall_speed
        # fall to the platform or the ground
        fall_to = Player.ground
        if self.is_above_platform(platform):
            fall_to = platform.pos.top + 70
        if self.pos.bottom > fall_to:
            self.pos.bottom = fall_to
            self.total_fall = 0

    # TODO fix
    def is_on_ladder(self, ladder):
        arr = self.camera.adjust(ladder.pos)
        return any(self.pos.colliderect(l[1].inflate(-50, -50)) for l in arr)

    def is_above_platform(self, platform):
        arr = self.camera.adjust(platform.pos)
        return any(self.pos.right > p[1].left+10 and self.pos.left < p[1].right-10 and self.pos.bottom < p[1].bottom - 30 for p in arr)

    def is_on_coin(self, coin, frame):
        arr = list(filter(lambda x: x[0] == frame, self.camera.adjust(coin.pos)))
        return any(self.pos.colliderect(c[1].inflate(-10, -10)) for c in arr)

    def should_die(self):
        return self.total_fall >= 200

class GameObject:
    def __init__(self, pos, name):
        self.pos = pos
        self.image = load_image(name, pos.width, pos.height)

    def draw(self, camera, screen, frame = None):
        for o in camera.adjust(self.pos):
            if not frame or frame == o[0]:
                screen.blit(self.image, o[1])

class Camera:
    def __init__(self, background, speed):
        self.speed = speed
        self.pos = background.pos
        self.frame = 0

    def move(self, direction):
        self.pos = self.pos.move(self.speed * direction, 0)
        if self.pos.left > 800:
            self.pos.left = 0
            self.frame += 1
        elif self.pos.left < 0:
            self.pos.left = 800
            self.frame -= 1

    def adjust(self, rect):
        arr = [
          (self.frame - 1, rect.move(-self.pos.left - 800, 0)),
          (self.frame, rect.move(-self.pos.left, 0)),
          (self.frame + 1, rect.move(-self.pos.left + 800, 0))
        ]
        return list(filter(lambda x: x[1].left < 800 and x[1].right > 0, arr))

class Score:
    def __init__(self, font_name, font_size):
        self.score = 0
        self.font = pg.font.Font(font_name, font_size)
        self.font.set_bold(1)
        msg = "Coins: %d" % self.score
        self.image = self.font.render(msg, 0, pg.Color("Yellow"))
        self.pos = self.image.get_rect().move(600, 10)

    def update(self):
        self.score = self.score + 1
        msg = "Coins: %d" % self.score
        self.image = self.font.render(msg, 0, pg.Color("Yellow"))

    def draw(self, screen):
        screen.blit(self.image, self.pos)

class EndScreen:
    def __init__(self, font_name, font_size, msg):
        self.font = pg.font.Font(font_name, font_size)
        self.font.set_bold(1)
        self.image = self.font.render(msg, 0, pg.Color("Yellow"))
        self.pos = self.image.get_rect().move(280, 280)

    def draw(self, screen):
        screen.blit(self.image, self.pos)

class Health:
    def __init__(self, health, name):
        self.health = health
        self.image = load_image(name, 50, 50)
        self.pos = self.image.get_rect().move(10, 10)

    def lose_health(self):
        self.health -= 1

    def draw(self, screen):
        for i in range(self.health):
            screen.blit(self.image, self.pos.move(i*50, 0))


# quick function to load an image
def load_image(name, width, height):
    path = os.path.join(main_dir, "data", name)
    img = pg.image.load(path).convert()
    return  pg.transform.scale(img, (width, height))

def load_font(name, size):
    path = os.path.join(main_dir, "data", name)
    return pg.font.Font(path, size)

def load_sound(file):
    """ because pygame can be be compiled without mixer.
    """
    if not pg.mixer:
        return None
    file = os.path.join(main_dir, "data", file)
    try:
        sound = pg.mixer.Sound(file)
        return sound
    except pg.error:
        print("Warning, unable to load, %s" % file)
    return None

def main():
    # Initialize pygame
    if pg.get_sdl_version()[0] == 2:
        pg.mixer.pre_init(44100, 32, 2, 1024)
    pg.init()
    if pg.mixer and not pg.mixer.get_init():
        print("Warning, no sound")
        pg.mixer = None

    #pg.mixer = None

    coin_sound = load_sound("netut_coin_sound_2.wav")
    grunt_sound = load_sound("netut_grunt.wav")
    if pg.mixer:
        music = os.path.join(main_dir, "data", "netut_song.wav")
        pg.mixer.music.load(music)
        pg.mixer.music.play(-1)

    window = (800, 600)
    screen = pg.display.set_mode(window, pg.FULLSCREEN)

    clock = pg.time.Clock()

    background = GameObject(pg.Rect(0, 0, 800, 600), "green_hills_1.png")
    ladder = GameObject(pg.Rect(400, 280, 100, 250), "ladder3.gif")
    platform = GameObject(pg.Rect(500, 245, 250, 160), "green_hills_platform.gif")
    coins = {}
    game_objects = [background, ladder, platform]

    camera = Camera(background, 10)
    player = Player("netut_standing.gif", "netut_walking_left.gif", "netut_walking_right.gif", "netut_climbing.gif", 5, 20, camera)
    score = Score(None, 40)
    health = Health(3, "netut_heart.gif")
    game_over = EndScreen(None, 60, "Game Over")
    you_win = EndScreen(None, 60, "You Win!")

    while health.health > 0 and score.score < 100:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return
        keystate = pg.key.get_pressed()
        direction = keystate[pg.K_RIGHT] - keystate[pg.K_LEFT]
        climb_direction = keystate[pg.K_DOWN] - keystate[pg.K_UP]

        camera.move(direction)
        for g in game_objects:
            g.draw(camera, screen)

        score.draw(screen)
        health.draw(screen)

        # TODO clean up coin logic
        for f in [camera.frame - 1, camera.frame, camera.frame + 1]:
            if f not in coins.keys():
                coins[f] = []
                for i in range(5):
                    coins[f].append(GameObject(pg.Rect(500 + (i * 50), 255, 40, 40), "netut_coin.gif"))
            for c in coins[f]:
                if player.is_on_coin(c, f):
                    if pg.mixer:
                        coin_sound.play()
                    coins[f].remove(c)
                    score.update()
                else:
                    c.draw(camera, screen, f)

        on_ladder = player.is_on_ladder(ladder)
        if on_ladder:
            player.climb(climb_direction)
        else:
            player.fall(platform)

        if player.should_die():
            health.lose_health()
            if pg.mixer:
                grunt_sound.play()

        player.draw(direction, on_ladder, screen)

        pg.display.update()
        clock.tick(40)

    screen.fill(pg.Color("Black"))
    if health.health == 0:
        game_over.draw(screen)
    elif score.score == 100:
        you_win.draw(screen)
    pg.display.update()

    if pg.mixer:
        pg.mixer.music.fadeout(1000)
    pg.event.wait()
    pg.time.wait(5000)
    pg.quit()


if __name__ == "__main__":
    main()
