# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action) #<로 방향 표시
        newPos = successorGameState.getPacmanPosition() #(x,y)
        newFood = successorGameState.getFood() #TF square
        newGhostStates = successorGameState.getGhostStates() #[<game.Agent~>]
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates] #[a,b]

        "*** YOUR CODE HERE ***"
        def Euclideandistance(xy1, xy2):
            return ((xy1[0] - xy2[0])**2 + (xy1[1]-xy2[1])**2)**0.5

        score = successorGameState.getScore()
        Food_distance = [Euclideandistance(newPos,food) for food in newFood.asList()]
        Ghost_distance = [Euclideandistance(newPos,ghost.getPosition()) for ghost in newGhostStates]

        if len(Food_distance):
            f_dist = min(Food_distance)
        else:
            f_dist = 1.0 #if list empty

        g_dist = min(Ghost_distance)
        if g_dist <= 3:
            return -1.0  # pacman run away first

        return score + g_dist / f_dist

def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.
/?{:"P=-
        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        def value(gameState, agentIndex, depth):
            if depth==self.depth or gameState.isWin() or gameState.isLose(): #terminal?
                return self.evaluationFunction(gameState)
            else:
                if agentIndex == 0:
                    return max_value(gameState, depth)
                else:
                    return min_value(gameState, agentIndex, depth)

        def max_value(gameState, depth):
            v = float('-inf')
            for i in gameState.getLegalActions(0):
                v = max(v, value(gameState.generateSuccessor(0, i), 1, depth))
            return v

        def min_value(gameState, agentIndex, depth):
            v = float('inf')
            for i in gameState.getLegalActions(agentIndex):
                if agentIndex == (gameState.getNumAgents()-1):
                    v = min(v, value(gameState.generateSuccessor(agentIndex, i), 0, depth+1))
                else:
                    v = min(v, value(gameState.generateSuccessor(agentIndex, i), agentIndex+1,depth))
            return v

        inf = float('-inf')
        for i in gameState.getLegalActions(0):
            v = value(gameState.generateSuccessor(0,i),1,0)
            if v > inf:
                inf = v
                move = i
        return move

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        def value(gameState, agentIndex, depth,alpha, beta):
            if depth==self.depth or gameState.isWin() or gameState.isLose(): #terminal?
                return self.evaluationFunction(gameState)
            else:
                if agentIndex == 0:
                    return max_value(gameState, depth,alpha,beta)
                else:
                    return min_value(gameState, agentIndex, depth,alpha,beta)

        def max_value(gameState, depth,alpha,beta):
            v = float('-inf')
            for i in gameState.getLegalActions(0):
                v = max(v, value(gameState.generateSuccessor(0, i), 1, depth,alpha,beta))
                if v>beta:
                    return v #pruning
                alpha = max(alpha,v)
            return v

        def min_value(gameState, agentIndex, depth,alpha,beta):
            v = float('inf')
            for i in gameState.getLegalActions(agentIndex):
                if agentIndex == (gameState.getNumAgents()-1):
                    v = min(v, value(gameState.generateSuccessor(agentIndex, i), 0, depth+1,alpha,beta))
                    if v<alpha:
                        return v
                    beta=min(beta,v)
                else:
                    v = min(v, value(gameState.generateSuccessor(agentIndex, i), agentIndex+1,depth,alpha,beta))
                    if v < alpha:
                        return v
                    beta = min(beta, v)
            return v
        alpha = float('-inf')
        beta = float('inf')
        inf = float('-inf')
        for i in gameState.getLegalActions(0):
            v = value(gameState.generateSuccessor(0,i),1,0,alpha,beta)
            if v > inf:
                inf = v
                move = i
            if v>beta:
                return move
            alpha = max(alpha,v)
        return move

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction
