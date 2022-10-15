import pygame
import os
import random
import math

# Рахимбердиев Темурмалик
# Интеллектуальные агенты и обучение с подкреплением

#инициализация pygame
pygame.init()
pygame.font.init()

#загрузить изображения
background = pygame.image.load('img/Y.jpg')
landingPad = pygame.image.load('img/landingPad.png')
rocket = pygame.image.load('img/rocket.png')
rocket_thrust = pygame.image.load('img/rocket_thrust.png')
rocket_right = pygame.image.load('img/rocket_right.png')
rocket_left = pygame.image.load('img/rocket_left.png')

#Иконка
icon = pygame.image.load('img/icon.png')
pygame.display.set_icon(icon)

#создать экран
screen = pygame.display.set_mode((background.get_width(), background.get_height()))
pygame.display.set_caption("Rocket Agent")

#установить посадочную площадку
landingPadX = (background.get_width()/2)-(landingPad.get_width()/2)
landingPadY = background.get_height()-landingPad.get_height()

#переменные
main_loop = True
end_loop = False
global acc_rate
acc_rate = 0.00015
fuel_rate = 0.01

#класс игровой объект
class Rocket:
    #переменные необходимые в классе
    thrustBool = False
    leftThrustBool = False
    rightThrustBool = False
    idleThrustBool = False

    def __init__(self):
        self.image = pygame.image.load('img/rocket.png')
        self.x = random.randint(100, screen.get_width()-100)
        self.y = random.randint(20, 100)
        self.x_speed = 0
        self.y_speed = 0.01
        self.x_acc = 0
        self.y_acc = acc_rate
        self.fuel = 100
        self.color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

    # переместите агентскую ракету
    def move(self):
        self.x_speed += self.x_acc
        self.y_speed += self.y_acc
        self.x += self.x_speed
        self.y += self.y_speed

    # показать агентскую ракету
    def display(self):
        self.rect = self.image.get_rect()
        self.rect.move_ip(int(self.x), int(self.y))
        screen.blit(self.image, (int(self.x), int(self.y)))
        fuel_text = pygame.font.SysFont('Segoe UI', 16).render(str(int(self.fuel)), False, (0,0,0))
        screen.blit(fuel_text, (int(self.x)+22, int(self.y)+5))
        pygame.draw.rect(screen, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 2)

    # установить изображение текущего элемента управления
    def set_image(self, image):
        self.image = image

    #сбросить значения для ракеты
    def reset(self):
        self.x = random.randint(100, screen.get_width()-100)
        self.y = random.randint(20, 100)
        self.x_speed = 0
        self.y_speed = 0.01
        self.fuel = 100
        self.x_acc = 0
        self.y_acc = acc_rate

    #подсчитывает балл
    def score(self):
        score = 0
        score += self.fuel * 20
        x_diff = abs((self.x + (self.image.get_width()/2)) - (landingPadX + (landingPad.get_width()/2)))
        y_diff = (self.y + self.image.get_height()) - landingPadY
        distance = math.sqrt(pow(x_diff,2) + pow(y_diff,2))
        score -= distance * 10
        print(x_diff, y_diff, distance)
        return int(score)

    # управление агентской ракетой
    def control(self):
        if self.leftThrustBool and self.fuel > 0:
            self.set_image(rocket_left)
            self.x_acc = -acc_rate
        if self.rightThrustBool and self.fuel > 0:
            self.set_image(rocket_right)
            self.x_acc = acc_rate
        if self.thrustBool and self.fuel > 0:
            self.set_image(rocket_thrust)
            self.y_acc = -acc_rate
        if self.idleThrustBool:
            self.set_image(rocket)
            self.x_acc = 0
            self.y_acc = acc_rate
        self.thrustBool = False
        self.leftThrustBool = False
        self.rightThrustBool = False
        self.idleThrustBool = False


#функции
def display(image, x, y):
    screen.blit(image, (x, y))

def stopAgent(agent):
    global acc_rate
    agent.x_speed = 0
    agent.y_speed = 0
    acc_rate = 0

def didAgentLand(agent):
    isInsideLandingPad = False
    distanceToLandingPad = landingPadY - agent.y - agent.image.get_height()
    if agent.x >= landingPadX and agent.x <= (landingPadX + landingPad.get_width() - agent.image.get_width()):
        isInsideLandingPad = True
    if distanceToLandingPad <= 0 and isInsideLandingPad:
        return True
    else:
        return False

def didAgentCrash(agent):
    if (agent.x < landingPadX or agent.x > (landingPadX + landingPad.get_width())):
        if agent.y + agent.image.get_height() > landingPadY:
            return True
        else:
            return False

def keepAgentInBounds(agent):
    if agent.x <= 0:
        agent.x = 0
        agent.x_speed = 0
    elif agent.x >= screen.get_width() - agent.image.get_width():
        agent.x = screen.get_width() - agent.image.get_width()
        agent.x_speed = 0
    if agent.y <= 0:
        agent.y = 0
        agent.y_speed = 0.01
    elif agent.y >= screen.get_height() - agent.image.get_height():
        agent.y = screen.get_height() - agent.image.get_height()
        agent.y_speed = -0.01

#взорвать ракету
def remove(index):
    agents.pop(index)

#рассчитать расход топлива
def adjustFuel(agent):
    if agent.y_acc != acc_rate or agent.x_acc != 0:
        agent.fuel -= fuel_rate
        if agent.fuel <= 0:
            agent.y_acc = acc_rate
            agent.x_acc = 0

#agent step — функция, управляющая всеми функциями, которые необходимо вызывать за шаг
def step(agent):
    agent.control()
    adjustFuel(agent)
    keepAgentInBounds(agent)
    agent.move()


def main():
    #global variables
    global main_loop
    global end_loop
    global acc_rate
    global fuel_rate
    global agents

    agents = [Rocket()]

    # создание ракеты
    agent = Rocket()

    # основной цикл -
    while main_loop:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                main_loop = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and agent.fuel > 0:
                    agent.leftThrustBool = True
                if event.key == pygame.K_RIGHT and agent.fuel > 0:
                    agent.rightThrustBool = True
                if event.key == pygame.K_UP and agent.fuel > 0:
                    agent.thrustBool = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    agent.idleThrustBool = True
                if event.key == pygame.K_UP:
                    agent.idleThrustBool = True

        step(agent)

        #отображать
        display(background, 0, 0)
        display(landingPad, landingPadX, landingPadY)

        if didAgentLand(agent) or didAgentCrash(agent):
            agent.set_image(rocket)
            print('Score: ', agent.score())
            agent.reset()

        agent.display()
        pygame.display.update()

main()

