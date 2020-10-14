#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""

source the problem in the launch command
ex:
python .\numberlink.py "instances/level15m.in"

"""

import time
import sys
import search
from search import Problem
from datetime import datetime

#################
# Problem class #
#################

class State:
	def __init__(self, array, actualPosition, end, actualChar):
		self.array=array
		self.actualPosition=actualPosition
		self.actualChar=actualChar
		self.end=end

	def __eq__(self, other):
		return (self.array == other.array and self.actualPosition == other.actualPosition 
			and self.actualChar == other.actualChar and self.end == other.end)
	
	def __hash__(self):
		tmpArray = []
		for i in self.array:
			tmpArray.append(tuple(i))
		return hash(tuple(tmpArray))

	def __str__(self):
		return "nobody uses you"

	def __lt__(self, other):
		return None

	def copy(self):
		newArray = []
		for i in self.array:
			newArray.append(i.copy())
		newActualPosition = self.actualPosition.copy()
		newActualChar = self.actualChar
		newEnd = self.end.copy()
		return State(newArray, newActualPosition, newEnd, newActualChar)
	
class ShortestRoute(Problem):

	def __init__(self, initial):
		#initial is a state from NumberLink
		self.initial = initial

	def goal_test(self, state):
		directions = [ [0, -1], [0, 1], [-1, 0], [1, 0] ]
		endNeighbor = []
		for i in directions:
			endNeighbor.append([state.end[0]+i[0], state.end[1]+i[1]])
		if state.actualPosition in endNeighbor:
			return True
		else:
			return False

	def actions(self, state):
		directions = [ [-1, 0], [1, 0], [0, -1], [0, 1] ]

		if state.actualPosition[0] == 0:
			directions.remove([-1, 0])
		if state.actualPosition[1] == 0:
			directions.remove([0, -1])
		if state.actualPosition[1] == len(state.array[0])-1:
			directions.remove([0, 1])
		if state.actualPosition[0] == len(state.array)-1:
			directions.remove([1, 0])
		tmp = directions.copy()
		triple = 0 
		for i in tmp:
			if state.array[state.actualPosition[0]+i[0]][state.actualPosition[1]+i[1]] != '.':
				directions.remove(i)
			if state.array[state.actualPosition[0]+i[0]][state.actualPosition[1]+i[1]] == state.actualChar:
				triple += 1
				if triple == 2:
					return []

		return directions

	def result(self, state, action):
		newState = state.copy()
		newState.actualPosition = [newState.actualPosition[0] + action[0], newState.actualPosition[1] + action[1]]
		newState.array[newState.actualPosition[0]][newState.actualPosition[1]] = newState.actualChar
		return newState

	def h(self, node):
		return manhattanHeuristicFunction(node.state.actualPosition, node.state.end)

	def path_cost(self, c, state1, action, state2):
		return manhattanHeuristicFunction(state2.actualPosition, state2.end)

class NumberLink(Problem):

	def __init__(self, initial):
		self.chars, self.startEnd = findPosAndChar(initial, True, True)
		self.initial = State(initial, self.startEnd[0][0], self.startEnd[0][1], self.chars[0])

	def goal_test(self, state):
		if state.actualChar != self.chars[len(self.chars)-1]:
			return False
		else:
			directions = [ [0, -1], [0, 1], [-1, 0], [1, 0] ]
			endNeighbor = []
			for i in directions:
				endNeighbor.append([state.end[0]+i[0], state.end[1]+i[1]])
			if state.actualPosition in endNeighbor:
				for i in range(len(state.array)):
					for j in range(len(state.array[0])):
						if state.array[i][j] == '.':
							return False
				return True
			return False
    
	def actions(self, state):
		directions = [ [-1, 0], [1, 0], [0, -1], [0, 1] ]
		for i in range(self.chars.index(state.actualChar)+1, len(self.chars)):
			if not pathExists(state.array, self.startEnd[i][0], self.startEnd[i][1]):
				return []

		if state.actualPosition[0] == 0:
			directions.remove([-1, 0])
		if state.actualPosition[1] == 0:
			directions.remove([0, -1])
		if state.actualPosition[1] == len(state.array[0])-1:
			directions.remove([0, 1])
		if state.actualPosition[0] == len(state.array)-1:
			directions.remove([1, 0])
		tmp = directions.copy()
		triple = 0 
		for i in tmp:
			if state.array[state.actualPosition[0]+i[0]][state.actualPosition[1]+i[1]] != '.':
				directions.remove(i)
			if state.array[state.actualPosition[0]+i[0]][state.actualPosition[1]+i[1]] == state.actualChar:
				triple += 1
				if triple == 2:
					return []

		return directions
    
	def result(self, state, action):
		newState = state.copy()
		newState.actualPosition = [newState.actualPosition[0] + action[0], newState.actualPosition[1] + action[1]]
		newState.array[newState.actualPosition[0]][newState.actualPosition[1]] = newState.actualChar
		directions = [ [0, -1], [0, 1], [-1, 0], [1, 0] ]
		endNeighbor = []
		for i in directions:
			endNeighbor.append([newState.end[0]+i[0], newState.end[1]+i[1]])
		if newState.actualPosition in endNeighbor and newState.actualChar != self.chars[len(self.chars)-1]:
			nextIndex = self.chars.index(newState.actualChar) + 1
			newState.actualChar = self.chars[nextIndex]
			newState.actualPosition = self.startEnd[nextIndex][0]
			newState.end = self.startEnd[nextIndex][1]
		return newState

	def h(self, node):
		nbOfPoint = 0
		for i in node.state.array:
			nbOfPoint += i.count('.')
		return nbOfPoint
		
	def path_cost(self, c, state1, action, state2):
		return manhattanHeuristicFunction(state2.actualPosition, state2.end)



######################
# Auxiliary function #
######################

def findPosAndChar(array, returnSorted, invertSort=False):
	"""
	this function will find the differents characters in the array and put them into chars array
	by the same time it'll put the position of the found characters into another array named startEnd 
	so with the index of a given character in chars, we'll be able to know where are the two characters
	in the whole array (at the beginning)
	for instance, with easy.in, it gives
	chars = ['A', 'B', 'C', 'D'] 
	startEnd = [[[0, 0], [0, 4]], [[1, 0], [1, 4]], [[2, 0], [2, 4]], [[3, 0], [3, 4]]]
	the index of A in chars is 0, so with startEnd at the index 0, we have the two position of 'A'
	which are [[0, 0], [0, 4]]
	then it'll sort the arrays in the way that the firsts indexes of sortedChars and sortedStartEnd
	are the one with the smallest path between start and end
	if invertSort = true, then the biggest path is returned first and the smallest last
	"""
	#find
	chars=[]
	startEnd=[]
	for i in range(len(array)):
			for j in range(len(array[0])):
				char = array[i][j]
				if char != '.' and char not in chars:
					chars.append(char)
					startEnd.append([[i, j]])
				elif char != '.' and char in chars:
					startEnd[chars.index(char)].append([i, j])
	if not returnSorted:
		return chars, startEnd

	#sort
	costs = []
	for i in range(len(chars)):
		state = State(array, startEnd[i][0], startEnd[i][1], chars[i])
		shortestPath = ShortestRoute(state)
		path = search.astar_search(shortestPath).path()
		cost = len(path)
		costs.append([cost, chars[i]])
	
	costs = sorted(costs)
	sortedChars = ['0' for _ in range(len(costs))]
	sortedStartEnd = [[[0,0], [0,0]] for _ in range(len(costs))]
	for i in range(len(costs)):
		if invertSort:
			index = len(costs)-1-i
		else:
			index = i
		sortedChars[index] = costs[i][1]
		sortedStartEnd[index] = startEnd[chars.index(costs[i][1])]

	return sortedChars, sortedStartEnd

def manhattanHeuristicFunction(firstPoint, secondPoint):
	return abs(secondPoint[1] - firstPoint[1]) + abs(secondPoint[0] - firstPoint[0])

directions = [ [0, -1], [0, 1], [-1, 0], [1, 0] ]

def pathExists(grid, start, end):
	visited = [ [0 for j in range(0, len(grid[0]))] for i in range(0, len(grid)) ]
	ok = pathExistsDFS(grid, start, end, visited)
	return ok

def pathExistsDFS(grid, start, end, visited):
	for d in directions:
		i = start[0] + d[0]
		j = start[1] + d[1]
		next = [i, j]
		if i == end[0] and j == end[1]:
			return True
		if inBounds(grid, next) and grid[i][j] == '.' and not visited[i][j]:
			visited[i][j] = 1
			exists = pathExistsDFS(grid, next, end, visited)
			if exists:
				return True
	return False

def inBounds(grid, pos):
	return 0 <= pos[0] and pos[0] < len(grid) and 0 <= pos[1] and pos[1] < len(grid[0])

def openFile(path):
	monfichier= open(path)
	text=monfichier.read()
	monfichier.close()
	text=text.split('\n')
	del text[-1]
	array=list()
	for n in text :
		array.append(list(n))
	output=[]
	for d in array:
		for n in d:
			if n not in output:
				output.append(n)

	return array


def beautifulPath(array):
	for i in array:
		for j in i:
			print(j, end=' ')
		print()
	print()

#####################
# Launch the search #
#####################

print("In the worst case, you'll have to wait 30 seconds (for the most difficult problem \"level15m\")")

grid = openFile(sys.argv[1])

now = datetime.now()

problem = NumberLink(grid)
resolution = search.astar_search(problem) 
#I use astar, it's way faster in general than breadth_first_graph_search and less RAM consuming than depth_first_graph_search

later = datetime.now()

for s in resolution.path():
	print(beautifulPath(s.state.array))

print("It takes", (later - now).total_seconds(), "s for the resolution\n")

"""

someStats = [
	["easy: ", 0.01],
	["path: ", 0.16],
	["level38s: ", 0.03],
	["level39s: ", 0.1],
	["level2m: ", 11],
	["level4m: ", 0.51],
	["level9m: ", 0.45],
	["level10m: ", 20],
	["level15m: ", 24]]

print("some statistics (in seconds) on levels solving with my seven years old computer")
beautifulPath(someStats)

"""