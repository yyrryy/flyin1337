# main.py
import sys
from parser import Parser
from exceptions import Parsing_error, Algo_error
from new_simulation import Simulation


def main(filename: str) -> None:
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
