# myAgents.py
# ---------------
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

from game import Agent
from searchProblems import PositionSearchProblem
from game import Directions
import util
import time
import search

"""
IMPORTANT
`agent` defines which agent you will use. By default, it is set to ClosestDotAgent,
but when you're ready to test your own agent, replace it with MyAgent
"""
def createAgents(num_pacmen, agent='ClosestDotAgent'):
    return [eval('MyAgent')(index=i) for i in range(num_pacmen)]

class MyAgent(Agent):
    """
    Implementation of your agent.
    """
    #1. 코드의 줄을 최대한 줄인다.
    #2. 딕셔너리의 처리 속도가 가장 빠른 점을 고려해, 저장은 딕셔너리로 최대한 한다.
    #3. 과제 1의 searchAgents.py와 하단의 closetDotAgent 활용


    def BFS(self, problem):
        CurrentState = [problem.getStartState(), [], 0] #position, move, cost
        fringe = util.Queue()
        fringe.push(CurrentState)
        visitedPosition = [CurrentState[0]] #checklist of visited node

        while fringe.isEmpty() is False:
            CurrentState = fringe.pop()
            position = CurrentState[0]

            if problem.isGoalState(position):
                return CurrentState[1]

            for item in problem.getSuccessors(position):
                if item[0] not in visitedPosition:
                    visitedPosition.append(item[0])
                    pacmanRoute = CurrentState[1].copy()
                    pacmanRoute.append(item[1])
                    fringe.push([item[0], pacmanRoute, CurrentState[2] + item[2]])

        return CurrentState[1]


    def getAction(self, state):
        """
        Returns the next action the agent will take
        """
        problem = AnyFoodSearchProblem(state, self.index)

        self.Action = self.BFS(problem)
        action = self.Action.pop(0)


        return action
    "*** YOUR CODE HERE ***"

    def initialize(self):
        """
        Intialize anything you want to here. This function is called
        when the agent is first created. If you don't need to use it, then
        leave it blank
        """

        "*** YOUR CODE HERE"
        self.Action = []

        #raise NotImplementedError()

"""
Put any other SearchProblems or search methods below. You may also import classes/methods in
search.py and searchProblems.py. (ClosestDotAgent as an example below)
"""

class ClosestDotAgent(Agent):

    def findPathToClosestDot(self, gameState):
        """
        Returns a path (a list of actions) to the closest dot, starting from
        gameState.
        """
        # Here are some useful elements of the startState
        startPosition = gameState.getPacmanPosition(self.index)
        food = gameState.getFood()
        walls = gameState.getWalls()
        problem = AnyFoodSearchProblem(gameState, self.index)

        "*** YOUR CODE HERE ***"

        pacmanCurrent = [problem.getStartState(), [], 0]
        visitedPosition = set()
        # visitedPosition.add(problem.getStartState())
        fringe = util.PriorityQueue()
        fringe.push(pacmanCurrent, pacmanCurrent[2])
        while not fringe.isEmpty():
            pacmanCurrent = fringe.pop()
            if pacmanCurrent[0] in visitedPosition:
                continue
            else:
                visitedPosition.add(pacmanCurrent[0])
            if problem.isGoalState(pacmanCurrent[0]):
                return pacmanCurrent[1]
            else:
                pacmanSuccessors = problem.getSuccessors(pacmanCurrent[0])
            Successor = []
            for item in pacmanSuccessors:  # item: [(x,y), 'direction', cost]
                if item[0] not in visitedPosition:
                    pacmanRoute = pacmanCurrent[1].copy()
                    pacmanRoute.append(item[1])
                    sumCost = pacmanCurrent[2]
                    Successor.append([item[0], pacmanRoute, sumCost + item[2]])
            for item in Successor:
                fringe.push(item, item[2])
        return pacmanCurrent[1]

    def getAction(self, state):
        return self.findPathToClosestDot(state)[0]

class AnyFoodSearchProblem(PositionSearchProblem):
    """
    A search problem for finding a path to any food.

    This search problem is just like the PositionSearchProblem, but has a
    different goal test, which you need to fill in below.  The state space and
    successor function do not need to be changed.

    The class definition above, AnyFoodSearchProblem(PositionSearchProblem),
    inherits the methods of the PositionSearchProblem.

    You can use this search problem to help you fill in the findPathToClosestDot
    method.
    """

    def __init__(self, gameState, agentIndex):
        "Stores information from the gameState.  You don't need to change this."
        # Store the food for later reference
        self.food = gameState.getFood()

        # Store info for the PositionSearchProblem (no need to change this)
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition(agentIndex)
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE

    def isGoalState(self, state):
        """
        The state is Pacman's position. Fill this in with a goal test that will
        complete the problem definition.
        """
        x,y = state
        if self.food[x][y] == True:
            return True
        return False

