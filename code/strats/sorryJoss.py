import random

# Variant of Joss that ask for peace when messed up.

# Reminder: For the history array, "cooperate" = 1, "defect" = 0

def strategy(history, memory):
    # initial state
    if memory == None: 
        memory = {}
        memory["DEFECT_RATE"] = 0.10
        memory["DEFECT_SET"] = "DOUBLE" # "DOUBLE" defect to fight simpleton
        memory["DEFECT_COMBO_COUNTER"] = 0
        
        # first move
        choice = 1

    # double defect to fight simpleton
    if memory["DEFECT_SET"] == "DOUBLE":
        if memory["DEFECT_COMBO_COUNTER"] == 1:
            memory["DEFECT_COMBO_COUNTER"] = 0
            choice = 0

            # fast return
            return choice, memory

    if history.shape[1] >= 1:
        if history[1,-1] == 0: # if enemy just defected
            choice = 0
        else: # if enemy cooperate
            if random.random() < memory["DEFECT_RATE"]:
                choice = 0

                # double defect to fight simpleton
                if memory["DEFECT_SET"] == "DOUBLE":
                    memory["DEFECT_COMBO_COUNTER"] = 1
            else:
                choice = 1

        # if fighting titForTat, say sorry
        if history.shape[1] >= 2:
            if history[0,-2] == 0 and history[1,-1] == 0: # if my defect countered with defect afterwards
                choice = 1

                # no more random defect
                memory["DEFECT_RATE"] = 0
        
    return choice, memory