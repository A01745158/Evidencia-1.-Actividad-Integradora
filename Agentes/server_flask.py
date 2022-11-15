from flask import Flask, request, jsonify
from agent import *
from server import *

# Size of the board:
number_agents = 5
width = 28
height = 28
randomModel = None
currentStep = 0

app = Flask("Robot-box example")


@app.route('/init', methods=['POST', 'GET'])
def initModel():
    global currentStep, randomModel, number_agents, width, height

    # Datos que estamos mandando
    if request.method == 'POST':
        number_agents = int(request.form.get('NAgents'))
        width = int(request.form.get('width'))
        height = int(request.form.get('height'))
        currentStep = 0

        print(request.form)
        print(number_agents, width, height)
        # Aquí se crea el modelo
        randomModel = RandomModel(number_agents, width, height)

        return jsonify({"message": "Parameters recieved, model initiated."})
# Para obtener agentes
if __name__ == '__main__':
    app.run(host="localhost", port=8585, debug=True)