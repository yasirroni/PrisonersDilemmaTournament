def strategy(history, memory):
    """
    Orannis's strategy:
        Cooperate, defect if opponent defects OR if they haven't defected in 3 turns.
    """
    choice = 1
    num_rounds = history.shape[1]
    if num_rounds >= 1 and history[1, -1] == 0:
        choice = 0
    if (
        num_rounds >= 5
        and history[1, -5] == 1
        and history[1, -4] == 1
        and history[1, -3] == 1
        and history[1, -2] == 1
        and history[1, -1] == 1
    ):
        choice = 0
    return choice, None
