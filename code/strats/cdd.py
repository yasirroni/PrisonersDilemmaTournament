def strategy(history, memory):
    if history.shape[1] % 3 == 0: # CDD
        return "cooperate", None # C
    else:
        return "defect", None # D