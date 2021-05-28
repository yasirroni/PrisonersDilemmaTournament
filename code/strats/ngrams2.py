# Implements an Aaronson Oracle, which uses n-grams to predict what action the other player will take
import random

NGRAM_SIZE = 2


def strategy(history, memory):
    if memory is None:
        memory = {}

    choice = None

    latestN = history[1][-(NGRAM_SIZE + 1) :]

    if len(latestN) >= 1:
        # Update ngrams with last opponent decision in history
        latestHistory = latestN[:-1]
        response = latestN[-1]
        historyStr = "".join(str(x) for x in latestHistory)
        if historyStr not in memory:
            memory[historyStr] = [0, 0]
        memory[historyStr][response] += 1

    toPredict = "".join(str(x) for x in latestN[1:])
    # print(toPredict)
    # print(memory)
    if toPredict in memory:
        responses = memory[toPredict]

        choice = 0 if responses[1] < responses[0] and sum(responses) > 1 else 1
        # choice = random.choices([0, 1], responses)[0]
    else:
        choice = 0 if history.shape[1] >= 1 and history[1, -1] == 0 else 1
    # print(choice)
    # print("===========")

    if history.shape[1] % 20 < 2:
        choice = 1

    # print(opponentHistory)
    # choice = random.randint(0, 1)

    return choice, memory