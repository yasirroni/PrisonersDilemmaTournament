# Reminder: For the history array, "cooperate" = 1, "defect" = 0

def strategy(history, memory):
    # default cooperate
    choice = 1

    if history.shape[1] >= 1:
        # if enemy defected revange
        if history[1,-1] == 0: 
            choice = 0

        # if fighting titForTat, say sorry
        if history.shape[1] >= 2:
            # if my defect countered with defect afterwards
            if history[0,-2] == 0 and history[1,-1] == 0:
                choice = 1


    return choice, None
