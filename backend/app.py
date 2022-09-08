import flask
from flask import request, jsonify
import json 
from ortools.linear_solver import pywraplp
from flask_cors import CORS, cross_origin

from ModelFunctions import createBinaryConstraints, createComplexConstraints, createEdgeFlowVariables, createMinimizeFunction, createMinimizeFunctionBinary, createMinimizeFunctionDemand, createNodeVariablesBinary, createNodeVariablesSimple, createPhaseVariables, createSimpleConstraints, exportEdgeJSON, exportNodesJSON, exportPlantsJSON, loadEdges, loadNode, loadPlants, loadPlantsJSON,getNode



_globalDemand = [
   1
]
periodOfTime = []
edgeSolutionPeriods = []
index = 0
solver = pywraplp.Solver.CreateSolver('SCIP')
shortage = []
overflow = []
TimeMax = 1
enforceStrict = True
mode = "simple"
inputNodesJSON = {}
inputEdgesJSON = {}
inputPlantsJSON = {}
outputResultJSON = {"test": "lets See"}
nodes = []
edges = []
toolConfig = {
    "mode": "simple",
    "enforceStrict": True,
    "timeMax": 1,
}

def returnNodes():
    return nodes

def returnEdges():
    return edges

def setNode( nodes, node):
    nodes = node

def setEdge(edges, edge):
    edges = edge


