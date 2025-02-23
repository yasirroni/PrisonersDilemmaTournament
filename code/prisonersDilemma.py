import csv
import importlib
import itertools
import os
import random
import pathlib

import numpy as np
from decimal import Decimal  # precise fixed-point arithmetic

def getVisibleHistory(history, player, turn):
    historySoFar = history[:, :turn].copy()
    if player == 1:
        historySoFar = np.flip(historySoFar, 0)
    return historySoFar

def strategyMove(move):
    if type(move) is str:
        defects = ["defect", "tell truth"]
        return 0 if (move in defects) else 1
    else:
        return move

def runRound(STRATEGY_FOLDER, pair, minGameLength=200, logMultiplier=40):
    """
    Returns a 2-by-n numpy array. The first axis is which player (0 = us, 1 = opponent)
    The second axis is which turn. (0 = first turn, 1 = next turn, etc.
    For example, it might have the values
    
    [[0 0 1]       a.k.a.    D D C
     [1 1 1]]      a.k.a.    C C C
    
    if there have been 3 turns, and we have defected twice then cooperated once,
    and our opponent has cooperated all three times.
    """

    moduleA = importlib.import_module(STRATEGY_FOLDER+"."+pair[0])
    moduleB = importlib.import_module(STRATEGY_FOLDER+"."+pair[1])
    memoryA = None
    memoryB = None

    LENGTH_OF_GAME = int(minGameLength-logMultiplier*np.log(random.random())) # The games are a minimum of 50 turns long. The np.log here guarantees that every turn after the 50th has an equal (low) chance of being the final turn.
    history = np.zeros((2,LENGTH_OF_GAME),dtype=int) # history(i,:) for player i
    
    for turn in range(LENGTH_OF_GAME):
        playerAmove, memoryA = moduleA.strategy(getVisibleHistory(history,0,turn),memoryA)
        playerBmove, memoryB = moduleB.strategy(getVisibleHistory(history,1,turn),memoryB)
        history[0,turn] = strategyMove(playerAmove)
        history[1,turn] = strategyMove(playerBmove)
        
    return history, memoryA, memoryB

def tallyRoundScores(history, pointsArray=[[1,5],[0,3]]):
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
    return Decimal(scoreA) / ROUND_LENGTH, Decimal(scoreB) / ROUND_LENGTH
    
def outputRoundResults(f, pair, roundHistory, scoresA, scoresB, memoryA, memoryB):
    moveLabels = ["D", "C"] # 1: D, 2: C
    # D = defect,     betray,       sabotage,  free-ride,     etc.
    # C = cooperate,  stay silent,  comply,    upload files,  etc.

    f.write(pair[0] + " (P1)  VS.  " + pair[1] + " (P2)\n")
    for p in range(2):
        for t in range(roundHistory.shape[1]):
            move = roundHistory[p, t]
            f.write(moveLabels[move] + " ")
        f.write("\n")
    f.write("Final score for " + pair[0] + ": " + str(scoresA) + "\n")
    f.write("Final score for " + pair[1] + ": " + str(scoresB) + "\n")
    
    if scoresA > scoresB:
        winner = pair[0]
    elif scoresA < scoresB:
        winner = pair[1]
    else:
        winner = None
    
    if winner:
        f.write("Winner: "+ winner)
    else:
        f.write("Tie!!")

    f.write("\n")

    f.write("Final memory for " + pair[0] + ": " + str(memoryA) + "\n")
    f.write("Final memory for " + pair[1] + ": " + str(memoryB) + "\n")

    f.write("\n")

def outputTournamentResults(f, STRATEGY_LIST, scoreKeeper):
    scoresNumpy = np.zeros(len(scoreKeeper))
    for i in range(len(STRATEGY_LIST)):
        scoresNumpy[i] = scoreKeeper[STRATEGY_LIST[i]]
    rankings = np.argsort(scoresNumpy)

    f.write("\n\nTOTAL SCORES\n")
    for rank in range(len(STRATEGY_LIST)):
        i = rankings[-1 - rank]
        score = scoresNumpy[i]
        scorePer = score / (len(STRATEGY_LIST) - 1)
        f.write(
            "#"
            + str(rank + 1)
            + ": "
            + pad(STRATEGY_LIST[i] + ":", 24)
            + " %.3f" % score
            + "  (%.3f" % scorePer
            + " average)\n"
        )

