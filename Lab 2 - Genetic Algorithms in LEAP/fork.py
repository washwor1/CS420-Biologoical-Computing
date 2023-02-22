import os
import sys
import pandas as pd
import threading
import math
import numpy as np
import multiprocessing


files = [] #stores all the file names as they are created
maxP = 32 #Number of active child proccesses at any one time

def proccessStep(subdf, index, result_list, pop, p_m, p_c, tor_size, generation, iteration):
    
    averageFitness = subdf['fitness'].mean()
    maxFitness = subdf['fitness'].max()
    bestGenome = subdf.loc[ (subdf['fitness'] == maxFitness), 'genome' ].iat[0]
    solutionCount = subdf.loc[(subdf['genome'].apply(lambda y: all(elem == 1 for elem in y))), :].shape[0] 
    solutionFound = 1 if solutionCount > 0 else 0

    genomes = list( subdf['genome'] )

    genomeDist = [[np.nan] * int(pop) for i in range(int(pop))]
    distAverage = [0.0] * int(pop)

    for currentG in range(0, int(pop)):
        for nextG in range(currentG + 1, int(pop)):
            genomeDist[currentG][nextG] = genomeDist[nextG][currentG] = math.dist(genomes[currentG], genomes[nextG])
        distAverage[currentG] = np.nanmean(genomeDist[currentG])

    finalAverage = np.average(distAverage)

    genomeString = str(bestGenome)
    genomeString = genomeString.strip(',')

    finalString = str(pop) + "," + str(p_c) + "," + str(p_m) + "," + str(tor_size) + "," + str(iteration) + "," + str(generation) + "," + str(averageFitness) \
                    + "," + str(maxFitness) + ",\"" + genomeString + "\"," + str(solutionFound) + "," + str(solutionCount) + "," + str(finalAverage) + '\n'
    result_list[index] = finalString

    return

def proccessFile(fileNumber):
    print("Proccessing: ", files[fileNumber])
    df = pd.read_csv(files[fileNumber], delimiter=",")
    txtFile = files[fileNumber].replace(".csv", ".txt")

    population, p_c, p_m, tor_size, iteration = txtFile[4:-4].split('_')
    
    df = df.astype({"step": int, "fitness": float})
    df['genome'] = df['genome'].apply(lambda x: [int(b) for b in x.strip('[]').split()])
     
    subsets = [subset for _, subset in df.groupby('step')]
    results = [""] * 30
    threads = []
    
    for i, subset in enumerate(subsets):
        t = threading.Thread(target=proccessStep, args=(subset, i, results, population, p_m, p_c, tor_size, i, iteration))
        threads.append(t)

    # Start the threads
    for t in threads:
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()

    with open(txtFile, "w") as f:
        f.writelines(results)

    return

def lab2exec(pop, pc, pm, tor, csv):
    os.execvp('python3', ['python3', 'lab2.py', '--n', str(pop), \
                                                '--p_c', str(pc), \
                                                '--p_m',  str(pm), \
                                                '--trn_size', str(tor), \
                                                '--csv_output', str(csv)])

def runLab2Program():

    pCount = 0
    popParam = ["25", "50", "75", "100"]
    pcParam = [ "0.00", "0.01", "0.03", "0.05"]
    pmParam = [ "0.00", "0.01", "0.03", "0.05"]
    torParam = ["2", "3", "4", "5"]
    
    for pop in popParam:
        for pc in pcParam:
            for pm in pmParam:
                for tor in torParam:
                    for iteration in range(0, 20):
                               
                        csv = "CSV/" + str(pop) + "_" + str(pc) + "_" + str(pm) + "_" + str(tor) + "_" + str(iteration) + ".csv"
                        #print("Creating: ", csv)                    
                        pid = os.fork()
                        if pid == 0:
                            lab2exec(pop, pc, pm, tor, csv)
                        else:
                            print("Creating: ", csv)
                            files.append(csv)
                            pCount += 1
                            if pCount == maxP:
                                pid, status = os.wait()
                                pCount -= 1
                            

    while(pCount > 0 ):
        os.wait()
        pCount -= 1

#end def
def formatFile(fileNumber):

    with open(files[fileNumber], "r") as f:
        lines = f.readlines()
    
    lines = [line.strip('\n') for line in lines]
    newLines = ["step,fitness,genome\n"]
    lineSwitch = 0

    for line in lines:
        if ( line == "step,fitness,genome"):
            continue
        if(lineSwitch == 0):
            newLines.append( str(line))
            lineSwitch = 1
        else:
            newLines[-1] += str(line) + '\n'
            lineSwitch = 0

    with open(files[fileNumber], "w") as f:
        f.writelines(newLines)

def formatCSVFiles():

    pCount = 0
    
    for i in range(0, 5120):

        pid = os.fork()
        if pid == 0:
            formatFile(i)
            os._exit(0)
        else:
            print("Formatting: ", files[i])
            pCount += 1
            if pCount == maxP:
                pid, status = os.wait()
                pCount -= 1
    while(pCount >  0):
        pid, status = os.wait()
        pCount -= 1


'''
    create a CSV directory
'''
pid = os.fork()
if pid == 0:
    os.execvp('mkdir', ['mkdir', 'CSV',])
else:
    os.wait()

runLab2Program()

formatCSVFiles()

"""
    Proccess each CSV file once they are all created!
"""

total_processes = 5120
batch_size = 32

for i in range(0, total_processes, batch_size):
    batch = []
    for j in range(i, min(i + batch_size, total_processes)):
        pid = os.fork()
        if pid == 0:
            proccessFile(j)
            os._exit(0)
        else:
            batch.append(pid)

    # Wait for all child processes in the batch to finish
    for pid in batch:
        os.waitpid(pid, 0)

print("Creating MASTER CSV file!")

files = [file.replace(".csv", ".txt") for file in files]

masterFile = open("masterCSV.csv", "w")

masterFile.write("N,P_c,P_m,Tournament Size,Iteration,Generation,Average Fitness,Best Fitness,Best Genome,Solution Found (0 or 1),Solution Count,Diversity Metric\n")

for i in range(len(files)):
    with open(files[i], "r") as f:
        #for line in range(30):
        masterFile.writelines(f.readlines())

masterFile.close()

print("Finished")
