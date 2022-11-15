from mesa import Agent


# Idea para memoria si es permitido, cada vez que un robot pase por una caja cuando esté en camino a dejar una caja que ya lleva cargando
# entonces le va a agregar a un diccionario en el robot de las coordenadas de la caja y se le asigna a un robot aleatorio para que pueda ir por ella directamente
# en vez de tener que buscarla. Se puede utilizar el unique_id del robot para identificarlo en el diccionario. El diccionario tendría {unique_id: [coordenadas]}.
# Se implementaria en move(), que si existe un valor de coordenada en su unique_id en el diccionario, entonces se mueve a esa coordenada y se elimina el valor del diccionario cuando la recoge.
class Robot(Agent):
    """ 
    A robot agent that can pick up boxes and place them in the right position
    """
    def __init__(self, unique_id, model):
        """
        Create a new Robot agent.

        Args:
            unique_id (int): Unique identifier for the agent
            model (Model): the model the agent is part of
        """
        super().__init__(unique_id, model)
        self.has_box = False
        self.box = None

    def step(self):
        """
        A step of the agent, if the agent moves a box to the ideal position and it reaches the limit of 5, 
        it will generate a new ideal position inside the model. It will also move the agent
        """
        if len(self.model.grid.get_cell_list_contents([self.model.ideal_position])) == 5:
            if self.model.ideal_position[0] == self.model.get_last_x_position():
                self.model.ideal_position = (0, self.model.ideal_position[1] + 1)
            else:
                self.model.ideal_position = (self.model.ideal_position[0] + 1, self.model.ideal_position[1])
                self.model.all_stacking_positions.append(self.model.ideal_position)

        self.move()


    def move(self):
        """
        Move the robot randomly until it finds a box to pick it up, then move it to the ideal position until it leaves the box to the ideal position.
        """
        if self.has_box:
            self.move_to_ideal_position()
            self.model.movements += 1
        else:
            if self.get_neighboor_box_position() is not None:
                self.pick_box()
            else:
                # Move randomly until it finds a box to move while not colliding with anything
                possible_positions = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
                if len(possible_positions) > 0:
                    # make copy of possible_positions to avoid changing the original list
                    possible_positions_copy = possible_positions.copy()
                    # select a random position from the possible positions
                    new_position = self.random.choice(possible_positions_copy)
                    
                    # get a new position until it is a position that is not a stacked box location
                    while new_position in self.model.all_stacking_positions:
                        # if there are non, return
                        if len(possible_positions_copy) == 0:
                            return
                        new_position = self.random.choice(possible_positions_copy)
                    
                    # iterate until a viable position is found, is none is found stay in the same position
                    while len(self.model.grid.get_cell_list_contents([new_position])) != 0:
                        random_cell_content = self.model.grid.get_cell_list_contents([new_position])
                        if len(random_cell_content) == 0:
                            self.model.grid.move_agent(self, new_position)
                            self.model.movements += 1
                            return
                        else:
                            possible_positions_copy.remove(new_position)
                            print(len(possible_positions_copy))
                            if len(possible_positions_copy) == 0:
                                self.model.grid.move_agent(self, (self.pos[0], self.pos[1]))
                                return
                            new_position = self.random.choice(possible_positions_copy)
                    
                    # case in which there is a viable position
                    self.model.grid.move_agent(self, new_position)
                    self.model.movements += 1
                    return
                # if there are no possible positions, return and do nothing
                self.model.grid.move_agent(self, (self.pos[0], self.pos[1]))
                return
                    
                # If there was a possible position to move, move to it, else stay in the same position

    def get_neighboor_box_position(self):
        """Searches its neighborhood for a box and returns its position if it exists

        Returns:
            coordinates: the coordinates of the position of the box
        """
        # Get the position of the box in the neighborhood of the robot
        for neighboor in self.model.grid.iter_neighbors(self.pos, moore=False, include_center=False):
            if isinstance(neighboor, Box):
                if neighboor.is_picked == False and neighboor.is_placed_correctly == False:
                    return neighboor.pos
        return None # No box found

    def pick_box(self):
        """
        Make the robot pick the box and assign it to the instance variable of box
        """
        box_pos = self.get_neighboor_box_position()
        if box_pos is not None:
            box = self.model.grid.get_cell_list_contents([box_pos])[0]
            self.box = box
            box.is_picked = True
            self.has_box = True

    def move_to_ideal_position(self):
        """
        Get the ideal position of the box, move all the way to the right, 
            then move all the way to the y position of the ideal position and then all 
            the way to the ideal position moving to the left until the ideal position is reached
        """
        ideal_position = self.model.ideal_position
        # If its the ideal position, stack the box
        for position in self.model.grid.iter_neighborhood(self.pos, moore=False, include_center=False):
            if position == ideal_position:
                self.model.grid.move_agent(self.box, position)
                self.box.is_placed_correctly = True
                self.has_box = False
                self.box = None
                return
        
        last_x_position = self.model.get_last_x_position()
        # Moves all the robot all the way to the right
        if self.pos[0] < last_x_position and self.pos[1] != ideal_position[1]:
            self.move_with_box(self.pos[0] + 1, self.pos[1])
            return

        # Moves all the robot all the way to the y position of the ideal position
        elif self.pos[1] > ideal_position[1]:
            self.move_with_box(self.pos[0], self.pos[1] - 1)
            return

        # Moves all the robot all the way to the ideal position moving to the left
        elif self.pos[1] == ideal_position[1]:
            left_cell = self.model.grid.get_cell_list_contents([(self.pos[0] - 1, self.pos[1])])
            if len(left_cell) != 0:
                for agent in left_cell:
                    if isinstance(agent, Robot):
                        self.model.grid.move_agent(self, (self.pos[0], self.pos[1]))
                        self.model.movements += 1
                        return

            self.move_with_box(self.pos[0] - 1, self.pos[1])
            return

    def move_with_box(self, x, y):
        """
        Move the robot and the box to the given position
        """
        self.model.grid.move_agent(self, (x, y))
        self.model.grid.move_agent(self.box, (x, y))


class Box(Agent):
    """
    A box agent that will be moved
    """
    def __init__(self, unique_id, model):
        """
        Create a new Box agent.

        Args:
            unique_id (_type_): Unique identifier for the agent
            model (_type_): the model the agent is part of
        """
        super().__init__(unique_id, model)
        self.is_picked = False
        self.is_placed_correctly = False

    def step(self):
        """
        Each step, get the number of boxes in its cell position
        """
        self.get_number_of_boxes_in_stack()

    def get_number_of_boxes_in_stack(self):
        """
        Get the number of boxes in the stack

        Returns:
            int: the number of boxes in the stack
        """
        return len(self.model.grid.get_cell_list_contents([self.pos]))