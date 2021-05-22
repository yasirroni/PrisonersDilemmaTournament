import random

# Reminder: For the history array, "cooperate" = 1, "defect" = 0

def strategy(history, memory):
    if random.randint(0,1) == 0:
        return 1, None
    else:
        return 0, None
