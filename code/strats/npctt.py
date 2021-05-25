from decimal import Decimal
import numpy


def strategy(history, memory):
    """
    Nice Patient Comparative Tit for Tat (NPCTT):
        1. Nice: Never initiate defection, else face the wrath of the Grudge.
        2. Patient: Respond to defection with defection, unless it was in possibly
            response to my defection. Give opponent a chance to cooperate again since,
            even if they backstab me a few more times, we'll both come out ahead.
            I don't have to worry about this causing my opponent to actually win
            because the Grudge and Tit for Tat will penalize them heavily for
            initiating defection.
        3. Comparative: Before cooperating in forgiveness, we compare number of 
            defection between ours and theirs. If D(ours)/D(theirs) is higher than 
            50%, we forgive.
        4. Tit for Tat: (see Patient)

    This strategy incorporate enemy that defect in late game and not too fast judging
    early impression.
    """

    num_rounds = history.shape[1]

    opponents_last_move = history[1, -1] if num_rounds >= 1 else 1
    our_second_last_move = history[0, -2] if num_rounds >= 2 else 1

    # if opponent defects more often, then screw 'em
    LOWER_BOUND = Decimal(1) / Decimal(2) # exclusive bound

    our_history = history[0, 0:num_rounds]
    opponent_history = history[1, 0:num_rounds]

    if num_rounds == 0:
        defection_ratio = 1
    else:
        our_stats = dict(zip(*numpy.unique(our_history, return_counts=True)))
        opponent_stats = dict(zip(*numpy.unique(opponent_history, return_counts=True)))

        our_n_defection = our_stats.get(0, 0)
        opponent_n_defection = opponent_stats.get(0, 0)

        if opponent_n_defection > 0:
            defection_ratio = Decimal(int(our_n_defection)) / Decimal(int(opponent_n_defection))
        else:
            defection_ratio = 1

    be_patient = defection_ratio > LOWER_BOUND

    choice = (
        1
        if (opponents_last_move == 1 or (be_patient and our_second_last_move == 0))
        else 0
    )

    return choice, None