import random
import numpy as np

def strategy(history, bad):
    choice = 1
    random_window = 7
    
    if history.shape[1] == 0:
        return 1, 0

    # Enemy just defected
    if history[1, -1] == 0:
        bad += 1
        choice = 0
    elif bad > history[0].sum():
        choice = 0
    elif history.shape[1] >= random_window:
        choice = random.choice(history[1, -random_window:])

    return choice, bad