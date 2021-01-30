from random import uniform
import pygame
import time
import math

pygame.init()

WIN_WIDTH = 700
WIN_HEIGHT = 700
win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))

pygame.display.set_caption("Markov Random Walk Simulation")

STEP = 10
WIDTH = STEP
HEIGHT = STEP

LEARN_RATE = 0.25
STARTING_BODIES = 10
MAX_HISTORY = 250
MAX_LOOP_COUNT = 4
IDLE_COUNTER = 5000

directions = {}
bodies = []



def generate_bodies(num_bodies):

    global bodies

    for i in range(0,num_bodies):
        x_start = math.ceil(round(uniform(round(WIN_WIDTH * 0.1),round(WIN_WIDTH * 0.9))) / STEP) * STEP
        y_start = math.ceil(round(uniform(round(WIN_HEIGHT * 0.1),round(WIN_HEIGHT * 0.9))) / STEP) * STEP

        dice_roll = round(uniform(1,4))

        if dice_roll == 1:
            direction = 'north'
        elif dice_roll == 2:
            direction = 'east'
        elif dice_roll == 3:
            direction = 'west'
        elif dice_roll == 4:
            direction = 'south'

        
        body = {'x': x_start, 'y': y_start,  'facing': direction, 'history': [], 'loop_count': 0}
        bodies.append(body)



def draw():
    
    win.fill((0,0,0))

    for row in directions:
        for col in directions[row]:
            #r_color = round(directions[row][col]['forward'] * 255)
            #g_color = round(directions[row][col]['right'] * 255)
            #b_color = round(directions[row][col]['left'] * 255)
            #pygame.draw.rect(win, (r_color, g_color, b_color), (row, col, WIDTH, HEIGHT))
            for move in directions[row][col]['moves']:
                directions[row][col]['idle'] -= 1

                if directions[row][col]['idle'] == 0:
                    reset_probabilities(row, col)

                if directions[row][col]['moves'][move] == 1:
                    if move == 'north':
                        pygame.draw.rect(win, (0, 255, 0), (row, col, WIDTH, HEIGHT))
                    elif move == 'west':
                        pygame.draw.rect(win, (0, 0, 255), (row, col, WIDTH, HEIGHT))
                    elif move == 'east':
                        pygame.draw.rect(win, (255, 0, 0), (row, col, WIDTH, HEIGHT))
                    elif move == 'south':
                        pygame.draw.rect(win, (255, 0, 255), (row, col, WIDTH, HEIGHT))

    for body in bodies:
        pygame.draw.rect(win, (255, 255, 255), (body['x'], body['y'], WIDTH, HEIGHT))

    pygame.display.update()


def reset_probabilities(x,y):
    global directions

    directions[x][y]['moves']['north'] = 0.25
    directions[x][y]['moves']['west'] = 0.25
    directions[x][y]['moves']['east'] = 0.25
    directions[x][y]['moves']['south'] = 0.25
    directions[x][y]['idle'] = IDLE_COUNTER


def generate_markov_chain(WIDTH, HEIGHT, STEP):
    
    global directions

    for i in range(0,WIDTH + 1, STEP):
        directions[i] = {}
        for j in range(0, HEIGHT + 1, STEP):
            directions[i][j] = {'moves':{'north': 0.25, 'east': 0.25, 'south': 0.25, 'west': 0.25}, 'idle': IDLE_COUNTER}

    return directions


def balance_probabilities(x, y, next_move, positive_bool=True):
    global directions

    if x > WIN_WIDTH or y > WIN_HEIGHT or x < 0 or y < 0:
        pass
    else:
        directions[x][y]['moves'] = {k: v for k, v in sorted(directions[x][y]['moves'].items(), key=lambda item: item[1], reverse=True)}

        if positive_bool:
            if directions[x][y]['moves'][next_move] + LEARN_RATE <= 1:
                adj_learn_rate = LEARN_RATE
            else:
                adj_learn_rate = 1 - directions[x][y]['moves'][next_move]
        else:
            if directions[x][y]['moves'][next_move] - LEARN_RATE >= 0:
                adj_learn_rate = LEARN_RATE * -1
            else:
                adj_learn_rate = directions[x][y]['moves'][next_move] * -1
        
        if positive_bool:
            directions[x][y]['moves'][next_move] += adj_learn_rate

            for move in directions[x][y]['moves']:
                if move != next_move:
                    directions[x][y]['moves'][move] -= adj_learn_rate / 3

                    if directions[x][y]['moves'][move] < 0:
                        directions[x][y]['moves'][move] = 0
        else:
            directions[x][y]['moves'][next_move] += adj_learn_rate
            if next_move == 'south':
                directions[x][y]['moves']['north'] -= adj_learn_rate * 0.80
                directions[x][y]['moves']['east'] -= adj_learn_rate * 0.10
                directions[x][y]['moves']['west'] -= adj_learn_rate * 0.10
            elif next_move == 'west':
                directions[x][y]['moves']['east'] -= adj_learn_rate * 0.80
                directions[x][y]['moves']['north'] -= adj_learn_rate * 0.10
                directions[x][y]['moves']['south'] -= adj_learn_rate * 0.10
            elif next_move == 'east':
                directions[x][y]['moves']['west'] -= adj_learn_rate * 0.80
                directions[x][y]['moves']['north'] -= adj_learn_rate * 0.10
                directions[x][y]['moves']['south'] -= adj_learn_rate * 0.10
            elif next_move == 'north':
                directions[x][y]['moves']['south'] -= adj_learn_rate * 0.80
                directions[x][y]['moves']['east'] -= adj_learn_rate * 0.10
                directions[x][y]['moves']['west'] -= adj_learn_rate * 0.10


