from decimal import Decimal
import numpy

# nprtt but compare various response
def strategy(history, memory):
    MEDIUM_WINDOW = 8

    num_rounds = history.shape[1] # elapsed round

    choice = None # place holder
    if num_rounds == 0:
        memory = {}
        memory["strategy_list"] = ["forgivingTitForTat", "nprtt", "titForTat", "alwaysDefect"]
        memory["strategy_counter"] = 0
        memory["moved_counter"] = 0
        memory["score"] = [0] * len(memory["strategy_list"])
        memory["strategy_fixed"] = False
        choice = 1

        return choice, memory
       
    # extract history move
    our_history = history[0, :]
    opponent_history = history[1, :]

    if memory["strategy_fixed"] == False:
        if num_rounds >= MEDIUM_WINDOW:
            if memory["strategy_counter"] == 0:
                if opponent_history[-1] == 0:
                    memory["strategy_counter"] += 1
                    memory["moved_counter"] = MEDIUM_WINDOW
        else:
            choice, _ = forgivingTitForTat(history, None)
            return choice, memory

        if memory["strategy_counter"] > 0:
            if memory["moved_counter"] == 0:
                memory["strategy_counter"] += 1
                memory["moved_counter"] = MEDIUM_WINDOW
            else:
                memory["moved_counter"] += -1
        
        if memory["strategy_counter"] == len(memory["strategy_list"]):
            memory["strategy_counter"] += -1
            upper_bound = num_rounds - 0
            lower_bound = upper_bound - MEDIUM_WINDOW

            ## evaluate who is the best
            while memory["strategy_counter"] > -1:
                history_slice = history[:,lower_bound:upper_bound]
                score, _ = compute_score(history_slice)
                memory["score"][memory["strategy_counter"]] = score
                memory["strategy_counter"] += -1

                upper_bound = lower_bound - 0
                lower_bound = upper_bound - MEDIUM_WINDOW

            memory["strategy_fixed"] = True
            memory["strategy_counter"] = numpy.argmin(memory["score"])

    if memory["strategy_list"][memory["strategy_counter"]] == "forgivingTitForTat" or choice == None:
        choice, _ = forgivingTitForTat(history, None)
        return choice, memory
    elif memory["strategy_list"][memory["strategy_counter"]] == "nprtt":
        choice, _ = nprtt(history, None)
        return choice, memory
    elif memory["strategy_list"][memory["strategy_counter"]] == "titForTat":
        choice, _ = titForTat(history, None)
        return choice, memory
    elif memory["strategy_list"][memory["strategy_counter"]] == "alwaysDefect":
        choice, _ = alwaysDefect(history, None)
        return choice, memory

    return choice, memory

def nprtt(history, memory):
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
    num_rounds = history.shape[1]

    opponents_last_move = history[1, -1] if num_rounds >= 1 else 1
    our_second_last_move = history[0, -2] if num_rounds >= 2 else 1

    # if opponent defects more often, then screw 'em
    MAX_DEFECTION_THRESHOLD = Decimal(1) / Decimal(2)

    opponent_history = history[1, 0:num_rounds]
    if num_rounds == 0:
        opponent_defection_rate = 0
    else:
        opponent_stats = dict(zip(*numpy.unique(opponent_history, return_counts=True)))
        opponent_defection_rate = Decimal(int(opponent_stats.get(0, 0))) / Decimal(
            num_rounds
        )

    be_patient = opponent_defection_rate <= MAX_DEFECTION_THRESHOLD

    choice = (
        1
        if (opponents_last_move == 1 or (be_patient and our_second_last_move == 0))
        else 0
    )

    return choice, None

def forgivingTitForTat(history, memory):
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

    return choice, None

def alwaysDefect(history, memory):
    return 0, None

def titForTat(history, memory):
    choice = 1
    if (
        history.shape[1] >= 1 and history[1, -1] == 0
    ):  # Choose to defect if and only if the opponent just defected.
        choice = 0
    return choice, None

def compute_score(history, pointsArray=[[1,5],[0,3]]):
    """
    :pointsArray: 2 x 2 points table
    
    The i-j-th element of this array is how many points you receive if you do play i, and your opponent does play j.
    """

    scoreA = 0
    scoreB = 0
    ROUND_LENGTH = history.shape[1]
    for turn in range(ROUND_LENGTH):
        playerAmove = history[0, turn]
        playerBmove = history[1, turn]
        scoreA += pointsArray[playerAmove][playerBmove]
        scoreB += pointsArray[playerBmove][playerAmove]
    return scoreA / ROUND_LENGTH, scoreB / ROUND_LENGTH
