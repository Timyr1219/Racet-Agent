import sys

import pygame
import os
import random
import math
import neat



# Рахимбердиев Темурмалик
# Интеллектуальные агенты и обучение с подкреплением

#инициализация pygame
pygame.init()
pygame.font.init()

#загрузить изображения
background = pygame.image.load('img/W.jpg')
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

#класс игровой объект
landingPadX = (background.get_width()/2)-(landingPad.get_width()/2)
landingPadY = background.get_height()-landingPad.get_height()

#переменные
global acc_rate
acc_rate = 0.02
fuel_rate = 0.1
y_speed_rate = 1

#класс игровой объект
class Rocket:
    # переменные необходимые в классе
    thrustBool = False
    leftThrustBool = False
    rightThrustBool = False
    idleThrustBool = False

    def __init__(self):
        self.image = pygame.image.load('img/rocket.png')
        self.x = random.randint(100, screen.get_width()-100)
        self.y = random.randint(20, 100)
        self.x_speed = 0
        self.y_speed = y_speed_rate
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
        #pygame.display.update() #this works too

    # установить изображение текущего элемента управления
    def set_image(self, image):
        self.image = image

    #сбросить значения для ракеты
    def reset(self):
        self.x = random.randint(100, screen.get_width()-100)
        self.y = random.randint(20, 100)
        self.x_speed = 0
        self.y_speed = y_speed_rate
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
        #print(x_diff, y_diff, distance, score, self.x_speed, self.y_speed)
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


#Функции
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
    if not didAgentLand(agent) and (agent.y + agent.image.get_height() > landingPadY):
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
        agent.y_speed = y_speed_rate
    elif agent.y >= screen.get_height() - agent.image.get_height():
        agent.y = screen.get_height() - agent.image.get_height()
        agent.y_speed = -y_speed_rate

#взорвать ракету
def remove(index):
    rockets.pop(index)
    ge.pop(index)
    nets.pop(index)

#рассчитать расход топлива
def adjustFuel(agent):
    if agent.y_acc != acc_rate or agent.x_acc != 0:
        agent.fuel -= fuel_rate
        if agent.fuel <= 0:
            agent.y_acc = acc_rate
            agent.x_acc = 0

#agent step — функция, управляющая всеми функциями, которые необходимо вызывать за шаг
def step(agent):
    agent.move()
    adjustFuel(agent)
    keepAgentInBounds(agent)
    agent.control()


#global variables
def eval_genomes(genomes, config):
    #global variables
    FONT = pygame.font.SysFont('Segoe UI', 16)
    global main_loop
    global acc_rate
    global agent_x_acc
    global agent_y_acc
    global fuel_rate
    global rockets
    global ge
    global nets
    global landingPadCenterX
    global landingPadcenterY

    clock = pygame.time.Clock()

    landingPadCenterX = landingPadX + (landingPad.get_width())
    landingPadCenterY = landingPadY

    rockets = []
    ge = []
    nets = []

    for genome_id, genome in genomes:
        rockets.append(Rocket())
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    # создание ракеты
    def statistics():
        global dinosaurs, game_speed, ge
        agentsCount = FONT.render(f'Agents Alive:  {str(len(rockets))}', True, (0, 0, 0))
        gen = FONT.render(f'Generation:  {pop.generation+1}', True, (0, 0, 0))
        screen.blit(agentsCount, (50, 50))
        screen.blit(gen, (50, 100))

    main_loop = True
    # основной цикл
    while main_loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                +
                main_loop = False
                sys.exit()

        if len(rockets) == 0:
            main_loop = False
            break

        # проверить, не упала или не приземлилась ракета
        for index, agent in enumerate(rockets):
            if didAgentCrash(agent):
                ge[index].fitness = agent.score() - 20000
                remove(index)
            if didAgentLand(agent) and agent.y_speed <= 2.0:
                ge[index].fitness = agent.score() + 1000
                remove(index) #рассмотрите возможность удаления
            elif didAgentLand(agent) and agent.y_speed > 2.0:
                ge[index].fitness = agent.score() - 2000
                remove(index) #рассмотрите возможность удаления

        # вызвать/активировать нейросеть
        for index, agent in enumerate(rockets):
            x_diff = abs((agent.x + (agent.image.get_width() / 2)) - (landingPadX + (landingPad.get_width() / 2)))
            y_diff = (agent.y + agent.image.get_height()) - landingPadY
            distance = math.sqrt(pow(x_diff, 2) + pow(y_diff, 2))
            #звонок в сеть
            output = nets[index].activate((agent.x, agent.y, distance,
                                           agent.x_speed, agent.y_speed,
                                           agent.x_acc, agent.y_acc, agent.fuel,
                                           landingPadCenterX, landingPadCenterY))
            if output[0] > 0.5:
                agent.thrustBool = True
            if output[1] > 0.5:
                agent.leftThrustBool = True
            if output[2] > 0.5:
                agent.rightThrustBool = True
            if output[2] > 0.5:
                agent.idleThrustBool = True

        for agent in rockets:
            # вызовите это, чтобы агент отреагировал, затем отобразите
            step(agent)
            # дисплейный агент
            agent.display()
            pygame.display.update()

        # отображать фон и посадочную площадку и вызывать обновление
        # статистика()
        display(background, 0, 0)
        display(landingPad, landingPadX, landingPadY)
        clock.tick(60) # 60 кадров в секунду, раньше использовал 30, но остановился на 60
        pygame.display.update()


# Настройте нейронную сеть NEAT
def run(config_path):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)

    #для предоставления статистики по генерации
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    pop.run(eval_genomes, 50)

#обработка основной функции
if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)

