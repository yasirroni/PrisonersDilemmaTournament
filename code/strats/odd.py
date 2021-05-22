def strategy(history, memory):
    if history.shape[1] % 2 == 0: # even, cooperate in odd
        return 1, None
    else:
        return 0, None