from decimal import Decimal
import numpy

# nprtt but have some experience about others
def strategy(history, memory):

    MAX_DEFECTION_THRESHOLD = Decimal(1) / Decimal(2)
    MAX_DEFECTION_THRESHOLD_PEACEFULL = Decimal(3) / Decimal(4)
    DETECTIVE_WINDOW = 3
    TEST_DETECTIVE_SCHEDULE = [0]
    SHORT_WINDOW = 4
    MEDIUM_WINDOW = 8
    LONG_WINDOW = 16
    VERY_LONG_WINDOW = 32
    RANDOM_DEFECTION_RATE_THRESHOLD = Decimal(0.6)
    num_rounds = history.shape[1] # elapsed round

    if num_rounds == 0:
        memory = {}
        memory["sin"] = 0
        memory["strategy"] = None
        memory["counter"] = 0
        memory["strategy_history"] = []
        memory["battle_state"] = None
        memory["num_war"] = 0
        memory["num_piece"] = 0
        choice = 1

        return choice, memory
       
    # get oponets last move
    if num_rounds >= 1:
        our_last_move = history[0, -1]
        opponents_last_move = history[1, -1]
    else:
        our_last_move = 1
        opponents_last_move = 1

    if num_rounds >= 2:
        our_second_last_move = history[0, -2]
        opponents_second_last_move = history[1, -2]
    else:
        our_second_last_move = 1
        opponents_second_last_move = 1

    # state evaluation
    if num_rounds == 1:
        # first round logic
        if opponents_last_move == 1:
            # enemy cooperate in first move
            memory["battle_state"] = "peace"
            memory["num_piece"] += 1
            choice = 1
            return choice, memory
        else:
            # enemy defect in first move
            memory["sin"] += 1
            memory["battle_state"] = "war_started"
            memory["num_war"] += 1
            memory["strategy"] = "nprtt_halflife"
            memory["strategy_history"].extend(memory["strategy"])
            choice = 0
            return choice, memory
    else:
        # not first round logic
        if opponents_last_move == 1:
            if memory["battle_state"] == "war" or  memory["battle_state"] == "war_started":
                memory["battle_state"] = "peace_started"
                memory["num_piece"] += 1
            else: # (peace_started or peace) already in peace
                memory["battle_state"] = "peace"

        if opponents_last_move == 0:
            # enemy defect in the last move
            memory["sin"] += 1

            # betrayal?
            if memory["battle_state"] == "peace" or memory["battle_state"] == "peace_started":
                memory["battle_state"] = "war_started"
                memory["num_war"] += 1
            else: # (war_started or war) already in war
                memory["battle_state"] = "war"

            # maybe fighting random?
            if num_rounds >= VERY_LONG_WINDOW:
                enemy_moves = history[1, :]
                flipped_enemy_move = numpy.abs(enemy_moves - 1)
                defection_rate_medium_window = numpy.average(flipped_enemy_move)
                if defection_rate_medium_window > (RANDOM_DEFECTION_RATE_THRESHOLD):
                    memory["previous_strategy"] = memory["strategy"]
                    memory["strategy"] = "fight_random"
                    memory["strategy_history"].extend(memory["strategy"])

            # defector (always) in the middle of the game
            if num_rounds >= VERY_LONG_WINDOW:
                enemy_moves = history[1, -MEDIUM_WINDOW:]
                if sum(enemy_moves) == 0:
                    memory["previous_strategy"] = memory["strategy"]
                    memory["strategy"] = "fight_defector"
                    memory["strategy_history"].extend(memory["strategy"])
            
            # TODO: detect opportunistic defector

    # strategy decision
    if memory["battle_state"] == "war_started":
        if memory["num_war"] == 1:
            memory["previous_strategy"] = memory["strategy"]
            memory["strategy"] = "nprtt_halflife"
            memory["strategy_history"].extend(memory["strategy"])
            memory["counter"] = 1 # one time to attack
        elif memory["num_war"] == 2:
            # second betrayal strategy
            memory["previous_strategy"] = memory["strategy"]
            memory["strategy"] = "nprtt_halflife"
            memory["strategy_history"].extend(memory["strategy"])
        elif memory["num_war"] >= 3:
            # third++ betrayal
            memory["previous_strategy"] = memory["strategy"]
            memory["strategy"] = "nprtt_halflife"
            memory["strategy_history"].extend(memory["strategy"])
    elif memory["battle_state"] == "war":
        pass # no need to change strategy
    else: # memory["battle_state"] == "peace"
        pass # no need to change strategy

    # strategy execution
    # I've asking for peace
    if memory["strategy"] == "nprtt_halflife":
        if memory["counter"] == 1:
            # you defect, i defect
            memory["counter"] -= 1
            choice = 0
            return choice, memory
        elif memory["counter"] == 0:
            # i have defect last turn, i've done my job
            memory["previous_strategy"] = memory["strategy"]
            memory["strategy"] = "nprtt_halflife"
            memory["strategy_history"].extend(memory["strategy"])

    # back to default strategy
    if memory["battle_state"] == "peace_started":
        memory["previous_strategy"] = memory["strategy"]
        memory["strategy"] = None

    if memory["strategy"] == "fight_defector":
        if opponents_last_move == 1:
            # want to make up?
            choice = 1
            memory["previous_strategy"] = memory["strategy"]
            memory["strategy"] == None
        else:
            choice = 0

    if memory["strategy"] == "fight_random":
        choice = 0
        enemy_moves = history[1, -MEDIUM_WINDOW:]

        # random should never always defect
        if numpy.sum(enemy_moves) <= 0.1: # <= 0 but avoiding floating error
            memory["previous_strategy"] = memory["strategy"]
            memory["strategy"] == "nprtt_halflife"

    if memory["strategy"] == "fight_opportunist":
        choice, _ = sorryOpportunisticDefector()

    # default strategy
    if memory["strategy"] == None or memory["strategy"] == "nprtt_halflife":
        choice, _ = nprtt_halflife(history, None)

    return choice, memory


