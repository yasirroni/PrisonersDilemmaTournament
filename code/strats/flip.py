def strategy(history, memory):
    if memory is None or memory == 1:
        return 0, 0
    else:
        return 1, 1
