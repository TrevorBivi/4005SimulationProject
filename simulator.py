import random
import math
from random import seed
import numpy as np

DEBUGPRINT = False
MAX_BUFFER_SIZE = 2

FLOAT_ERR = 0.00000000001

def printHandler(*args):
    if DEBUGPRINT:
        print(*args)

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
        return self.inverse_cdf(uniform_random)


class RandomDataGenerator(object):
    '''
    Generates random numbers by returning a random value from a data file
    '''
    def __init__(self, dataFile):
        """
        dataFile -- the file to get data values from
        """
        data = open(dataFile,'r').read() # the file data
        lines = data.split('\n') #the lines of file data
        self.floats = [float(l) for l in lines[:-2]] #a list of all values in the data file

    def generate(self):
        """picks a random time directly from the given data file"""
        index = random.randint(0,len(self.floats)-1) #The randomly chosen data index to return
        return self.floats[index]

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
        self.workstations = workstations #all the workstations

        self.workTime = 0 #The time for the inspectors current busy work
        self.timeWaiting = 0 # the time spent waiting over the simulation
        self.blocked = False # whether the inspector is currently blocked
        self.currentComponent = None # The component currently in the inspectors focus
        self.workOnNextComponent()

    def workOnNextComponent(self):
        """start working on a new component"""
        assert self.workTime == 0
        index = random.randint(0,len(self.components)-1)
        self.currentComponent = self.components[index]
        self.workTime = self.currentComponent.generateRandomWorkTime() 
        printHandler("I",self.name,"new worktime -",self.workTime)
      
    def placeComponentInBuffer(self):
        """return whether currentComponent was placed in some workstation's buffer. Prioratizes least full buffer then lowest index buffer in global workstations list"""
        assert self.workTime == 0
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
        return chosen

    def advanceTime(self, amount):
        """
        advances the inspector
        amount -- amount of time to advance (if inspector is busy this should never be larger than time to unbusy)
        """
        if self.blocked:
            assert self.workTime == 0
            self.timeWaiting += amount
        else:
            assert self.workTime - amount >= -FLOAT_ERR
            self.workTime = max(self.workTime - amount, 0)
            if self.workTime == 0:
                printHandler("I", self.name, "finishes a - ", self.currentComponent.name)
            
        if self.workTime == 0:
            oldComponent = self.currentComponent
            workstationUsed = self.placeComponentInBuffer()
            if workstationUsed:
                printHandler("I", self.name, "places a", oldComponent.name, 'in', workstationUsed.name)
                self.blocked = False
                self.workOnNextComponent()
            else:
                self.blocked = True

class Workstation(object):
    def __init__(self, name, components, randomGenerator):
        """
        name -- name of workstation for debugging
        components -- list of components that the workstation must have a buffer to hold
        randomGenerator -- An object for generating random numbers (must have a method "generate")
        """
        self.name = name #name for debugging
        
        self.randomGenerator = randomGenerator #The object for generating random times

        self.buffers = {} #Stores how full each buffer

        for component in components:
            self.buffers[component] = 0

        self.workTime = 0 # The time for busy work to finish
        self.timeWaiting = 0 #The amount of iterations spent waiting to have all the components needed to start working
        self.blocked = True #Whether the workstaion is currently waiting to start work

        self.timeSinceLastCompletion = None #time since last component was completed
        self.completionTimes = [] #stores completion times
            
    def generateRandomWorkTime(self):
        """set a new random work time"""
        assert self.workTime == 0
        self.workTime = self.randomGenerator.generate()
        printHandler("W",self.name,"worktime",self.workTime)

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
        assert self.workTime == 0
        return not 0 in self.buffers.values()

    def takeFromBuffers(self):
        """decrements all buffers"""
        assert self.workTime == 0
        for k in self.buffers.keys():
            #assert self.buffers[k] > 0
            self.buffers[k] -= 1
    
    def advanceTime(self, amount):
        """
        advances workstation in time
        amount -- amount of time (if workstation is busy this should never be larger than workTime)
        """
        if self.timeSinceLastCompletion != None:
            self.timeSinceLastCompletion += amount
        
        if self.blocked:
            assert self.workTime == 0
            self.timeWaiting += amount
        else:
            assert self.workTime - amount >= - FLOAT_ERR
            self.workTime = max(self.workTime - amount, 0)
            if self.workTime == 0:
                printHandler("W",self.name,"completes a product canTakeFromBuffers:",self.canTakeFromBuffers())
                if self.timeSinceLastCompletion != None:
                    self.completionTimes.append(self.timeSinceLastCompletion)
                self.timeSinceLastCompletion = 0

        if self.workTime == 0:
            if self.canTakeFromBuffers():
                printHandler("W",self.name,"takes from buffers")
                self.blocked = False
                self.takeFromBuffers()
                self.generateRandomWorkTime()
            else:
                self.blocked = True

