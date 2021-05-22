from decimal import Decimal
import random

import numpy as np

def forgivingCopycat(history):
    round = history.shape[1]
    choice = 1
    if history[1,-1] == 0:
        choice = 0
    if round > 3 and choice == 0:
        if history [0, -1] == 1 and history [0,-2] == 0 and history [1, -2] == 1:
            choice = 1
    return choice

def strategy(history, memory):
    """
    :history: 2d numpy array of our and opponent past moves
    :memory: mode string, which may be None, 'tit-for-tat', 'alternate', or 'defect'
    """
    DELAY=15
    num_rounds = history.shape[1]
    testing_schedule = [1, 0, 0, 1, 1]
    max_defection_threshold = Decimal(1) / Decimal(2)  # do not forgive high defections
    small_defection_window = 15
    max_local_unprovoked_defections = 4  # too many unprovoked defections? random
    if num_rounds ==0:
        return 1, memory
    if num_rounds < DELAY:  # intitial testing phase
        return forgivingCopycat(history), memory


    if num_rounds > 50:
        sin = 0
        for i in range (1, 51):
                if history[1, -i] == 0:
                    sin +=1
        if sin >32:
            memory="grudge"
    num_rounds-=DELAY
    if num_rounds < len(testing_schedule):  # intitial testing phase
        choice = testing_schedule[num_rounds]
    elif num_rounds == len(testing_schedule):  # time to transition to our modes
       
        if history[1,-1] ==1 and history[1,-2] ==1 and history[1,-3] ==1 and history[1,-4] ==1and history[1,-5] ==1:  # they never defected, take advantage of them
            choice = 0
            memory = "grudge"
        elif history[1,-1] ==0 and history[1,-2] ==0 and history[1,-3] ==0 and history[1,-4] ==0 and history[1,-5] ==0:  # they always defect
            choice = 0
            memory = "defect"
        elif history[1,-2] ==0 and history[1,-3] ==1:  # ftft detected
            choice = 0
            memory = "alternate"
        else:
            choice = 1
            memory = "tit-for-tat"
    else:  # num_rounds > len(testing_schedule)
        num_rounds+=DELAY
        if memory == "defect":
            # break out of defection if they cooperated twice in a row
            if history[1, -1] == 1 and history[1,-2] ==1:
                choice = 1
                memory = "tit-for-tat"
            else:
                choice = 0
                memory = "defect"
        elif memory == "grudge":
            choice = 0
            memory = "grudge"
        elif memory == "alternate":
            our_last_move = history[0, -1] if num_rounds > 0 else 1
            choice = 0 if our_last_move else 1
            memory = "alternate"
        else:  # nprtt or None
            # first check whether we've detected a random
            window_start = max(0, num_rounds - small_defection_window)
            window_end = num_rounds
            opponents_recent_moves = history[1, window_start + 1 : window_end]
            our_recent_moves = history[0, window_start : window_end - 1]
            defections = opponents_recent_moves - our_recent_moves
            opponents_recent_defections = np.count_nonzero(defections == 1)
            if opponents_recent_defections > max_local_unprovoked_defections:
                choice = 0
                memory = "defect"

            else:
                opponents_last_move = history[1, -1] if num_rounds >= 1 else 1
                our_second_last_move = history[0, -2] if num_rounds >= 2 else 1
                opponent_history = history[1, 0:num_rounds]
                opponent_stats = dict(
                    zip(*np.unique(opponent_history, return_counts=True))
                )
                opponent_defection_rate = Decimal(
                    int(opponent_stats.get(0, 0))
                ) / Decimal(num_rounds)

                be_patient = opponent_defection_rate <= max_defection_threshold

                choice = (
                    1
                    if (
                        opponents_last_move == 1
                        or (be_patient and our_second_last_move == 0)
                    )
                    else 0
                )
                memory = "tit-for-tat"

    return choice, memory