from Bees import *


class ABC:

    def __init__(self, endValue):

        print("INITIALIZING")
        self.scouts = []
        self.employers = []
        self.bestValues = []
        self.cycle = 0
        self.onlooker = Bee('onlooker')
        self.bestFitnessScore = 10000
        self.fitnessAverage = 0
        self.endValue = endValue

        for i in range(10):
            self.scouts.append(Bee('scout'))

        for i in range(50):
            print("Creating bee number:", i + 1)
            self.employers.append(Bee('employer', generateRandomValues()))
            self.employers[i].currFitnessScore = runNeuralNet(self.employers[i].values)

    def assignNewPositions(self, firstBee):
        secondBee = randint(0, len(self.employers) -1)
        while (secondBee == firstBee):
            secondBee = randint(0, len(self.employers) -1)
        self.onlooker.getPosition(self.employers, firstBee, secondBee)

    def getFitnessAverage(self):
        self.fitnessAverage = 0
        for employer in self.employers:
            self.fitnessAverage += employer.currFitnessScore
            if employer.currFitnessScore < self.bestFitnessScore:
                self.bestFitnessScore = employer.currFitnessScore
                self.bestValues = employer.values
        self.fitnessAverage /= len(self.employers)

    def checkNewPositions(self, bee):
        if bee.currFitnessScore  > self.fitnessAverage:
            print("Assigning new value for a bee")
            bee.values = self.onlooker.findRandomLocation()
            bee.currFitnessScore = runNeuralNet(bee.values)

    def checkIfDone(self):
        keepGoing = True
        for employer in self.employers:
            if employer.currFitnessScore <= self.endValue:
                print("Fitness score =", employer.currFitnessScore)
                print("Values =", employer.values)
                keepGoing = False
        return keepGoing

    def runABC(self):
        running = True

        while True:
            print("Assigning new positions")
            for i in range(len(self.employers)):
                self.assignNewPositions(i)

            print("Checking if done")
            running = self.checkIfDone()
            if running == False:
                break

            print("Getting fitness average")
            self.getFitnessAverage()

            print("Current fitness average:", self.fitnessAverage)
            print("Checking new positions, assigning random positions to bad ones")
            for employer in self.employers:
                self.checkNewPositions(employer)

            print("Best score:", self.bestFitnessScore)
            print("Best value:", self.bestValues)
