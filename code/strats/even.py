def strategy(history, memory):
    if history.shape[1] % 2 == 1: # odd, cooperate in even
        return 1, None
    else:
        return 0, None