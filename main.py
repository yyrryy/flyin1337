# main.py
import sys
from parser import Parser
from exceptions import Parsing_error, Algo_error
from new_simulationlivecoding import Simulation


def main(filename: str) -> None:
    """Run the drone simulation with the given map file.

    Args:
        filename: Path to the map file containing the drone network.

    Raises:
        FileNotFoundError: If the map file does not exist.
        PermissionError: If the map file cannot be read.
        Algo_error: If pathfinding fails (no path found).
        Parsing_error: If the map file format is invalid.

    Returns:
        None: Exits with status code 0 on success, non-zero on failure.
    """
    try:
        with open(filename) as file:
            file_content = file.readlines()
        parser = Parser()
        parser.parse_data(file_content)
        data = parser.get_dict()
        start_zone = next(i["name"] for i in data["zones"] if i["is_start"])
        end_zone = next(i["name"] for i in data["zones"] if i["is_end"])
        sim = Simulation(
            data["nb_drones"],
            data["zones"],
            data["connections"],
            start_zone,
            end_zone
        )
        sim.run()
    except FileNotFoundError:
        print(f"File error: {filename} not found", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"File error: enable to read {filename}", file=sys.stderr)
        sys.exit(1)
    except Algo_error as e:
        print(f"Algorithm Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Parsing_error as e:
        print(f"Parse Error: {e}", file=sys.stderr)
        sys.exit(1)
    except (Exception, KeyboardInterrupt) as e:
        print(f"Unexpected error {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <map_file>", file=sys.stderr)
        sys.exit(1)
    map_file = sys.argv[1]
    main(map_file)
