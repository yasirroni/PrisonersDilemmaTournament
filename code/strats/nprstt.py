from decimal import Decimal
import numpy


def strategy(history, memory):
    """
    Nice Patient Reflective Static Tit for Tat (NPRTT):
        1. Nice: Never initiate defection, else face the wrath of the Grudge.
        2. Patient: Respond to defection with defection, unless it was in possibly
            response to my defection. Give opponent a chance to cooperate again since,
            even if they backstab me a few more times, we'll both come out ahead.
            I don't have to worry about this causing my opponent to actually win
            because the Grudge and Tit for Tat will penalize them heavily for
            initiating defection.
        3. Reflective: Before cooperating in forgiveness, we check opponent history.
        4. Static: Instead of using defection rate, use unprovoked defection / 
            cooperative ration. 
        5. Tit for Tat: (see Patient)

    This strategy generates interesting results. If you look at head-to-head matchups,
    for example, it "loses" to strategies like joss. However, compare that to Tit for
    Tat: Tit for Tat has a low-scoring "win" vs. joss. NPRTT, on the other hand, has
    a high-scoring "loss" vs. joss.

    A cycle of mutual defection is costly because C/C is worth 2 more points than D/D.
    So even if we suffer one D/C (0) for every 2 C/C's (+6), that's still 2 points on
    average for that group of 3, vs. 1 point on average for a series of D/D. This also
    guides the 1/2 cutoff for the Reflective trait. But, the Static trait make it not
    counting provoked move due to our response, make the score more static.
    """
    num_rounds = history.shape[1]

    opponents_last_move = history[1, -1] if num_rounds >= 1 else 1
    our_second_last_move = history[0, -2] if num_rounds >= 2 else 1

    # if opponent defects more often, then screw 'em
    MAX_DEFECTION_THRESHOLD = Decimal(1) / Decimal(2)

    our_shifted_move = numpy.append([1], history[0, :-1])
    opponent_moves = history[1, :]
        
    diff = our_shifted_move - opponent_moves
    num_cooperation = (opponent_moves == 1).sum()
    if num_rounds == 0:
        unprovoked_defections_rate = 0
    elif num_cooperation == 0:
        unprovoked_defections_rate = numpy.inf
    else:
        unprovoked_defections_rate = (diff == 1).sum() / (opponent_moves == 1).sum()

    be_patient = unprovoked_defections_rate <= MAX_DEFECTION_THRESHOLD

    choice = (
        1
        if (opponents_last_move == 1 or (be_patient and our_second_last_move == 0))
        else 0
    )

    return choice, None
