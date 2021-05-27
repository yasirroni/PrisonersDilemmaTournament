from decimal import Decimal
import numpy

# nprtt but have some experience about others
def strategy(history, memory):
    SHORT_WINDOW = 4
    MEDIUM_WINDOW = 8
    LONG_WINDOW = 16
    VERY_LONG_WINDOW = 32

    UNPROVOKED_DEFECTION_RATE_THRESHOLD = Decimal(0.4)
    RANDOM_DEFECTION_RATE_THRESHOLD = Decimal(0.4)
    TEST_RANDOM_SCHEDULE =    [0, 0, 0, 1, 1]
    EXPECTED_MOVES_OPPORTUNIST = [0, 0, 0, 1] # expected moves from opportunist / joss / titForTat

    num_rounds = history.shape[1] # elapsed round

    choice = None # place holder

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
       
    # extract history move
    our_history = history[0, :]
    opponent_history = history[1, :]

    if num_rounds >= 1:
        our_last_move = our_history[-1]
        opponents_last_move = opponent_history[-1]
    else:
        our_last_move = 1
        opponents_last_move = 1

    if num_rounds >= 2:
        our_second_last_move = our_history[-2]
        opponents_second_last_move = opponent_history[-2]
    else:
        our_second_last_move = 1
        opponents_second_last_move = 1

    # state evaluation
    if num_rounds == 1:
        # first round logic
        if opponents_last_move == 1:
            # opponent cooperate in first move
            memory["battle_state"] = "peace"
            memory["num_piece"] += 1
            choice = 1
            return choice, memory
        else:
            # opponent defect in first move
            memory["sin"] += 1
            memory["battle_state"] = "war_started"
            memory["num_war"] += 1
            memory["strategy"] = "nprtt_halflife"
            memory["strategy_history"].append(memory["strategy"])
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
            # opponent defect in the last move
            memory["sin"] += 1

            # betrayal?
            if memory["battle_state"] == "peace" or memory["battle_state"] == "peace_started":
                memory["battle_state"] = "war_started"
                memory["num_war"] += 1
            else: # (war_started or war) already in war
                memory["battle_state"] = "war"

            # maybe fighting random?
            if (
                "test_random" not in memory["strategy_history"]
                and "fight_random" not in memory["strategy_history"]
            ):
                if num_rounds >= LONG_WINDOW:
                    our_shifted_move = history[0, -(LONG_WINDOW):(num_rounds-1)]
                    opponent_moves = history[1, -(LONG_WINDOW-1):]

                    diff = our_shifted_move - opponent_moves 
                    num_cooperation = (opponent_moves == 1).sum()
                    if num_cooperation == 0:
                        unprovoked_defections_rate = numpy.inf
                    else:
                        unprovoked_defections_rate = (diff == 1).sum() / (opponent_moves == 1).sum()

                    flipped_opponent_move = numpy.abs(opponent_moves - 1)
                    defection_rate = numpy.average(flipped_opponent_move)

                    # too much unprovoked defection
                    if unprovoked_defections_rate > UNPROVOKED_DEFECTION_RATE_THRESHOLD:
                        memory["previous_strategy"] = memory["strategy"]
                        memory["strategy"] = "test_random"
                        memory["strategy_history"].append(memory["strategy"])
                        memory["counter"] = len(TEST_RANDOM_SCHEDULE)

                    # too much defection rate
                    elif defection_rate > (RANDOM_DEFECTION_RATE_THRESHOLD):
                        memory["previous_strategy"] = memory["strategy"]
                        memory["strategy"] = "test_random"
                        memory["strategy_history"].append(memory["strategy"])
                        memory["counter"] = len(TEST_RANDOM_SCHEDULE)

            # defector (always) in the middle of the game
            if num_rounds >= VERY_LONG_WINDOW:
                if "test_random" not in memory["strategy_history"]:
                    if memory["strategy"] == None:
                        opponent_moves = history[1, -MEDIUM_WINDOW:]
                    else:
                        opponent_moves = history[1, -LONG_WINDOW:]

                    if sum(opponent_moves) == 0:
                        memory["previous_strategy"] = memory["strategy"]
                        memory["strategy"] = "fight_defector"
                        if "fight_defector" not in memory["strategy"]:
                            memory["strategy_history"].append(memory["strategy"])
            
    # strategy decision and execution
    if memory["strategy"] == "test_random":
        if memory["counter"] == 0:
            # evaluation
            window = len(TEST_RANDOM_SCHEDULE) - 1
            opponent_moves = opponent_history[-window:].tolist()
            if  opponent_moves == EXPECTED_MOVES_OPPORTUNIST:
                memory["previous_strategy"] = memory["strategy"]
                memory["strategy"] = "fight_opportunist"
                memory["strategy_history"].append(memory["strategy"])
            else:
                memory["previous_strategy"] = memory["strategy"]
                memory["strategy"] = "fight_random"
                memory["counter"] =  num_rounds
                memory["strategy_history"].append(memory["strategy"])

        elif memory["counter"] > 0:
            choice = TEST_RANDOM_SCHEDULE[-memory["counter"]]
            memory["counter"] += -1

    if memory["strategy"] == "fight_random":
        choice = 0
        if num_rounds >= memory["counter"] + MEDIUM_WINDOW:
            opponent_moves = history[1, memory["counter"]:]
            if numpy.sum(opponent_moves) == 0:
                # random should never always defect
                memory["previous_strategy"] = memory["strategy"]
                memory["strategy"] = "nprtt_halflife"
                memory["strategy_history"].append(memory["strategy"])
        if num_rounds >= LONG_WINDOW:
            opponent_moves = history[1, -LONG_WINDOW:]
            if numpy.sum(opponent_moves) == 0:
                # random should never always defect
                memory["previous_strategy"] = memory["strategy"]
                memory["strategy"] = "nprtt_halflife"
                memory["strategy_history"].append(memory["strategy"])
    
    if memory["strategy"] == "fight_opportunist":
        if num_rounds >= MEDIUM_WINDOW:
            opponent_moves = history[1, -MEDIUM_WINDOW:]
            if numpy.sum(opponent_moves) == 0:
                # opportunist should never always defect
                memory["previous_strategy"] = memory["strategy"]
                memory["strategy"] = "nprtt_halflife"
                memory["strategy_history"].append(memory["strategy"])
            elif numpy.sum(history[:, -2:]) == 0:
                # must break D/D loop
                choice = 1
            else:
                choice, _ = forgivingDefector(history, memory)  

    if memory["strategy"] == "fight_defector":
        if opponents_last_move == 1:
            # want to make up?
            memory["previous_strategy"] = memory["strategy"]
            memory["strategy"] == None
        else:
            choice = 0

    # default strategy
    if memory["strategy"] == None or memory["strategy"] == "nprtt_halflife" or choice == None:
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

def forgivingDefector(history, memory):
    # default cooperate
    choice = 1

    # revenge
    if history.shape[1] >= 1:
        # if enemy defected revange
        if history[1,-1] == 0: 
            choice = 0

    # forgive
    if history.shape[1] >= 2 and choice == 0:
        # forgive if their defect because of our defect when they are not
        if history[0, -1] == 1 and history[0, -2] == 0 and history[1, -2] == 1:
            # [
            #   [0, 1],
            #   [1, X]
            # ]
            choice = 1

    # defector 
    if history.shape[1] >= 2 and choice == 1:
        # defect if I already cooperate two times
        if history[0, -2] == 1 and history[0, -1] == 1:
            # [
            #   [1, 1],
            #   [X, X]
            # ]
            choice = 0

    return choice, None