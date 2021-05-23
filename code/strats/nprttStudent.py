from decimal import Decimal
import numpy


# nprtt but have some experience about others
def strategy(history, memory):
    # num_rounds == 0
    if memory == None:
        memory = {}
        memory["sin"] = 0
        memory["strategy"] = None
        memory["counter"] = 0
        choice = 1

        return choice, memory

    MAX_DEFECTION_THRESHOLD = Decimal(1) / Decimal(2)
    DETECTIVE_WINDOW = 3
    TEST_DETECTIVE_SCHEDULE = [0, 0]
    SHORT_WINDOW = 4
    MEDIUM_WINDOW = 8
    LONG_WINDOW = 16
    VERY_LONG_WINDOW = 32
    RANDOM_DEFECTION_RATE_THRESHOLD = Decimal(0.4)
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
    else:
        our_second_last_move = 1

    # enemy defect in the last move
    if opponents_last_move == 0:
        # add sin counter
        memory["sin"] += 1

        # maybe fighting detective?
        if num_rounds <= DETECTIVE_WINDOW:
            if memory["sin"] <= 2 and memory["strategy"] != "detective":
                # enemy first time to defect
                memory["strategy"] = "detective"
                memory["counter"] = len(TEST_DETECTIVE_SCHEDULE)

        # maybe fighting delayedDetective?
        if num_rounds > DETECTIVE_WINDOW:
            if memory["sin"] <= 2 and memory["strategy"] != "detective":
                # enemy first time to defect
                memory["strategy"] = "detective"
                memory["counter"] = len(TEST_DETECTIVE_SCHEDULE)

        # maybe fighting defector?
        if num_rounds == SHORT_WINDOW:
            if memory["sin"] == num_rounds:
                memory["strategy"] = "fight_defector"

        # forgive early stage
        if num_rounds <= LONG_WINDOW:
            if memory["strategy"] == None:
                choice = 1
                memory["strategy"] = "forgivingAgent"
        elif memory["strategy"] == "forgivingAgent":
            memory["strategy"] = None

        # maybe fighting random?
        if num_rounds >= VERY_LONG_WINDOW:
            enemy_moves = history[1, :]
            flipped_enemy_move = numpy.abs(enemy_moves - 1)
            defection_rate_medium_window = numpy.average(flipped_enemy_move)
            if defection_rate_medium_window >= (RANDOM_DEFECTION_RATE_THRESHOLD):
                memory["strategy"] = "fight_random"

    if memory["strategy"] == "detective":
        # most detective is either:
        #   1. defect at first round and have two more schedule
        #   2. defect at second round and have two more schedule
        #   3. defect at second round and have three more schedule
        
        if memory["counter"] > 0:
            choice = TEST_DETECTIVE_SCHEDULE[memory["counter"]-1]
            memory["counter"] -= 1
        elif memory["counter"] <= 0:
            memory["strategy"] = None

    if memory["strategy"] == "fight_defector":
        # want to make up?
        if opponents_last_move == 1:
            choice = 1
            memory["strategy"] == None
        else:
            choice = 0

    if memory["strategy"] == "fight_random":
        choice = 0
        enemy_moves = history[1, -MEDIUM_WINDOW:]

        # random shold never always defect
        if numpy.sum(enemy_moves) <= 0.1: # <= 0 but avoiding floating error
            memory["strategy"] == None
            choice = 1

    # default strategy
    if (
        (num_rounds <= LONG_WINDOW and memory["strategy"] == None)
        or memory["strategy"] == "forgivingAgent"
    ):
        # forgivingAgent
        choice, _ = forgivingAgent(history, memory)
    elif (
        memory["strategy"] == None
        or memory["strategy"] == "nprtt"
        ):
        
        choice, _ = nprtt(
            history, 
            None, 
            num_rounds, 
            opponents_last_move, 
            our_second_last_move, 
            MAX_DEFECTION_THRESHOLD
            )
        
    try:
        return choice, memory
    except:
        print(memory)
        print(choice)


def nprtt(history, memory, num_rounds, opponents_last_move, our_second_last_move, defection_threshold=0.5):
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
    opponent_history = history[1, 0:num_rounds]
    if num_rounds == 0:
        opponent_defection_rate = 0
    else:
        opponent_stats = dict(zip(*numpy.unique(opponent_history, return_counts=True)))
        opponent_defection_rate = Decimal(int(opponent_stats.get(0, 0))) / Decimal(
            num_rounds
        )

    # be patient?
    if opponent_defection_rate <= defection_threshold:
        be_patient = True
    else:
        be_patient = False

    choice = (
        1
        if (
            opponents_last_move == 1 
            or (be_patient and our_second_last_move == 0)
            )
        else 0
    )

    return choice, None

def forgivingAgent(history, memory):
    num_rounds = history.shape[1]
    choice = 1 # default is play nice
    if history[1, -1] == 0:
        # [
        #   [X],
        #   [0]
        # ]
        choice = 0
    if num_rounds > 3 and choice == 0:
        # forgive
        if history[0, -2] == 0:
            # [
            #   [0, X],
            #   [1, X]
            # ]
            choice = 1
    return choice, memory
