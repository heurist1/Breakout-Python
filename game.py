"""Break out Game
  - Player Name Prompt
  - 10 by 10 bricks set up
"""


from __future__ import division
import math
import sys
#import os
import pygame
import random
#import operator

def draw_center(surface1, surface2, color):
    """Draw surface1 onto surface2 with center at position"""
    rect = surface1
    rect = pygame.draw.rect(surface2, color, rect, 1)
    surface2.fill(color, rect)

def load_image(image):
    return pygame.image.load(image).convert()

#########
class GameObject(object):
    def __init__(self, position, rect, color):
        self.position = list(position[:])
        self.rect = rect
        self.color = None
    
    def draw_on(self, screen, color):
        draw_center(self.rect, screen, color)

class Ball(GameObject):
    def __init__(self, position, image, rect = None, color = None):
        super(Ball, self).__init__(position, rect, color)
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.speed = 8
        self.velocity = [1, 1]

    def draw_on(self, screen, position):
        rect = self.image.get_rect()
        rect.centerx = position[0]
        rect.centery = position[1]
        self.rect = rect
        screen.blit(self.image, rect)
        #screen.fill(self.color, self.rect)

    def radius(self):
        return self.rect.width/2


    def move(self, length):
        mouse_pos = pygame.mouse.get_pos()
        v = self.velocity
        #convert vector to a new vector of magnitude 10
        mag_v = math.sqrt(v[0]**2 + v[1]**2)
        a = mag_v/length
        v = v[0]/a, v[1]/a
        self.position[0] += v[0]
        self.position[1] += v[1]
           
        """Do one frame's worth of updating for the ball"""

class Brick(GameObject):
    def __init__(self, position, rect, strength=0, power_up=None, color = None):
        super(Brick, self).__init__(position, rect, color)
        self.strength = strength
        self.power_up = power_up
        self.speed_x = 0

class Paddle(Brick):
    def __init__(self, position, rect, color = None):
        super(Paddle, self).__init__(position, rect)
        self.velocity = [1, 0]

class PowerUp(GameObject):
    def __init__(self, position, rect, type, duration, color = (255,255,255)):
        super(PowerUp, self).__init__(position, rect, color)
        self.type = type
        self.color = None
        self.label = None
        self.duration = duration
        self.velocity = [0, 5]

    def draw_on(self, screen, color):
        screen.blit(self.label, self.rect)

