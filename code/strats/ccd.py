def strategy(history, memory):
    if history.shape[1] % 3 == 2: # CC
        return 0, None # D
    else:
        return 1, None # C