def pad(stri, leng):
    result = stri
    for i in range(len(stri), leng):
        result = result + " "
    return result

def fetch_strategy(inFolder, exceptStrategy=[]):
    STRATEGY_LIST = []
    script_path = pathlib.Path(__file__).parent.absolute()
    for file in os.listdir(os.path.join(script_path, inFolder)):
        if file.endswith(".py") and file[:-3] not in exceptStrategy:
            STRATEGY_LIST.append(file[:-3])
    return STRATEGY_LIST

def insertIntoNestedDict(nestedDict, keyA, keyB, value):
    if keyA not in nestedDict:
        nestedDict[keyA] = dict()
    nestedDict[keyA][keyB] = value

def runFullPairingTournament(inFolder, outFileResult, outFileHead2Head=None, exceptStrategy=[], singleVersusEveryoneResult=None):
    print("Reading files from " + inFolder)
    scoreKeeper = {}
    headToHead = {}

    script_path = pathlib.Path(__file__).parent.absolute()

    STRATEGY_LIST = fetch_strategy(inFolder, exceptStrategy=exceptStrategy)

    for strategy in STRATEGY_LIST:
        scoreKeeper[strategy] = 0

    if isinstance(outFileResult, str):
        f = open(os.path.join(script_path, outFileResult),"w+")
    else:
        f = outFileResult
    
    if singleVersusEveryoneResult:
        for strategy in STRATEGY_LIST:
            single_result_file = "results_" + strategy + ".txt"
            single_output_path = os.path.join(script_path, single_result_file)
            if os.path.exists(single_output_path):
                os.remove(single_output_path)
                print("REMOVED: " + single_output_path)
    
    print("Starting tournament...")
    for pair in itertools.combinations(STRATEGY_LIST, r=2):
        [roundHistory, scoresA, scoresB, memoryA, memoryB] = _runSinglePairingTournament(inFolder, pair)

        scoreKeeper[pair[0]] += scoresA
        scoreKeeper[pair[1]] += scoresB

        outputRoundResults(f, pair, roundHistory, scoresA, scoresB, memoryA, memoryB)
        insertIntoNestedDict(headToHead, pair[0], pair[1], scoresA)
        insertIntoNestedDict(headToHead, pair[1], pair[0], scoresB)

        if singleVersusEveryoneResult:
            single_result_file = "results_" + pair[0] + ".txt"
            single_output_path = os.path.join(script_path, single_result_file)

            with open(single_output_path, "a+") as single_file:
                outputRoundResults(single_file, pair, roundHistory, scoresA, scoresB, memoryA, memoryB)
            
            single_result_file = "results_" + pair[1] + ".txt"
            single_output_path = os.path.join(script_path, single_result_file)

            with open(single_output_path, "a+") as single_file:
                outputRoundResults(single_file, [pair[1], pair[0]], np.flip(roundHistory, 0), scoresB, scoresA, memoryB, memoryA)

    outputTournamentResults(f, STRATEGY_LIST, scoreKeeper)
        
    f.flush()
    f.close()

    # head2head csv
    if outFileHead2Head:
        script_path = pathlib.Path(__file__).parent.absolute()
        with open(os.path.join(script_path, outFileHead2Head), "w+", newline="") as csvfile:
            h2hwriter = csv.writer(csvfile)  # defaults to Excel dialect
            h2hwriter.writerow(
                [
                    "",
                ]
                + STRATEGY_LIST
            )  # column header
            for strategy in STRATEGY_LIST:
                row = [
                    strategy,
                ]
                for otherStrategy in STRATEGY_LIST:
                    row.append(str(headToHead.get(strategy, dict()).get(otherStrategy, "")))
                h2hwriter.writerow(row)
    
def runSinglePairingTournament(inFolder, outFile, pair):
    """
    pair = list of strategy being evaluated
    """

    if isinstance(outFile, str):
        script_path = pathlib.Path(__file__).parent.absolute()
        f = open(os.path.join(script_path, outFile),"w+")
    else:
        f = outFile

    [roundHistory, scoresA, scoresB, memoryA, memoryB] = _runSinglePairingTournament(inFolder, pair)

    outputRoundResults(f, pair, roundHistory, scoresA, scoresB, memoryA, memoryB) 

    f.flush()
    f.close()

