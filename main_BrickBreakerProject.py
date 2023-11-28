import pygame
import math
from pygame import mixer

pygame.init()

WIDTH, HEIGHT = 1000, 600   # WIDTH and HEIGHT of the game window
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GISS Project - Brick Breaker")

mixer.music.load('back_sound.mp3') # sound that plays in loop
mixer.music.play(-1) 

COLIDE_SOUND= mixer.Sound('colide_sound.mp3') # sound that plays at colisions

FPS = 90 # frames per second
PADDLE_WIDTH = 200 
PADDLE_HEIGHT = 20
BALL_RADIUS = 10


TEXT_FONT = pygame.font.SysFont("times", 50) 


class Brick:
    
    def __init__(self, x, y, width, height, health, colors):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.health = health
        self.max_health = health
        self.colors = colors
        self.color = colors[0]

    def draw(self, WINDOW):
        pygame.draw.rect(
            WINDOW, self.color, (self.x, self.y, self.width, self.height))

    def collide(self, ball,bricks):
        if not (ball.x <= self.x + self.width and ball.x >= self.x):
            return False
        if not (ball.y - ball.radius <= self.y + self.height):
            return False

        ball.set_vel(ball.x_vel, ball.y_vel * -1) # set velocity
        bricks.remove(self)
        COLIDE_SOUND.play()
        return True

    
class Paddle:
    VEL = 5 # velocity

    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def draw(self, WINDOW):
        pygame.draw.rect(
            WINDOW, self.color, (self.x, self.y, self.width, self.height))

    def move(self, direction=1):
        self.x = self.x + self.VEL * direction


class Ball:
    VEL = 5 # velocity

    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.x_vel = 0
        self.y_vel = -self.VEL

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def set_vel(self, x_vel, y_vel):
        self.x_vel = x_vel
        self.y_vel = y_vel

    def draw(self, WINDOW):
        pygame.draw.circle(WINDOW, self.color, (self.x, self.y), self.radius)


def draw(WINDOW, paddle, ball, bricks, lives, score):
    WINDOW.fill("white") # white background
    paddle.draw(WINDOW) 
    ball.draw(WINDOW)

    for brick in bricks:
        brick.draw(WINDOW)

    # Text component
    lives_text = TEXT_FONT.render(f"Lives: {lives}", 1, "black")
    score_text = TEXT_FONT.render(f"Score: {score}", 1, "black")
    
    # Positioning of the text
    WINDOW.blit(lives_text, (10, HEIGHT - lives_text.get_height() - 20))
    WINDOW.blit(score_text, (10, HEIGHT - lives_text.get_height()
                             - score_text.get_height() - 10))
    
    pygame.display.update()


def ball_collision(ball): 
    if ball.x - BALL_RADIUS <= 0 or ball.x + BALL_RADIUS >= WIDTH:
        ball.set_vel(ball.x_vel * -1, ball.y_vel)
        COLIDE_SOUND.play()
    if ball.y + BALL_RADIUS >= HEIGHT or ball.y - BALL_RADIUS <= 0:
        ball.set_vel(ball.x_vel, ball.y_vel * -1)
        COLIDE_SOUND.play()

 

def ball_paddle_collision(ball, paddle):

    if not (ball.x <= paddle.x + paddle.width and ball.x >= paddle.x):
        return
    if not (ball.y + ball.radius >= paddle.y):
        return

    paddle_center = paddle.x + paddle.width/2
    distance_to_center = ball.x - paddle_center

    # angle of reflexion from paddle set to be proportional with the place of colision 
    # distance  from the center of the paddle
    percent_width = distance_to_center / paddle.width
    angle = percent_width * 90
    angle_radians = math.radians(angle)

    x_vel = math.sin(angle_radians) * ball.VEL
    y_vel = math.cos(angle_radians) * ball.VEL * -1

    ball.set_vel(x_vel, y_vel)


def generate_bricks(rows, cols):
    gap = 2 # gap between bricks
    brick_width = WIDTH // cols - gap 
    brick_height = 20

    bricks = []
    for row in range(rows):
        for col in range(cols):
            if not((col in (3,5,9)) or 
                   (row==1 and col not in (0,6,10)) or 
                   (row==3 and col not in(0,2,4,8,12))):
                brick = Brick(col * brick_width + gap * col, row * brick_height +
                          gap * row, brick_width, brick_height, 2, [(0, 255, 0), (255, 0, 0)])
                bricks.append(brick)
                
    return bricks


def main():
    clock = pygame.time.Clock()

    paddle_x = WIDTH/2 - PADDLE_WIDTH/2
    paddle_y = HEIGHT - PADDLE_HEIGHT - 5
    
    # generate the paddle and ball
    paddle = Paddle(paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT, "black") 
    ball = Ball(WIDTH/2, paddle_y - BALL_RADIUS, BALL_RADIUS, "red")

    # generate the bricks
    bricks = generate_bricks(5, 13)
    
    #set variables 
    lives = 3
    score = 0
    bricks_nr = len(bricks)

    # def reset():
    #     paddle.x = paddle_x
    #     paddle.y = paddle_y
    #     ball.x = WIDTH/2
    #     ball.y = paddle_y - BALL_RADIUS


    def display_text(text):
        text_render = TEXT_FONT.render(text, 1, "red")
        WINDOW.blit(text_render, (WIDTH/2 - text_render.get_width() /
                               2, HEIGHT/2 - text_render.get_height()/2))
        pygame.display.update()
        pygame.time.delay(3000)

    run = True
    while run:
        clock.tick(FPS)
        score= bricks_nr - len(bricks)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        # arrow keys are moving the paddle
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle.x - paddle.VEL >= 0:
            paddle.move(-1)
        if keys[pygame.K_RIGHT] and paddle.x + paddle.width + paddle.VEL <= WIDTH:
            paddle.move(1)

        ball.move()
        ball_collision(ball)
        ball_paddle_collision(ball, paddle)

        for brick in bricks[:]:
            brick.collide(ball, bricks)

        # lives check
        if ball.y + ball.radius >= HEIGHT:
            lives -= 1
            ball.x = paddle.x + paddle.width/2
            ball.y = paddle.y - BALL_RADIUS
            ball.set_vel(0, ball.VEL * -1)

        if lives <= 0:  
            display_text("You Lost!")

        if len(bricks) == 0:
            display_text("You Won!")
        
        draw(WINDOW, paddle, ball, bricks, lives, score)

    pygame.quit()
    quit()


if __name__ == "__main__":
    main()
# The above it's boilerplate code that protects users from accidentally 
# invoking the script when they didn't intend to
    
    
    