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

    def __init__(
        self, standing, walking_left, walking_right,
        standing_arm_up, walking_left_arm_up, walking_right_arm_up,
        climbing, climb_speed, fall_speed, camera
    ):
        self.image_standing = load_image(standing, 100, 150)
        self.image_walking_left = load_image(walking_left, 100, 150)
        self.image_walking_right = load_image(walking_right, 100, 150)
        self.image_standing_arm_up = load_image(standing_arm_up, 100, 150)
        self.image_walking_left_arm_up = load_image(walking_left_arm_up, 100, 150)
        self.image_walking_right_arm_up = load_image(walking_right_arm_up, 100, 150)
        self.image_climbing = load_image(climbing, 120, 150)
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

    def draw(self, direction, on_ladder, modal_active, screen):
        if not modal_active:
            if direction < 0:
                if self.arm_up:
                    screen.blit(self.image_walking_left_arm_up, self.pos)
                else:
                    screen.blit(self.image_walking_left, self.pos)
                if self.bought_item_left:
                    screen.blit(self.bought_item_left.image, self.bought_item_left_pos)
            elif direction > 0:
                if self.arm_up:
                    screen.blit(self.image_walking_right_arm_up, self.pos)
                else:
                    screen.blit(self.image_walking_right, self.pos)
                if self.bought_item_right:
                    screen.blit(self.bought_item_right.image, self.bought_item_right_pos)
            elif on_ladder:
                screen.blit(self.image_climbing, self.pos)
            else:
                if self.arm_up:
                    screen.blit(self.image_standing_arm_up, self.pos)
                else:
                    screen.blit(self.image_standing, self.pos)
                if self.bought_item_right:
                    screen.blit(self.bought_item_right.image, self.bought_item_right_pos)

    def climb(self, direction):
        self.pos = self.pos.move(0, self.climb_speed * direction)
        # make sure we don't go beneath the ground or above the sky
        if self.pos.bottom > Player.ground:
            self.pos.bottom = Player.ground
        elif self.pos.top < Player.sky:
            self.pos.top = Player.sky
        if self.arm_up:
            self.bought_item_left_pos = self.pos.move(-30, 25)
            self.bought_item_right_pos = self.pos.move(80, 25)
        else:
            self.bought_item_left_pos = self.pos.move(-30, 50)
            self.bought_item_right_pos = self.pos.move(80, 50)

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
        if self.arm_up:
            self.bought_item_left_pos = self.pos.move(-30, 25)
            self.bought_item_right_pos = self.pos.move(80, 25)
        else:
            self.bought_item_left_pos = self.pos.move(-30, 50)
            self.bought_item_right_pos = self.pos.move(80, 50)

    def buy_item(self, left, right):
        self.bought_item_left = left
        self.bought_item_left_pos = self.pos.move(-30, 50)
        self.bought_item_right = right
        self.bought_item_right_pos = self.pos.move(80, 50)

    def set_arm_up(self, arm_up):
        changed = self.arm_up != arm_up
        self.arm_up = arm_up
        if changed and self.bought_item_left_pos and self.bought_item_right_pos:
            if arm_up:
                self.bought_item_left_pos = self.bought_item_left_pos.move(0, -25)
                self.bought_item_right_pos = self.bought_item_right_pos.move(0, -25)
            else:
                self.bought_item_left_pos = self.bought_item_left_pos.move(0, 25)
                self.bought_item_right_pos = self.bought_item_right_pos.move(0, 25)

    def is_on_object(self, pos, frame=None):
        arr = self.camera.adjust(pos)
        if frame:
            arr = list(filter(lambda x: x[0] == frame, arr))
        return any(self.pos.colliderect(a[1]) for a in arr)

    def is_on_ladder(self, ladder):
        return self.is_on_object(ladder.pos.inflate(-50, -50))

    def is_above_platform(self, platform):
        arr = self.camera.adjust(platform.pos)
        return any(self.pos.right > p[1].left+10 and self.pos.left < p[1].right-10 and self.pos.bottom < p[1].bottom - 30 for p in arr)

    def is_on_coin(self, coin, frame):
        return self.is_on_object(coin.pos.inflate(-10, -10), frame)

    def should_die(self):
        return self.total_fall >= 200

