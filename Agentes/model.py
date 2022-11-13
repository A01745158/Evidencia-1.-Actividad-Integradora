from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
from agent import Robot, Box

class BoxPicking(Model):
    def __init__(self, width, height, n_boxes, max_steps):
        """
        Create a new BoxPicking model, where it will include Robot agents and Box agents.

        Args:
            width (int): the width of the multigrid
            height (int): The height of the multigrid
            n_boxes (int): The number of boxes in the model
        """
        self.width = width
        self.height = height
        self.number_of_boxes = n_boxes
        self.max_steps = max_steps
        self.movements = 0

        self.box_agents = []
        self.ideal_position = (0, 0)
        self.all_stacking_positions = [self.ideal_position]

        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width, height, False)
        self.running = True

        # Collect data about movements across all agents
        self.datacollector = DataCollector(
            {
                "movements": BoxPicking.get_movements
            }
        )
        
        for i in range(n_boxes):
            box = Box(i, self)
            # move box to random empty position
            empty_coordinates = self.grid.find_empty()
            self.grid.place_agent(box, empty_coordinates)
            # if the position where the box is placed is the ideal position, set the instance variable to True
            if box.pos[0] == self.ideal_position[0] and box.pos[1] == self.ideal_position[1]:
                box.is_placed_correctly = True
            self.box_agents.append(box)

        for i in range(5):
            robot = Robot(i, self)
            self.schedule.add(robot)
            # Get the coordinates for an empty cell
            empty_coordinates = self.grid.find_empty()
            # If there are no more empty cells, stop adding robots
            if empty_coordinates == None:
                break
            # while the coordinates for the empty position are the ideal position, get another random empty position
            while empty_coordinates[0] == self.ideal_position[0] and empty_coordinates[1] == self.ideal_position[1]:
                empty_coordinates = self.grid.find_empty()
                if empty_coordinates == None:
                    break
            self.grid.place_agent(robot, empty_coordinates)

    def step(self):
        self.schedule.step()
        if self.get_number_of_placed_boxes() == self.number_of_boxes or self.schedule.steps == self.max_steps - 1:
            self.running = False
            self.print_data()

    def get_last_x_position(self):
        """
        Returns the last x position of the model

        Returns:
            int: The last x position of the model
        """
        return self.width - 1

    def get_last_y_position(self):
        """
        Returns the last y position of the model

        Returns:
            int: The last y position of the model
        """
        return self.height - 1

    def get_number_of_placed_boxes(self):
        """
        Returns the number of placed boxes in the model

        Returns:
            int: The number of placed boxes in the model
        """
        placed_boxes = 0
        for agent in self.box_agents:
            if agent.is_placed_correctly:
                placed_boxes += 1
        return placed_boxes

    def get_movements(self):
        """
        Returns the number of movements that all agents have done

        Returns:
            int: The number of movements that all agents have done
        """
        return self.movements

    def print_data(self):
        """
        Prints the data of the model
        """
        print("Number of steps to finalization: " + str(self.schedule.steps))
        print("Number of movements across all agents: " + str(self.movements))