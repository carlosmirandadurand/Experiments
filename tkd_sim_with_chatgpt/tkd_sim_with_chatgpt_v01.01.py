
# Instructions sent to ChatGPT v4:

#--------------------------------------------------------------------------------------------------

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

#--------------------------------------------------------------------------------------------------

# Please make the following modifications to the program:

# Printing enhancements:
# - Move the printing of the agent parameters to a method of the agent named print_parameters().
# - Please round the coordinate parameters to the nearest centimener and the angles to the nearest degree.   

# Ploting the environment:
# - Create an function plot_environment_from_top(agent_list, image_file) that receives a list of agent objects and an output file name as paremeters 
# - The plot_environment_from_top function should render an image of all the agents and of the flat surface as visualized from the top.
# - The flat surface should be ploted with gray lines
# - The agents should be plotted each one in a different color 
# - When an agent is plotted, we should see a 30-75-75-degree triangle designating the position of the center of mass with the 30 degree angle pointing in the direction that the agent is facing.
# - When an agent is plotted, we should see the position of the left foot desigated with an "L" and the position of the right foot designated with an inverted "L".
# - When an agent is plotted, we should see line segments connecting the center of mass with the feet. 
# - After the image is rendered, it should be saved to disk with the filename designated by the 'image_file' parameter
# - If the path does not exist, the plot_environment_from_top function should create the directories and subdirectories before saving the image.  

# form01 function:
# - It should call the method print_parameters() after each step in order to produce the desired output.
# - It should call the function plot_environment_from_top after each step, passing the agent object and a unique filename as a paramater. The filename should be "var/image_nnn" where nnn represents a unique sequential number for each step.

#--------------------------------------------------------------------------------------------------

# Please write a new function plot_environment_from_top that prints a larger image (please triple the pixel dimensions of the surface.)  
# To represent the center of mass, the function should not plot a dot, but only the triangle. 
# Make the radius of the triangle 10 cm.  
# Make the font size of the feet smaller so each foot also measures less than 10 cm. 

#--------------------------------------------------------------------------------------------------

# Please make sure that the plot_environment_from_top displays the north at the top of the image, south at the bottom, east on the right, and west on the left.  Actually, please print these labels on alongside each one of the surface boundaries, using gray text, font size 8.
# ChatGPT: "You're right, we should adjust our plot so that it respects the cardinal directions as you mentioned. Here is the corrected function:"

#--------------------------------------------------------------------------------------------------



import math
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

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

    def print_parameters(self):
        leg_angle = round(math.degrees(math.atan2(abs(self.left_y - self.right_y), abs(self.left_x - self.right_x))))
        print(f"LEFT_X: {round(self.left_x, 2)}, LEFT_Y: {round(self.left_y, 2)}, RIGHT_X: {round(self.right_x, 2)}, RIGHT_Y: {round(self.right_y, 2)}, AGENT_DIRECTION: {round(self.agent_direction)}, LEG_ANGLE: {leg_angle}")


def plot_environment_from_top(agent_list, image_file):
    fig, ax = plt.subplots(figsize=(15, 15))

    # Plot flat surface
    flat_surface = patches.Rectangle((-Agent.S/2, -Agent.S/2), Agent.S, Agent.S, linewidth=1, edgecolor='grey', facecolor='none')
    ax.add_patch(flat_surface)

    colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']  # Different colors for different agents

    for i, agent in enumerate(agent_list):
        color = colors[i % len(colors)]

        # Plot agent's center of mass
        center_of_mass_x = (agent.left_x + agent.right_x) / 2
        center_of_mass_y = (agent.left_y + agent.right_y) / 2

        # Plot agent's legs
        plt.plot([agent.left_x, center_of_mass_x], [agent.left_y, center_of_mass_y], color=color)
        plt.plot([agent.right_x, center_of_mass_x], [agent.right_y, center_of_mass_y], color=color)

        # Plot 'L' for left foot and an inverted 'L' for right foot
        plt.text(agent.left_x, agent.left_y, 'L', fontsize=8, color=color, ha='center')
        plt.text(agent.right_x, agent.right_y, '\u0315L', fontsize=8, color=color, ha='center')

        # Plot triangle representing agent's direction
        triangle = patches.RegularPolygon((center_of_mass_x, center_of_mass_y), numVertices=3, radius=0.1, orientation=math.radians(agent.agent_direction-90), edgecolor=color, facecolor='none')
        ax.add_patch(triangle)

    plt.xlim([-Agent.S/2 - 1, Agent.S/2 + 1])
    plt.ylim([-Agent.S/2 - 1, Agent.S/2 + 1])
    plt.gca().set_aspect('equal', adjustable='box')

    # Add cardinal directions
    plt.text(0, Agent.S/2 + 0.5, 'North', fontsize=8, color='grey', ha='center')
    plt.text(0, -Agent.S/2 - 0.5, 'South', fontsize=8, color='grey', ha='center')
    plt.text(Agent.S/2 + 0.5, 0, 'East', fontsize=8, color='grey', va='center')
    plt.text(-Agent.S/2 - 0.5, 0, 'West', fontsize=8, color='grey', va='center')

    # Ensure output directory exists
    os.makedirs(os.path.dirname(image_file), exist_ok=True)
    
    # Save the plot
    plt.savefig(image_file, dpi=300)  # increase dpi for a larger image
    plt.close()



def form01(agent):
    try:
        agent.move_left_leg(0.5, 0)
        agent.print_parameters()
        plot_environment_from_top([agent], 'var/image_001')

        agent.move_right_leg(1, 0)
        agent.print_parameters()
        plot_environment_from_top([agent], 'var/image_002')

        agent.rotate_body(90)
        agent.print_parameters()
        plot_environment_from_top([agent], 'var/image_003')

        agent.move_left_leg(-1, 0)
        agent.print_parameters()
        plot_environment_from_top([agent], 'var/image_004')
    except AgentOutOfBounds:
        print("Agent out of bounds!")
    except InvalidLegAngle:
        print("Invalid leg angle!")

def main():
    agent = Agent()
    form01(agent)

if __name__ == "__main__":
    main()
