def strategy(history, memory):
    """
    Orannis's punitive detective:
        Cooperate but when the other player defects, cooperate one more turn to
        see if they defect again. If they do, defect for 10 turns.
        Cooperate twice more and if they defect the second time, defect forever.

    memory is a tuple of (state, counter)
    where state is one of:
        "initial_cooperation"
        "first_punishment"
        "second_cooperation"
        "final_punishment"
    """
    num_rounds = history.shape[1]

    if memory is None or memory[0] == "initial_cooperation":
        # If they defected twice in a row, transition to first punishment
        if num_rounds >= 2 and history[1, -1] == 0 and history[1, -2] == 0:
            return 0, ("first_punishment", 9)
        # Otherwise keep cooperating
        return 1, ("initial_cooperation", 0)
    elif memory[0] == "first_punishment":
        # Punish until the counter runs out
        if memory[1] > 0:
            return 0, ("first_punishment", memory[1] - 1)
        # Once done, transition to second cooperation
        else:
            return 1, ("second_cooperation", 0)
    elif memory[0] == "second_cooperation":
        # If they defected twice in a row, transition to final punishment
        if num_rounds >= 2 and history[1, -1] == 0 and history[1, -2] == 0:
            return 0, ("final_punishment", 0)
        # Otherwise keep cooperating
        return 1, ("second_cooperation", 0)
    elif memory[0] == "final_punishment":
        return 0, ("final_punishment", 0)
