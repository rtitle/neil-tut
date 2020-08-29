#!/usr/bin/env python

"""
Energy Punch
This game has stuff you can buy and characters.
"""
import os
import time
import pygame as pg

main_dir = os.path.split(os.path.abspath(__file__))[0]

# TODO: classes should extend pg.sprite.Sprite and use pg.sprite.Group

# TODO: interaction of camera and game objects feels a little clunky

class Player:
    ground = 530
    sky = 100

    def __init__(
        self, standing, walking_left, walking_right,
        standing_arm_up, walking_left_arm_up, walking_right_arm_up,
        climbing, climb_speed, fall_speed, camera
    ):
        self.set_player_image(standing, walking_left, walking_right, standing_arm_up, walking_left_arm_up, walking_right_arm_up, climbing)
        self.climb_speed = climb_speed
        self.fall_speed = fall_speed
        self.camera = camera
        self.pos = self.image_standing.get_rect().move(200, Player.ground - 150)
        self.total_fall = 0
        self.bought_item_left = None
        self.bought_item_right = None
        self.bought_item_left_pos = None
        self.bought_item_right_pos = None
        self.arm_up = False
        self.knock_direction = 0
        self.hit_time = None
        self.is_enchanted_character = False

    def set_player_image(self, standing, walking_left, walking_right, standing_arm_up, walking_left_arm_up, walking_right_arm_up, climbing, width = 100, height = 150):
        self.image_standing = load_image(standing, width, height)
        self.image_walking_left = load_image(walking_left, width, height)
        self.image_walking_right = load_image(walking_right, width, height)
        self.image_standing_arm_up = load_image(standing_arm_up, width, height)
        self.image_walking_left_arm_up = load_image(walking_left_arm_up, width, height)
        self.image_walking_right_arm_up = load_image(walking_right_arm_up, width, height)
        self.image_climbing = load_image(climbing, width + 20, height)
        if walking_left == "enchanted_character_left.png":
            self.is_enchanted_character = True
        else:
            self.is_enchanted_character = False

    def draw(self, direction, on_ladder, on_top_of_ladder, modal_active, screen):
        if not modal_active:
            if direction < 0:
                img = self.image_walking_left_arm_up if self.arm_up else self.image_walking_left
                screen.blit(img, self.pos)
                if self.bought_item_left:
                    screen.blit(self.bought_item_left.image, self.bought_item_left_pos)
            elif direction > 0:
                img = self.image_walking_right_arm_up if self.arm_up else self.image_walking_right
                screen.blit(img, self.pos)
                if self.bought_item_right:
                    screen.blit(self.bought_item_right.image, self.bought_item_right_pos)
            elif on_ladder and not on_top_of_ladder:
                screen.blit(self.image_climbing, self.pos)
            else:
                img = self.image_standing_arm_up if self.arm_up else self.image_standing
                screen.blit(img, self.pos)
                if self.bought_item_right:
                    screen.blit(self.bought_item_right.image, self.bought_item_right_pos)

    def climb(self, direction):
        self.pos = self.pos.move(0, self.climb_speed * direction)
        # make sure we don't go beneath the ground or above the sky
        if self.pos.bottom > Player.ground:
            self.pos.bottom = Player.ground
        elif self.pos.top < Player.sky:
            self.pos.top = Player.sky
        self.set_buy_item_pos()

    def fall(self, platform):
        self.pos = self.pos.move(0, self.fall_speed)
        self.total_fall += self.fall_speed
        # fall to the platform or the ground
        fall_to = platform.pos.top + 70 if platform and self.is_above_platform(platform) else Player.ground
        if self.pos.bottom > fall_to:
            self.pos.bottom = fall_to
            self.total_fall = 0
        self.set_buy_item_pos()

    def move(self, direction, speed):
        self.pos = self.pos.move(speed * direction, 0)
        if self.pos.right > 800:
            self.pos.right = 800
        elif self.pos.left < 0:
            self.pos.left = 0
        self.set_buy_item_pos()

    def buy_item(self, left, right):
        self.bought_item_left = left
        self.bought_item_right = right
        self.set_buy_item_pos()

    def set_buy_item_pos(self):
        # enchanted character has a big tail
        if self.arm_up:
            if self.is_enchanted_character:
                self.bought_item_left_pos = self.pos.move(-20, 25)
                self.bought_item_right_pos = self.pos.move(180, 25)
            else:
                self.bought_item_left_pos = self.pos.move(-30, 25)
                self.bought_item_right_pos = self.pos.move(80, 25)
        else:
            if self.is_enchanted_character:
                self.bought_item_left_pos = self.pos.move(-20, 50)
                self.bought_item_right_pos = self.pos.move(180, 50)
            else:
                self.bought_item_left_pos = self.pos.move(-30, 50)
                self.bought_item_right_pos = self.pos.move(80, 50)

    def set_arm_up(self, arm_up):
        changed = self.arm_up != arm_up
        self.arm_up = arm_up
        if changed and self.bought_item_left_pos and self.bought_item_right_pos:
            self.set_buy_item_pos()

    def reset_pos(self):
        self.pos = self.image_standing.get_rect().move(200, Player.ground - 150)

    def reset_fall(self):
        self.total_fall = 0

    def reset_buy_item(self):
        self.bought_item_left = None
        self.bought_item_right = None
        self.bought_item_left_pos = None
        self.bought_item_right_pos = None

    def is_on_object(self, pos, frame=None):
        arr = self.camera.adjust(pos)
        if frame:
            arr = list(filter(lambda x: x[0] == frame, arr))
        return any(self.pos.colliderect(a[1]) for a in arr)

    def is_on_ladder(self, ladder): 
        arr = self.camera.adjust(ladder.pos)
        return any(self.pos.right > p[1].left+25 and self.pos.left < p[1].right-25 and self.pos.bottom > p[1].top+20 and self.pos.top < p[1].bottom for p in arr)

    def is_on_top_of_ladder(self, ladder):
        arr = self.camera.adjust(ladder.pos)
        return any(self.pos.right > p[1].left+25 and self.pos.left < p[1].right-25 and self.pos.bottom < p[1].top+30 for p in arr)

    def is_above_platform(self, platform):
        arr = self.camera.adjust(platform.pos)
        return any(self.pos.right > p[1].left+10 and self.pos.left < p[1].right-10 and self.pos.bottom < p[1].bottom - 30 for p in arr)

    def is_on_coin(self, coin, frame):
        return self.is_on_object(coin.pos.inflate(-10, -10), frame)

    def should_die(self):
        return self.total_fall >= 200

    def is_on_octopus(self, octopus):
        arr = self.camera.adjust(octopus.pos)
        left = any(self.pos.right > o[1].left+25 and self.pos.right < o[1].right - 50 and self.pos.bottom > o[1].top and self.pos.top < o[1].bottom for o in arr)
        right = any(self.pos.left < o[1].right-25 and self.pos.left > o[1].left + 50 and self.pos.bottom > o[1].top and self.pos.top < o[1].bottom for o in arr)
        if left:
            return -1
        elif right:
            return 1
        else:
            return 0

    def set_knock_direction(self, knock_direction):
        self.knock_direction = knock_direction

    def is_on_final_boss(self):
        arr = self.camera.adjust(pg.Rect(350, 200, 100, 400))
        return any(self.pos.right > p[1].left+10 and self.pos.left < p[1].right-10 and self.pos.bottom < p[1].bottom - 30 for p in arr)

    def set_hit(self, time):
        self.hit_time = time

    def is_hit(self, time):
        return not self.hit_time or time - self.hit_time > 3000


