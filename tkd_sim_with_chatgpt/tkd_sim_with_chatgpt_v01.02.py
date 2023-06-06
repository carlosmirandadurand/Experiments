
# Instructions sent to ChatGPT v4:

#--------------------------------------------------------------------------------------------------

# Write a python object-oriented program to simulate the movements of a three-dimensional agent on a flat horizontal surface. 

# The surface: 
# - The flat surface is a square with side length S = 10 meters.
# - The coordinates of flat surface are fixed: (x ranging from -S/2 to S/2, y ranging from -S/2 to S/2, z = 0).
# - The direction of the positive Y axis is "North" and the direction of the positive X axis is "East".

# The agent: 
# - The agent is a model of a person that has only two legs amd two feet (nothing else).  
# - The legs are two straight line segments of lenghth L = 85 cm.
# - The feet are two straight line segments of lenghth F = 25 cm.

# The agent legs:
# - The coordinates of the bottom of the left leg are: (LEFT_X, LEFT_Y, 0).
# - The coordinates of the bottom of the right leg are: (RIGHT_X, RIGHT_Y, 0).
# - When an agent object is constructed, the coordinates should be set to the following initial values: LEFT_X = -L/5, RIGHT_X = L/5, LEFT_Y = 0, RIGHT_Y = 0  
# - The agent should have a setter method set_left_leg(x, y) that updates the position of the left leg to the coordinates passed as parameter  
# - The agent should have a setter method set_right_leg(x, y) that updates the position of the left leg to the coordinates passed as parameter  

# The agent center of mass:
# - The legs are joined at the top. The point where the two legs meet will be designated the "center of mass" of the agent. 
# - The plane that contains the two legs and the center of mass is always vertical (signifing that the agent is always standing up). 
# - The coordinates of the "center of mass" (CENTER_X, CENTER_Y, CENTER_Z) should be calculated automatically by the agent object every time that the left leg or the right leg moves.
# - After calculating the position of the center of mass, the code of the agent object should verify that the position of the left leg and right legs are physically feasible.  Otherwise the python program should raise and exception "Unfeasible Leg Position."
# - Also, if the (x,y) coordinates of the center of mass of the agent fall outside the boundaries of the flat surface, the python program should raise and exception "Out Of Bounds"  

# The angle between the two legs:
# - After calculating the position of the center of mass, the agent object should also automatically calculate an attribute LEG_ANGLE = the angle between the two leg segments (which is an angle in the hotizontal plane having the center of mass as it's vertex.) 
# - The angle between the two legs may range between MIN_LEG_ANGLE = 2 degrees (closed position) and MAX_LEG_ANGLE = 80 degrees (fully open position.)  
# - If any leg movement causes LEG_ANGLE to fall outside the [MIN_LEG_ANGLE, MAX_LEG_ANGLE] range, the program will generate an exception named "Invalid Leg Angle".


#--------------------------------------------------------------------------------------------------



import math

class Agent:
    def __init__(self):
        self.S = 10  # Surface side length
        self.L = 0.85  # Leg length
        self.F = 0.25  # Foot length
        self.LEFT_X = -self.L / 5
        self.RIGHT_X = self.L / 5
        self.LEFT_Y = 0
        self.RIGHT_Y = 0
        self.CENTER_X = 0
        self.CENTER_Y = 0
        self.CENTER_Z = 0
        self.LEG_ANGLE = 0

    def set_left_leg(self, x, y):
        self.LEFT_X = x
        self.LEFT_Y = y
        self.calculate_center_of_mass()
        self.validate_leg_positions()

    def set_right_leg(self, x, y):
        self.RIGHT_X = x
        self.RIGHT_Y = y
        self.calculate_center_of_mass()
        self.validate_leg_positions()

    def calculate_center_of_mass(self):
        self.CENTER_X = (self.LEFT_X + self.RIGHT_X) / 2
        self.CENTER_Y = (self.LEFT_Y + self.RIGHT_Y) / 2
        self.LEG_ANGLE = math.degrees(math.atan2(self.LEFT_Y - self.RIGHT_Y, self.LEFT_X - self.RIGHT_X))

    def validate_leg_positions(self):
        if self.LEG_ANGLE < 2 or self.LEG_ANGLE > 80:
            raise Exception("Invalid Leg Angle")

        if abs(self.LEFT_X) > self.S / 2 or abs(self.LEFT_Y) > self.S / 2 or abs(self.RIGHT_X) > self.S / 2 or abs(self.RIGHT_Y) > self.S / 2:
            raise Exception("Out Of Bounds")

    def print_agent_state(self):
        print("Left Leg Position: ({}, {})".format(self.LEFT_X, self.LEFT_Y))
        print("Right Leg Position: ({}, {})".format(self.RIGHT_X, self.RIGHT_Y))
        print("Center of Mass Position: ({}, {}, {})".format(self.CENTER_X, self.CENTER_Y, self.CENTER_Z))
        print("Leg Angle: {}".format(self.LEG_ANGLE))


# Example usage
agent = Agent()
agent.print_agent_state()

agent.set_left_leg(-0.5, 0.2)
agent.print_agent_state()

agent.set_right_leg(0.3, -0.1)
agent.print_agent_state()

agent.set_right_leg(2, 0)  # Out of bounds
