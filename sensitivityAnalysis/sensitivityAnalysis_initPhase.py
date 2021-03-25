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

SIMULATION_TIME = 1
ITERATIONS_PER_UNIT_TIME = 50

samplesPer = 50000

p1Complete = []
p2Complete = []
p3Complete = []

w1Wait = []
w2Wait = []
w3Wait = []
i1Wait = []
i2Wait = []

initTimes = [i for i in range(0,125,5)]
for initTime in initTimes:


    p1 = 0
    p2 = 0
    p3 = 0
    w1 = 0
    w2 = 0
    w3 = 0
    i1 = 0
    i2 = 0
    
    print('initTime',initTime)
    for i in range(samplesPer):
        randomGenerators = {
            'servinsp1': RandomExponentialGenerator('../dataFiles/servinsp1.dat',ITERATIONS_PER_UNIT_TIME),
            'servinsp22': RandomExponentialGenerator('../dataFiles/servinsp22.dat',ITERATIONS_PER_UNIT_TIME),
            'servinsp23': RandomExponentialGenerator('../dataFiles/servinsp23.dat',ITERATIONS_PER_UNIT_TIME),
            'ws1': RandomExponentialGenerator('../dataFiles/ws1.dat',ITERATIONS_PER_UNIT_TIME),
            'ws2': RandomExponentialGenerator('../dataFiles/ws2.dat',ITERATIONS_PER_UNIT_TIME),
            'ws3': RandomExponentialGenerator('../dataFiles/ws3.dat',ITERATIONS_PER_UNIT_TIME)
        }
        res = simulate(randomGenerators,SIMULATION_TIME,ITERATIONS_PER_UNIT_TIME,initTime)
        w1 += res['waitTimes']['workstation1']
        w2 += res['waitTimes']['workstation2']
        w3 += res['waitTimes']['workstation3']
        i1 += res['waitTimes']['inspector1']
        i2 += res['waitTimes']['inspector2']

        p1 += res['completed']['product1']
        p2 += res['completed']['product2']
        p3 += res['completed']['product3']
    p1Complete.append(p1 / samplesPer)
    p2Complete.append(p2 / samplesPer)
    p3Complete.append(p3 / samplesPer)

    w1Wait.append(w1 / samplesPer)
    w2Wait.append(w2 / samplesPer)
    w3Wait.append(w3 / samplesPer)
    i1Wait.append(i1 / samplesPer)
    i2Wait.append(i2 / samplesPer)

for i in range(len(initTimes)-1):
    p1l, = plt.plot( initTimes[i], p1Complete[i], 'r,')
    p2l, = plt.plot( initTimes[i], p2Complete[i], 'g,')
    p3l, = plt.plot( initTimes[i], p3Complete[i], 'b,')
    plt.title( "products completed / varying initilization time / " + str(SIMULATION_TIME) + ' time' )
    plt.xlabel( "initialization time")
    plt.ylabel( "products completed (avg 50000 samples)")
plt.legend([p1l,p2l,p3l], ["Product 1", "Product 2", "Product 3"])
plt.savefig(fname="output/"+'initTime_completed.png')
plt.clf()

for i in range(len(initTimes)-1):
    w1l, = plt.plot( initTimes[i], w1Wait[i], 'r,')
    w2l, = plt.plot( initTimes[i], w2Wait[i], 'g,')
    w3l, = plt.plot( initTimes[i], w3Wait[i], 'b,')
    i1l, = plt.plot( initTimes[i], i1Wait[i], 'k,')
    i2l, = plt.plot( initTimes[i], i2Wait[i], 'm,')
    plt.title( "time waiting / varying initilization time / " + str(SIMULATION_TIME) + ' time' )
    plt.xlabel( "initialization time")
    plt.ylabel( "time waiting (avg 50000 samples)")
plt.legend([w1l,w2l,w3l,i1l,i2l], ["Workstation 1", "Workstation 2", "Workstation 3", "Inspector 1", "Inspector 2"])
plt.savefig(fname="output/"+'initTime_waiting.png')
plt.clf()
