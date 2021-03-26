SIMULATION_TIME = 1
SAMPLES_PER_POINT = 10000
MAX_TO_TEST = 300
TEST_POINTS = 20


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

p1Complete = []
p2Complete = []
p3Complete = []

w1Wait = []
w2Wait = []
w3Wait = []
i1Wait = []
i2Wait = []

initTimes = [MAX_TO_TEST * i / TEST_POINTS for i in range(TEST_POINTS)]
for initTime in initTimes:


    p1 = 0
    p2 = 0
    p3 = 0
    w1 = 0
    w2 = 0
    w3 = 0
    i1 = 0
    i2 = 0
    
    print('initTime',initTime,'/',initTimes[-1])
    for i in range(SAMPLES_PER_POINT):
        randomGenerators = {
            'servinsp1': RandomExponentialGenerator('../dataFiles/servinsp1.dat'),
            'servinsp22': RandomExponentialGenerator('../dataFiles/servinsp22.dat'),
            'servinsp23': RandomExponentialGenerator('../dataFiles/servinsp23.dat'),
            'ws1': RandomExponentialGenerator('../dataFiles/ws1.dat'),
            'ws2': RandomExponentialGenerator('../dataFiles/ws2.dat'),
            'ws3': RandomExponentialGenerator('../dataFiles/ws3.dat')
        }
        res = simulate(randomGenerators,SIMULATION_TIME,initTime)
        w1 += res['waitTimes']['workstation1']
        w2 += res['waitTimes']['workstation2']
        w3 += res['waitTimes']['workstation3']
        i1 += res['waitTimes']['inspector1']
        i2 += res['waitTimes']['inspector2']

        p1 += res['completed']['product1']
        p2 += res['completed']['product2']
        p3 += res['completed']['product3']
    p1Complete.append(p1 / SAMPLES_PER_POINT)
    p2Complete.append(p2 / SAMPLES_PER_POINT)
    p3Complete.append(p3 / SAMPLES_PER_POINT)

    w1Wait.append(w1 / SAMPLES_PER_POINT)
    w2Wait.append(w2 / SAMPLES_PER_POINT)
    w3Wait.append(w3 / SAMPLES_PER_POINT)
    i1Wait.append(i1 / SAMPLES_PER_POINT)
    i2Wait.append(i2 / SAMPLES_PER_POINT)

for i in range(len(initTimes)):
    p1l, = plt.plot( initTimes[i], p1Complete[i], 'r,')
    p2l, = plt.plot( initTimes[i], p2Complete[i], 'g,')
    p3l, = plt.plot( initTimes[i], p3Complete[i], 'b,')
    plt.title( "products completed / varying initilization time / " + str(SIMULATION_TIME) + ' time units' )
    plt.xlabel( "initialization time")
    plt.ylabel( "products completed (avg " + str(SAMPLES_PER_POINT) + " samples)")
plt.legend([p1l,p2l,p3l], ["Product 1", "Product 2", "Product 3"])
plt.savefig(fname="output/"+'initTime_completed_noiter.png')
plt.clf()

for i in range(len(initTimes)):
    w1l, = plt.plot( initTimes[i], w1Wait[i], 'r,')
    w2l, = plt.plot( initTimes[i], w2Wait[i], 'g,')
    w3l, = plt.plot( initTimes[i], w3Wait[i], 'b,')
    i1l, = plt.plot( initTimes[i], i1Wait[i], 'k,')
    i2l, = plt.plot( initTimes[i], i2Wait[i], 'm,')
    plt.title( "time waiting / varying initilization time / " + str(SIMULATION_TIME) + ' time units' )
    plt.xlabel( "initialization time")
    plt.ylabel( "time waiting (avg " + str(SAMPLES_PER_POINT) + " samples)")
plt.legend([w1l,w2l,w3l,i1l,i2l], ["Workstation 1", "Workstation 2", "Workstation 3", "Inspector 1", "Inspector 2"])
plt.savefig(fname="output/"+'initTime_waiting_noiter.png')
plt.clf()
