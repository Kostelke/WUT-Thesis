import json
from ortools.linear_solver import pywraplp
from ModelFunctions import createBinaryConstraints, createComplexConstraints, createEdgeFlowVariables, createMinimizeFunction, createMinimizeFunctionBinary, createMinimizeFunctionDemand, createNodeVariablesBinary, createNodeVariablesSimple, createPhaseVariables, createSimpleConstraints, exportEdgeJSON, exportNodesJSON, exportPlantsJSON, loadEdges, loadNode, loadPlants

_globalDemand = [
    16000
    ]


def main():
    nodes = loadNode("Scenario#3/Demand.txt")
    edges = loadEdges("Scenario#3/Lines.txt")
    loadPlants(nodes, "Scenario#3/PowerPlants.txt")
    

    
    periodOfTime = []
    time = 0
    mode = "binary"
    shortage = []
    overflow = []
    enforceStrict = True
    solver = pywraplp.Solver.CreateSolver('SCIP')
    TimeMax = 1
    zvar = []

    if mode == "simple":
        while time <TimeMax :
            plantsInNodes = createNodeVariablesSimple(solver, nodes, _globalDemand, time)
            phaseVariable = createPhaseVariables(solver, nodes)
            edgeFlowVariables = createEdgeFlowVariables(solver,nodes,edges)
            createSimpleConstraints(solver,nodes, edges, edgeFlowVariables, phaseVariable, plantsInNodes, periodOfTime, time, _globalDemand, shortage, overflow, enforceStrict)
            time +=1


        if enforceStrict:
            sumOfGeneration = createMinimizeFunction(solver,periodOfTime)
        else:
            sumOfGeneration = createMinimizeFunctionDemand(solver, periodOfTime, shortage, overflow,)    
    
    if mode == "binary":
        while time <TimeMax :
            plantsInNodes = createNodeVariablesBinary(solver, nodes, _globalDemand, time)
            phaseVariable = createPhaseVariables(solver, nodes)
            edgeFlowVariables = createEdgeFlowVariables(solver,nodes,edges)
            createBinaryConstraints(solver,nodes, edges, edgeFlowVariables, phaseVariable, plantsInNodes, periodOfTime, time, _globalDemand, shortage, overflow, enforceStrict)
            time +=1


        if enforceStrict:
            sumOfGeneration = createMinimizeFunctionBinary(solver,periodOfTime)
        else:
            sumOfGeneration = createMinimizeFunctionDemand(solver, periodOfTime, shortage, overflow,)           
    
    if mode == "complex":
        while time <TimeMax :
            plantsInNodes = createNodeVariablesBinary(solver, nodes, _globalDemand, time)
            phaseVariable = createPhaseVariables(solver, nodes)
            edgeFlowVariables = createEdgeFlowVariables(solver,nodes,edges)
            createComplexConstraints(solver,nodes, edges, edgeFlowVariables, phaseVariable, plantsInNodes, periodOfTime, time, _globalDemand, shortage, overflow, enforceStrict, zvar)
            time +=1


        if enforceStrict:
            sumOfGeneration = createMinimizeFunction(solver,periodOfTime)
        else:
            sumOfGeneration = createMinimizeFunctionDemand(solver, periodOfTime, shortage, overflow,)   

    solver.Minimize(sum(sumOfGeneration))

    status = solver.Solve()

   
    print('Solution:')
    print('Objective value =', solver.Objective().Value())
    print('\nAdvanced usage:')
    suma = 0
    for time in periodOfTime:
        for node in time:
            for plant in node["plants"]:
                print(plant.solution_value())
    # for time in periodOfTime:
    #     for node in time:
    #         for work in node["isPlantWorking"]:
    #             print(work.solution_value())
    # print("zVar")
    # for z in zvar:
    #     print(z.solution_value())
 
    # if not enforceStrict:
    #     print("\n SHORTAGE \n")
    #     for short in shortage:
    #         print(short.solution_value())

    #     print("\n Overflow \n")
    #     for over in overflow:
    #         print(over.solution_value())
        


    print('Problem solved in %f milliseconds' % solver.wall_time())
    print('Problem solved in %d iterations' % solver.iterations())
    print('Problem solved in %d branch-and-bound nodes' % solver.nodes())

    # y = json.dumps(exportEdgeJSON(edgeFlowVariables))

    # print(y)

    # z = json.dumps(exportNodesJSON(nodes, shortage, overflow, periodOfTime[0]))
    # print(z)

    # x = json.dumps(exportPlantsJSON(periodOfTime[0], nodes))
    # print(x)



if __name__ == '__main__':
    main()