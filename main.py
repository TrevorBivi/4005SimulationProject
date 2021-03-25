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
        """
        name -- name of workstation for debugging
        components -- list of components that the workstation must have a buffer to hold
        randomGenerator -- An object for generating random numbers (must have a method "generate")
        """
        self.name = name

        self.completed = 0
        self.iterationsLeftOnWork = 0
        self.iterationsWaiting = 0
        
        self.randomGenerator = randomGenerator

        self.buffers = {}
        for component in components:
            self.buffers[component] = 0
            
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

    def canTakeFromBuffers(self):
        """returns whether all buffers have an item or not"""
        assert self.iterationsLeftOnWork == 0
        return not 0 in self.buffers.values()

    def takeFromBuffers(self):
        """decrements all buffers"""
        assert self.iterationsLeftOnWork == 0
        for k in self.buffers.keys():
            assert self.buffers[k] > 0
            self.buffers[k] -= 1
    
    def performIteration(self):
        """
        If done working on a component, 
        """
        assert self.iterationsLeftOnWork > -1
        
        if self.iterationsLeftOnWork > 0:
            self.iterationsLeftOnWork -= 1
            if self.iterationsLeftOnWork == 0:
                self.completed += 1
            
        if self.iterationsLeftOnWork == 0:
            if self.canTakeFromBuffers() == True:
                self.takeFromBuffers()
                self.generateRandomWorkTime()
            else:
                self.iterationsWaiting += 1


class Inspector(object):
    def __init__(self, name, components):
        """
        name -- name of inspector for debugging
        components -- iterable of Component objects

        The inspector takes a component on initialization!
        """
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
        """
        If done working on a component, try placing it in a buffer
        If successfully places a component in a buffer, start working on a new component
        """
        assert self.iterationsLeftOnWork > -1
        
        if self.iterationsLeftOnWork > 0:
            self.iterationsLeftOnWork -= 1
        if self.iterationsLeftOnWork == 0:
            if self.placeComponentInBuffer():
                self.getNextComponent()
            else:
                self.iterationsWaiting += 1


class Component(object):
    '''
    Represents some component that needs to go through the simulated system.
    '''
    def __init__(self, name, randomGenerator):
        '''
        name -- name of the component for debugging
        randomGenerator -- An object for making random numbers (must have a method "generate")
        '''
        self.name = name
        self.randomObject = randomGenerator

    def generateRandomWorkTime(self):
        """return a new random time (To be called by workers since the work time depends on component type, not worker)"""
        return self.randomObject.generate()



if __name__ == "__main__":

    #seed(1)
    
    #randomGenerator = RandomDataGenerator
    randomGenerator = RandomExponentialGenerator

    randomGenerators = {
            'servinsp1': randomGenerator('dataFiles/servinsp1.dat'),
            'servinsp22': randomGenerator('dataFiles/servinsp22.dat'),
            'servinsp23': randomGenerator('dataFiles/servinsp23.dat'),
            'ws1': randomGenerator('dataFiles/ws1.dat'),
            'ws2': randomGenerator('dataFiles/ws2.dat'),
            'ws3': randomGenerator('dataFiles/ws3.dat')
        }

    print("Input parameters before...")
    for key in randomGenerators.keys():
        print(key+':',randomGenerators[key].lmbda)

    components = {
        'C1': Component('C1', randomGenerators['servinsp1']),
        'C2': Component('C2', randomGenerators['servinsp22']),
        'C3': Component('C3', randomGenerators['servinsp23']),
        }

    workstations = [
        Workstation('workstation 1', ('C1',), randomGenerators['ws1']),
        Workstation('workstation 2', ('C1','C2'), randomGenerators['ws2']),
        Workstation('workstation 3', ('C1','C3'), randomGenerators['ws3']),
        ]

    inspectors = [
        Inspector('inspector 1', (components['C1'],)),
        Inspector('inspector 1', (components['C2'],components['C3']) ),
        ]



    iterables = inspectors + workstations

    tenPercentTest = int(SIMULATION_TIME * ITERATIONS_PER_UNIT_TIME / 10)
    print("\nrunning...")
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

    print("\nInput parameters after...")
    for key in randomGenerators.keys():
        print(key+':',randomGenerators[key].lmbda)