def _runSinglePairingTournament(inFolder, pair):
    roundHistory, memoryA, memoryB = runRound(inFolder, pair)
    scoresA, scoresB = tallyRoundScores(roundHistory)

    return roundHistory, scoresA, scoresB, memoryA, memoryB

if __name__ == "__main__":
    # files
    STRATEGY_FOLDER = "strats"
    RESULTS_FILE = "results.txt"
    H2H_FILE = "headToHead.csv"

    # seed for repeatability
    SEED = 69
    random.seed(SEED)

    # EXCEPT_STRATEGY
    NO_ALWAYS = False
    NO_PURE_RANDOM = False
    NO_MACHINE_LEARNING = False
    NO_PATTERN_BASED_STRATEGY = True
    NO_ADVERSARY_BASED_STRATEGY = False

    EXCEPT_STRATEGY = []

    if NO_ALWAYS:
        EXCEPT_STRATEGY.extend([
            "alwaysCooperate",
            "alwaysDefect"
            ])
    
    if NO_PURE_RANDOM:
        EXCEPT_STRATEGY.extend([
            "randomChoice", # renamed random to randomChoice
            ])

    if NO_MACHINE_LEARNING:
        EXCEPT_STRATEGY.extend([
            "oracle",
            "ngrams2",
            "ngrams2Betrayal",
            "ngrams3"
            ])

    if NO_PATTERN_BASED_STRATEGY:
        EXCEPT_STRATEGY.extend([
            "odd",
            "even",
            "ccd",
            "cdd",
            "fibonacciDefector",
            ])

    if NO_ADVERSARY_BASED_STRATEGY:
        EXCEPT_STRATEGY.extend([
            "confusedTitForTat",
            "opportunisticDefector-1",
            "opportunisticDefector-2",
            "opportunisticDefector-3",
            "opportunisticDefector-4",
            "opportunisticDefector-5",
            "fodnprtthl",
            "properOpportunisticDefector-3",
            "windowed",
            ])

    ## FULL PAIRING TOURNAMENT:
    RESULTS_FILE = "results.txt"
    SINGLE_VERSUS_EVERYONE_RESULT = True
    runFullPairingTournament(
        STRATEGY_FOLDER, 
        RESULTS_FILE, 
        H2H_FILE, 
        EXCEPT_STRATEGY, 
        singleVersusEveryoneResult=SINGLE_VERSUS_EVERYONE_RESULT)
    print("Done with everything! Results file written to " + RESULTS_FILE)

    ## SINGLE PAIRING TOURNAMENT:
    # pair = ["nprstt", "joss"]
    # RESULTS_FILE = "results_" + pair[0] + "_" + pair[1] + ".txt"
    # runSinglePairingTournament(STRATEGY_FOLDER, RESULTS_FILE, pair)
    # print("Done with everything! Results file written to " + RESULTS_FILE)

    ## MYSTRATEGY VS EVERYONE:
    # MYSTRATEGY = "nprttStudent"
    # EXCEPT_STRATEGY.append(MYSTRATEGY)
    # STRATEGY_LIST = fetch_strategy(STRATEGY_FOLDER, exceptStrategy=EXCEPT_STRATEGY)
    # RESULTS_FILE = "results_" + MYSTRATEGY + ".txt"

    # SCRIPT_PATH = pathlib.Path(__file__).parent.absolute()
    # OUTPUT_PATH = os.path.join(SCRIPT_PATH, RESULTS_FILE)
    # if os.path.exists(OUTPUT_PATH):
    #     os.remove(OUTPUT_PATH)
    #     print("REMOVED: " + OUTPUT_PATH)
        
    # for strategy in STRATEGY_LIST:
    #     f = open(OUTPUT_PATH, "a+")
    #     pair = [MYSTRATEGY, strategy]
    #     runSinglePairingTournament(STRATEGY_FOLDER, f, pair)
    # print("Done with everything! Results file written to " + RESULTS_FILE)

    # try: # for safety meassure
    #     f.flush()
    #     f.close()
    # except:
    #     pass
