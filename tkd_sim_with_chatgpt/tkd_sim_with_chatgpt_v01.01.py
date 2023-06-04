
# Instructions sent to ChatGPT v4:

# Write a python object-oriented program to simulate the movements of an three-dimensional agent on a flat horizontal surface. 

# The surfacece: 
# - The flat surface is a square with side length S = 10 meters and it should be modeleded as a cartesian plane with two axes ("x" and "y" axis respectively) each one with a range between -S/2 and +S/2.
# - The direction of the positive Y axis is "North" and the direction of the positive X axis is "East". 

# The agent: 
# - The agent is a model of a person that has only two legs (nothing else).  The legs are straight line segments of lenghth L = 85 cm.  
# - The legs are joined at the top.  The point where the two legs meet will be designated the "center of mass" of the agent.

# The behaviors of the agent:
# - The agent can rotate on the horizontal plane in order to face any direction. 
# - The paramenter "AGENT_DIRECTION" indicates in which direction the agent is facing. The value of AGENT_DIRECTION is interpreted as a compass (0 degrees = agent is facing north, 90 degrees = agent is facing west)  
# - When the agent is constructed it should be initialized as facing south.
# - The agent object has a method rotate_body(r) which rotates AGENT_DIRECTION by "r" degrees.
# - The agent can also move its left leg and right leg independently.  
# - Each leg has a position: The tuples (LEFT_X, LEFT_Y) and (RIGHT_X, RIGHT_Y) define the coordinates of the left and right legs, respectively, on the flat surface.
# - When the agent is constructed it should be initialized as standing with both feet in the center of the flat surface. 
# - The agent object has two methods to move the legs: move_left_leg(forward_distance, side_distance) and move_right_leg(forward_distance, side_distance). 
# - The forward_distance parameter moves the respective leg in the same direction where the agent is pointing. Positive values move the leg forward and negative values move the leg backwards.  
# - The side_distance parameter moves the respective leg in a direction perpendicular towards that of the agent.  Positive values move the left leg towards the left of the agent and move the right leg towards the right of the agent. Negative values have the opposite effect. 

# Constraints on the movement of the agent:
# - After every leg movement, the agent will recalculate the position of the center of mass. 
# - If the center of mass of the agent falls outside the boundaries of the flat surface, the python program should raise and exception "Agent Out Of Bounds"  
# - The angle between the two legs (LEG_ANGLE) may range between MIN_LEG_ANGLE = 0 degrees (closed position) and MAX_LEG_ANGLE = 80 degrees (fully open position.)  
# - Whenever the legs of the agent move, the agent will recalculate LEG_ANGLE. If a leg movement causes LEG_ANGLE to fall outside the [MIN_LEG_ANGLE, MAX_LEG_ANGLE] range, the program will generate an exception named "InvalidLegAngle".

# Main program
# - The main program should create the agent object and then call a function named "form01" that executes the following movemenents:
# - First move the left leg forward 50 cm, move the right leg forward 100 cm, turn the agent 90 degrees counterclockwise
# - Then move the left leg backward 100 cm 
# - After each one of those moves, the program should report the values of all these parameters: LEFT_X, LEFT_Y, RIGHT_X, RIGHT_Y, AGENT_DIRECTION, LEG_ANGLE


import math

class AgentOutOfBounds(Exception):
    pass

class InvalidLegAngle(Exception):
    pass

class Agent:
    S = 10
    L = 0.85
    MIN_LEG_ANGLE = 0
    MAX_LEG_ANGLE = 80

    def __init__(self):
        self.agent_direction = 180  # Facing south
        self.left_x = 0
        self.left_y = 0
        self.right_x = 0
        self.right_y = 0

    def rotate_body(self, r):
        self.agent_direction = (self.agent_direction + r) % 360

    def move_left_leg(self, forward_distance, side_distance):
        self.left_x += forward_distance * math.cos(math.radians(self.agent_direction)) - side_distance * math.sin(math.radians(self.agent_direction))
        self.left_y += forward_distance * math.sin(math.radians(self.agent_direction)) + side_distance * math.cos(math.radians(self.agent_direction))
        self._check_boundaries()
        self._check_leg_angle()

    def move_right_leg(self, forward_distance, side_distance):
        self.right_x += forward_distance * math.cos(math.radians(self.agent_direction)) + side_distance * math.sin(math.radians(self.agent_direction))
        self.right_y += forward_distance * math.sin(math.radians(self.agent_direction)) - side_distance * math.cos(math.radians(self.agent_direction))
        self._check_boundaries()
        self._check_leg_angle()

    def _check_boundaries(self):
        center_of_mass_x = (self.left_x + self.right_x) / 2
        center_of_mass_y = (self.left_y + self.right_y) / 2
        if abs(center_of_mass_x) > self.S / 2 or abs(center_of_mass_y) > self.S / 2:
            raise AgentOutOfBounds

    def _check_leg_angle(self):
        leg_angle = math.degrees(math.atan2(abs(self.left_y - self.right_y), abs(self.left_x - self.right_x)))
        if leg_angle < self.MIN_LEG_ANGLE or leg_angle > self.MAX_LEG_ANGLE:
            raise InvalidLegAngle

def form01(agent):
    try:
        agent.move_left_leg(0.5, 0)
        print(agent.left_x, agent.left_y, agent.right_x, agent.right_y, agent.agent_direction)
        agent.move_right_leg(1, 0)
        print(agent.left_x, agent.left_y, agent.right_x, agent.right_y, agent.agent_direction)
        agent.rotate_body(90)
        print(agent.left_x, agent.left_y, agent.right_x, agent.right_y, agent.agent_direction)
        agent.move_left_leg(-1, 0)
        print(agent.left_x, agent.left_y, agent.right_x, agent.right_y, agent.agent_direction)
    except AgentOutOfBounds:
        print("Agent out of bounds!")
    except InvalidLegAngle:
        print("Invalid leg angle!")

def main():
    agent = Agent()
    form01(agent)

if __name__ == "__main__":
    main()