app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Distant Reading Archive</h1>
<p>A prototype API for distant reading of science fiction novels.</p>'''


@app.route('/api/nodes-results', methods=['GET'])
@cross_origin(origin='*')
def api_nodeResults():

    response = jsonify(outputResultJSON)
    # response.headers.add('Access-Control-Allow-Origin', 'http://localhost')
    return response

@app.route('/api/post-nodes', methods=['POST'])
@cross_origin(origin='*')
def api_postNodes():
    response = jsonify("ok")
    # response.headers.add('Access-Control-Allow-Origin', 'http://localhost')
    global nodes
    nodes = request.get_json()
    return response

@app.route('/api/post-edges', methods=['POST'])
@cross_origin(origin='*')
def api_postEdges():
    response = jsonify("ok")
    # response.headers.add('Access-Control-Allow-Origin', 'http://localhost')
    global edges 
    edges = request.get_json()
    return response

@app.route('/api/post-config', methods=['POST'])
@cross_origin(origin='*')
def api_postConfig():
    response = jsonify("ok")
    global toolConfig 
    toolConfig = request.get_json()
    return response

@app.route('/api/post-plants', methods=['POST'])
@cross_origin(origin='*')
def api_postPlants():
    response = jsonify("ok")
    global nodes
    loadPlantsJSON(nodes, request.get_json())
    return response



@app.route('/api/get-results', methods=['GET'])
@cross_origin(origin='*')
def api_getResults():
    global nodes
    global edges
    global _globalDemand
    global solver
    global toolConfig
    global periodOfTime
    global edgeSolutionPeriods
    shortage = []
    mode = toolConfig["mode"]
    sumOfGeneration = []
    edgeFlowVariables = []
    overflow

    periodOfTime = []
    edgeSolutionPeriods = []
    
    enforceStrict = toolConfig["enforceStrict"]

    TimeMax = toolConfig["timeMax"]
    print(toolConfig)
    
    time = 0

    if mode == "simple":
        while time <TimeMax :
            plantsInNodes = createNodeVariablesSimple(solver, nodes, _globalDemand, time)
            phaseVariable = createPhaseVariables(solver, nodes)
            edgeFlowVariables = createEdgeFlowVariables(solver,nodes,edges, edgeSolutionPeriods)
            createSimpleConstraints(solver,nodes, edges, edgeFlowVariables, phaseVariable, plantsInNodes, periodOfTime, time, _globalDemand, shortage, overflow, enforceStrict)
            time +=1


        if enforceStrict:
            sumOfGeneration = createMinimizeFunction(solver,periodOfTime)
        else:
            sumOfGeneration = createMinimizeFunctionDemand(solver, periodOfTime, shortage)    
    
    if mode == "binary":
        while time <TimeMax :
            plantsInNodes = createNodeVariablesBinary(solver, nodes, _globalDemand, time)
            phaseVariable = createPhaseVariables(solver, nodes)
            edgeFlowVariables = createEdgeFlowVariables(solver,nodes,edges, edgeSolutionPeriods)
            createBinaryConstraints(solver,nodes, edges, edgeFlowVariables, phaseVariable, plantsInNodes, periodOfTime, time, _globalDemand, shortage, overflow, enforceStrict)
            time +=1


        if enforceStrict:
            sumOfGeneration = createMinimizeFunctionBinary(solver,periodOfTime)
        else:
            sumOfGeneration = createMinimizeFunctionDemand(solver, periodOfTime, shortage)           
    
    if mode == "complex":
        while time <TimeMax :
            plantsInNodes = createNodeVariablesBinary(solver, nodes, _globalDemand, time)
            phaseVariable = createPhaseVariables(solver, nodes)
            edgeFlowVariables = createEdgeFlowVariables(solver,nodes,edges, edgeSolutionPeriods)
            createComplexConstraints(solver,nodes, edges, edgeFlowVariables, phaseVariable, plantsInNodes, periodOfTime, time, _globalDemand, shortage, overflow, enforceStrict)
            time +=1


        if enforceStrict:
            sumOfGeneration = createMinimizeFunction(solver,periodOfTime)
        else:
            sumOfGeneration = createMinimizeFunctionDemand(solver, periodOfTime, shortage)   

    solver.Minimize(sum(sumOfGeneration))
    status = solver.Solve()
    
    t = 0
    edgeResponse = exportEdgeJSON(edgeSolutionPeriods[t])
    nodeResponse = exportNodesJSON(nodes, t, _globalDemand)
    plantResponse = exportPlantsJSON(periodOfTime[t], nodes, toolConfig["mode"])
    
    response = {
        "nodes": nodeResponse,
        "edges": edgeResponse,
        "plants": plantResponse
    }
    return jsonify(response)


@app.route('/api/next', methods=['GET'])
@cross_origin(origin='*')
def api_next():
    global nodes
    global edges
    global _globalDemand
    global solver
    global toolConfig
    global periodOfTime
    global edgeSolutionPeriods
    global index
    mode = toolConfig["mode"]  

    if len(periodOfTime) - 1 > index :
         index = index + 1
    else: 
        index = len(periodOfTime) - 1 
    
    t = index
        
    edgeResponse = exportEdgeJSON(edgeSolutionPeriods[t])
    nodeResponse = exportNodesJSON(nodes, t, _globalDemand)
    plantResponse = exportPlantsJSON(periodOfTime[t], nodes, toolConfig["mode"])
    response = {
        "nodes": nodeResponse,
        "edges": edgeResponse,
        "plants": plantResponse
    }
    return response

@app.route('/api/prev', methods=['GET'])
@cross_origin(origin='*')
def api_prev():
    global nodes
    global edges
    global _globalDemand
    global solver
    global toolConfig
    global periodOfTime
    global edgeSolutionPeriods
    global index
    mode = toolConfig["mode"]  

    if  index > 0 :
         index = index - 1
    else: 
        index = 0
    
    t = index
        
    edgeResponse = exportEdgeJSON(edgeSolutionPeriods[t])
    nodeResponse = exportNodesJSON(nodes, t, _globalDemand)
    plantResponse = exportPlantsJSON(periodOfTime[t], nodes, toolConfig["mode"])
    response = {
        "nodes": nodeResponse,
        "edges": edgeResponse,
        "plants": plantResponse
    }
    return response

  
if __name__ == "__main__":
    app.run(debug=True)