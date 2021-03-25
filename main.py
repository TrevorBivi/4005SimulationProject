import random
from random import seed

import numpy as np

MAX_BUFFER_SIZE = 2
SIMULATION_TIME = 10000.0
ITERATIONS_PER_UNIT_TIME = 25


def lambdaFromFile(self, file):
    data = open("../dataFiles/" + dataFile,'r').read()
    lines = data.split('\n')
    floats = [float(l) for l in lines[:-2]]
    
    n = len(floats)
    mean = sum(floats) / n
    lmb = 1/mean
    
    return lmb


class RandomExponentialGenerator(object):
    '''
    Generates random numbers using ITT of an exponential distribution
    '''
    def lambdaFromFile(file):
        data = open(file,'r').read()
        lines = data.split('\n')
        floats = [float(l) for l in lines[:-2]]
        
        n = len(floats)
        mean = sum(floats) / n
        lmb = 1/mean
        return lmb

    def __init__(self,initParam):
        if type(initParam) is str:
            self.lmbda = RandomExponentialGenerator.lambdaFromFile(initParam)
        elif type(initParam) is float:
            self.lmbda = initPram
        else:
            raise ValueError("Must pass a lambda or a data file path")
        
    def inverse_cdf(self,uniform_random):
        return np.log(1-uniform_random)/-self.lmbda
    
    def generate(self):
        "generates a random time using the inverse CDF"
        uniform_random = random.uniform(0.0,1.0)
        return int(self.inverse_cdf(uniform_random) * ITERATIONS_PER_UNIT_TIME)


class RandomDataGenerator(object):
    '''
    Generates random numbers by returning a random value from a data file
    '''
    def __init__(self, dataFile):
        data = open(dataFile,'r').read()
        lines = data.split('\n')
        floats = [float(l) for l in lines[:-2]]
        self.tempFloats = floats

    def generate(self):
        """picks a random time directly from the given data file"""
        index = random.randint(0,len(self.tempFloats)-1)
        return int(self.tempFloats[index] * ITERATIONS_PER_UNIT_TIME)

class Workstation(object):
    def __init__(self, name, components, randomGenerator):
        self.name = name

        self.completed = 0
        self.iterationsLeftOnWork = 0
        self.iterationsWaiting = 0
        
        self.randomGenerator = randomGenerator

        self.buffers = {}
        self.takenFromBuffers = {}
        for component in components:
            self.buffers[component] = 0
            self.takenFromBuffers[component] = False
            
    def generateRandomWorkTime(self):
        """set a new random work time"""
        assert self.iterationsLeftOnWork == 0
        self.iterationsLeftOnWork = self.randomGenerator.generate()

    def addToBuffer(self, component):
        """increase the value representing the items in a component buffer"""
        assert (self.buffers[component] < MAX_BUFFER_SIZE)
        self.buffers[component] += 1
        
    def getBuffer(self, componentName):
        """Return how full a buffer is"""
        return self.buffers[componentName]

    def takenFromAllBuffers(self):
        """Check if the workstation is ready to start creating a product"""
        return not (False in list(self.takenFromBuffers.values()))

    def resetTakenFromAllBuffers(self):
        """set the takenFromBuffer dict values to false meaning the workstation needs to take new components"""
        for componentName in list(self.takenFromBuffers.keys()):
            self.takenFromBuffers[componentName] = False

    def attemptTakeFromBuffers(self):
        """for all keys (component names) in takenFromBuffers with False values, try to take from coresponding buffer and set to True"""
        assert not self.takenFromAllBuffers()
        for componentName in list(self.takenFromBuffers.keys()):
            if self.takenFromBuffers[componentName] == False and self.buffers[componentName] > 0:
                self.buffers[componentName] -= 1
                self.takenFromBuffers[componentName] = True
    
    def performIteration(self):
        if self.iterationsLeftOnWork > 0:
            self.iterationsLeftOnWork -= 1
            
        if self.iterationsLeftOnWork == 0:
            if self.takenFromAllBuffers() == True:
                self.resetTakenFromAllBuffers()
                self.completed += 1
                
            self.attemptTakeFromBuffers()
            
            if self.takenFromAllBuffers() == True:
                self.generateRandomWorkTime()
            else:
                self.iterationsWaiting += 1