def simulate(randomGenerators, simTime, initPhaseTime=0, printInfo=False):
    """
    return wait times and products complete
    randomGenerators -- dictionary of random generators to represent each data file
    simTime -- the time to simulate
    initPhaseTime -- the unit time to run before starting simulation monitoring
    printInfo -- print info about simulation
    """
    if printInfo:
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
        Inspector('inspector 2', (components['C2'],components['C3']), workstations ),
        ]

    iterables =  inspectors + workstations

    def passTime(amountTime):
        timePassed = 0
        while timePassed < amountTime:
            #Calculate time to next interesting thing
            timeToPass = float('inf')
            for iterable in iterables:
                if not iterable.blocked and iterable.workTime < timeToPass:
                    timeToPass = iterable.workTime
                
                if timePassed + timeToPass >= amountTime:
                    timeToPass = amountTime - timePassed
            printHandler("\nT",timeToPass)

            timePassed += timeToPass

            #Advance time until next interesting thing
            for iterable in iterables:#make inspectors check for opening
                iterable.advanceTime(timeToPass)
                
            for inspector in inspectors:#make inspectors check for opening
                inspector.advanceTime(0)
            

    if initPhaseTime:
        passTime(initPhaseTime)
        for iterable in iterables:
            iterable.timeWaiting = 0
        for workstation in workstations:
            workstation.completionTimes = []
            workstation.timeSinceLastCompletion = None
        printHandler("## BEGIN ACTUAL SIMULATION")

    passTime(simTime)



    def completionInfo(workstation):
        amnt = len(workstation.completionTimes)
        if amnt != 0:
            avg = sum(workstation.completionTimes) / amnt
            if amnt != 1:
                var = math.sqrt(sum([ (y - avg) ** 2 for y in workstation.completionTimes ]) / (amnt - 1))
            else:
                var = 0
        else:
            avg = 0
            var = None
        return {'amount':amnt, 'average':avg, 'variance':var}
    
    returnInfo =  {

            
            'waitTimes':{
                'inspector1':inspectors[0].timeWaiting,
                'inspector2':inspectors[1].timeWaiting,
                'workstation1':workstations[0].timeWaiting,
                'workstation2':workstations[1].timeWaiting,
                'workstation3':workstations[2].timeWaiting,
                },

            #redundant info so sensitivity analysis stuff doesn't need to change
            'completed':{
                'product1':len(workstations[0].completionTimes),
                'product2':len(workstations[1].completionTimes),
                'product3':len(workstations[2].completionTimes),
                },

            'completionInfo':{
                'product1':completionInfo(workstations[0]),
                'product2':completionInfo(workstations[1]),
                'product3':completionInfo(workstations[2]),
                }
            
        }

    if printInfo:
        print("\nSimulated", simTime, "time...")

        for p in ('product1','product2','product3'):
            print("workstation 1 - amnt:",returnInfo['completionInfo'][p]['amount'],
                  'avg:',returnInfo['completionInfo'][p]['average'],
                  'var',returnInfo['completionInfo'][p]['variance'])
                
        for iterable in iterables:
            print(iterable.name, "time waiting:", iterable.timeWaiting, ' time units)')


        
        print("\nInput parameters after...")
        for key in randomGenerators.keys():
            print(key+':',randomGenerators[key].lmbda)

    return returnInfo

if __name__ == "__main__":

    #Use a seed to get reproducable results
    #seed(1)

    SIMULATION_TIME = 100000.0 # The amount of time to simulate
    INIT_PHASE_TIME = 1500 # The time to run the simulation before starting to calculate output

    #the randomGenerators instances that will be used for input
    randomGenerators = {
            'servinsp1': RandomExponentialGenerator('dataFiles/servinsp1.dat'),
            'servinsp22': RandomExponentialGenerator('dataFiles/servinsp22.dat'),
            'servinsp23': RandomExponentialGenerator('dataFiles/servinsp23.dat'),
            'ws1': RandomExponentialGenerator('dataFiles/ws1.dat'),
            'ws2': RandomExponentialGenerator('dataFiles/ws2.dat'),
            'ws3': RandomExponentialGenerator('dataFiles/ws3.dat')
        }
    for k in randomGenerators.keys():
        print(k,randomGenerators[k].lmbda)
    for i in range(25):
        ret = simulate(randomGenerators, SIMULATION_TIME, INIT_PHASE_TIME, False)
        print( ret['waitTimes']['inspector1']/100000, '\t',
                ret['waitTimes']['inspector2']/100000, '\t',
               ret['completed']['product1']/100000, '\t',
               ret['completed']['product2']/100000, '\t',
               ret['completed']['product3']/100000 )
        
