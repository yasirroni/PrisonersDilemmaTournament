def strategy(history, memory):
    num_rounds = history.shape[1]
    if num_rounds == 0:
        return 1, memory
    if num_rounds == 1:
        if history[1, -1] == 0:
            return 0, memory
        else:
            return 1, memory
    if num_rounds >= 2:
        if history[1, -1] == 0 or history[1, -2] == 0:
            return 0, memory
    return 1, memory