def nprtt_halflife(history, memory):
    """
    Nice Patient Reflective Tit for Tat (NPRTT):
        1. Nice: Never initiate defection, else face the wrath of the Grudge.
        2. Patient: Respond to defection with defection, unless it was in possibly
            response to my defection. Give opponent a chance to cooperate again since,
            even if they backstab me a few more times, we'll both come out ahead.
            I don't have to worry about this causing my opponent to actually win
            because the Grudge and Tit for Tat will penalize them heavily for
            initiating defection.
        3. Reflective: Before cooperating in forgiveness, we check whether the opponent
            has defected so far more than 1/2 of the time. If they have, then we'd
            probably lose out by cooperating.
        4. Tit for Tat: (see Patient)

    This strategy generates interesting results. If you look at head-to-head matchups,
    for example, it "loses" to strategies like joss. However, compare that to Tit for
    Tat: Tit for Tat has a low-scoring "win" vs. joss. NPRTT, on the other hand, has
    a high-scoring "loss" vs. joss.

    A cycle of mutual defection is costly because C/C is worth 2 more points than D/D.
    So even if we suffer one D/C (0) for every 2 C/C's (+6), that's still 2 points on
    average for that group of 3, vs. 1 point on average for a series of D/D. This also
    guides the 1/2 cutoff for the Reflective trait.
    """
    HALF_LIFE = 20

    num_rounds = history.shape[1]

    opponents_last_move = history[1, -1] if num_rounds >= 1 else 1
    our_second_last_move = history[0, -2] if num_rounds >= 2 else 1

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

    choice = (
        1
        if (opponents_last_move == 1 or (be_patient and our_second_last_move == 0))
        else 0
    )

    return choice, memory

def sorryOpportunisticDefector(history, memory):
    num_rounds = history.shape[1] # elapsed round

    # get oponets last move
    if num_rounds >= 1:
        our_last_move = history[0, -1]
        opponents_last_move = history[1, -1]
    else:
        our_last_move = 1
        opponents_last_move = 1

    if num_rounds >= 2:
        our_second_last_move = history[0, -2]
        opponents_second_last_move = history[1, -2]
    else:
        our_second_last_move = 1
        opponents_second_last_move = 1

    # default
    choice = 1
    if opponents_last_move == 0:
        # counter defect with defect
        choice = 0
        if our_second_last_move == 0:
            # forgive if it might be because our previous defect
            choice = 1

    else: # opponents_last_move == 1
        if our_last_move == 1:
            # opportuny
            choice = 0

    return choice, memory
