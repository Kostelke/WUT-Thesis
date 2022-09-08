from cmath import phase
from numpy import double
from ortools.linear_solver import pywraplp
from ortools.init import pywrapinit
from ortools.sat.python import cp_model
import math


_globalDemand = [
    13000,
    14500,
    12000,
    10000,
    11000,
    12000,
    14000,
    15000,
    16403,
    17400,
    18300,
    18500,
    18400,
    17600,
    18300,
    18500,
    18400,
    17600,
    16200,
    15409,
    15302,
    13000,
    12000,
    12222,
] 
# in MW

def createNode(nodeName, demand, index):
    node = {
        "nodeName" : nodeName,
        "demand" : double(demand),
        "index" : index,
        "plants" : [],
    }
    return node

def createPlants(sourceNode, plantName, blockName, Pmin, Pmax, ):
    sourceNode["plants"].append({
        "plantName" : plantName,
        "blockName" : blockName,
        "Pmin" : double(Pmin),
        "Pmax" : double(Pmax)
    })

def getNode(nodeList, nodeToFind):
    for node in nodeList:
        if node["nodeName"] == nodeToFind:
            return node

def loadNode(fileNodes):
    nodeList = []
    count = 0
    file = open(fileNodes, 'r')
    for line in file:  
        _initialData = []
        for word in line.split():
            _initialData.append(word)
        nodeList.append(
            createNode(_initialData[0], _initialData[1] , count)
            )            
        count = count + 1
    file.close
    return nodeList


#Get appropiate node and add to it powerplants and its specificiation  
def loadPlants(nodeList, filePlants):
    file = open(filePlants, 'r')
    for line in file:  
        _initialData = []
        for word in line.split():
            _initialData.append(word)
        createPlants(getNode(nodeList, _initialData[0]), _initialData[1], _initialData[2],  _initialData[3],  _initialData[4])


def createEdge(nodeA, nodeB,  capacity, admitance, voltageA, voltageB):
    edge = {
        "name" : nodeA + nodeB,
        "capacity": double(capacity),
        "admitance" : double(admitance),
        "voltageA" : double(voltageA),
        "voltageB" : double(voltageB),
    }
    return edge

def loadEdges(fileEdges):
    edgeList = []
    file = open(fileEdges, 'r')
    for line in file:
        _initialData = []
        for word in line.split():
            _initialData.append(word)
        edgeList.append(createEdge(_initialData[0], _initialData[1], _initialData[2], _initialData[3], _initialData[4], _initialData[5]))
    file.close
    return edgeList

def isNeighbour(nodeA, nodeB, edges):
    for edge in edges:
        if nodeA+nodeB == edge["name"] or nodeB+nodeA == edge["name"]:
            return edge
    return -1

def getSourceVoltage(nodeA,nodeB, edge):
    if nodeA["nodeName"] + nodeB["nodeName"] == edge["name"]:
        return edge["voltageA"]
    else: 
        return edge["voltageB"]


