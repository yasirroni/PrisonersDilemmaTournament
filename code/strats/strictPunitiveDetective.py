def strategy(history, memory):
    """
    A variation on Orannis's punitive detective:
        Cooperate but when the other player defects twice (not in a row), defect
        for 10 turns to punish them. Coooperate again, same rule, but if they defect
        twice defect forever.

    memory is a tuple of (state, counter)
    where state is one of:
        "initial_cooperation"
        "first_punishment"
        "second_cooperation"
        "final_punishment"
    """
    num_rounds = history.shape[1]

    if memory is None or memory[0] == "initial_cooperation":
        if num_rounds >= 1 and history[1, -1] == 0:
            past_defections = memory[1] if memory is not None else 0
            if past_defections >= 2:
                return 0, ("first_punishment", 9)
            else:
                return 1, ("initial_cooperation", past_defections + 1)
        return 1, ("initial_cooperation", 0)
    elif memory[0] == "first_punishment":
        # Punish until the counter runs out
        if memory[1] > 0:
            return 0, ("first_punishment", memory[1] - 1)
        # Once done, transition to second cooperation
        else:
            return 1, ("second_cooperation", 0)
    elif memory[0] == "second_cooperation":
        if num_rounds >= 1 and history[1, -1] == 0:
            past_defections = memory[1] if memory is not None else 0
            if past_defections >= 2:
                return 0, ("final_punishment", 0)
            else:
                return 1, ("second_cooperation", past_defections + 1)
        return 1, ("second_cooperation", 0)
    elif memory[0] == "final_punishment":
        return 0, ("final_punishment", 0)
