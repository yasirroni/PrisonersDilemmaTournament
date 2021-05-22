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


def tickedOffCopycat(history, memory):
    round = history.shape[1]
    if round == 0:
        return 1, memory
    if round == 1:
        if history[1, -1] == 0:
            return 0, memory
        else:
            return 1, memory
    if history[1, -1] == 0 or history[1, -2] == 0:
        return 0, memory
    return 1, memory


def strategy(history, memory):
    round = history.shape[1]
    TRUTHWORTHY = 0
    ABSOLOTION = 1
    ABSOLUTING = 2
    GRUDGED = 3
    COOLDOWN = 4
    if round == 0:
        mem = []
        mem.append(True)
        mem.append(True)
        mem.append(False)
        mem.append(False)
        mem.append(0)
        return 1, mem
    mem = memory
    if round > 50:
        sin = 0
        for i in range(1, 51):
            if history[1, -i] == 0:
                sin += 1
        if sin > 30:
            mem[GRUDGED] = True
    if mem[GRUDGED]:
        return 0, mem
    if mem[ABSOLUTING] and mem[COOLDOWN] > 0:
        mem[COOLDOWN] -= 1
        return 1, mem
    if mem[ABSOLUTING] and mem[COOLDOWN] == 0:
        mem[ABSOLUTING] = False
        sin = 0
        for i in range(1, 6):
            if history[1, -i] == 0:
                sin += 1
        if sin < 5:
            mem[ABSOLOTION] = True
            return 1, mem
        else:
            mem[GRUDGED] = True
            return 0, mem
    if round == 4:
        sin = 0
        for i in range(1, 5):
            if history[1, -i] == 0:
                sin += 1
            if sin == 4:
                mem[ABSOLOTION] = False
    if round > 4 and mem[ABSOLOTION]:
        sin = 0
        for i in range(1, 5):
            if history[1, -i] == 0:
                sin += 1
            if sin == 4:
                mem[COOLDOWN] = 3
                mem[ABSOLOTION] = False
                mem[ABSOLUTING] = True
                return 1, mem

    if round > 24:
        sin = 0
        for i in range(1, 25):
            if history[1, -i] == 0:
                sin += 1
        if sin > 10:
            mem[TRUTHWORTHY] = False
    if mem[TRUTHWORTHY]:
        return forgivingCopycat(history), mem
    else:
        return tickedOffCopycat(history, mem)
