from algorithm import Path_finder
from classes import Drone
import webcolors
from rich import print


class Simulation:
    def __init__(
        self,
        nb_drones: int,
        zones: dict,
        connections: dict,
        start_zone: str,
        end_zone: str
    ):
        self.nb_drones = nb_drones
        self.zones = {z["name"]: z for z in zones}
        self.connections: dict[tuple[str | None, str], dict] = {
            (c["from"], c["to"]): c for c in connections
        }
        self.start_zone = start_zone
        self.end_zone = end_zone
        self.drones = []
        self.turn = 0
        self.drones_in_zone: dict = {name: 0 for name in self.zones}
        self.drones_in_conn: dict = {(c["from"], c["to"]): 0 for c in connections}
        for i in range(nb_drones):
            self.drones.append(Drone(i + 1, start_zone))
        self.drones_in_zone[start_zone] = nb_drones

    def assign_paths(self) -> None:
        pathfinder = Path_finder(
            list(self.zones.values()),
            list(self.connections.values())
        )
        best_paths = pathfinder.find_all_paths(
            self.start_zone,
            self.end_zone,
            paths_needed=self.nb_drones
        )
        # if not all_paths:
        #     raise ValueError("No path found")
        # best_paths = all_paths[:2]
        # print('best_paths', best_paths)
        for i, drone in enumerate(self.drones):
            path = best_paths[i % len(best_paths)]
            drone.path = path[1:]

    def run(self) -> None:
        self.assign_paths()
        while not self.all_delivered():
            self.turn += 1
            self.process_turn()
        print(f"\nSimulation finished in {self.turn} turns")

    def print_with_colors(self, movement: str) -> str:
        def print_rainbow(text: str) -> str:
            colors = [
                "red", "orange1", "yellow", "green", "blue", "indigo", "violet"
            ]
            colored_text = ""
            for i, char in enumerate(text):
                color = colors[i % len(colors)]
                colored_text += f"[{color}]{char}[/]"
            return colored_text
        parts = movement.split('-')
        if len(parts) == 2:
            drone, zone = parts
            zone_color = self.zones[zone]["color"]
            if zone_color is None:
                return movement
            if zone_color == "rainbow":
                return f"{drone}-{print_rainbow(zone)}"
            hex_color = webcolors.name_to_hex(zone_color)
            return (f"{drone}-[{hex_color}]{zone}[/]")
        else:
            drone, zone_from, zone_to = parts
            zone_from_color = self.zones[zone_from]["color"]
            zone_to_color = self.zones[zone_to]["color"]
            if zone_from_color is None:
                output_of_zone_from = zone_from
            elif zone_from_color == "rainbow":
                output_of_zone_from = print_rainbow(zone_from)
            else:
                hex_color_from = webcolors.name_to_hex(zone_from_color)
                output_of_zone_from = f'[{hex_color_from}]{zone_from}[/]'
            if zone_to_color is None:
                output_of_zone_to = zone_to
            elif zone_to_color == "rainbow":
                output_of_zone_to = print_rainbow(zone_to)
            else:
                hex_color_to = webcolors.name_to_hex(zone_to_color)
                output_of_zone_to = f'[{hex_color_to}]{zone_to}[/]'
            return (f"{drone}-{output_of_zone_from}-{output_of_zone_to}")

    def process_turn(self) -> None:
        # Reset connection usage for this turn
        for key in self.drones_in_conn:
            self.drones_in_conn[key] = 0
        movements = []
        for drone in self.drones:
            # handle the flying drones first
            if drone.status == "in_connection":
                to_zone_instence = self.zones[drone.next_zone]
                # if drone.next_zone != self.end_zone:
                # if (
                #     self.drones_in_zone[drone.next_zone]
                #     >= to_zone_instence["max_drones"]
                # ):
                #     continue
                if drone.current_connection is None:
                    continue
                conn_instance_ = (
                    self.connections.get(drone.current_connection)
                )
                if conn_instance_ is None:
                    continue
                if conn_instance_:
                    if self.drones_in_conn[drone.current_connection] > 0:
                        self.drones_in_conn[drone.current_connection] -= 1
                drone.current_zone = drone.next_zone
                if drone.current_zone == self.end_zone:
                    drone.status = "delivered"
                else:
                    drone.status = "waiting"
                movements.append(f"D{drone.id}-{drone.next_zone}")
                # remove from path (the zone we just arrived at)
                if drone.path and drone.path[0] == drone.next_zone:
                    drone.path.pop(0)
                drone.next_zone = None
                drone.current_connection = None
                continue
            if drone.status == "delivered":
                continue
            if not drone.path:
                continue
            from_zone: str | None = drone.current_zone
            to_zone: str = drone.path[0]
            to_zone_instence = self.zones[to_zone]
            conn_key = (from_zone, to_zone)
            conn_instance: dict | None = self.connections.get(conn_key)
            if conn_instance is None:
                continue
            if (
                self.drones_in_conn[conn_key] >=
                conn_instance["max_link_capacity"]
            ):
                continue
            if to_zone != self.end_zone:
                if (
                    self.drones_in_zone[to_zone] >=
                    to_zone_instence["max_drones"]
                ):
                    continue
            # handle the next zone is restricted
            if to_zone_instence["zone_type"] == "restricted":
                if to_zone != self.end_zone:
                    if (
                        self.drones_in_zone[to_zone] >=
                        to_zone_instence["max_drones"]
                    ):
                        continue
                drone.status = "in_connection"
                self.drones_in_conn[conn_key] += 1
                self.drones_in_zone[to_zone] += 1
                self.drones_in_zone[from_zone] -= 1
                drone.next_zone = to_zone
                drone.current_connection = conn_key
                movements.append(f"D{drone.id}-{from_zone}-{to_zone}")
            else:
                # Normal or priority - immediate arrival
                self.drones_in_zone[from_zone] -= 1
                self.drones_in_zone[to_zone] += 1
                drone.current_zone = to_zone
                drone.path.pop(0)
                movements.append(f"D{drone.id}-{to_zone}")
                # Check if delivered
                if to_zone == self.end_zone:
                    drone.status = "delivered"
        if movements:
            colored_movements = [
                self.print_with_colors(movement)
                for movement in movements
            ]
            print(' '.join(colored_movements))

    def all_delivered(self) -> bool:
        return all(d.status == "delivered" for d in self.drones)
