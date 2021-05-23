def strategy(history, memory):
    num_rounds = history.shape[1]
    choice = 1 # default is play nice
    if num_rounds >= 1:
        if history[1, -1] == 0:
            # [
            #   [X],
            #   [0]
            # ]
            choice = 0
            
    if num_rounds > 3 and choice == 0:
        # forgive
        if history[0, -1] == 1 and history[0, -2] == 0 and history[1, -2] == 1:
            # [
            #   [0, 1],
            #   [1, X]
            # ]
            choice = 1
    return choice, memory
