import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
# N = 50, pm = 0.01, pc = 0.3, and tournament size at 2
# N,P_c,P_m,Tournament Size,Iteration,Generation,Average Fitness,Best Fitness,Best Genome,Solution Found (0 or 1),Solution Count,Diversity Metric

df = pd.read_csv('masterCSV.csv')

pop = df.columns[0]
PC = df.columns[1]
PM = df.columns[2]
TOR = df.columns[3]
it = df.columns[4]
gen = df.columns[5]
div = df.columns[11]
af = df.columns[6]
bf = df.columns[7]
totSol = df.columns[10]

df = df.astype({pop: int, PC: float, PM : float, TOR : int, it: int, gen: int,\
                         af: float, bf: float, totSol: int, div: float})

subdf = [df.loc[ (df[PM] == 0.01) & (df[PC] == 0.3) & (df[TOR] == 2)]] #population
subdf.append(df.loc[ (df[pop] == 50 ) & (df[PC] == 0.3) & (df[TOR] == 2)]) #p_m
subdf.append(df.loc[ (df[PM] == 0.01) & (df[pop] == 50) & (df[TOR] == 2)]) #P_c
subdf.append(df.loc[ (df[PM] == 0.01) & (df[PC] == 0.3) & (df[pop] == 50)]) #Tor size

currentLine = 0

linesXAxis = [[i for i in range(0, 30)]] * 30
linesYAxis = []

currentLine = 0
colorOption = -1
colors = ['b', 'r', 'g', 'orange']
                    #pop                  #PM                    #PC                 #TOR
indepVarsList = [[25, 50, 75, 100], [0.00, 0.01, 0.03, 0.05], [0.0, 0.1, 0.3, 0.5] ,[2, 3, 4, 5]]
legendTitle = [pop, PM, PC, TOR]
figures = [0] * 12
figuresSaveTitle = [" "] * 12
currFigure = 0

column = [pop, PM, PC, TOR]

for bestAvgDiv in [af, bf, div]:

    #go through each of the lists in indepVarsList
    for currSubDFIndex, indepVars in enumerate(indepVarsList):
        figuresSaveTitle[currFigure] = "".join([word[0] for word in bestAvgDiv.split()]) + "-" + legendTitle[currSubDFIndex].replace(" ", "-") + ".png"
        figures[currFigure] = plt.figure()
        currFigure += 1
        colorOption = -1

        #make the mean line, and shading for each of the variables in current indepVars list
        for ind, var in enumerate(indepVars):
            colorOption += 1
            linesYAxis = []
            subSubDF = subdf[currSubDFIndex].loc[ (subdf[ currSubDFIndex ][column[currSubDFIndex]] == var) ]
            
            #Go through each iteration line
            currentLine = 0
            for iterationLine in range(0, 20):              #each line has 30 generations
                linesYAxis.append(subSubDF[bestAvgDiv].iloc[currentLine:currentLine + 30].tolist())
                currentLine += 30

            #Get mean line and standard deviation lines for fill_between
            meanLine = np.mean( linesYAxis, axis = 0)
            lowstd = meanLine - np.std(linesYAxis, axis = 0)
            highstd = meanLine + np.std(linesYAxis, axis = 0)
            
            if bestAvgDiv != div:
                highstd = np.clip(highstd, a_min=None, a_max=1)
                
            #shade in between std deviation lines, and plot mean line
            plt.fill_between(linesXAxis[0], lowstd, highstd, color=colors[colorOption], alpha=.2)
            plt.plot(linesXAxis[0], meanLine, color=colors[colorOption], label= str(var))
        

        if bestAvgDiv != div:
            plt.legend(loc="lower right", title=legendTitle[currSubDFIndex])
        elif currFigure == 10:
            plt.legend(loc="lower left", title=legendTitle[currSubDFIndex])
        else:
            plt.legend(loc="upper right", title=legendTitle[currSubDFIndex])
        #plt.legend(loc="lower right", title=legendTitle[currSubDFIndex])
        plt.xlabel("Generation")
        plt.ylabel(bestAvgDiv)
        plt.title('Effect of ' + legendTitle[currSubDFIndex] + " on " + bestAvgDiv)


for i in range(0, 12):
    figures[i].savefig("graphs/" + figuresSaveTitle[i])

plt.show()
