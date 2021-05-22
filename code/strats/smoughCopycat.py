import numpy as np


def forgivingCopycat(history):
    round = history.shape[1]
    choice = 1
    if history[1, -1] == 0:
        choice = 0
    if round > 3 and choice == 0:
        if history[0, -1] == 1 and history[0, -2] == 0 and history[1, -2] == 1:
            choice = 1
    return choice


def tickedOffCopycat(history):
    round = history.shape[1]
    choice = 1
    if history[1, -1] == 0 or history[1, -2] == 0:
        choice = 0
    return choice


def strategy(history, memory):
    round = history.shape[1]
    if round == 0:
        truthworthy = True
        return 1, truthworthy
    truthworthy = memory
    if round > 12 and truthworthy == True:
        if history[0, -12]:
            sin = 0
            for i in range(1, 13):
                sin += history[1, -i]
            if sin > 4:
                truthworthy = False
    if truthworthy:
        return forgivingCopycat(history), truthworthy
    else:
        return tickedOffCopycat(history), truthworthy
