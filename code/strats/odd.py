def strategy(history, memory):
    if history.shape[1] % 2 == 0: # even, cooperate in odd
        return "cooperate", None
    else:
        return "defect", None