class Inspector(object):
    def __init__(self, name, components):
        self.name = name
        self.components = components
        
        self.iterationsLeftOnWork = 0
        self.iterationsWaiting = 0
        
        self.getNextComponent()
        
    def generateRandomWorkTime(self):
        """set a new random work time"""
        assert self.iterationsLeftOnWork == 0
        self.iterationsLeftOnWork = self.currentComponent.generateRandomWorkTime()
        
    def getNextComponent(self):
        """start working on a new component"""
        assert self.iterationsLeftOnWork == 0
        
        index = random.randint(0,len(self.components)-1)
        self.currentComponent = self.components[index]
            
        self.generateRandomWorkTime()

    def placeComponentInBuffer(self):
        """return whether currentComponent was placed in some workstation's buffer. Prioratizes least full buffer then lowest index buffer in global workstations list"""
        chosen = None
        chosenSize = MAX_BUFFER_SIZE
        
        for workstation in workstations:
            if self.currentComponent.name in list(workstation.buffers.keys()): #workstation has a corresponding buffer
                workstationBufferSize = workstation.getBuffer(self.currentComponent.name)
                
                if workstationBufferSize < chosenSize: #new least full buffer
                    chosen = workstation
                    chosenSize = workstationBufferSize
                    
        if chosen:
            chosen.addToBuffer(self.currentComponent.name)
            self.currentComponent = None
        return chosen != None

    def performIteration(self):
        if self.iterationsLeftOnWork > 0:
            self.iterationsLeftOnWork -= 1
        if self.iterationsLeftOnWork == 0:
            if self.placeComponentInBuffer():
                self.getNextComponent()
            else:
                self.iterationsWaiting += 1


class Component(object):
    def __init__(self, name, randomGenerator):
        self.name = name
        self.randomObject = randomGenerator

    def generateRandomWorkTime(self):
        """return a new random time"""
        return self.randomObject.generate()



if __name__ == "__main__":

    #seed(1)
    
    #randomGenerator = RandomDataGenerator
    randomGenerator = RandomExponentialGenerator

    components = {
        'C1': Component('C1', randomGenerator('dataFiles/servinsp1.dat')),
        'C2': Component('C2', randomGenerator('dataFiles/servinsp22.dat')),
        'C3': Component('C3', randomGenerator('dataFiles/servinsp23.dat')),
        }

    workstations = [
        Workstation('workstation 1', ('C1',), randomGenerator('dataFiles/ws1.dat')),
        Workstation('workstation 2', ('C1','C2'), randomGenerator('dataFiles/ws2.dat')),
        Workstation('workstation 3', ('C1','C3'), randomGenerator('dataFiles/ws3.dat')),
        ]

    inspectors = [
        Inspector('inspector 1', (components['C1'],)),
        Inspector('inspector 1', (components['C2'],components['C3']) ),
        ]

    iterables = inspectors + workstations

    tenPercentTest = int(SIMULATION_TIME * ITERATIONS_PER_UNIT_TIME / 10)
    print("running...")
    for loop in range(int(SIMULATION_TIME * ITERATIONS_PER_UNIT_TIME)):
        if not loop == 0 and loop % tenPercentTest == 0:
            print(str(loop / tenPercentTest * 10)+"%...")
        for iterable in iterables:
            iterable.performIteration()

    print("Simulated", SIMULATION_TIME, "time  with ", ITERATIONS_PER_UNIT_TIME, "iterations per unit time...")

    for num, workstation in enumerate(workstations):
        print("P" + str(num+1) + " created:", workstation.completed, '(' + str(workstation.completed / SIMULATION_TIME) + " / time unit)")
        
    for iterable in iterables:
        print(iterable.name, "time waiting:", iterable.iterationsWaiting, '(' + str(iterable.iterationsWaiting / ITERATIONS_PER_UNIT_TIME) + ' time units)')
