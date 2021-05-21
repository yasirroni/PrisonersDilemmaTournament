def strategy(history, memory):
    if history.shape[1] % 3 == 2: # CC
        return "defect", None # D
    else:
        return "cooperate", None # C