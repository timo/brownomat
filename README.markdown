Brownomat
=========

This program simulates an asynchronous cellular automaton, that utilises
brownian motion of electron-like signals. It is based on the paper
"Efficient Circuit Construction in Brownian Cellular Automata Based on a
New Building-Block for Delay-Insensitive Circuits" by Lee and Peper.



The Automaton
=============

The Automaton has a von Neumann-Neighbourhood, but replaces its own state
as well as the states of all cells in the neighbourhood. Each cell has a
state of {0, 1, 2}, depicted by white, gray and black in the GUI version or
" ", "#" and "O" in the input and text output respectively. The three rules
R1, R2 and R3 are rotationally symmetric and in every step a random field
will fire.

R1:

    O##  ->  #O#

R2:

     #        #
    O##  ->  ##O
     #        #

R3:

     #        O
    O O  ->  # #
     #        O

The Rules R1, R2 and R3 are referred to in the code as "absorb", "reflect"
and "rotate" respectively.

Labels
------

Additionally to the three states, labels for input and output periphery can
be added to the lines by writing any text starting with a letter, followed
by a combination of letters, digits, ' and ".".

Any label ending in a "." will be considered an output label.

The program will look for the field the label belongs to above, left of,
below and then right of the label.


Invocation
==========

Pygame Frontend
---------------

Running pygamefe.py will start a pygame based UI that displays the
configuration of the automaton and runs it with a given speed.


### Controls

    Spacebar        Pause/Resume
    r               Reset with a random input
    Mouse up/down   Faster/Slower

Closing the window quits the program.

Headless Frontend
-----------------

Running field.py will run a million steps on a configuration, resetting the
automaton to a random input every time as many output labels have been hit
as there have been input signals.

At the end it will output the average number of steps needed for each input
to generate a complete output and the number of rounds that have been
completed with a million steps.

Hitting ctrl-c will cause the simulation to end and the current
configuration to be printed.