class MyGame(object):
    def __init__(self):
        """Initialize a new game"""
        pygame.mixer.init()
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()
        
        # set up a 640 x 480 window
        self.width = 450
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Break Out")
        
        # use a black background
        self.bg_color = 0, 0, 0
        
        # Setup a timer to refresh the display FPS times per second
        self.FPS = 60
        self.REFRESH = pygame.USEREVENT+1
        self.Power_UP_SHOWER = pygame.USEREVENT+2
        self.NEW_HIGH_SCORE_SHOWER = pygame.USEREVENT+3
        self.BACKGROUND_CHANGE = pygame.USEREVENT+4
        
        pygame.time.set_timer(self.REFRESH, 1000//self.FPS)
        pygame.time.set_timer(self.BACKGROUND_CHANGE, 6000)
        
        self.game_images = ["img1.jpeg", "img2.jpeg", "img3.jpeg", "img4.jpeg", "img5.jpeg",\
                            "img6.jpeg", "img7.jpeg", "img8.jpeg", "img9.jpeg", "img10.jpeg",\
                            "img11.jpeg"]
        self.sound = None
        self.level = 1
        self.bricks = []
        self.moveable_bricks = []
        self.visible_pu = []
        self.paddle = None
        self.balls = []
        self.mouse_pos = [self.width/2, 0]
        self.score = 0
        self.state = False
        self.lives = 2
        self.name = ""
        self.playing = False
        self.missile = 0
        self.missiles = []
        self.newLevel = False
        self.picked_pu = None
        self.new_record = False
        self.shown_high_score = False
        self.img_count = 0
        self.game_image = load_image(self.game_images[self.img_count])
        self.background_image = load_image("background.png")
        self.image = load_image("image.png")
        self.play_button = None
        self.play_rect = None



################################################################################################
# Drawing code
################################################################################################
    
    def make_label(self, size, text, color, underline = False, bg_color = None):
        myfont = pygame.font.Font("bones.ttf", size)
        myfont.set_underline(underline)
        if(bg_color == None): label = myfont.render(text, 1, color)
        else: label = myfont.render(text, 1, color, bg_color)
        return label, label.get_rect()
    
    def score_game(self):
        # draw score on the canvas
        score = "Score: %d" %self.score
        label, label_rect = self.make_label(20, score, (255, 255, 255))
        label_rect.topleft = (0, 0)
        self.screen.blit(label, label_rect)
    
    def lives_left(self):
        # draw score on the canvas
        lives_left = "Lives Left: %d" %self.lives
        label, label_rect = self.make_label(20, lives_left, (255, 255, 255))
        label_rect.topleft = (0,20)
        self.screen.blit(label, label_rect)
    
    
    def show_level(self):
        level = "Level : %d" %self.level
        label, label_rect = self.make_label(20, level, (255, 255, 255))
        label_rect.topleft = ((self.width - label_rect.width)/2, 0)
        self.screen.blit(label, label_rect)
    
    def end_level(self):
        self.state = False
        level_cleared = "Level %d cleared!!!" %self.level
        label, label_rect = self.make_label(50, level_cleared, (255, 0, 0))
        label_rect.topleft = ((self.width - label_rect.width)/2, (self.height - label_rect.height)/2)
        self.screen.blit(label, label_rect)

    def show_missile_info(self):
        # draw missile info on the canvas
        missiles_left = "missiles left: %d" %self.missile
        label, label_rect = self.make_label(20, missiles_left, (255,255,255))
        label_rect.topleft = (self.width - label_rect.width, 0)
        self.screen.blit(label, label_rect)

    def draw_power_up_on_screen(self, power_up):
        label, label_rect = self.make_label(100, power_up.type, power_up.color)
        label_rect.topleft = ((self.width - label_rect.width)/2, (self.height - label_rect.height)/2)
        self.screen.blit(label, label_rect)
        
        
    def draw_new_high_score_on_screen(self):
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        new_highscore = "New HighScore!!!!"
        label, label_rect = self.make_label(45, new_highscore, color)
        label_rect.topleft = ((self.width - label_rect.width)/2, (self.height - label_rect.height)/2 - 50)
        self.screen.blit(label, label_rect)


    def game_over(self):
        # draw Game Over on the canvas
        self.set_score(self.name, self.score)
        self.screen.fill((0,0,0))
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        rect = self.image.get_rect()
        rect.topleft = (self.width - rect.width)/2, (self.height - rect.height)/4
        self.screen.blit(self.image, rect)
        
        label, label_rect = self.make_label(50, "Game Over!!!!", color)
        label_rect.topleft = ((self.width-label_rect.width)/2, (self.height-label_rect.height)/2)
        self.screen.blit(label, label_rect)
        
        score = "Your Score was: %s" %int(self.score)
        score_label, score_label_rect = self.make_label(30, score, (255, 255, 255))
        score_label_rect.topleft = (self.width - score_label_rect.width)/2, (self.height - score_label_rect.height)*3/4
        self.screen.blit(score_label, score_label_rect)
        
        prompt, prompt_rect = self.make_label(30, "Click to Play Again...", (255, 0, 0))
        prompt_rect.bottomleft = (self.width - prompt_rect.width)/2, self.height
        self.screen.blit(prompt, prompt_rect)

    def draw_prompt(self, color):
        #draw a prompt on the screen
        label, label_rect = self.make_label(25, "Click To Start", color)
        label_rect.topleft = ((self.width - label_rect.width)/2,(self.height - label_rect.height)/2)
        self.screen.blit(label, label_rect)

    def show_scores(self):
        label, label_rect = self.make_label(25, "High Scores", (0 ,0 , 255), True)
        label_rect.topleft = ((self.width - label_rect.width)/2, 0)
        self.screen.blit(label, label_rect)
        scores, high_scorers = self.get_score_list()
        y_pos = label_rect.bottom
        for name in high_scorers:
            name_string = "%s :" %name
            score_label, score_label_rect = self.make_label(18, name_string, (0, 104, 139))
            score_label_rect.topright = ((self.width)/2, y_pos)
            self.screen.blit(score_label, score_label_rect)
            
            num_string = " %d" %int(scores[name])
            num_label, num_label_rect = self.make_label(18, num_string, (0, 104, 139))
            num_label_rect.topleft = ((self.width)/2, y_pos)
            self.screen.blit(num_label, num_label_rect)
            y_pos = score_label_rect.bottom



    def show_projectile(self):
        v = self.mouse_pos[0] - self.balls[0].position[0], self.mouse_pos[1] - self.balls[0].position[1]
        mag_v = math.sqrt(v[0]**2 + v[1]**2)
        a = mag_v/20
        v = v[0]/a, v[1]/a
        v = [self.balls[0].position[0] + v[0], self.balls[0].position[1] + v[1]]
        pygame.draw.line(self.screen, (0, 0, 0), self.balls[0].position, v, 1)



    def draw_startup(self):
        """Update the display"""
        # everything we draw now is to a buffer that is not displayed
        image_rect = self.background_image.get_rect()
        self.screen.blit(self.background_image, image_rect)
        self.show_scores()
        
        label, label_rect = self.make_label(25, "Enter Your Name:", (0 ,0 ,255), True)
        label_rect.topleft = ((self.width - label_rect.width)/2,(self.height - label_rect.height)/2)
        self.screen.blit(label, label_rect)
        
        name = "%s" %self.name
        input_label, input_label_rect = self.make_label(25, name, (0 ,0 , 255))
        input_label_rect.topleft = ((self.width - input_label_rect.width)/2,label_rect.bottom)
        self.screen.blit(input_label, input_label_rect)
        
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.play_button, self.play_rect = self.make_label(25, "Play", color, False, (0 ,0 , 255))
        self.play_rect.topleft = (self.width - self.play_rect.width)/2, input_label_rect.bottom
        self.screen.blit(self.play_button, self.play_rect)
        
        pygame.display.flip()



    def draw(self):
        """Update the display"""
        # everything we draw now is to a buffer that is not displayed
        img_rect = self.game_image.get_rect()
        self.screen.blit(self.game_image, img_rect)
        #self.screen.fill(self.bg_color)
        self.paddle.draw_on(self.screen, self.paddle.color)
        if(len(self.bricks) == 0):
            self.end_level()
        else:
            if(self.new_record == True):
                self.draw_new_high_score_on_screen()
            if(self.missile > 0): self.show_missile_info()
            for bullet in self.missiles:
                bullet.draw_on(self.screen, bullet.position)
            for ball in self.balls:
                ball.draw_on(self.screen, ball.position)
            self.show_level()
            self.score_game()
            self.lives_left()
            for brick in self.bricks:
                brick.draw_on(self.screen, brick.color)
            for pu in self.visible_pu:
                pu.draw_on(self.screen, pu.color)
            if(not self.picked_pu == None):
                self.draw_power_up_on_screen(self.picked_pu)
            if(not self.state):
                if(self.lives == 2 or self.newLevel): self.show_projectile()
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                self.draw_prompt(color)
            if(self.lives < 0 and not self.state):
                self.game_over()
        pygame.display.flip()

################################################################################################



    def start_game(self):
        self.bricks = []
        self.moveable_bricks = []
        n_brick_row = 10
        n_brick_column = 10
        brick_gap = 1
        brick_width = 40
        brick_height = 20
        paddle_width = 55
        paddle_height = 10
        color = [(255,0,0), (255, 182, 193), (251,165,0), (218, 165, 32), (255,255,0), (0, 255, 255), (0,255,0), (153, 50, 204), (0,0,255)]
        types = [["missile", 10000], ["ooo", 10000], ["pad++", 10000], ["speed++", 10000], ["live++", 10000]]
        
        formation = []
        
        for i in range(10):
            row_formation = []
            for j in range(10):
                row_formation.append(random.randint(-1, 0))
            formation.append(row_formation)

        for i in range(int(math.ceil(10 * (self.level-1)/10)) * 2):
            row = random.randint(0, 9)
            column = random.randint (0, 9)
            formation[row][column] = self.level

        """Game start up  code here"""
        for i in range(n_brick_row):
            y_pos = 50 + (brick_gap + brick_height)*i
            x_pos = (self.width - ((brick_width * n_brick_column) + (brick_gap * (n_brick_column+1))))/2
            for j in range(n_brick_column):
                position = [x_pos, y_pos]
                rect = pygame.Rect((position[0], position[1])\
                                   ,(brick_width, brick_height))
                if (formation[i][j] == -1):
                    brick = Brick(position, rect)
                    brick.color = color[random.randint(0, len(color)-1)]
                    self.bricks.append(brick)
                
                elif(formation[i][j] == self.level):
                    brick = Brick(position, rect)
                    brick.color = (0, 0, 0)
                    brick.strength = 2
                    self.bricks.append(brick)
                
                
                
                    if(i*j % self.level == 0):
                        x = random.randint(0, self.width - brick_width)
                        y = random.randint(self.height/2 - 50, self.height - 250)
                        new_rect = pygame.Rect((x, y), (brick_width, brick_height))
                        new_brick = Brick([x, y], new_rect)
                        new_brick.color = (205, 205, 193)
                        new_brick.strength = 10000
                        new_brick.speed_x = random.randint(-self.level, self.level)
                        self.bricks.append(new_brick)
                        self.moveable_bricks.append(new_brick)
                

                x_pos += brick_width + brick_gap

        position = [(self.width- paddle_width)/2, self.height - (20 + paddle_height)]
        rect = pygame.Rect((position[0], position[1]), (paddle_width, paddle_height))
        self.paddle = Paddle(position, rect)
        self.paddle.color = (255,255,255)
    
        self.balls.append(Ball([], "ball.png"))
        position = [int((self.paddle.position[0] + paddle_width/2)),\
                    self.paddle.rect.top - self.balls[0].radius()]
        self.balls[0].position = position
        
        #set Power ups
        for i in range(10):
            brick_num = random.randint(0, len(self.bricks)-1)
            brick = self.bricks[brick_num]
            if(brick.power_up == None and not brick.color == (0, 0, 0) and not brick.color == (205, 205, 193)):
                pos = [brick.position[0] + brick.rect.width/2, brick.position[1]\
                       + brick.rect.height/2]
                num = random.randint(0, (len(types)-2))
                if(i == 9):
                    if(self.level%2 == 0): num = len(types)-1
                type = types[num][0]
                duration = types[num][1]
                
                label, rect = self.make_label(15, type, brick.color)
                rect.center = pos
                power = PowerUp(pos, rect, type, duration)
                power.label = label
                power.color = brick.color
                brick.power_up = power

    def run(self):
        """Loop forever processing events"""
        while True:
            event = pygame.event.wait()
            
            # player is asking to quit
            if event.type == pygame.QUIT:
                self.playing = False
                break
            
            # time to draw a new frame
            elif (event.type == self.REFRESH and self.playing == True):
                self.mouse_pos = pygame.mouse.get_pos()
                if(self.state):
                    self.paddle.velocity[0] = (self.mouse_pos[0] - (self.paddle.position[0]+self.paddle.rect.width/2))
                    self.paddle.position[0] = self.mouse_pos[0]- self.paddle.rect.width/2
                    self.paddle.rect.left = self.paddle.position[0]
                    self.physics()
                self.draw()
    
    
            elif (event.type == self.Power_UP_SHOWER):
                pygame.time.set_timer(self.Power_UP_SHOWER, 0)
                self.picked_pu = None
    
            elif (event.type == self.NEW_HIGH_SCORE_SHOWER):
                pygame.time.set_timer(self.NEW_HIGH_SCORE_SHOWER, 0)
                self.new_record = False
                self.shown_high_score = True
        
    
            elif (event.type == self.REFRESH and self.playing == False):
            	self.draw_startup()
            
            
            elif (event.type == pygame.MOUSEBUTTONUP and self.playing == False):
                if(self.play_rect.collidepoint(event.pos)):
                    if(not self.name == ""):
                        self.playing = True
                        self.setup_player()
                        self.bg_color = (255, 255, 255)
                        self.start_game()
            
            
            elif (event.type == pygame.MOUSEBUTTONUP and self.state == False\
                  and self.playing == True and not len(self.bricks) == 0):
                if(self.lives == 2 or self.newLevel):
                    self.state = True
                    pos = event.pos
                    v = [pos[0]-self.balls[0].position[0], pos[1]-self.balls[0].position[1]]
                    self.balls[0].velocity = v
                    self.newLevel = False
                    self.play_music()
                elif(self.lives < 2 and self.lives >= 0):
                    self.state = True
                    self.play_music()
                else:
                    self.sound.stop()
                    self.sound = None
                    self.visible_pu = []
                    self.balls = []
                    self.bricks = []
                    self.lives = 2
                    self.score = 0
                    self.level = 1
                    self.img_count = 0
                    self.game_image = load_image(self.game_images[self.img_count])
                    self.newLevel = False
                    self.start_game()
                
            elif (event.type == pygame.MOUSEBUTTONUP and self.state == True\
                  and self.playing == True and self.missile > 0):
                self.shoot_missile()
                self.missile -= 1
                  
            elif (event.type == pygame.MOUSEBUTTONUP and self.state == False \
                  and self.playing == True and len(self.bricks) == 0):
                
                if(self.img_count < len(self.game_images)-1):
                    self.img_count += 1
                else: self.img_count = 0
                self.game_image = load_image(self.game_images[self.img_count])
                
                self.img_count
                self.visible_pu = []
                self.balls = []
                self.bricks = []
                self.missile = 0
                self.missiles = []
                self.level += 1
                self.newLevel = True
                self.start_game()
                pygame.mixer.music.stop()
              
            
            elif (event.type == pygame.KEYUP and self.playing == False):
                if(event.key >= pygame.K_a and event.key <= pygame.K_z):
                    self.name += pygame.key.name(event.key)
                
            	elif(event.key == pygame.K_RETURN):
                    if(not self.name == ""):
                        self.playing = True
                        self.setup_player()
                        self.bg_color = (255, 255, 255)
                        self.start_game()
                
                elif(event.key == pygame.K_BACKSPACE):
                    self.name = self.name[:len(self.name)-1]
                
                # player is asking to quit
                elif(event.key == pygame.K_ESCAPE):
                    break
            
            else:
                pass # an event type we don't handle

    def shoot_missile(self):
        position = [0, 0]
        position[0] = self.paddle.position[0] + self.paddle.rect.width/2
        position[1] = self.paddle.position[1]
        bullet = Ball(position, "bullet.png")
        bullet.velocity = [0, 0 - bullet.position[1]]
        self.missiles.append(bullet)
    


    def set_score(self, player_name, score):
        """This function writes the score and the players name into a text file"""
        high_scores = self.get_score_list()[0]
        
        if(not player_name in high_scores.keys()):
            high_scores[player_name] = score
        
        if(len([x for x in high_scores.values() if int(x) >= score]) == 0):
            if(self.shown_high_score == False and self.new_record == False):
                self.play_high_score_sound()
                pygame.time.set_timer(self.NEW_HIGH_SCORE_SHOWER, 1000)
                self.new_record = True
        
        if(score >= int(high_scores[player_name])):
            high_scores[player_name] = score
            f = open("scores.txt", 'w')
            for key in high_scores.keys():
                line = "%s = %d" %(key, int(high_scores[key]))
                f.write(line)
                f.write("\n")
            f.close()

    def sort_scores(self, scores):
        sorted_scores = sorted(scores.items(), key = lambda x: x[1], reverse = True)
        if(len(sorted_scores) > 10): sorted_scores = sorted_scores[:10]
        return [x[0] for x in sorted_scores]

    def get_score_list(self):
        """this function gets the persistent scores of the game
            from a text file and saves it as a {name : score} pair in a dictionary"""
        scores = {}
        f = open("scores.txt", 'r')
        for line in f:
            k, v = line.strip().split('=')
            scores[k.strip()] = int(v.strip())
        f.close()
        high_scorers = self.sort_scores(scores)
        return scores, high_scorers

    def setup_player(self):
        """This function is responsible for making a new entry for a new player
            or to detect if a former player has just returned"""
        scores, high_scorers = self.get_score_list()
            # while True:
        highScore = {high_scorers[0]: scores[high_scorers[0]]}
        player_name = str(self.name)
        player_name = player_name.strip()

    def make_balls(self):
        position = [0, 0]
        position[0] = self.paddle.position[0] + self.paddle.rect.width/2
        position[1] = self.paddle.position[1] + self.balls[0].radius()
        num = 10 - len(self.balls)
        for i in range(num):
            ball = Ball(position, "ball.png")
            x_pos = random.randint(0, self.width)
            y_pos = random.randint(0, self.height/2)
            v = [x_pos - ball.position[0], y_pos - ball.position[1]]
            ball.velocity = v
            ball.speed = self.balls[0].speed
            self.balls.append(ball)
            


    def continue_play(self):
        self.visible_pu = []
        paddle_width = 55
        self.balls[0].position = [self.width/2, self.height/2]
        self.balls[0].velocity[0] = 0
        self.paddle.rect.width = paddle_width
        self.missile = 0
        self.missiles = []
        self.balls[0].speed = 8
    
    def process_power(self, power_up):
        if(power_up.type == "missile"):
            self.missile += 5
        elif(power_up.type == "ooo"):
            self.make_balls()
        elif(power_up.type == "pad++"):
            if self.paddle.rect.width < 120:
                self.paddle.rect.width += 20
        elif(power_up.type == "speed++"):
            for ball in self.balls:
                ball.speed += 5
        elif(power_up.type == "live++"):
                self.lives += 1

    def check_for_collisions(self, ball, item):
        
        # check collision with certain areas of the block/paddle
        cornerwidth = item.rect.width/32
        cornerheight = item.rect.height/32
        
        # if the item is the paddle, apply some of its velocity to the ball
        if hasattr(item, 'velocity'):
            ball.velocity[0] += item.velocity[0]*0.5


        # test corners first
        # if the ball hit the top left
        
        """if ball.rect.colliderect( pygame.Rect(item.rect.left, item.rect.top, cornerwidth, cornerheight) ):"""
        if ball.rect.collidepoint(item.rect.topleft):
            speed = math.hypot(ball.velocity[0], ball.velocity[1])
            component = speed * .7071
            if ball.velocity[0] >= 0:
                ball.velocity [0] = -component
            if ball.velocity[1] >= 0:
                ball.velocity[1] = -component
            # move out of collision
            ball.rect.bottom = item.rect.top -1
            ball.position[1] = ball.rect.bottom - ball.radius()
            return
        
        # if the ball hit the top right
        """if ball.rect.colliderect( pygame.Rect(item.rect.right-cornerwidth, item.rect.top, cornerwidth, cornerheight) ):"""
        if(ball.rect.collidepoint(item.rect.topright)):
            speed = math.hypot(ball.velocity[0], ball.velocity[1])
            component = speed * .7071
            if ball.velocity[0] <= 0:
                ball.velocity[0] = component
            if ball.velocity[1] >= 0:
                ball.velocity[1] = -component
            # move out of collision
            ball.rect.bottom = item.rect.top -1
            ball.position[1] = ball.rect.bottom - ball.radius()
            return
        
        # if the ball hit the bottom left
        """if ball.rect.colliderect( pygame.Rect(item.rect.left, item.rect.bottom-cornerheight, cornerwidth, cornerheight) ):"""
        if(ball.rect.collidepoint(item.rect.bottomleft)):
            speed = math.hypot(ball.velocity[0], ball.velocity[1])
            component = speed * .7071
            if ball.velocity[0] >= 0:
                ball.velocity[0] = -component
            if ball.velocity[1] <= 0:
                ball.velocity[1] = component
            # move out of collision
            ball.rect.top  = item.rect.bottom + 1
            ball.position[1] = ball.rect.top + ball.radius()
            return
        
        # if the ball hit the bottom right
        """if ball.rect.colliderect( pygame.Rect(item.rect.right, item.rect.bottom-cornerheight, cornerwidth, cornerheight) ):"""
        if(ball.rect.collidepoint(item.rect.bottomright)):
            speed = math.hypot(ball.velocity[0], ball.velocity[1])
            component = speed * .7071
            if ball.velocity[0] <= 0:
                ball.velocity[0] = component
            if ball.velocity[1] <= 0:
                ball.velocity[1] = component
            # move out of collision
            ball.rect.top = item.rect.bottom + 1
            ball.position[1] = ball.rect.top + ball.radius()
            return
        
        # if the ball hit the top edge
        if ball.rect.colliderect( pygame.Rect(item.rect.left, item.rect.top, item.rect.width, cornerheight) ):
            ball.velocity[1] *= -1
            # move out of collision
            ball.rect.bottom = item.rect.top - 1
            ball.position[1] = ball.rect.bottom - ball.radius()
            return
        
        # if the ball hit the bottom edge
        elif ball.rect.colliderect( pygame.Rect(item.rect.left, item.rect.bottom-cornerheight, item.rect.width, cornerheight) ):
            ball.velocity[1] *= -1
            # move out of collision
            ball.rect.top = item.rect.bottom + 1
            ball.position[1] = ball.rect.top + ball.radius()
            return
        
        # if the ball hit the left side
        if ball.rect.colliderect(pygame.Rect(item.rect.left, item.rect.top, cornerwidth, item.rect.height)):
            ball.velocity[0] *= -1
            # move out of collision
            ball.rect.right = item.rect.left - 1
            ball.position[0] = ball.rect.right - ball.radius()
            return
        
        # if the ball hit the right side
        elif ball.rect.colliderect(pygame.Rect(item.rect.right-cornerwidth, item.rect.top, cornerwidth, item.rect.height)):
            ball.velocity[0] *= -1
            # move out of collision
            ball.rect.left = item.rect.right + 1
            ball.position[0] = ball.rect.left + ball.radius()
            return

    def physics(self):
        """Do in-game physics here"""
        
        # move moveable_bricks
        for brick in self.moveable_bricks:
            brick.rect = brick.rect.move(brick.speed_x, 0)
        
            if(brick.rect.right >= self.width): brick.speed_x = -brick.speed_x
            elif(brick.rect.left <= 0): brick.speed_x = -brick.speed_x
        
            if(self.moveable_bricks == self.bricks):
                self.moveable_bricks = []
                self.bricks = []
        
        # move visible power_ups
        for pu in self.visible_pu:
            pu.rect = pu.rect.move(pu.velocity)
            if(self.paddle.rect.colliderect(pu)):
                pygame.time.set_timer(self.Power_UP_SHOWER, 1000)
                self.play_power_up_sound()
                self.process_power(pu)
                self.picked_pu = pu
                self.visible_pu.remove(pu)
    
        # move visible missiles
        for bullet in self.missiles:
            bullet.move(15)
            for brick in self.bricks:
                if bullet.rect.colliderect(brick.rect):
                    if(not brick.power_up == None):
                        self.visible_pu.append(brick.power_up)
                        self.score += brick.strength * 25
                        self.set_score(self.name, self.score)
                    if(brick.strength == 0):
                        self.score += brick.strength * 25
                        self.set_score(self.name, self.score)
                        self.bricks.remove(brick)
                    elif(brick.strength > 1000):
                        self.bricks.remove(brick)
                        self.moveable_bricks.remove(brick)
                    else:
                        brick.strength -= 1
                        self.score += brick.strength * 25
                        self.set_score(self.name, self.score)
                    self.missiles.remove(bullet)
    
        # move visible balls
        for ball in self.balls:
            ball.move(ball.speed)

            if self.paddle.rect.colliderect(ball.rect):
				oldVal = ball.velocity[1]
                self.check_for_collisions(ball, self.paddle)
				if oldVal==ball.velocity[1]:
					print('Paddle failed')
					ball.velocity[1] *= -1
					# move out of collision
					ball.rect.bottom = self.paddle.rect.top - 1
					ball.position[1] = ball.rect.bottom - ball.radius()
                self.play_sound()
            
            for brick in self.bricks:
                if(brick.rect.colliderect(ball.rect)):
                    self.play_sound()
                    self.check_for_collisions(ball, brick)
                    self.score += 50/(brick.strength+1)
                    self.set_score(self.name, self.score)
                    if(not brick.power_up == None):
                        self.visible_pu.append(brick.power_up)
                    if(brick.strength == 0):
                        
                        self.bricks.remove(brick)
                    else:
                        brick.strength -= 1
            
			# Hit left
            if(ball.position[0] - ball.radius() <= 0):
                self.play_sound()
                ball.velocity[0] = -ball.velocity[0]
                ball.position[0] = 0 + ball.radius()

			# Hit right
            elif(ball.position[0] + ball.radius() >= self.width):
                self.play_sound()
                ball.velocity[0] = -ball.velocity[0]
                ball.position[0] = self.width - ball.radius()

			# Hit top
            elif(ball.position[1] - ball.radius() <= 0):
                self.play_sound()
                ball.velocity[1] = -ball.velocity[1]
                ball.position[1] = 0 + ball.radius()

			# Restrict paddle movement
            if(self.paddle.rect.left <= 0): self.paddle.rect.left = 0
            elif(self.paddle.rect.right >= self.width): self.paddle.rect.right = self.width
            
            for pu in self.visible_pu:
                if(pu.rect.top >= self.height): self.visible_pu.remove(pu)

			# Hit bottom
            if(ball.rect.top >= self.height):
                if(len(self.balls) == 1):
                    pygame.mixer.music.stop()
                    self.lives -= 1
                    self.state = False
                    if(self.lives >= 0):
                        self.continue_play()
                    else:
                        self.play_game_over_sound()
                else:
                    self.balls.remove(ball)




    def play_music(self):
        pygame.mixer.music.load("soundtrack.wav")
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)

    def play_sound(self):
        self.sound = pygame.mixer.Sound("bounce.wav")
        self.sound.play()

    def play_game_over_sound(self):
		self.sound = pygame.mixer.Sound("loose.wav")
        self.sound.play()

    def play_power_up_sound(self):
        self.sound = pygame.mixer.Sound("power_up.wav")
        self.sound.play()

    def play_high_score_sound(self):
        if(not self.sound == None): self.sound = None
        self.sound = pygame.mixer.Sound("high_score.wav")
        self.sound.play()


MyGame().run()
pygame.quit()
sys.exit()
		