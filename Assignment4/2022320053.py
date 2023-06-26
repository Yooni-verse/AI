#2022320053 ShinJungYoon BestAgent

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
 
  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()    
    features['successorScore'] = -len(foodList)
  
    myPos = successor.getAgentState(self.index).getPosition()
    getFood = gameState.getAgentState(self.index).numCarrying #number of current food in offensive agent.

    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    ghost_gurdians = [a for a in enemies if not a.isPacman and a.getPosition() != None]
    
    # if my team is red, my Pacman in blue side run away from opponent's ghost
    for ghost in ghost_gurdians:
      ghost_position = ghost.getPosition()
      if successor.getAgentState(self.index).isPacman and getFood!=0:
        ghost_dist = self.getMazeDistance(myPos,ghost_position)
        if getFood != 0:
          if ghost_dist<8: 
            features['run'] = 1
            if ghost_dist<4:
              features['run'] = (9-ghost_dist)*1000
        else:
          features['run'] = 0
    
    if self.getTeam(gameState)[0] % 2 == 0: #red team
      Capsule = gameState.getBlueCapsules()
      team = 0
    else: #blue team
      Capsule = gameState.getRedCapsules()
      team = 1

    #if the score exceeds 4(red team), a new mission is assigned.
    if (team == 0 and gameState.getScore() > 4) or (team ==1 and gameState.getScore()<-4):
        if len(Capsule)>0:
          cap_dist = self.getMazeDistance(myPos,Capsule[0])
          if cap_dist < 4:
            features['Capsule'] = 1
              
    #if Pacman eat food, he go to home and get score
    if getFood >= 1:
      dist = self.getMazeDistance(myPos, self.start)
      features['home'] = dist

    # Compute distance to the nearest food

    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1, 'run':-1000000000000, 'home': -100000000, 'Capsule': -10}

class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    ghostTimer = gameState.getAgentState(self.index).scaredTimer

    
    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    
    if self.getTeam(gameState)[0] % 2 == 0: #red team
      Capsule = gameState.getRedCapsules()
    else: #blue team
      Capsule = gameState.getBlueCapsules()

         

    for invade in invaders:
      invader_position = invade.getPosition()
      dist = self.getMazeDistance(myPos, invader_position)

      if dist < 4:
      #if the distance between ghost and invader becomes less than 4, protect the capsule as much as possible.
        if len(Capsule) > 0:
          features ['protect'] = self.getMazeDistance(myPos,Capsule[0])
      #if denfender is "scared", he run away
      if ghostTimer != 0:
        features ['scared_run'] = dist
      else:
        features ['scared_run'] = 0
    

    
    
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2, 'scared_run': -100, 'protect': 10}
