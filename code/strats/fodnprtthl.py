from decimal import Decimal
import numpy

def strategy(history, memory):
    """
    Forgiving Opportunistic Defector based on Nice Patient Reflective Tit for Tat with Half-Life bound.
    """
    OPPORTUNITY_WINDOW = 3
    num_rounds = history.shape[1] # elapsed round

    # get oponets last move
    if num_rounds >= 1:
        our_last_move = history[0, -1]
        opponentlast_move = history[1, -1]
    else:
        our_last_move = 1
        opponentlast_move = 1

    if num_rounds >= 2:
        our_second_last_move = history[0, -2]
        opponentsecond_last_move = history[1, -2]
    else:
        our_second_last_move = 1
        opponentsecond_last_move = 1
        

    HALF_LIFE = 20 

    # if opponent defects more often, then screw 'em
    MAX_DEFECTION_THRESHOLD = 0.5 + 0.5 * numpy.power(0.5,(num_rounds/HALF_LIFE))

    opponent_history = history[1, 0:num_rounds]
    if num_rounds == 0:
        opponent_defection_rate = 0
    else:
        opponent_stats = dict(zip(*numpy.unique(opponent_history, return_counts=True)))
        opponent_defection_rate = Decimal(int(opponent_stats.get(0, 0))) / Decimal(
            num_rounds
        )

    be_patient = opponent_defection_rate <= Decimal(MAX_DEFECTION_THRESHOLD)

    # default
    choice = 1

    if opponentlast_move == 0: # opponent defect
        # counter defect with defect
        choice = 0

        # forgive if their defect because of our defect when they are not
        if our_last_move == 1 and our_second_last_move == 0 and opponentsecond_last_move == 1:
            # [
            #   [0, 1],
            #   [1, X]
            # ]
            choice = 1
        
            if be_patient == False:
                # should not forgive because they had done too much
                choice = 0

    else: # opponentlast_move == 1
        if num_rounds >= OPPORTUNITY_WINDOW:
            if numpy.sum(history[1, -OPPORTUNITY_WINDOW:]) == OPPORTUNITY_WINDOW:
                choice = 0

    return choice, memory
