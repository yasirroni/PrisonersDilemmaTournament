def strategy(history, memory):
    if history.shape[1] % 2 == 1: # odd, cooperate in even
        return "cooperate", None
    else:
        return "defect", None