class Boss:
    def __init__(self, pos, left_name, right_name, left_hit_name, right_hit_name, speed, health):
        self.pos = pos
        self.original_pos = pos
        self.left_image = load_image(left_name, pos.width, pos.height)
        self.right_image = load_image(right_name, pos.width, pos.height)
        self.left_image_hit = load_image(left_hit_name, pos.width, pos.height)
        self.right_image_hit = load_image(right_hit_name, pos.width, pos.height)
        self.speed = speed
        self.health = health
        self.original_health = health
        self.direction = 1
        self.active = False
        self.is_hit = False
        self.flash_count = 0
        self.falling = False
        self.won = False

    def draw(self, screen):
        if self.is_hit:
            img = self.right_image_hit if self.direction == 1 else self.left_image_hit
            self.flash_count += 1
            if self.flash_count > 5:
                self.flash_count = 0
                self.is_hit = False
        else:
            img = self.right_image if self.direction == 1 else self.left_image

        screen.blit(img, self.pos)

    def move(self):
        if self.falling:
            if self.pos.bottom < Player.ground:
                self.pos = self.pos.move(5 * self.direction, 7)
        else:
            self.pos = self.pos.move(self.speed * self.direction, 0)
        if self.pos.right > 800 or self.pos.left < 0:
            self.change_direction()
        if self.pos.bottom > Player.ground:
            self.pos.bottom = Player.ground

    def activate(self):
        self.active = True

    def hit(self):
        self.health -= 1
        self.is_hit = True

    def set_won(self):
        self.won = True

    def is_on_player(self, player, offset):
        return self.pos.inflate(offset, 0).colliderect(player.pos)

    def is_on_ground(self):
        return self.pos.bottom == Player.ground

    def change_direction(self):
        self.direction *= -1

    def set_falling(self):
        self.falling = True

    def reset(self):
        self.won = False
        self.active = False
        self.falling = False
        self.pos = self.original_pos
        self.health = self.original_health
        self.direction = 1

class GameObject:
    def __init__(self, pos, name):
        self.pos = pos
        self.image = load_image(name, pos.width, pos.height)
        self.active = True

    def deactivate(self):
        self.active = False

    def activate(self):
        self.active = True

    def draw(self, camera, screen, frame = None):
        for o in camera.adjust(self.pos):
            if not frame or frame == o[0]:
                screen.blit(self.image, o[1])

