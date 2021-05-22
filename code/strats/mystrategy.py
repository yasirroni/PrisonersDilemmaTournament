import random

# Reminder: For the history array, "cooperate" = 1, "defect" = 0
def strategy(history, memory):
    """
    history is numpy array.
    history[1,-1]: oponents last move
    history[1,n]: oponents move in round (n+1)
    """
    
    def remove_possible_enemy(memory, remove_now):
        for strategy in remove_now:
            try :
                memory['possible_enemy'].remove(strategy)
            except ValueError:
                pass

    def compute_enemy_defectiveness(enemy_memory, constantMul=1):
        return constantMul * sum(enemy_memory) / len(enemy_memory)

    # default titForTat
    choice = 1
    if history.shape[1] >= 1 and history[1,-1] == 0: # Choose to defect if and only if the opponent just defected.
        choice = 0
    
    # first move is to "cooperate"
    if memory == None:
        memory = {}
        memory['possible_enemy'] = [
            'alwaysCooperate',
            'alwaysDefect', 
            'detective', 
            'ftft', 
            'grimTrigger', 
            'joss', # random is hard
            'random',  # random is hard
            'simpleton', 
            'titForTat',
            'UNKNOWN_STRATEGY'
            ]
        memory['used_strategy'] = []
        memory['current_strategy'] = []
        memory['reserved_move'] = []
        memory['testing_enemy'] = []

        return choice, memory

    previous_round = history.shape[1]

    remove_now = []
    if previous_round == 1:
        cooperate_first_move = ['alwaysCooperate', 'detective', 'ftft', 'grimTrigger', 'simpleton', 'titForTat']
        defect_first_move = ['alwaysDefect']

        # see what happen after first round
        if history[1,-1] == 0: # enemy defects
            remove_now = cooperate_first_move
            choice = 0 # go defect and see
        else:
            remove_now = defect_first_move
            choice = 1 # keep cooperate and see

    elif previous_round == 2:
        cooperate_second_move = ['alwaysCooperate', 'ftft', 'grimTrigger', 'simpleton', 'titForTat']
        defect_second_move = ['detective', 'alwaysDefect']
        if history[1,-1] == 0: # enemy defects
            remove_now = cooperate_second_move
            choice = 0 # go defect and see
        else:
            remove_now = defect_second_move
            choice = 1 # keep cooperate and see
    
    elif previous_round == 4:
        if 'detective' in memory['possible_enemy']:
            if any(history[1,0:4] != [1, 0, 1, 1]):
                remove_now = ['detective']
        
        if history[1,-1] == 0:
            choice = 0

    elif history[1,-1] == 1: # Opponent just cooperated.
        remove_now = ['alwaysDefect']
        choice = 1
    
    elif history[1,-1] == 0: # Opponent just defected.
        remove_now = ['alwaysCooperate']
        if 0 not in history[0,:]: # We never defect:
            remove_now.extend(['grimTrigger','simpleton','ftft','titForTat'])
        
        choice = 0
        # if random.random() <= 0.025:
        #     choice = 1
        # else:
        #     choice = 0

    # TODO: FORGIVING JOSS, BUT DON'T TOO MUCH
    # if len(memory['possible_enemy']) == 3 and 'joss' in memory['possible_enemy']:

    #     enemy_defectiveness = compute_enemy_defectiveness(history[1,:],constantMul=2)

    #     if random.random() < enemy_defectiveness:
    #         choice = 0
    #     else:
    #         choice = 1

        # maybe fighting with 'joss' better off just forgive him
        # if previous_round%2 == 0:
        #     choice = 1
        # else:
        #     choice = 0

        # choice = 1
        

    remove_possible_enemy(memory, remove_now)
    return choice, memory