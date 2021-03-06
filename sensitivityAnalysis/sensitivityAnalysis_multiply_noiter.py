SIMULATION_TIME = 10000
TEST_POINTS = 100
MAX_MULTIPLIERS = {
    'servinsp1':40.0,
    'servinsp22':1.5,
    'servinsp23':1.5,
    'ws1':10.0,
    'ws2':1.5,
    'ws3':1.5,
    'all':10.0
    }

import sys
sys.path.append("..")

from simulator import *
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
    
    iVals = [ MAX_MULTIPLIERS[multiplyKey] * i / TEST_POINTS for i in range(1,TEST_POINTS) ]
    
    for i in iVals:
        print('multiply', multiplyKey, 'by', i, '/', iVals[-1])
        randomGenerators={
        }
        for key in defaultLambdas.keys():
            if multiplyKey == 'all' or key == multiplyKey:
                randomGenerators[key] = RandomExponentialGenerator(defaultLambdas[key] * i)
            else:
                randomGenerators[key] = RandomExponentialGenerator(defaultLambdas[key])

        results = simulate(randomGenerators, simTime=SIMULATION_TIME, initPhaseTime=0, printInfo=False)
                
        p1Complete.append( results['completed']['product1'] )
        p2Complete.append( results['completed']['product2'] )
        p3Complete.append( results['completed']['product3'] )

        w1Wait.append( results['waitTimes']['workstation1'] )
        w2Wait.append( results['waitTimes']['workstation2'] )
        w3Wait.append( results['waitTimes']['workstation3'] )
        i1Wait.append( results['waitTimes']['inspector1'] )
        i2Wait.append( results['waitTimes']['inspector2'] )
        
    for i in range(len(iVals)-1):
        p1l, = plt.plot( iVals[i], p1Complete[i], 'r,')
        
        if i % 2 == 0: #change which of p2 p3 will overlap the other every other sample
            p2l, = plt.plot( iVals[i], p2Complete[i], 'g,')
            p3l, = plt.plot( iVals[i], p3Complete[i], 'b,')
        else:
            p3l, = plt.plot( iVals[i], p3Complete[i], 'b,')
            p2l, = plt.plot( iVals[i], p2Complete[i], 'g,')
        
        plt.title( "products completed / scaling " + multiplyKey + " ?? / " + str(SIMULATION_TIME) + ' time units' )
        plt.xlabel( "lambda multiplier")
        plt.ylabel( "products completed")
    plt.legend([p1l,p2l,p3l], ["Product 1", "Product 2", "Product 3"])
    plt.savefig(fname="output/"+multiplyKey+'_completed_noiter.png')
    plt.clf()

    for i in range(len(iVals)-1):
        w1l, = plt.plot( iVals[i], w1Wait[i], 'r,')
        w2l, = plt.plot( iVals[i], w2Wait[i], 'g,')
        w3l, = plt.plot( iVals[i], w3Wait[i], 'b,')
        i1l, = plt.plot( iVals[i], i1Wait[i], 'k,')
        i2l, = plt.plot( iVals[i], i2Wait[i], 'm,')

        plt.title( "time waiting / scaling " + multiplyKey + " ?? / " + str(SIMULATION_TIME) + ' time units' )
        plt.xlabel( "lambda multiplier")
        plt.ylabel( "time waiting")
    plt.legend([w1l,w2l,w3l,i1l,i2l], ["Workstation 1", "Workstation 2", "Workstation 3", "Inspector 1", "Inspector 2"])
    plt.savefig(fname="output/"+multiplyKey+'_waiting_noiter.png')
    plt.clf()
