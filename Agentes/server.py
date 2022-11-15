from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

from model import BoxPicking
from model import Robot, Box

GRID_WIDTH = 15
GRID_HEIGHT = 15

MAX_STEPS = 10000
NUMBER_OF_BOXES = 30

def agent_portrayal(agent):
    # if the agent is a robot, return a brown circle
    if isinstance(agent, Robot):
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Color": "rgb(146, 90, 55)",
                     "r": 0.4,
                     "Layer": 1}
            
    elif isinstance(agent, Box):
        # if the agent is a box, placed correctly and its stack size is 5, return a blue rectangle
        if agent.is_placed_correctly and agent.get_number_of_boxes_in_stack() == 5:
            portrayal = {"Shape": "rect",
                         "Filled": "true",
                         "Color": "rgb(0, 255, 0)",
                         "w": 0.9,
                         "h": 0.9,
                         "Layer": 0,
                         "text": agent.get_number_of_boxes_in_stack(),
                         "text_color": "black"}
        # if the agent is a box, placed correctly and its stack size is less than 5, return a yellow rectangle
        elif agent.is_placed_correctly and agent.get_number_of_boxes_in_stack() < 5:
            portrayal = {"Shape": "rect",
                         "Filled": "true",
                         "Color": "rgb(255, 255, 0)",
                         "w": 0.9,
                         "h": 0.9,
                         "Layer": 0,
                         "text": agent.get_number_of_boxes_in_stack(),
                         "text_color": "black"}
        # if the agent is a box and picked up by a robot, return a yellow-ish smaller rectangle
        elif agent.is_picked:
            portrayal = {"Shape": "rect",
                    "Filled": "true",
                    "Color": "rgb(223, 190, 44)",
                    "w": 0.6,
                    "h": 0.6,
                    "Layer": 0}
        # if the agent is not picked up, not placed correctly and its stack size is less than 5, return a red rectangle
        else:
            portrayal = {"Shape": "rect",
                         "Filled": "true",
                         "Color": "rgb(255, 0, 0)",
                         "w": 0.6,
                         "h": 0.6,
                         "Layer": 0}

    return portrayal


grid = CanvasGrid(agent_portrayal, GRID_WIDTH, GRID_HEIGHT, 500, 500)

server = ModularServer(BoxPicking,
                          [grid],
                            "Box Picking",
                            {"n_boxes": NUMBER_OF_BOXES, "width": GRID_WIDTH, "height": GRID_HEIGHT, "max_steps": MAX_STEPS})

server.port = 8521 # The default
server.launch()