def main():

    nodes = loadNode("Demand.txt")
    edges = loadEdges("Lines.txt")
    loadPlants(nodes, "PowerPlants.txt")


    solver = pywraplp.Solver.CreateSolver('SCIP')

    #Create Variables - pj, Pab, 0a - phase
    periodOfTime = []
    time = 0
    while time < 3 :

        plantsInNodes = []
        edgeFlowVariables = []
        phaseVariable = []
        

        for node in nodes:
            solverNode = {
                "nodeName" : node["nodeName"],
                "demand" : node["demand"] * _globalDemand[time],
                "plants" : [],
                "isPlantWorking" : [] # binary variable, same size as plants, defines if block is working
            }
            if len(node["plants"]) != 0:
                for plant in node["plants"]:
                    solverNode["plants"].append(
                        solver.NumVar(0, plant["Pmax"], plant["plantName"]+"_"+plant["blockName"])
                    )
                    solverNode["isPlantWorking"].append(
                        solver.BoolVar(plant["blockName"] +  " Is working: ")
                    )
            else :
                solverNode["plants"].append(
                    solver.NumVar(0, 0, node["nodeName"])
                )
                solverNode["isPlantWorking"].append(
                    solver.BoolVar( node["nodeName"] + " Is not working")
                )
            plantsInNodes.append(solverNode)
            maxPhase = math.pi
            phaseVariable.append(
                solver.NumVar(-maxPhase, maxPhase, node["nodeName"])
            )
        

        for nodeA in nodes:
            flowAB = []
            for nodeB in nodes:
                flag = isNeighbour(nodeA["nodeName"], nodeB["nodeName"], edges)
                if flag != -1:
                    edgeDataObject = {
                        "srcNodeVolt" : getSourceVoltage(nodeA, nodeB, flag),
                        "dstNodeVolt" : getSourceVoltage(nodeB, nodeA, flag),
                        "var" : solver.NumVar(-flag["capacity"], flag["capacity"], nodeA["nodeName"]+nodeB["nodeName"])
                    }
                    flowAB.append(edgeDataObject)
                if flag == -1: 
                    flowAB.append(0)
            edgeFlowVariables.append(flowAB)

        # Create constraint - flow into and from node, flow on edge and phase on first node
    
        for nodeA in nodes:
            neighbouringEdges = []
            for nodeB in nodes:
                edgeToConstrain = isNeighbour(nodeA["nodeName"], nodeB["nodeName"], edges)
                if edgeToConstrain != -1 :
                    edgeFlowDataObject = edgeFlowVariables[nodeA["index"]][nodeB["index"]]
                    neighbouringEdges.append(edgeFlowDataObject["var"])
                    solver.Add(
                        edgeFlowDataObject["var"] == edgeFlowDataObject["srcNodeVolt"] * edgeFlowDataObject["dstNodeVolt"]*edgeToConstrain["admitance"]*(
                            phaseVariable[nodeA["index"]]- phaseVariable[nodeB["index"]]
                            )
                    )
            index = 0
            for plant in plantsInNodes[nodeA["index"]]["plants"]:
                if len(nodes[nodeA["index"]]["plants"]) > 0:
                    solver.Add(
                        plant <= plantsInNodes[nodeA["index"]]["isPlantWorking"][index]*nodes[nodeA["index"]]["plants"][index]["Pmax"]
                    )
                    solver.Add(
                        plant >= plantsInNodes[nodeA["index"]]["isPlantWorking"][index]*nodes[nodeA["index"]]["plants"][index]["Pmin"]
                    )
                    if time > 0:
                        solver.Add(
                            periodOfTime[time - 1][nodeA["index"]]["plants"][index] - plant <= 0.3* (
                                nodes[nodeA["index"]]["plants"][index]["Pmax"]
                            )
                        )
                        solver.Add(
                            periodOfTime[time - 1][nodeA["index"]]["plants"][index] - plant >= -0.3* (
                                nodes[nodeA["index"]]["plants"][index]["Pmax"]
                            )
                        )
                    index = index + 1
            solver.Add(
                sum(plantsInNodes[nodeA["index"]]["plants"]) - nodeA["demand"]*_globalDemand[time] - sum(neighbouringEdges)==0
            )
        time +=1    
        periodOfTime.append(plantsInNodes)


    sumOfGeneration = []
    for hour in periodOfTime:
        for node in hour :
            for plant in node["plants"]:
                sumOfGeneration.append(plant)

    solver.Minimize(sum(sumOfGeneration))
    status = solver.Solve()

   
    print('Solution:')
    print('Objective value =', solver.Objective().Value())
    print('\nAdvanced usage:')
    suma = 0
    for d in periodOfTime:
        for node in d:
            for plant in node["plants"]:
                suma = suma + plant.solution_value()
 
    
    # mathDifference = []
    # i = 0
    # for node in nodes:
    #     pindex = 0
    #     if len(node["plants"]) > 0 :
    #         for plant in node["plants"]:
    #             if difference[0][i][pindex] - difference[1][i][pindex] > plant["Pmax"]* 0.4:
    #                 mathDifference.append("Error")
    #             if difference[0][i][pindex] - difference[1][i][pindex] < -plant["Pmax"]* 0.4:
    #                  mathDifference.append("Error")
    #             if difference[1][i][pindex] - difference[2][i][pindex] > plant["Pmax"]* 0.4:
    #                 mathDifference.append("Error")
    #             if difference[1][i][pindex] - difference[2][i][pindex] < -plant["Pmax"]* 0.4:
    #                  mathDifference.append("Error")
    #             pindex +=1
    #     i +=1

    # print(mathDifference)
    # print( "len is ")
    # print(len(mathDifference))
                
    print(" sum of energy = ")
    print(suma)
    print("\n Aiming for: ")
    t = 0
    cel = 0
    while t < time :
        cel = cel + _globalDemand[t]
        t+=1
    print(cel)
    print('Problem solved in %f milliseconds' % solver.wall_time())
    print('Problem solved in %d iterations' % solver.iterations())
    print('Problem solved in %d branch-and-bound nodes' % solver.nodes())



if __name__ == '__main__':
    main()



