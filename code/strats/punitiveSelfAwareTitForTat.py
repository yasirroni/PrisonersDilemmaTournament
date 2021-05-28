
def strategy(history, memory):
    """
    If opponent defected, respond with defection. *UNLESS* we defected the turn before.
    Or if they've never cooperated before.
    """
    opponents_last_move = history[1, -1] if history.shape[1] >= 1 else 1
    our_second_last_move = history[0, -2] if history.shape[1] >= 2 else 1
    # only forgive defections if they've cooperated with us before
    choice = (
        1
        if (opponents_last_move == 1 or (memory is True and our_second_last_move == 0))
        else 0
    )

    memory = (
        True
        if (history.shape[1] > 0 and opponents_last_move == 1 or memory is True)
        else False
    )

    return choice, memory