def strategy(history, memory):
    choice = 1
    if (
        history.shape[1] >= 1 and history[1, -1] == 0
    ):  # Choose to defect if and only if the opponent just defected.
        choice = 0

        # being nice periodically
        if history.shape[1] % 20 < 2:
            choice = 1

    return choice, None