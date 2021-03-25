import random
from random import seed

import numpy as np

MAX_BUFFER_SIZE = 2 # The size of the workstation buffers
SIMULATION_TIME = 100000.0 # The amount of time to simulate
ITERATIONS_PER_UNIT_TIME = 15 #The iterations per unit of time


class RandomExponentialGenerator(object):
    '''
    Generates random numbers using ITT of an exponential distribution
    '''
    def lambdaFromFile(file):
        """Calculates the lambda value for an exponential representation of a data file"""
        data = open(file,'r').read() # the file data
        lines = data.split('\n') #the lines of file data
        floats = [float(l) for l in lines[:-2]] #The floats stored in the data
        
        n = len(floats) #number of floats
        mean = sum(floats) / n #mean
        lmb = 1/mean #lambda
        return lmb

    def __init__(self,initParam):
        """
        initParam -- the value for the variable lambda or a file to calculate lambda using
        """
        #self.lmbda is the value of variable lambda for the exponential function
        if type(initParam) is str:
            self.lmbda = RandomExponentialGenerator.lambdaFromFile(initParam)
        elif type(initParam) is float:
            self.lmbda = initParam
        else:
            raise ValueError("Must pass a lambda or a data file path")
        
    def inverse_cdf(self,uniform_random):
        """
        Calculates the inverse cdf for the exponenetial function
        uniform_random -- value between 0-1 inclusive
        """
        return np.log(1-uniform_random)/-self.lmbda
    
    def generate(self):
        "generates a random time using the inverse CDF"
        uniform_random = random.uniform(0.0,1.0) #A value from 0-1
        return int(self.inverse_cdf(uniform_random) * ITERATIONS_PER_UNIT_TIME)


class RandomDataGenerator(object):
    '''
    Generates random numbers by returning a random value from a data file
    '''
    def __init__(self, dataFile):
        """
        dataFile -- the file to get data values from
        """
        data = open(file,'r').read() # the file data
        lines = data.split('\n') #the lines of file data
        self.floats = [float(l) for l in lines[:-2]] #a list of all values in the data file

    def generate(self):
        """picks a random time directly from the given data file"""
        index = random.randint(0,len(self.tempFloats)-1) #The randomly chosen data index to return
        return int(self.floats[index] * ITERATIONS_PER_UNIT_TIME)

class Workstation(object):
    def __init__(self, name, components, randomGenerator):
        """
        name -- name of workstation for debugging
        components -- list of components that the workstation must have a buffer to hold
        randomGenerator -- An object for generating random numbers (must have a method "generate")
        """
        self.name = name #name for debugging
        
        self.completed = 0 #amount of products fully completed
        self.iterationsLeftOnWork = 0 #the amount of iterations before another product is completed
        self.iterationsWaiting = 0 #The amount of iterations spent waiting to have all the components needed to start working
        
        self.randomGenerator = randomGenerator #The object for generating random times

        self.buffers = {} #Stores how full each buffer

        for component in components:
            self.buffers[component] = 0
            
    def generateRandomWorkTime(self):
        """set a new random work time"""
        assert self.iterationsLeftOnWork == 0
        self.iterationsLeftOnWork = self.randomGenerator.generate()

    def addToBuffer(self, componentName):
        """
        increase the value representing the items in a component buffer
        componentName -- the component name to know which buffer to increase
        """
        assert (self.buffers[componentName] < MAX_BUFFER_SIZE)
        self.buffers[componentName] += 1
        
    def getBuffer(self, componentName):
        """
        Return how full a buffer is
        componentName -- the name of the component
        """
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
        If done working on a component and can take from all buffers, take from all buffers and start working again
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
    def __init__(self, name, components, workstations):
        """
        name -- name of inspector for debugging
        components -- iterable of Component objects
        workstations -- all the workstations

        The inspector takes a component on initialization!
        """
        self.name = name # name for debugging
        self.components = components #list of component objects that can be picked to work on from infite queue
        
        self.iterationsLeftOnWork = 0 #iterations left before done and should try putting component in a buffer
        self.iterationsWaiting = 0 #iterations left waiting for a buffer spot to open

        self.workstations = workstations #all the workstations
        
        self.getNextComponent()
        
    def generateRandomWorkTime(self):
        """set a new random work time"""
        assert self.iterationsLeftOnWork == 0
        self.iterationsLeftOnWork = self.currentComponent.generateRandomWorkTime()
        
    def getNextComponent(self):
        """start working on a new component"""
        assert self.iterationsLeftOnWork == 0
        
        index = random.randint(0,len(self.components)-1) # The index of the randomly chosen component to work on next
        self.currentComponent = self.components[index]
            
        self.generateRandomWorkTime()

    def placeComponentInBuffer(self):
        """return whether currentComponent was placed in some workstation's buffer. Prioratizes least full buffer then lowest index buffer in global workstations list"""
        chosen = None #Stores the chosen buffer
        chosenSize = MAX_BUFFER_SIZE #Stores amount of items stored in the chosen buffer (want to get this as low as possible)
        
        for workstation in self.workstations:
            if self.currentComponent.name in list(workstation.buffers.keys()): #workstation has a corresponding buffer
                workstationBufferSize = workstation.getBuffer(self.currentComponent.name) # amount of items stored in current chosen buffer
                
                if workstationBufferSize < chosenSize: #check if current is new least full buffer
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
        name -- name of the component for debugging and workstation buffer keys
        randomGenerator -- An object for making random numbers (must have a method "generate")
        '''
        self.name = name # name of component
        self.randomGenerator = randomGenerator #object to generate random numbers for workers with

    def generateRandomWorkTime(self):
        """return a new random time (To be called by workers since the work time depends on component type, not worker)"""
        return self.randomGenerator.generate()


if __name__ == "__main__":

    #Use a seed to get reproducable results
    #seed(1)

    #The random generator type to use
    #randomGenerator = RandomDataGenerator
    randomGenerator = RandomExponentialGenerator

    #the randomGenerators instances that will be used (stored for printing after running for verification purposes)
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

    #The component instances
    components = {
        'C1': Component('C1', randomGenerators['servinsp1']),
        'C2': Component('C2', randomGenerators['servinsp22']),
        'C3': Component('C3', randomGenerators['servinsp23']),
        }

    #The workstation instances
    workstations = [
        Workstation('workstation 1', ('C1',), randomGenerators['ws1']),
        Workstation('workstation 2', ('C1','C2'), randomGenerators['ws2']),
        Workstation('workstation 3', ('C1','C3'), randomGenerators['ws3']),
        ]

    #The inspector instances
    inspectors = [
        Inspector('inspector 1', (components['C1'],), workstations),
        Inspector('inspector 1', (components['C2'],components['C3']), workstations ),
        ]

    
    iterables = inspectors + workstations #All objects that need to have performIteration called once an iteration

    tenPercentTest = int(SIMULATION_TIME * ITERATIONS_PER_UNIT_TIME / 10) #If remainder iteration count divided by this is 0 then print percent complete info
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
