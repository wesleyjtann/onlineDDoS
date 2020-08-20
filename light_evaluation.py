import pickle
# import matplotlib.pyplot as plot
import yaml
import pandas as pd
import pickle
import sys
import numpy as np

# Plot and save fig without displaying it on X server 
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plot



def loadConfig():
    with open(sys.argv[1], "r") as ymlfile:
        cfg = yaml.load(ymlfile)
    return cfg

def filterAndSort(df) :
    df = df.sort_values(by=['timestamp'])
    before = len(df)
    df = df.groupby('remote_addr').filter(lambda x: len(x) > 10)
    after = len(df)
    df = df.reset_index()

    print("Before = {}, After = {}".format(before, after))

    return df

#Create a function that plots the graphs with acceptance rate of 0.1,0.2 ..... 1.0
#Calculate those who got normal how many were rejected wrongly and not inside the AGT List.
import math

def calculateFalsePositives(agtIPList, scoreDict, percentages, numNorm) :
    numNormal = numNorm
    numTotalIP = len(scoreDict)
    cutOff = []
    falsepositives = []
    
    for percent in percentages :
        cutOff.append(math.ceil(numTotalIP * percent))
    
    scoreCount = 0
    index = 0

    for (IP, IPD, score) in list(scoreDict.itertuples(index=False, name=None)):
        if IP + IPD in agtIPList:
            scoreCount = scoreCount + 1
            
        index = index + 1
        if index in cutOff :
            falsepositives.append(scoreCount/numNormal)
            
    return falsepositives
        
def plotAndSaveGraph(PQ, P, PQTil, Qonline, Qoffline, config):
# def plotAndSaveGraph(PQ, P, config):
    percentages = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    plot.rcParams['figure.figsize'] = [9, 9]
    fig = plot.figure()
    ax = plot.subplot(111)
    # #ax.plot(percentages, old_graphScoreList, label = "Old P Over Q Scores")
    # #ax.plot(percentages, old_graphPList, label = "Old P Scores")
    ax.plot(percentages, percentages, label = "Randomized Rejection")
    ax.plot(percentages, P, label = "P Only")
    ax.plot(percentages, PQ, label = "Online P/Q With Transfer")
    ax.plot(percentages, PQTil, label = "Offline P/Q Without Transfer") 
    ax.plot(percentages, Qonline, label = "Online Q")
    ax.plot(percentages, Qoffline, label = "Offline Q") 
    
    plot.xlabel('Rejection Threshold')
    plot.ylabel('False Reject Rates')
    plot.title("False Positive rates for " + config['metadata']['name'])
    ax.legend()
    # plot.savefig(config['metadata']['uniqueID'] + '/' + config['metadata']['result'] + '/' + config['metadata']['name'] + '_FPGraph')
    plot.savefig(config['metadata']['uniqueID'] + '/' + config['metadata']['result'] + '_FPGraph')

def main():
    print("*****     Starting Evaluation     ******")
    config = loadConfig()

    # #Load User Scores
    # userScoreP = pickle.load(open(config['metadata']['uniqueID'] + '/' + config['metadata']['result'] + '/' + 'PScore', 'rb'))
    userScoreP = pickle.load(open(config['metadata']['uniqueID'] + '/' + config['metadata']['artefact'] + '/' + 'PScore', 'rb'))
    userScoreP = userScoreP.sort_values(by = ['P'],ascending=False) # add
    
    # userScorePQ  = pickle.load(open(config['metadata']['uniqueID'] + '/' + config['metadata']['result'] + '/' + 'POverQWithTransferScore', 'rb'))
    userScorePQ = pickle.load(open(config['metadata']['uniqueID'] + '/' + config['metadata']['artefact'] + '/' + 'POverQWithTransferScore', 'rb'))
    userScorePQ = userScorePQ.sort_values(by = ['PoverQWithTransfer'],ascending=False) # add 

    # userScorePQTil = pickle.load(open(config['metadata']['uniqueID'] + '/' + config['metadata']['result'] + '/' + 'POverQWithoutTransferScore', 'rb'))
    userScorePQTil = pickle.load(open(config['metadata']['uniqueID'] + '/' + config['metadata']['artefact'] + '/' + 'POverQWithoutTransferScore', 'rb'))
    userScorePQTil = userScorePQTil.sort_values(by = ['PoverQWithoutTransfer'],ascending=False) 

    userScoreQonline = pickle.load(open(config['metadata']['uniqueID'] + '/' + config['metadata']['artefact'] + '/' + 'onlineQ', 'rb'))
    userScoreQonline = userScoreQonline.sort_values(by = ['QWithT'],ascending=False)

    userScoreQoffline = pickle.load(open(config['metadata']['uniqueID'] + '/' + config['metadata']['artefact'] + '/' + 'offlineQ', 'rb'))
    userScoreQoffline = userScoreQoffline.sort_values(by = ['QWithoutT'],ascending=False)


    trueNormals = []
    
    print("Length of userScoreP: ", len(userScoreP))
        
    for (IP, IPD, score) in list(userScoreP.itertuples(index=False, name=None)):
        if IP != '172.16.0.1' and IP == '192.168.10.50': # equivalent to (if IP == '192.168.10.50')
            trueNormals.append(IP + IPD)

    print("Length of trueNormals: ", len(trueNormals))

    #Plot some graphs
    percentages = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    num = len(trueNormals)

    graphPQ = calculateFalsePositives(trueNormals, userScorePQ, percentages, num)
    graphP = calculateFalsePositives(trueNormals, userScoreP, percentages, num)
    graphPQTil = calculateFalsePositives(trueNormals, userScorePQTil, percentages, num)
    graphQonline = calculateFalsePositives(trueNormals, userScoreQonline, percentages, num)
    graphQoffline = calculateFalsePositives(trueNormals, userScoreQoffline, percentages, num)    
    
    
    # print("graphPQ: ", graphPQ)
    
    graphPQ.insert(0, 0)
    graphP.insert(0, 0)
    graphPQTil.insert(0, 0)
    graphQonline.insert(0, 0)
    graphQoffline.insert(0, 0)
    
    plotAndSaveGraph(graphPQ, graphP, graphPQTil, graphQonline, graphQoffline, config)
    # plotAndSaveGraph(graphPQ, graphP, config)

    print("*****     Ending Evaluation     ******")

if __name__ == "__main__":
    main()