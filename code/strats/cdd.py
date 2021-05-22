def strategy(history, memory):
    if history.shape[1] % 3 == 0: # CDD
        return 1, None # C
    else:
        return 0, None # D