class BuyObject(GameObject):
    def __init__(self, pos, name, item_name, price, is_character=False):
        super().__init__(pos, name)
        self.name = name
        self.price = price
        self.item_name = item_name
        self.is_character = is_character

class Enemy(GameObject):
    def __init__(self, pos, name, speed, distance):
        super().__init__(pos, name)
        self.speed = speed
        self.distance = distance
        self.orig_pos = pos
        self.direction = -1

    def move(self):
        self.pos = self.pos.move(self.speed * self.direction, 0)
        if self.pos.left < self.orig_pos.left - self.distance or self.pos.left > self.orig_pos.left + self.distance:
            self.direction *= -1

    def change_direction(self):
        self.direction *= -1

# blue - enchanted sword - 85 coins
# pink - enchanted character - 99 coins
class Barn(GameObject):
    def __init__(self, pos, name):
        super().__init__(pos, name)
        self.pink_rect = pg.Rect(100, 280, 100, 100)
        self.blue_rect = pg.Rect(550, 300, 100, 100)
        self.back_rect = pg.Rect(700, 500, 100, 100)

    def is_in_pink_button(self, x, y):
        return self.pink_rect.collidepoint(x, y)
    
    def is_in_blue_button(self, x, y):
        return self.blue_rect.collidepoint(x, y)

    def is_in_back_button(self, x, y):
        return self.back_rect.collidepoint(x, y)

class Camera:
    def __init__(self, background, speed):
        self.speed = speed
        self.background = background
        self.pos = background.pos
        self.frame = 0

    def move2(self, direction, speed):
        self.pos = self.pos.move(speed * direction, 0)
        if self.pos.left > 800:
            self.pos.left = 0
            self.frame += 1
            return True
        elif self.pos.left < 0:
            self.pos.left = 800
            self.frame -= 1
            return True
        return False

    def move(self, direction):
        return self.move2(direction, self.speed)

    def adjust(self, rect):
        arr = [
          (self.frame - 1, rect.move(-self.pos.left - 800, 0)),
          (self.frame, rect.move(-self.pos.left, 0)),
          (self.frame + 1, rect.move(-self.pos.left + 800, 0))
        ]
        return list(filter(lambda x: x[1].left < 800 and x[1].right > 0, arr))

    def reset(self):
        self.pos = self.background.pos
        self.frame = 0

    def visible_frames(self):
        return [self.frame - 1, self.frame, self.frame + 1]

class Score:
    def __init__(self, font_name, font_size):
        self.score = 0
        self.font = pg.font.Font(font_name, font_size)
        self.font.set_bold(1)
        msg = "Coins: %d" % self.score
        self.image = self.font.render(msg, 0, pg.Color("Yellow"))
        self.pos = self.image.get_rect().move(600, 10)

    def update(self, delta):
        self.score += delta
        msg = "Coins: %d" % self.score
        self.image = self.font.render(msg, 0, pg.Color("Yellow"))

    def reset(self):
        self.score = 0
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

class Poster:
    def __init__(self, pos, name):
        self.pos = pos
        self.image = load_image(name, pos.width, pos.height)

    def draw(self, screen):
        screen.blit(self.image, self.pos)

class Health:
    def __init__(self, health, name):
        self.health = health
        self.orig_health = health
        self.image = load_image(name, 50, 50)
        self.pos = self.image.get_rect().move(10, 10)

    def lose_health(self):
        self.health -= 1

    def reset(self):
        self.health = self.orig_health

    def draw(self, screen):
        for i in range(self.health):
            screen.blit(self.image, self.pos.move(i*50, 0))