class GameObject:
    def __init__(self, pos, name):
        self.pos = pos
        self.image = load_image(name, pos.width, pos.height)
        self.active = True

    def deactivate(self):
        self.active = False

    def draw(self, camera, screen, frame = None):
        for o in camera.adjust(self.pos):
            if not frame or frame == o[0]:
                screen.blit(self.image, o[1])

class BuyObject(GameObject):
    def __init__(self, pos, name, item_name, price):
        super().__init__(pos, name)
        self.price = price
        self.item_name = item_name

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
            return True
        elif self.pos.left < 0:
            self.pos.left = 800
            self.frame -= 1
            return True
        return False

    def adjust(self, rect):
        arr = [
          (self.frame - 1, rect.move(-self.pos.left - 800, 0)),
          (self.frame, rect.move(-self.pos.left, 0)),
          (self.frame + 1, rect.move(-self.pos.left + 800, 0))
        ]
        return list(filter(lambda x: x[1].left < 800 and x[1].right > 0, arr))

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
        self.buy_object = None
        
        self.font = pg.font.Font(font_name, font_size)
        self.font.set_bold(1)

        self.yes_image = self.font.render("Yes", 0, pg.Color("Yellow"))
        self.yes_pos = self.yes_image.get_rect().move(pos.left + 50, pos.bottom - 50)

        self.no_image = self.font.render("No", 0, pg.Color("Yellow"))
        self.no_pos = self.no_image.get_rect().move(pos.right - 90, pos.bottom - 50)

    def set_active(self, buy_object):
        self.active = True
        self.buy_object = buy_object

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
    ring_box = GameObject(pg.Rect(900, 450, 75, 75), "coin_box.gif")
    hammer_left = BuyObject(pg.Rect(700, 460, 50, 50), "hammer_left.gif", "hammer", 10)
    hammer_right = BuyObject(pg.Rect(700, 460, 50, 50), "hammer_right.gif", "hammer", 10)
    game_objects = [background, ladder, platform]
    coins = {}
    buy_objects = {1: [hammer_right]}
    ring_boxes = {}

    camera = Camera(background, 10)
    player = Player(
        "netut_standing.gif", "netut_walking_left.gif", "netut_walking_right.gif", 
        "netut_standing_arm_up.gif", "netut_walking_left_arm_up.gif", "netut_walking_right_arm_up.gif",
        "netut_climbing.gif", 5, 20, camera)
    score = Score(None, 40)
    health = Health(3, "netut_heart.gif")
    modal = YesNoModal(pg.Rect(150, 100, 450, 200), None, 40)
    no_money_modal = OkModal(pg.Rect(150, 100, 500, 150), None, 40, "You don't have enough coins.")
    game_over = EndScreen(None, 60, "Game Over")
    you_win = EndScreen(None, 60, "You Win!")

    while health.health > 0 and score.score < 100:
        click = False
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

        # move the camera
        if not modal.active and not no_money_modal.active:
            if camera.move(direction):
                # reset the buy modal so it pops up again
                modal.buy_object = None

        # display each static game object, including the background
        for g in game_objects:
            g.draw(camera, screen)

        # display each stateful game object
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
                    if o.active:
                        o.draw(camera, screen, f)
                        if not modal.active and modal.buy_object != o and player.is_on_object(o.pos, f):
                            modal.set_active(o)
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
        if modal.active and modal.buy_object:
            modal.set_message(f"Buy {modal.buy_object.item_name} for {modal.buy_object.price} coins?")
            modal.draw(screen)
            if click:
                if modal.is_in_yes(mouse_pos[0], mouse_pos[1]):
                    modal.dismiss()
                    if modal.buy_object.price <= score.score:
                        modal.buy_object.deactivate()
                        player.buy_item(hammer_left, modal.buy_object)  # TODO
                        score.update(-modal.buy_object.price)
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
        on_ladder = player.is_on_ladder(ladder)
        if on_ladder:
            player.climb(climb_direction)
        else:
            player.fall(platform)

        # make the player die
        if player.should_die():
            health.lose_health()
            if pg.mixer:
                grunt_sound.play()

        # make the player punch
        player.set_arm_up(space_pressed)

        # draw the player
        player.draw(direction, on_ladder, modal.active or no_money_modal.active, screen)

        # draw the score and health
        score.draw(screen)
        health.draw(screen)

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
