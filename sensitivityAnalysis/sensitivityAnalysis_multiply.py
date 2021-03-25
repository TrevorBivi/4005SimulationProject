import sys
sys.path.append("..")

from main import *
import random
from random import seed

import matplotlib
import matplotlib.pyplot

import matplotlib.pyplot as plt


import os
if not os.path.exists('output'):
    os.makedirs('output')

seed(1)


defaultLambdas = {
    'servinsp1':RandomExponentialGenerator.lambdaFromFile('../dataFiles/servinsp1.dat'),
    'servinsp22':RandomExponentialGenerator.lambdaFromFile('../dataFiles/servinsp22.dat'),
    'servinsp23':RandomExponentialGenerator.lambdaFromFile('../dataFiles/servinsp23.dat'),
    'ws1':RandomExponentialGenerator.lambdaFromFile('../dataFiles/ws1.dat'),
    'ws2':RandomExponentialGenerator.lambdaFromFile('../dataFiles/ws2.dat'),
    'ws3':RandomExponentialGenerator.lambdaFromFile('../dataFiles/ws3.dat'),
    
    }

for multiplyKey in ('servinsp1','servinsp22','servinsp23','ws1','ws2','ws3','all'):
    p1Complete = []
    p2Complete = []
    p3Complete = []

    w1Wait = []
    w2Wait = []
    w3Wait = []
    i1Wait = []
    i2Wait = []

    iVals = None
    if multiplyKey in ('ws2', 'ws3','servinsp22','servinsp23'):
        iVals = [ i / 133 for i in range(1,200,4) ]
    else:
        iVals = [ i / 10 for i in range(1,100,2) ]
    
    for i in iVals:
        print('multiply', multiplyKey, 'by', i)
        randomGenerators={
        }
        for key in defaultLambdas.keys():
            if multiplyKey == 'all' or key == multiplyKey:
                randomGenerators[key] = RandomExponentialGenerator(defaultLambdas[key] * i)
            else:
                randomGenerators[key] = RandomExponentialGenerator(defaultLambdas[key])
        
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
            Inspector('inspector 1', (components['C2'],components['C3']), workstations),
            ]

        
        iterables = inspectors + workstations #All objects that need to have performIteration called once an iteration
        for loop in range(int(SIMULATION_TIME * ITERATIONS_PER_UNIT_TIME)):
            for iterable in iterables:
                iterable.performIteration()
                
        p1Complete.append( workstations[0].completed )
        p2Complete.append( workstations[1].completed )
        p3Complete.append( workstations[2].completed )

        w1Wait.append(workstations[0].iterationsWaiting )
        w2Wait.append(workstations[1].iterationsWaiting )
        w3Wait.append(workstations[2].iterationsWaiting )
        i1Wait.append(inspectors[0].iterationsWaiting )
        i2Wait.append(inspectors[1].iterationsWaiting )

    for i in range(len(iVals)-1):
        p1l, = plt.plot( iVals[i], p1Complete[i], 'r,')
        p2l, = plt.plot( iVals[i], p2Complete[i], 'g,')
        p3l, = plt.plot( iVals[i], p3Complete[i], 'b,')
        plt.title( "products completed / scaling " + multiplyKey + " λ / " + str(SIMULATION_TIME) + ' time' )
        plt.xlabel( "lambda multiplier")
        plt.ylabel( "products completed")
    plt.legend([p1l,p2l,p3l], ["Product 1", "Product 2", "Product 3"])
    plt.savefig(fname="output/"+multiplyKey+'_completed.png')
    plt.clf()

    for i in range(len(iVals)-1):
        w1l, = plt.plot( iVals[i], w1Wait[i] / ITERATIONS_PER_UNIT_TIME, 'r,')
        w2l, = plt.plot( iVals[i], w2Wait[i] / ITERATIONS_PER_UNIT_TIME, 'g,')
        w3l, = plt.plot( iVals[i], w3Wait[i] / ITERATIONS_PER_UNIT_TIME, 'b,')
        i1l, = plt.plot( iVals[i], i1Wait[i] / ITERATIONS_PER_UNIT_TIME, 'k,')
        i2l, = plt.plot( iVals[i], i2Wait[i] / ITERATIONS_PER_UNIT_TIME, 'm,')

        plt.title( "time waiting / scaling " + multiplyKey + " λ / " + str(SIMULATION_TIME) + ' time' )
        plt.xlabel( "lambda multiplier")
        plt.ylabel( "time waiting")
    plt.legend([w1l,w2l,w3l,i1l,i2l], ["Workstation 1", "Workstation 2", "Workstation 3", "Inspector 1", "Inspector 2"])
    plt.savefig(fname="output/"+multiplyKey+'_waiting.png')
    plt.clf()