class Pause:
    def __init__(self, pause_button, pause_screen, question, pause_characters):
        self.button_image = load_image(pause_button, 60, 60)
        self.screen_image = load_image(pause_screen, 800, 600)
        self.button_pos = self.button_image.get_rect().move(10, 530)
        self.screen_pos = self.screen_image.get_rect()
        self.question_image = load_image(question, 70, 70)
        self.font = pg.font.Font(None, 32)
        self.is_paused = False
        self.pause_characters = pause_characters
        self.process_pause_characters()

    def add_pause_character(self, character, name):
        self.pause_characters.append((character, name))
        self.process_pause_characters()

    def process_pause_characters(self):
        self.processed_pause_characters = []
        for i in range(5):
            border_pos = pg.Rect(150, 80 + i*90, 480, 70)
            img = load_image(self.pause_characters[i][0], 60, 60) if len(self.pause_characters) > i else self.question_image
            pos = img.get_rect().move(160, 80 + i*90)
            font = self.font.render(self.pause_characters[i][1], 0, pg.Color("Orange")) if len(self.pause_characters) > i else self.font.render("???", 0, pg.Color("Orange"))
            font_pos = font.get_rect().move(350, 90 + i*90)
            self.processed_pause_characters.append((border_pos, img, pos, font, font_pos))

    def set_paused(self, is_paused):
        self.is_paused = is_paused

    def is_in_button(self, x, y):
        return self.button_pos.collidepoint(x, y)

    def is_in_resume_button(self, x, y):
        return pg.Rect(585, 431, 100, 100).collidepoint(x, y)

    def is_in_neil_tut(self, x, y):
        return len(self.pause_characters) > 0 and self.processed_pause_characters[0][2].collidepoint(x, y)

    def is_in_sonic(self, x, y):
        return len(self.pause_characters) > 1 and self.processed_pause_characters[1][2].collidepoint(x, y)

    def is_in_tails(self, x, y):
        return len(self.pause_characters) > 2 and self.processed_pause_characters[2][2].collidepoint(x, y)

    def is_in_knuckles(self, x, y):
        return len(self.pause_characters) > 3 and self.processed_pause_characters[3][2].collidepoint(x, y)

    def is_in_enchanted_tails(self, x, y):
        return len(self.pause_characters) > 4 and self.processed_pause_characters[4][2].collidepoint(x, y)

    def draw(self, screen):
        if self.is_paused:
            screen.blit(self.screen_image, self.screen_pos)
            for c in self.processed_pause_characters:
                pg.draw.rect(screen, pg.Color("White"), c[0])
                screen.blit(c[1], c[2])
                screen.blit(c[3], c[4])
        else:
            screen.blit(self.button_image, self.button_pos)

# TODO: modal class hierarchy

class OkModal:
    def __init__(self, pos, font_name, font_size, msg):
        self.pos = pos
        self.active = False
        font = pg.font.Font(font_name, font_size)
        font.set_bold(1)

        self.message_image = font.render(msg, 0, pg.Color("Yellow"))
        self.message_pos = self.message_image.get_rect().move(pos.left + 20, pos.top + 20)

        self.ok_image = font.render("OK", 0, pg.Color("Yellow"))
        self.ok_pos = self.ok_image.get_rect().move(pos.left + 210, pos.bottom - 50)

    def set_active(self):
        self.active = True

    def dismiss(self): 
        self.active = False

    def is_in_ok(self, x, y):
        return self.ok_pos.inflate(20, 20).collidepoint(x, y)

    def draw(self, screen):
        pg.draw.rect(screen, pg.Color("Blue"), self.pos)
        screen.blit(self.message_image, self.message_pos)
        pg.draw.rect(screen, pg.Color(173, 216, 230), self.ok_pos.inflate(20, 20))
        screen.blit(self.ok_image, self.ok_pos)

class YesNoModal:
    def __init__(self, pos, font_name, font_size):
        self.pos = pos
        self.active = False
        self.buy_object_left = None
        self.buy_object_right = None
        
        self.font = pg.font.Font(font_name, font_size)
        self.font.set_bold(1)

        self.yes_image = self.font.render("Yes", 0, pg.Color("Yellow"))
        self.yes_pos = self.yes_image.get_rect().move(pos.left + 50, pos.bottom - 50)

        self.no_image = self.font.render("No", 0, pg.Color("Yellow"))
        self.no_pos = self.no_image.get_rect().move(pos.right - 90, pos.bottom - 50)

    def set_active(self, buy_object_left, buy_object_right):
        self.active = True
        self.buy_object_left = buy_object_left
        self.buy_object_right = buy_object_right

    def dismiss(self):
        self.active = False

    def set_message(self, msg):
        self.message_image = self.font.render(msg, 0, pg.Color("Yellow"))
        self.message_pos = self.message_image.get_rect().move(self.pos.left + 20, self.pos.top + 20)

    def is_in_yes(self, x, y):
        return self.yes_pos.inflate(20, 20).collidepoint(x, y)
    
    def is_in_no(self, x, y):
        return self.no_pos.inflate(20, 20).collidepoint(x, y)

    def draw(self, screen):
        pg.draw.rect(screen, pg.Color("Blue"), self.pos)
        screen.blit(self.message_image, self.message_pos)
        pg.draw.rect(screen, pg.Color(173, 216, 230), self.yes_pos.inflate(20, 20))
        screen.blit(self.yes_image, self.yes_pos)
        pg.draw.rect(screen, pg.Color(173, 216, 230), self.no_pos.inflate(20, 20))
        screen.blit(self.no_image, self.no_pos)

def load_image(name, width, height):
    path = os.path.join(main_dir, "data", name)
    img = pg.image.load(path).convert_alpha()
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

