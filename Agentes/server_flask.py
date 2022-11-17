from flask import Flask, request, jsonify
from model import *
from agent import *

# Size of the board:
NUMBER_OF_BOXES = 115
width = 15
height = 15
randomModel = None
currentStep = 0
max_steps = 5000
running = True

app = Flask("Robot-box example")


@app.route('/init', methods=['POST', 'GET'])
def initModel():
    global currentStep, randomModel, width, height, NUMBER_OF_BOXES, max_steps

    # Datos que estamos mandando
    if request.method == 'POST':
        width = int(request.form.get('width'))
        height = int(request.form.get('height'))
        NUMBER_OF_BOXES = int(request.form.get('NBoxes'))
        # PReguntar max steps
        max_steps = int(request.form.get('MaxSteps'))
        currentStep = 0

        print(request.form)
        print(width, height, NUMBER_OF_BOXES, max_steps)
        # Aquí se crea el modelo
        randomModel = BoxPicking(width, height, NUMBER_OF_BOXES, max_steps)

        return jsonify({"message": "Parameters recieved, model initiated."})


# Para obtener agentes
@app.route('/getAgents', methods=['GET'])
def getAgents():
    global randomModel

    if request.method == 'GET':
        # List comprehension
        agentsPositions = []
        for i in list(randomModel.grid.coord_iter()):
            agents = i[0]
            x = i[1]
            z = i[2]
            for a in agents:
                if isinstance(a, Robot):
                    agentsPositions.append({"id": str(a.unique_id), "x": x, "y": .3, "z": z})

        return jsonify({'positions': agentsPositions})


# Para obtener obstáculos
@app.route('/getObstacles', methods=['GET'])
def getObstacles():
    global randomModel

    if request.method == 'GET':
        # List comprehension
        print(list(randomModel.grid.coord_iter()))
        carPositions = []
        for i in list(randomModel.grid.coord_iter()):
            agents = i[0]
            x = i[1]
            z = i[2]
            for a in agents:
                if isinstance(a, Box):
                    carPositions.append({"id": str(a.unique_id), "x": x, "y": 0.3, "z": z})

        return jsonify({'positions': carPositions})


# Se encarga de hacerle el update al modelo, puede ser muy tardado
@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, randomModel
    if request.method == 'GET':
        randomModel.step()
        currentStep += 1
        return jsonify({'message': f'Model updated to step {currentStep}.',
                        'currentStep': currentStep})


if __name__ == '__main__':
    app.run(host="localhost", port=8585, debug=True)