def get_next_step(x, y):
    global directions

    directions[x][y]['moves'] = {k: v for k, v in sorted(directions[x][y]['moves'].items(), key=lambda item: item[1], reverse=True)}
    dice = uniform(0,1)
    cum_probability = 0.0

    for move in directions[x][y]['moves']:
        cum_probability += directions[x][y]['moves'][move]
        if dice <= cum_probability:
            next_move = move
            balance_probabilities(x, y, move)

            if next_move == 'north':
                balance_probabilities(x, y - STEP, 'south', False)
            elif next_move == 'east':
                balance_probabilities(x + STEP, y, 'west', False)
            elif next_move == 'west':
                balance_probabilities(x - STEP, y, 'east', False)
            elif next_move == 'south':
                balance_probabilities(x, y + STEP, 'north', False)

            return next_move
            

def run_simulation():

    global directions
    global LEARN_RATE

    generate_markov_chain(WIN_WIDTH, WIN_HEIGHT, STEP)
    generate_bodies(STARTING_BODIES)

    run = True

    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.time.delay(50)

        i = 0
        j = 0

        for body in bodies:

            j += 1

            LEARN_RATE = max(0, LEARN_RATE - (j / 100000000))
            
            out_of_bounds = body['x'] > WIN_WIDTH or body['y'] > WIN_HEIGHT or body['x'] < 0 or body['y'] < 0

            if out_of_bounds or body['loop_count'] > MAX_LOOP_COUNT:

                if body['loop_count'] > MAX_LOOP_COUNT:
                    reset_probabilities(body['x'], body['y'])
                
                bodies.pop(i)
                generate_bodies(1)
                i -= 1
                continue

            directions[body['x']][body['y']]['idle'] = IDLE_COUNTER

            next_move = get_next_step(body['x'], body['y'])
            

            if next_move == 'north':
                body['y'] -= STEP

                if (body['x'], body['y']) in body['history']:
                    body['loop_count'] += 1
                else:
                    body['loop_count'] = 0

                body['history'].append((body['x'], body['y']))
                if len(body['history']) > MAX_HISTORY:
                    body['history'].pop(0)

            elif next_move == 'west':
                body['x'] -= STEP

                if (body['x'], body['y']) in body['history']:
                    body['loop_count'] += 1
                else:
                    body['loop_count'] = 0

                body['history'].append((body['x'], body['y']))
                if len(body['history']) > MAX_HISTORY:
                    body['history'].pop(0)

            elif next_move == 'east':
                body['x'] += STEP

                if (body['x'], body['y']) in body['history']:
                    body['loop_count'] += 1
                else:
                    body['loop_count'] = 0

                body['history'].append((body['x'], body['y']))
                if len(body['history']) > MAX_HISTORY:
                    body['history'].pop(0)

            elif next_move == 'south':
                body['y'] += STEP

                if (body['x'], body['y']) in body['history']:
                    body['loop_count'] += 1
                else:
                    body['loop_count'] = 0

                body['history'].append((body['x'], body['y']))
                if len(body['history']) > MAX_HISTORY:
                    body['history'].pop(0)


           # if body['facing'] == 'north':
           #     if next_move == 'forward':
           #         body['y'] -= STEP
           #         body['facing'] = 'north'
           #     elif next_move == 'right':
           #         body['x'] += STEP
           #         body['facing'] = 'east'
           #     elif next_move == 'left':
           #         body['x'] -= STEP
           #         body['facing'] = 'west'
           # elif body['facing'] == 'east':
           #     if next_move == 'forward':
           #         body['x'] += STEP
           #         body['facing'] = 'east'
           #     elif next_move == 'right':
           #         body['y'] += STEP
           #         body['facing'] = 'south'
           #     elif next_move == 'left':
           #         body['y'] -= STEP
           #         body['facing'] = 'north'
           # elif body['facing'] == 'west':
           #     if next_move == 'forward':
           #         body['x'] -= STEP
           #         body['facing'] = 'west'
           #     elif next_move == 'right':
           #         body['y'] -= STEP
           #         body['facing'] = 'north'
           #     elif next_move == 'left':
           #         body['y'] += STEP
           #         body['facing'] = 'south'
           # elif body['facing'] == 'south':
           #     if next_move == 'forward':
           #         body['y'] += STEP
           #         body['facing'] = 'south'
           #     elif next_move == 'right':
           #         body['x'] -= STEP
           #         body['facing'] = 'west'
           #     elif next_move == 'left':
           #         body['x'] += STEP
           #         body['facing'] = 'east'

            i += 1
    
        draw()

        if len(bodies) == 0:
            run = False

    pygame.quit()


run_simulation()