def get_time_millis():
    return int(round(time.time() * 1000))

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
    bounce_sound = load_sound("bounce.wav")
    boing_sound = load_sound("boing.wav")
    if pg.mixer:
        music = os.path.join(main_dir, "data", "netut_song.wav")
        pg.mixer.music.load(music)
        pg.mixer.music.play(-1)

    window = (800, 600)
    screen = pg.display.set_mode(window, pg.FULLSCREEN)

    clock = pg.time.Clock()

    background = GameObject(pg.Rect(0, 0, 800, 600), "green_hills_1.png")
    background_level_2 = GameObject(pg.Rect(0, 0, 800, Player.ground), "background_level_2.png")
    background_level_3 = GameObject(pg.Rect(0, 0, 800, Player.ground), "background_level_3.png")
    background_level_4 = GameObject(pg.Rect(0, 0, 800, 600), "background_level_4.png")
    background_level_5 = GameObject(pg.Rect(0, 0, 800, 600), "background_level_5.png")
    ground_level_2 = GameObject(pg.Rect(0, Player.ground, 800, 600 - Player.ground), "ground_level_2.png")
    ground_level_3 = GameObject(pg.Rect(0, Player.ground, 800, 600 - Player.ground), "ground_level_3.png")
    ladder = GameObject(pg.Rect(400, 280, 100, 250), "ladder3.gif")
    boss_ladder_left = GameObject(pg.Rect(10, 280, 100, 250), "ladder3.gif")
    boss_ladder_right = GameObject(pg.Rect(690, 280, 100, 250), "ladder3.gif")
    platform = GameObject(pg.Rect(500, 245, 250, 160), "green_hills_platform.gif")
    ring_box = GameObject(pg.Rect(900, 450, 75, 75), "coin_box.gif")
    hammer_left = BuyObject(pg.Rect(700, 460, 50, 50), "hammer_left.gif", "hammer", 10)
    hammer_right = BuyObject(pg.Rect(700, 460, 50, 50), "hammer_right.gif", "hammer", 10)
    axe_left = BuyObject(pg.Rect(700, 460, 50, 50), "axe_left.png", "axe", 20)
    axe_right = BuyObject(pg.Rect(700, 460, 50, 50), "axe_right.png", "axe", 20)
    sword_left = BuyObject(pg.Rect(700, 460, 50, 50), "sword_left.jpg", "sword", 35)
    sword_right = BuyObject(pg.Rect(700, 460, 50, 50), "sword_right.jpg", "sword", 35)
    shield = BuyObject(pg.Rect(700, 460, 50, 50), "shield.jpg", "shield", 50)
    sonic = BuyObject(pg.Rect(700, 430, 100, 130), "sonic_left.png", "Sonic", 40, True)
    tails = BuyObject(pg.Rect(700, 430, 100, 130), "tails_left.png", "Tails", 55, True)
    knuckles = BuyObject(pg.Rect(700, 430, 100, 130), "knuckles_left.png", "Knuckles", 50, True)
    octopus = Enemy(pg.Rect(600, 385, 200, 200), "octopus.png", 1, 50)
    octopus.deactivate()
    barn = Barn(pg.Rect(0, 0, 800, 600), "barn_b.png")
    barn_platform = GameObject(pg.Rect(0, 300, 800, 160), "green_hills_platform.gif")
    barn.deactivate()
    enchanted_character = BuyObject(pg.Rect(700, 430, 100, 130), "enchanted_character_left.png", "Enchanted Character", 55, True)
    enchanted_sword = BuyObject(pg.Rect(700, 460, 50, 50), "enchanted_sword.png", "Enchanted Sword", 55)
    final_boss_background = GameObject(pg.Rect(0, 0, 800, Player.ground), "final_boss.png")
    poster = Poster(pg.Rect(225, 0, 450, 600), "poster.jpg")

    game_objects = [background, ladder, platform]
    coins = {}
    buy_objects = {1: [(hammer_left, hammer_right)]}
    ring_boxes = {}

    camera = Camera(background, 10)
    player = Player(
        "netut_standing.gif", "netut_walking_left.gif", "netut_walking_right.gif", 
        "netut_standing_arm_up.gif", "netut_walking_left_arm_up.gif", "netut_walking_right_arm_up.gif",
        "netut_climbing.gif", 5, 20, camera)
    score = Score(None, 40)
    health = Health(3, "netut_heart.gif")
    pause = Pause("pause.png", "pause_screen.png", "question_mark.png", [("netut_standing_arm_up.gif", "Neil Tut")])
    modal = YesNoModal(pg.Rect(100, 100, 550, 200), None, 40)

    no_money_modal = OkModal(pg.Rect(150, 100, 500, 150), None, 40, "You don't have enough coins.")
    game_over = EndScreen(None, 60, "Game Over")
    boss_time = EndScreen(None, 60, "Boss Time")
    level_two = EndScreen(None, 60, "Level 2")
    level_three = EndScreen(None, 60, "Level 3")
    level_four = EndScreen(None, 60, "Level 4")
    level_five = EndScreen(None, 60, "Level 5")
    final_boss = EndScreen(None, 60, "Final Boss")
    you_win = EndScreen(None, 60, "You Win!")
    boss = Boss(pg.Rect(500, 150, 200, 150), "eggman_boss_left.gif", "eggman_boss_right.gif", "eggman_boss_left_hit.gif", "eggman_boss_right_hit.gif", 3, 2)

    cur_level = 1

    #cur_level = 4
    #pause.add_pause_character("sonic_left.png", "Sonic")
    #pause.add_pause_character("tails_left.png", "Tails")
    #pause.add_pause_character("knuckles_left.png", "Knuckles")
    #boss.won = True

    knock_distance = 0
    final_boss_direction = -1
    final_boss_hit_time = None
    final_boss_num_hits = 0
    space_pressed = False

    while health.health > 0 and cur_level <= 5:
        click = False
        prev_space_pressed = space_pressed
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return
            if event.type == pg.MOUSEBUTTONDOWN:
                click = True
        keystate = pg.key.get_pressed()
        mouse_pos = pg.mouse.get_pos()
        direction = keystate[pg.K_RIGHT] - keystate[pg.K_LEFT]
        climb_direction = keystate[pg.K_DOWN] - keystate[pg.K_UP]
        space_pressed = keystate[pg.K_SPACE]

        # move the camera or player
        if not modal.active and not no_money_modal.active and not pause.is_paused:
            if boss.active or barn.active:
                player.move(direction, camera.speed)
            else:
                if player.knock_direction == 0:
                    if camera.move(direction):
                        # reset the buy modal so it pops up again
                        modal.buy_object_left = None
                        modal.buy_object_right = None
                else:
                    camera.move2(player.knock_direction, camera.speed * 1)
                    knock_distance += camera.speed * 2
                    if knock_distance >= 400:
                        player.set_knock_direction(0)
                        knock_distance = 0

        # move the boss
        if boss.active and not pause.is_paused:
            if cur_level == 5:
                camera.move2(final_boss_direction, 2)
            else:
                boss.move()

        # move the octopus
        if octopus.active and not pause.is_paused:
            octopus.move()
            on_oct = player.is_on_octopus(octopus)
            if on_oct != 0 and direction == 0:
                player.set_knock_direction(on_oct)
                if pg.mixer:
                    bounce_sound.play()

        # display each static game object, including the background
        if not pause.is_paused:
            for g in game_objects:
                g.draw(camera, screen)

        # display each stateful game object
        if not boss.active and not pause.is_paused and not barn.active:
            for f in camera.visible_frames():
                # populate infinite coins
                if f not in coins:
                    coins[f] = []
                    for i in range(5):
                        coins[f].append(GameObject(pg.Rect(500 + (i * 50), 255, 40, 40), "netut_coin.gif"))
                # populate infinite ring boxes
                if f not in ring_boxes:
                    ring_boxes[f] = [ring_box]
                # display coins
                for c in coins[f]:
                    if player.is_on_coin(c, f):
                        if pg.mixer:
                            coin_sound.play()
                        coins[f].remove(c)
                        score.update(1)
                    else:
                        c.draw(camera, screen, f)
                # display buy objects
                if f in buy_objects:
                    for o in buy_objects[f]:
                        if o[0].active:
                            o[0].draw(camera, screen, f)
                            if not modal.active and modal.buy_object_left != o[0] and player.is_on_object(o[0].pos, f):
                                modal.set_active(o[0], o[1])
                # display ring boxes
                for o in ring_boxes[f]:
                    if player.is_on_object(o.pos, f) and player.arm_up and player.bought_item_left:
                        if pg.mixer:
                            coin_sound.play()
                        ring_boxes[f].remove(o)
                        score.update(10)
                    else:
                        o.draw(camera, screen, f)

        # display buy modal
        if modal.active and modal.buy_object_left:
            modal.set_message(f"Buy {modal.buy_object_left.item_name} for {modal.buy_object_left.price} coins?")
            modal.draw(screen)
            if click:
                if modal.is_in_yes(mouse_pos[0], mouse_pos[1]):
                    modal.dismiss()
                    if modal.buy_object_left.price <= score.score:
                        modal.buy_object_left.deactivate()
                        if modal.buy_object_left.is_character:
                            pause.add_pause_character(modal.buy_object_left.name, modal.buy_object_left.item_name)
                        else:
                            player.buy_item(modal.buy_object_left, modal.buy_object_right)
                        score.update(-modal.buy_object_left.price)
                    else:
                        no_money_modal.set_active()
                if modal.is_in_no(mouse_pos[0], mouse_pos[1]):
                    modal.dismiss()

        # display "not enough money" modal
        if no_money_modal.active:
            no_money_modal.draw(screen)
            if click:
                if no_money_modal.is_in_ok(mouse_pos[0], mouse_pos[1]):
                    no_money_modal.dismiss()

        # make the player climb or fall
        if not pause.is_paused:
            if boss.active or barn.active:
                on_ladder = player.is_on_ladder(boss_ladder_left) or player.is_on_ladder(boss_ladder_right)
                on_top_of_ladder = player.is_on_top_of_ladder(boss_ladder_left) or player.is_on_top_of_ladder(boss_ladder_right)
                if on_ladder:
                    if climb_direction == 1 or not on_top_of_ladder:
                        player.climb(climb_direction)
                else:
                    if barn.active:
                        player.fall(barn_platform)
                    else:
                        player.fall(None)
            else:
                on_ladder = player.is_on_ladder(ladder)
                on_top_of_ladder = player.is_on_top_of_ladder(ladder)
                if on_ladder:
                    if climb_direction == 1 or not on_top_of_ladder:
                        player.climb(climb_direction)
                else:
                    player.fall(platform)

        # make the player die
        if player.should_die():
            health.lose_health()
            player.reset_fall()
            if pg.mixer:
                grunt_sound.play()

        # make the boss get hit or hit the player
        if boss.active and not pause.is_paused and cur_level != 5:
            if player.arm_up and player.bought_item_left and boss.is_on_player(player, 0):
                if boss.is_on_ground():
                    boss.set_won()
                elif not boss.falling:
                    boss.hit()
                    boss.change_direction()
                    if boss.health == 0:
                        boss.set_falling()
            elif boss.is_on_player(player, -60) and not boss.falling:
                health.lose_health()
                boss.change_direction()
                if pg.mixer:
                    grunt_sound.play()

        # make the final boss get hit or hit the player
        if boss.active and not pause.is_paused and cur_level == 5:
            on_top_of_ladder = player.is_on_top_of_ladder(boss_ladder_left) or player.is_on_top_of_ladder(boss_ladder_right)
            cur_time = get_time_millis()
            if player.arm_up and player.bought_item_left == enchanted_sword and on_top_of_ladder and (not final_boss_hit_time or cur_time - final_boss_hit_time > 3000):
                final_boss_direction *= -1
                final_boss_hit_time = cur_time
                final_boss_num_hits += 1
                if pg.mixer:
                    bounce_sound.play()
            elif player.is_on_final_boss() and player.is_hit(cur_time):
                health.lose_health()
                if pg.mixer:
                    grunt_sound.play()
                player.set_hit(cur_time)

        # make the player punch
        player.set_arm_up(space_pressed)

        # draw the player
        player.draw(direction, on_ladder, on_top_of_ladder, modal.active or no_money_modal.active, screen)

        # draw the boss
        if boss.active and cur_level != 5:
            boss.draw(screen)

        if click:
            if not pause.is_paused and pause.is_in_button(mouse_pos[0], mouse_pos[1]):
                pause.set_paused(True)
            elif pause.is_paused:
                if pause.is_in_resume_button(mouse_pos[0], mouse_pos[1]):
                    pause.set_paused(False)
                elif pause.is_in_sonic(mouse_pos[0], mouse_pos[1]):
                    player.set_player_image("sonic_right.png", "sonic_left.png", "sonic_right.png", "sonic_right.png", "sonic_left.png", "sonic_right.png", "sonic_right.png")
                    pause.set_paused(False)
                elif pause.is_in_neil_tut(mouse_pos[0], mouse_pos[1]):
                    player.set_player_image("netut_standing.gif", "netut_walking_left.gif", "netut_walking_right.gif", "netut_standing_arm_up.gif", "netut_walking_left_arm_up.gif", "netut_walking_right_arm_up.gif", "netut_climbing.gif")
                    pause.set_paused(False)
                elif pause.is_in_tails(mouse_pos[0], mouse_pos[1]):
                    player.set_player_image("tails_right.png", "tails_left.png", "tails_right.png", "tails_right.png", "tails_left.png", "tails_right.png", "tails_right.png")
                    pause.set_paused(False)
                elif pause.is_in_knuckles(mouse_pos[0], mouse_pos[1]):
                    player.set_player_image("knuckles_right.png", "knuckles_left.png", "knuckles_right.png", "knuckles_right.png", "knuckles_left.png", "knuckles_right.png", "knuckles_right.png")
                    pause.set_paused(False)
                elif pause.is_in_enchanted_tails(mouse_pos[0], mouse_pos[1]):
                    player.set_player_image("enchanted_character_right.png", "enchanted_character_left.png", "enchanted_character_right.png", "enchanted_character_right.png", "enchanted_character_left.png", "enchanted_character_right.png", "enchanted_character_right.png", 200, 150)
                    pause.set_paused(False)

        # draw the score and health and pause button
        score.draw(screen)
        health.draw(screen)
        pause.draw(screen)

        # Change to barn mode
        if cur_level == 5 and not boss.active:
            is_barn_on_player = pg.Rect(300, 0, 100, 600).colliderect(camera.pos)
            if not barn.active and space_pressed and not prev_space_pressed and is_barn_on_player:
                barn.activate()
                camera.reset()
                game_objects = [barn, boss_ladder_left, boss_ladder_right]
            if barn.active and not modal.active and not no_money_modal.active:
                if click:
                    if barn.is_in_blue_button(mouse_pos[0], mouse_pos[1]):
                        modal.set_active(enchanted_sword, enchanted_sword)
                    if barn.is_in_pink_button(mouse_pos[0], mouse_pos[1]):
                        modal.set_active(enchanted_character, enchanted_character)
                    if barn.is_in_back_button(mouse_pos[0], mouse_pos[1]):
                        barn.deactivate()
                        game_objects = [background_level_5, platform, ladder]
                        player.reset_pos()

        # Change to boss mode
        if not boss.active and score.score >= 100:
            screen.fill(pg.Color("Black"))
            if cur_level == 5:
                final_boss.draw(screen)
            else:
                boss_time.draw(screen)
            boss.activate()
            octopus.deactivate()
            if cur_level == 1:
                game_objects = [background, boss_ladder_left, boss_ladder_right]
            elif cur_level == 2:
                game_objects = [background_level_2, ground_level_2, boss_ladder_left, boss_ladder_right]
            elif cur_level == 3:
                game_objects = [background_level_3, ground_level_3, boss_ladder_left, boss_ladder_right]
            elif cur_level == 4:
                game_objects = [background_level_4, boss_ladder_left, boss_ladder_right]
            elif cur_level == 5:
                # FINAL BOSS
                game_objects = [final_boss_background, ground_level_2, boss_ladder_left, boss_ladder_right]
            coins = {}
            ring_boxes = {}
            buy_objects = {}
            player.reset_pos()
            camera.reset()
            pg.display.update()
            if pg.mixer:
                pg.mixer.music.fadeout(1000)
            pg.event.wait()
            pg.time.wait(3000)
            if pg.mixer:
                if cur_level == 5:
                    music = os.path.join(main_dir, "data", "Interstellar Odyssey.ogg")
                else:
                    music = os.path.join(main_dir, "data", "boss_music.wav")
                pg.mixer.music.load(music)
                pg.mixer.music.play(-1)

        # Change to next level
        if boss.won or final_boss_num_hits == 10:
            cur_level += 1
            screen.fill(pg.Color("Black"))
            coins = {}
            ring_boxes = {}
            player.reset_pos()
            player.reset_buy_item()
            camera.reset()
            score.reset()
            health.reset()
            boss.reset()
            if cur_level == 2:
                level_two.draw(screen)
                pg.display.update()
                if pg.mixer:
                    pg.mixer.music.fadeout(1000)
                pg.event.wait()
                pg.time.wait(3000)
                game_objects = [background_level_2, ground_level_2, platform, ladder]
                buy_objects = {2: [(axe_left, axe_right)], 4: [(sonic, sonic)]}
                if pg.mixer:
                    music = os.path.join(main_dir, "data", "Solve The Puzzle.ogg")
                    pg.mixer.music.load(music)
                    pg.mixer.music.play(-1)
            elif cur_level == 3:
                level_three.draw(screen)
                pg.display.update()
                if pg.mixer:
                    pg.mixer.music.fadeout(1000)
                pg.event.wait()
                pg.time.wait(3000)
                game_objects = [background_level_3, ground_level_3, platform, ladder]
                buy_objects = {-2: [(sword_left, sword_right)], 4: [(tails, tails)]}
                if pg.mixer:
                    music = os.path.join(main_dir, "data", "No Place For Straw Cowboys.ogg")
                    pg.mixer.music.load(music)
                    pg.mixer.music.play(-1)
            elif cur_level == 4:
                level_four.draw(screen)
                pg.display.update()
                if pg.mixer:
                    pg.mixer.music.fadeout(1000)
                pg.event.wait()
                pg.time.wait(3000)
                game_objects = [background_level_4, platform, ladder, octopus]
                octopus.activate()
                buy_objects = {4: [(shield, shield)], 5: [(knuckles, knuckles)]}
                if pg.mixer:
                    music = os.path.join(main_dir, "data", "Su Turno.ogg")
                    pg.mixer.music.load(music)
                    pg.mixer.music.play(-1)
            elif cur_level == 5:
                level_five.draw(screen)
                pg.display.update()
                if pg.mixer:
                    pg.mixer.music.fadeout(1000)
                pg.event.wait()
                pg.time.wait(3000)
                #score.update(99)
                game_objects = [background_level_5, platform, ladder]
                buy_objects = {}
                if pg.mixer:
                    music = os.path.join(main_dir, "data", "Humble Match.ogg")
                    pg.mixer.music.load(music)
                    pg.mixer.music.play(-1)
            elif cur_level == 6:
                you_win.draw(screen)
                pg.display.update()
                if pg.mixer:
                    pg.mixer.music.fadeout(1000)
                pg.event.wait()
                pg.time.wait(3000)
                screen.fill(pg.Color("Black"))
                poster.draw(screen)
                pg.display.update()
                pg.event.wait()
                pg.time.wait(10000)
                pg.quit()

        pg.display.update()
        clock.tick(40)

    screen.fill(pg.Color("Black"))
    game_over.draw(screen)
    pg.display.update()

    if pg.mixer:
        pg.mixer.music.fadeout(1000)
    pg.event.wait()
    pg.time.wait(5000)
    pg.quit()


if __name__ == "__main__":
    main()