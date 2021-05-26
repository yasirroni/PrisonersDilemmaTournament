import numpy

def strategy(history, memory):
    """
    Revenge Sorry Opportunity TitForTat
    Hierarchy:
        default < revenge < sorry < opportunity
    """
    OPPORTUNITY_WINDOW = 3

    # default
    choice = 1
    num_rounds = history.shape[1]
    
    # revenge
    if num_rounds >= 1:
        if history[1, -1] == 0:
            choice = 0

    # sorry
    if num_rounds >= 2:
        if history[0, -2] == 0:
            # forgive if it might be because our previous defect
            choice = 1
    
    # opportunity
    if num_rounds >= 3:
        if numpy.sum(history[1, -OPPORTUNITY_WINDOW:]) == OPPORTUNITY_WINDOW:
            choice = 0
    
    return choice, None
