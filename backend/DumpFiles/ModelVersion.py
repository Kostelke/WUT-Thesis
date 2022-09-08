from cmath import phase
from numpy import double
from ortools.linear_solver import pywraplp
from ortools.init import pywrapinit
from ortools.sat.python import cp_model
import math


_globalDemand = 18000 
# in MW

def createNode(nodeName, demand, index):
    node = {
        "nodeName" : nodeName,
        "demand" : int( double(demand) * _globalDemand),
        "index" : index,
        "plants" : [],
    }
    return node

def createPlants(sourceNode, plantName, blockName, Pmin, Pmax, ):
    sourceNode["plants"].append({
        "plantName" : plantName,
        "blockName" : blockName,
        "Pmin" : int(Pmin),
        "Pmax" : int(Pmax)
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
        "capacity": int(capacity),
        "admitance" : int(admitance),
        "voltageA" : int(voltageA),
        "voltageB" : int(voltageB),
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


    solver = cp_model.CpModel()

    #Create Variables - pj, Pab, 0a - phase

    plantsInNodes = []
    edgeFlowVariables = []
    phaseVariable = []

    for node in nodes:
        solverNode = {
            "nodeName" : node["nodeName"],
            "demand" : node["demand"],
            "plants" : [],
            "isPlantWorking" : [] # binary variable, same size as plants, defines if block is working
        }
        if len(node["plants"]) != 0:
            for plant in node["plants"]:
                solverNode["plants"].append(
                    solver.NewIntVar(0, plant["Pmax"], plant["plantName"]+"_"+plant["blockName"])
                )
                solverNode["isPlantWorking"].append(
                    solver.NewBoolVar(plant["blockName"] +  " Is working: ")
                )
        else :
            solverNode["plants"].append(
                solver.NewIntVar(0, 0, node["nodeName"])
            )
            solverNode["isPlantWorking"].append(
                solver.NewBoolVar( node["nodeName"] + " Is not working")
            )
        plantsInNodes.append(solverNode)
        maxPhase = math.pi
        phaseVariable.append(
            solver.NewIntVar(0, 360, node["nodeName"])
        )
    

    for nodeA in nodes:
        flowAB = []
        for nodeB in nodes:
            flag = isNeighbour(nodeA["nodeName"], nodeB["nodeName"], edges)
            if flag != -1:
                edgeDataObject = {
                    "srcNodeVolt" : getSourceVoltage(nodeA, nodeB, flag),
                    "dstNodeVolt" : getSourceVoltage(nodeB, nodeA, flag),
                    "var" : solver.NewIntVar(-flag["capacity"], flag["capacity"], nodeA["nodeName"]+nodeB["nodeName"])
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
        generation = []
        index = 0
        for plant in plantsInNodes[nodeA["index"]]["plants"]:
            solver.Add(
                plant == 0
            ).OnlyEnforceIf(plantsInNodes[nodeA["index"]]["isPlantWorking"][index])
            solver.Add(
                plant >= nodeA["Pmin"]
            ).OnlyEnforceIf(plantsInNodes[nodeA["index"]]["isPlantWorking"][index].Not)

    
        solver.Add(
            sum(plantsInNodes[nodeA["index"]]["plants"]) - nodeA["demand"] - sum(neighbouringEdges)==0
        )


    sumOfGeneration = []
    for node in plantsInNodes:
        for plant in node["plants"]:
            sumOfGeneration.append(plant)

    solver.Minimize(sum(sumOfGeneration))
    solver2 = cp_model.CpSolver()
    status = solver2.Solve()

   
    print('Solution:')
    print('Objective value =', solver2.Objective().Value())
    print('\nAdvanced usage:')
    for node in plantsInNodes:
        for plant in node["plants"]:
            name = plant.name()
            print(name + "=")
            print(plant.solution_value())
            print("\n")
    print('Problem solved in %f milliseconds' % solver.wall_time())
    print('Problem solved in %d iterations' % solver.iterations())
    print('Problem solved in %d branch-and-bound nodes' % solver.nodes())


if __name__ == '__main__':
    main()



