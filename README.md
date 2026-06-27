*This project has been created as part of the 42 curriculum by aaliali*

## Description

Fly-in Drones is a drone routing simulation system that navigates multiple drones through a network of connected zones. The goal is to move all drones from a central start zone to a target end zone in the fewest possible simulation turns while respecting movement constraints, zone capacities, and connection limits.

The project implements:
- A custom parser for the drone network map format
- Pathfinding algorithms (DFS) for route planning
- A turn-based simulation engine with conflict resolution
- Colored terminal output for visual feedback


## Instructions

- Installing dependencies
    make install
        This installs all project dependencies using uv (Python package manager).

- Running the Simulation
    make run
        Provide map file first.

- Debug Mode
    make debug
        Runs the simulation with Python's built-in debugger (pdb) for step-by-step debugging.

- Cleaning Temporary Files
    make clean
        Removes:
            
            __pycache__ directories

            .mypy_cache

            .pytest_cache

- Code Linting
    make lint
        Runs:

        flake8: Code style checking

        mypy: Static type checking with strict flags




## Resources
- Documentation
    Python 3.10+ Documentation
    UV Package Manager
    Rich Library Documentation
    Webcolors Documentation

- Algorithms & References
    Depth-First Search
    -Python re Module (Regular Expressions)

- AI Usage
    Provide ressources
    Suggest type hints
    Visualize simulation
    Code Review: Identifying edge cases and potential bugs


## Algorithm Description

The system uses **iterative DFS** to find all possible paths from start to end, filtering out blocked zones. Each zone has a movement cost based on its type (normal: 1, priority: 1, restricted: 2). Only paths with the **minimum algo_cost** are returned, ensuring drones always take the shortest routes.

Drones are assigned paths using **round-robin distribution** for load balancing across available routes. The iterative DFS approach avoids recursion limits and works efficiently on maps of any size.

**Why DFS?** It finds ALL needed paths, enabling load balancing across multiple routes. 
**Why cost filtering?** Prevents drones from taking unnecessarily long detours.
**Why round-robin?** Distributes drones evenly across paths to reduce congestion.

### Visual Representation
The simulation provides **colored terminal output** using the `rich` library. Each zone displays in its assigned color from the map file, making it easy to identify zones visually.

**What is displayed:**
- Drone movements with color-coded destination zones
- Zone names in their assigned colors
- Rainbow effect for special zones

**Color handling:**
- Standard colors: red, green, blue, yellow, etc.
- Custom colors: Any valid single-word string
- Rainbow: Special gradient effect

**Why it enhances UX:**
- Instant visual identification of zones
- Clear tracking of drone movements
- Real-time feedback on simulation progress

**Example inputand output:**
- Input: map.txt file:

        nb_drones: 3

        start_hub: start +0 0 [color=green max_drones=+4]
        hub: a 1 0 [color=red max_drones=+6]
        hub: d 1 1 [color=orange max_drones=3 zone=normal]
        end_hub: goal 4 0 [color=red max_drones=1]

        connection: start-a [max_link_capacity=6]
        connection: a-d [max_link_capacity=6]
        connection: d-goal [max_link_capacity=3]

- Outout:

        D1-a D2-a D3-a
        D1-d D2-d D3-d
        D1-goal D2-goal D3-goal
