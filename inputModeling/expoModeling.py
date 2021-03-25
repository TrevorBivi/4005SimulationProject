"""
This file is just to help generate data for the second milestone
"""

import matplotlib
import matplotlib.pyplot

import matplotlib.pyplot as plt
import math as m
import numpy as np
import scipy.stats as scistats

import os
if not os.path.exists('output'):
    os.makedirs('output')

floats = None


def pdf (lmb,x):
    if x <= 0:
        return 0
    return lmb * m.e ** (- lmb * x)

def cdf (lmb, x):
    if x <= 0:
        return 0
    return 1- m.e ** ( -lmb * x)

def icdf (lmb, x):
    #x = 1- m.e ** ( -lmb * y)
    #m.e ** ( -lmb * y) = 1-x
    #( -lmb * y) = log(1-x,m.e)
    #y = log(1-x,m.e) / -lmb
    
    return np.log(1-x) /-lmb

hist_bins = 12

for dataFile in ("ws1.dat","ws2.dat","ws3.dat","servinsp1.dat","servinsp22.dat","servinsp23.dat"):


    #get data
    data = open("../dataFiles/" + dataFile,'r').read()
    lines = data.split('\n')
    floats = [float(l) for l in lines[:-2]]

    xi = floats
    yi = xi.copy()
    yi.sort()
    
    n = len(floats)
    mean = sum(floats) / n
    lmb = 1/mean


    #ugly chi testing
    oi,classes = np.histogram(floats,bins=hist_bins)
    
    last_class = 0
    pi = []
    Ei = []
    xs = []
    print("\n=====", dataFile ,"===== lmbda:",lmb)
    print('rng \t\t','oi[i]','\t','p','\t','E','\t','x0')
    loop_classes = list(classes)
    loop_classes[0] = 0.0
    loop_classes[-1] = (999999999)
    for i in range(hist_bins):
        p = cdf(lmb,loop_classes[i+1]) - cdf(lmb,loop_classes[i])
        
        E = n*p
        Ei.append(E)
        pi.append(p)
        x0 = (oi[i]-E)**2 / E
        xs.append( x0 )

        if i == 0:
            lcf = '< ' + str(loop_classes[i+1])[:5]
        elif i == hist_bins - 1:
            lcf = '> ' + str(loop_classes[i])[:5]
        else:
            lcf = str(loop_classes[i])[:5] + '-'+ str(loop_classes[i+1])[:5]
       
        
        str_oi = str(oi[i])[:5]
        str_E = str(E)[:5]
        str_p = str(p)[:5]
        str_x0 = str(x0)[:5]
        
        print(lcf,'\t',str_oi,'\t',str_p,'\t',str_E,'\t',str_x0)        
    print('\t\t\t\t',sum(xs))

        
    #generate a histogram
    plt.clf()
    plt.title(dataFile)
    plt.xlabel("Time for completion")
    plt.ylabel("Frequency count")
    plt.hist(floats, bins=hist_bins)
    
    plt.savefig(fname="output/"+dataFile+'_hist.png')

    #function for qq stuff
    def fqq(t):
        return icdf(lmb, (t-0.5)/n )

    
    #generate yi (sorted samples) and qq func
    if False: #not really needed
        plt.clf()
        t1 = np.arange(0.0,n+1,1)
        plt.plot(fqq(t1))
        for t in range(n):
            plt.plot(t,yi[t], ',')
        plt.savefig(fname="output/"+dataFile+'_yj_and_fqq.png')

    
    #generate a qq
    plt.clf()
    plt.title(dataFile)
    plt.xlabel("yj")
    plt.ylabel("F-1((j-1/2)/n)")
    def f(t):
        return t
    t1 = np.arange(0.0,yi[-1],1)
    plt.plot(t1,f(t1))
    for t in range(n):
        plt.plot(yi[t], fqq(t) , '.r')
    
    plt.savefig(fname="output/"+dataFile+'_qq.png')

