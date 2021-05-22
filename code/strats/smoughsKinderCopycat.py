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
    TRUTHWORTHY = 0
    GRUDGED = 1
    COOLDOWN = 2
    CHANCES = 3
    if round == 0:
        pamet = []
        pamet.append(True)
        pamet.append(False)
        pamet.append(0)
        pamet.append(3)
        return 1, pamet
    pamet = memory

    if pamet[GRUDGED]:
        return 0, pamet

    if pamet[TRUTHWORTHY] == False and pamet[COOLDOWN] > 0:
        pamet[COOLDOWN] -= 1
    if round >= 12 and pamet[TRUTHWORTHY]:
        if history[0, -12]:
            sin = 0
            for i in range(1, 13):
                if history[1, -i] == 0:
                    sin += 1
            if sin > 4:
                pamet[TRUTHWORTHY] = False
                pamet[COOLDOWN] = 7

    if pamet[TRUTHWORTHY]:
        return forgivingCopycat(history), pamet
    if pamet[COOLDOWN] == 0:
        sin = 0
        for i in range(1, 8):
            if history[1, -i] == 0:
                sin += 1
        if sin < 4:
            pamet[TRUTHWORTHY] = True
            if sin < 2:
                pamet[CHANCES] = 3
        pamet[CHANCES] -= 1
        if sin == 7 or pamet[CHANCES] == 0:
            pamet[GRUDGED] = True
        else:
            pamet[COOLDOWN] = 7
    if pamet[GRUDGED]:
        return 0, pamet
    return tickedOffCopycat(history), pamet
