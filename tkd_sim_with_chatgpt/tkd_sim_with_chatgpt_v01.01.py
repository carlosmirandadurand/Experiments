
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

# Please write a new version of function plot_environment_from_top with the following changes:
# - Instead of plotting an L and an inverted L for the feet, please plot two arrows.
# - The base of each arrow should match exactly the end of the respective leg.   
# - Both arrows should have length 25 cm and point in the same direction that the agent is facing.
# - In other words, we should see the triangle and the two feel always pointing in the same direction (in the same direction that the agent is facing.)

# A: You're right. Adding arrows to represent the feet could make the visualization clearer and more aligned with the direction that the agent is facing. Here is the updated function:

#--------------------------------------------------------------------------------------------------

# Please add a plot at the begining of form01, to show the initial status, before any movement takes place, and name that file 'var/image_000'.

# Please also check the program to make sure that everything is correct.  
# - The initial direction of the agent should be south, so the triangle and the arrows should point down.  
# - The first two moves are in the forward direction for the agent, so we should see the agent moving down in the plot (in the south direction.)

# Feel free to rewrite the entire program, if this is needed to fix the issue.

# A: Thanks for your patience. Based on your instructions, I've modified the existing code to create an initial plot (image_000) before any movement occurs. I've also ensured that the initial direction of the agent is facing south and that forward movement results in the agent moving towards the south in the plots.
# Here is the modified program:

#--------------------------------------------------------------------------------------------------

# No, this version of the program has not corrected the problem.

# For one, you have been confusing the "direction that the agent is facing" with the "angle between the legs". 
# - Both are angles indeed, but the "direction that the agent is facing" is an angle in the horizontal plane and the "angle between the legs" is an angle in the vertical plane.
# - Remember from the initial instructions that the surface is flat (two-dimensional) but the agent is three-dimensional. 
# - The "angle between the legs" should be calculated based on the position of each foot and the length of the legs "L".
# - The "direction that the agent is facing" control the movement of the legs of the agent.    
# - The MIN_LEG_ANGLE and MAX_LEG_ANGLE limits apply only to the "angle between the legs".  What these limits try to ensure is that the agent does not move a foot so far away from the other foot that it would leave its body stretched too far or stretched unrealistcally.     

# For two, the same issues that I mentioned in the previous message still exist:
# - The initial direction of the agent should be south, so the triangle and the arrows should point down.  
# - The first two moves are in the forward direction for the agent, so we should see the agent moving down in the plot (in the south direction.)
# - Only if the third move the agent is changing directions. 

# Feel free to rewrite the entire program, if this is needed to meet the requirements.

# Answer from ChatGPT: I apologize for misunderstanding your request, and thank you for your patience. Let's go over the requirements again to ensure that I understand them correctly:
# The agent's direction refers to the direction that the agent is facing in the horizontal plane, i.e., it determines the direction that the agent will move when it takes a step forward. This direction is independent of the relative position of the agent's feet. It is determined by the orientation of the agent's body.
# The angle between the legs is a measure in the vertical plane, determined by the position of each foot relative to the agent's center of mass and the length of the legs.
# The constraints MIN_LEG_ANGLE and MAX_LEG_ANGLE apply to the angle between the legs, not the direction that the agent is facing. The goal of these constraints is to prevent the agent from moving a foot too far away from the other foot, thereby maintaining a reasonable and realistic body posture.
# The agent starts facing south, so the initial plot should show the agent's triangle and the arrows pointing down (towards the south).
# The first two steps are forward movements, so the agent should move towards the south on the plot.
# Let's implement these changes:

#--------------------------------------------------------------------------------------------------

# No, this program is not correcting the issue.  Lets simplify the requirements.  
# - Please write this program again without calculating the "angle between the legs" and without using the MIN_LEG_ANGLE & MAX_LEG_ANGLE constraints. 
# - Please do implement the methods rotate_body(r), move_left_leg(forward_distance, side_distance) and move_right_leg(forward_distance, side_distance) to execute all the movements of the agent across the horizontal flat surface. 
# - Please make sure that the initial position of the agent is centered, facing south, with legs together. 
# - The InvalidLegAngle exception would not exist anymore but the "Agent Out Of Bounds" exceptions will

#--------------------------------------------------------------------------------------------------

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon


class Agent:
    S = 10
    L = 0.85

    def __init__(self):
        self.direction = 180  # facing south
        self.left_x = self.right_x = self.center_x = 0
        self.left_y = self.right_y = self.center_y = 0

    def rotate_body(self, r):
        self.direction = (self.direction + r) % 360

    def move_left_leg(self, forward_distance, side_distance):
        self._move_leg(forward_distance, side_distance, True)

    def move_right_leg(self, forward_distance, side_distance):
        self._move_leg(forward_distance, side_distance, False)

    def _move_leg(self, forward_distance, side_distance, is_left):
        # Calculate delta_x and delta_y based on direction
        delta_x = forward_distance * np.sin(np.radians(self.direction))
        delta_y = forward_distance * np.cos(np.radians(self.direction))
        if is_left:
            delta_x -= side_distance * np.cos(np.radians(self.direction))
            delta_y += side_distance * np.sin(np.radians(self.direction))
        else:
            delta_x += side_distance * np.cos(np.radians(self.direction))
            delta_y -= side_distance * np.sin(np.radians(self.direction))

        # Update leg position
        if is_left:
            self.left_x += delta_x
            self.left_y += delta_y
        else:
            self.right_x += delta_x
            self.right_y += delta_y

        # Update center of mass
        self.center_x = (self.left_x + self.right_x) / 2
        self.center_y = (self.left_y + self.right_y) / 2

        # Check if agent is out of bounds
        if not (-self.S/2 <= self.center_x <= self.S/2 and -self.S/2 <= self.center_y <= self.S/2):
            raise Exception("Agent Out Of Bounds")


def plot_environment_from_top(agent, filename):
    # Create figure and axes
    fig, ax = plt.subplots(figsize=(15, 15))

    # Plot agent
    head = (agent.center_x, agent.center_y)
    foot_left = (agent.left_x, agent.left_y)
    foot_right = (agent.right_x, agent.right_y)
    arrow = Polygon([head, foot_left, foot_right], closed=False)
    ax.add_patch(arrow)

    # Plot flat surface
    ax.set_xlim([-agent.S/2, agent.S/2])
    ax.set_ylim([-agent.S/2, agent.S/2])
    ax.grid(True)

    # Add cardinal directions
    ax.text(0, agent.S/2, 'N', ha='center', va='bottom', fontsize=8, color='grey')
    ax.text(0, -agent.S/2, 'S', ha='center', va='top', fontsize=8, color='grey')
    ax.text(agent.S/2, 0, 'E', ha='right', va='center', fontsize=8, color='grey')
    ax.text(-agent.S/2, 0, 'W', ha='left', va='center', fontsize=8, color='grey')

    # Ensure output directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Save the figure
    plt.savefig(filename, dpi=300)
    plt.close()


def form01(agent):
    plot_environment_from_top(agent, 'var/image_000.png')

    agent.move_left_leg(0.5, 0)
    plot_environment_from_top(agent, 'var/image_001.png')

    agent.move_right_leg(1, 0)
    plot_environment_from_top(agent, 'var/image_002.png')

    agent.rotate_body(-90)
    plot_environment_from_top(agent, 'var/image_003.png')

    agent.move_left_leg(-1, 0)
    plot_environment_from_top(agent, 'var/image_004.png')


def main():
    agent = Agent()
    form01(agent)


if __name__ == "__main__":
    main()
