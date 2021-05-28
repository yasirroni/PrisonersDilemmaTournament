import random
import numpy as np

# Fast Detective using:
# Defect, Cooperate, Cooperate

# Reminder: For the history array, "cooperate" = 1, "defect" = 0

def strategy(history, memory):
    testingSchedule = ["defect","cooperate","cooperate"]
    testingDuration = len(testingSchedule)
    gameLength = history.shape[1]
    shallIExploit = memory
    choice = None
    
    if gameLength < testingDuration: # We're still in that initial testing stage.
        choice = testingSchedule[gameLength]
    elif gameLength == testingDuration: # Time to analyze the testing stage and decide what to do based on what the opponent did in that time!
        opponentsActions = history[1]
        if np.count_nonzero(opponentsActions-1) == 0: # The opponent cooperated all turns! Never defected!
            shallIExploit = True # Let's exploit forever.
        else:
            shallIExploit = False # Let's switch to Tit For Tat.
    
    if gameLength >= testingDuration:
        if shallIExploit:
            choice = 0
        else:
            choice = history[1,-1] # Do Tit for Tat
    
    return choice, shallIExploit
