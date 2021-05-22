import random
import numpy as np

# Fast Detective using:
# Defect, Cooperate, Cooperate
# If enemy ever defect, use titForTat
# If fighting happen, say sorry

# Reminder: For the history array, "cooperate" = 1, "defect" = 0

def strategy(history, memory):
    testingSchedule = ["defect", "defect"]
    testingDuration = len(testingSchedule)
    gameLength = history.shape[1]
    
    # titForTat as default
    choice = "cooperate"
    if gameLength >= 1 and history[1,-1] == 0: # Choose to defect if and only if the opponent just defected.
        choice = "defect"

    if memory == None:
        memory = {}
        memory["strategy"] = "initial"
        choice = testingSchedule[0]
        
    if gameLength < testingDuration: # We're still in that initial testing stage.
        choice = testingSchedule[gameLength]
    else:
        if gameLength == testingDuration: # Evaluate exploit
            if history[1,-1] == 1 and history[1,-2] == 1:
                memory["strategy"] = "check_ftft"
            if history[1,-1] == 0 and history[1,-2] == 0:
                memory["strategy"] = "check_peace_willingness"

        if history[1,-1] == 0: # if enemy just defected
            choice = "defect"

            if memory["strategy"] in ["initial", "check_peace_willingness"]:
                # if fighting titForTat, say sorry
                if history[0,-2] == 0 and history[1,-1] == 0: # if my defect countered with defect afterwards
                    choice = "cooperate"
                    memory["strategy"] == "asking_peace"
        else:

            # TODO: VS FTFT
            # TODO: VS JOSS
            # if memory["strategy"] == "exploit" and gameLength >= testingDuration+1:
            #     choice = "defect"
            if memory["strategy"] == "exploit":
                choice = "defect"
            elif memory["strategy"] == "check_ftft":
                choice = "cooperate"
            else:
                choice = "cooperate"
        
        if memory["strategy"] in ["initial", "check_peace_willingness", "asking_peace"]:
            if gameLength > 4:
                if history[0,-1] == 1 and history[0,-2] == 1:
                    # check if my two times peace resulted in two times war
                    if history[1,-2] == 0 and history[1,-1] == 0:
                        memory["strategy"] = "titForTat"
                        choice = "defect"
                    if history[1,-2] == 0 and history[1,-1] == 1:
                        memory["strategy"] = "in_peace"
                        choice = "cooperate"
                    if history[1,-2] == 1 and history[1,-1] == 0:
                        memory["strategy"] = "titForTat" # confused
                        choice = "defect"
                    else: # 1 1
                        memory["strategy"] = "in_peace"
                        choice = "cooperate"
                    if history[0,-4:].tolist() == [1,1,1,1] and history[1,-4:].tolist() == [0,0,0,0]:
                        memory["strategy"] = "defector"
                        choice = "defect"
                else:
                    choice = "cooperate"

        if memory["strategy"] == "titForTat":
            if history[1,-1] == 0:
                choice = "defect"

            if gameLength > 4:
                if history[1,-2] == 0 and history[1,-1] == 0 and 1 in history[1,-4:]:
                    memory["strategy"] = "asking_peace"
                    choice = "cooperate"

        if memory["strategy"] == "check_ftft":
            if gameLength >= testingDuration + 1:
                if history[0,-3] == 0 and history[0,-2] == 0 and history[1,-2] == 1 and history[1,-1] == 0:
                    memory["strategy"] = "exploit_ftft"
                    if history[0,-1] == 0:
                        choice = "cooperate"
                    else:
                        choice = "defect"
                else:
                    memory["strategy"] = "exploit_always_cooperate"
                    choice = "defect"
        
        if memory["strategy"] == "exploit_ftft":
            if history[0,-1] == 0:
                choice = "cooperate"
            else:
                choice = "defect"

            # something wrong, ftft should never defected
            if history[1,-1] == 0:
                if history[0,-2] == 0 and history[0,-3] == 0:
                    # myfault attacking ftft two times
                    if history[0,-1] == 0:
                        choice = "cooperate"
                    else:
                        choice = "defect"
                else:
                    # really, ftft should never defected
                    memory["strategy"] = "asking_peace"
                    choice = "cooperate"

        if memory["strategy"] == "exploit_always_cooperate":
            choice = "defect"
            
            # something wrong, in always cooperate should never defected
            if history[1,-1] == 0:
                memory["strategy"] = "asking_peace"
                choice = "cooperate"

        if memory["strategy"] == "in_peace":
            choice = "cooperate"
            
            # something wrong, in peace should never defected
            if history[1,-1] == 0:
                memory["strategy"] = "asking_peace"
                choice = "cooperate"

        if memory["strategy"] == "exploit_pattern":
            choice = "defect"
            if gameLength >= 12:
                enemy_pattern = history[1,-3:].tolist()
                if enemy_pattern == [0,0,0]:
                    # something wrong, pattern changed
                    memory["strategy"] = "asking_peace"
                    choice = "cooperate"

        # pattern check
        if memory["strategy"] in ["initial", "check_peace_willingness", "asking_peace", "titForTat"]:
            if gameLength >= 12:
                self_pattern = history[0,-4:].tolist()
                enemy_pattern = history[1,-6:].tolist()
                if enemy_pattern == [0,0,0,0,0,0]:
                    memory["strategy"] = "defector"
                elif enemy_pattern == [1,0,1,0,1,0]:
                    if self_pattern != [0,1,0,1]:
                        memory["strategy"] = "exploit_pattern"
                    else:
                        memory["strategy"] = "asking_peace"
                        choice = "cooperate"
                elif enemy_pattern == [0,1,0,1,0,1]:
                    if self_pattern != [1,0,1,0]:
                        memory["strategy"] = "exploit_pattern"
                    else:
                        memory["strategy"] = "asking_peace"
                        choice = "cooperate"
                elif enemy_pattern == [1,0,0,1,0,0]:
                    memory["strategy"] = "exploit_pattern"
                elif enemy_pattern == [0,1,0,0,1,0]:
                    memory["strategy"] = "exploit_pattern"
                elif enemy_pattern == [0,0,1,0,0,1]:
                    memory["strategy"] = "exploit_pattern"
                elif enemy_pattern == [1,1,0,1,1,0]:
                    memory["strategy"] = "exploit_pattern"
                elif enemy_pattern == [0,1,1,0,1,1]:
                    memory["strategy"] = "exploit_pattern"
                elif enemy_pattern == [1,0,1,1,0,1]:
                    memory["strategy"] = "exploit_pattern"
        
        if memory["strategy"] in ["defector", "exploit"]:
            choice = "defect"


    return choice, memory
