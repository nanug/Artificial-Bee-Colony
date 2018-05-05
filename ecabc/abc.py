#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ecabc/abc.py
#  v.1.1.0.dev1
#  Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  This program implements an artificial bee colony to tune ecnet hyperparameters
#

# 3rd party packages (open src.)
import sys as sys
from random import randint

# artificial bee colony packages
from ecabc.bees import Bee
from ecabc.helper_functions import generateRandomValues, saveScore, blockPrint, enablePrint

### Artificial bee colony object, which contains multiple bee objects ###
class ABC:

    def __init__(self, valueRanges, fitnessFunction=None, endValue = None, iterationAmount = None, amountOfEmployers = 50, filename = 'scores.txt'):
        if endValue == None and iterationAmount == None:
            raise ValueError("must select either an iterationAmount or and endValue")
        if fitnessFunction == None:
            raise ValueError("must pass a fitness function")
        print("***INITIALIZING***")
        self.filename = filename                # Name of file where the scores will be stored
        self.iterationCount = 0
        self.valueRanges = valueRanges
        self.fitnessFunction = fitnessFunction
        self.employers = []
        self.bestValues = []                    # Store the values that are currently performing the best
        self.onlooker = Bee('onlooker')
        self.bestFitnessScore = None            # Store the current best Fitness Score
        self.fitnessAverage = 0
        self.endValue = endValue
        self.iterationAmount = iterationAmount
        self.mm = 'min'
        # Initialize employer bees, assign them values/fitness scores
        self.createEmployerBees(amountOfEmployers)
        print("***DONE INITIALIZING***")
     
    ### Assign a new position to the given bee
    def assignNewPositions(self, firstBee):
        valueTypes = [t[0] for t in self.valueRanges]
        secondBee = randint(0, len(self.employers) -1)
        # Avoid both bees being the same
        while (secondBee == firstBee):
            secondBee = randint(0, len(self.onlooker.bestEmployers) -1)
        self.onlooker.getPosition(self.employers, firstBee, secondBee, self.fitnessFunction, valueTypes)
    
    ### Collect the average fitness score across all employers
    def getFitnessAverage(self):
        self.fitnessAverage = 0
        for employer in self.employers:
            self.fitnessAverage += employer.currFitnessScore
            # While iterating through employers, look for the best fitness score/value pairing
            if self.isBetterThanCurrBest(employer):
                self.bestFitnessScore = employer.currFitnessScore
                self.bestValues = employer.values  
        self.fitnessAverage /= len(self.employers)
    
    ### Check if new position is better than current position held by a bee
    def checkNewPositions(self, bee):
        # Update the bee's fitness/value pair if the new location is better
        if self.isWorseThanAverage(bee):
            bee.values = generateRandomValues(self.valueRanges)
            bee.currFitnessScore = self.fitnessFunction(bee.values)
        else:
            # Assign the well performing bees to the onlooker
            self.onlooker.bestEmployers.append(bee)

    ### If termination depends on a target value, check to see if it has been reached
    def checkIfDone(self, count):
        keepGoing = True
        if self.endValue != None:
            for employer in self.employers:
                    if self.betterThanEndValue(employer):
                        print("Fitness score =", employer.currFitnessScore)
                        print("Values =", employer.values)
                        keepGoing = False
        elif count >= self.iterationAmount:
            keepGoing = False
        return keepGoing
    
    ### Create employer bees
    def createEmployerBees(self, amountOfEmployers):
        for i in range(amountOfEmployers):
            sys.stdout.flush()
            sys.stdout.write("Creating bee number: %d \r" % (i + 1))
            self.employers.append(Bee('employer', generateRandomValues(self.valueRanges)))
            self.employers[i].currFitnessScore = self.fitnessFunction(self.employers[i].values)
    
    ### Specify whether the artificial bee colony will maximize or minimize the fitness cost
    def specifyMinOrMax(self, mm):
        if (mm == 'max'):
            self.mm = 'max'
        
    ### Return whether the bee has a fitness score worse than the average
    def isWorseThanAverage(self, bee):
        return (self.mm == 'min' and bee.currFitnessScore  > self.fitnessAverage) or\
               (self.mm == 'max' and bee.currFitnessScore < self.fitnessAverage)
    
    ### Return whether the bee's fitness score hits the specified end value
    def betterThanEndValue(self, bee):
        return (self.mm == 'min' and bee.currFitnessScore <= self.endValue) or\
               (self.mm == 'max' and bee.currFitnessScore >= self.endValue)

    ### Return whether a bee's fitness average is better than the current best fitness score
    def isBetterThanCurrBest(self, bee):
        return self.bestFitnessScore == None or (self.mm == 'min' and bee.currFitnessScore < self.bestFitnessScore) or\
               (self.mm == 'max' and bee.currFitnessScore > self.bestFitnessScore)

    ### Decide whether print statements will occur
    def printInfo(self, yn):
        if yn == True:
            enablePrint()
        elif yn == False:
            blockPrint()
            
    ### Run the artificial bee colony
    def runABC(self):
        running = True

        while True:
            self.onlooker.bestEmployers.clear()
            print("Assigning new positions")
            for i in range(len(self.onlooker.bestEmployers)):
                sys.stdout.flush()
                sys.stdout.write('At bee number: %d \r' % (i+1))
                self.assignNewPositions(i)
            print("Getting fitness average")
            self.getFitnessAverage()
            print("Checking if done")
            running = self.checkIfDone(self.iterationCount)
            if running == False and self.endValue != None:
                saveScore(self.bestFitnessScore, self.bestValues, self.iterationCount, self.filename)
                break
            print("Current fitness average:", self.fitnessAverage)
            print("Checking new positions, assigning random positions to bad ones")
            for employer in self.employers:
                self.checkNewPositions(employer)
            print("Best score:", self.bestFitnessScore)
            print("Best value:", self.bestValues)
            if self.iterationAmount != None:
                print("Iteration {} / {}".format(self.iterationCount, self.iterationAmount))
            if running == False:
                saveScore(self.bestFitnessScore, self.bestValues, self.iterationCount, self.filename)
                break
            saveScore(self.bestFitnessScore, self.bestValues, self.iterationCount, self.filename)
            self.iterationCount+=1

        return self.bestValues
