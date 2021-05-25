def strategy(history, memory):
    if history.shape[1] == 0:
        choice = 0
    else:
        choice = 1
        
    if (
        history.shape[1] >= 1 and history[1, -1] == 0
    ):  # Choose to defect if and only if the opponent just defected.
        choice = 0
    return choice, None
