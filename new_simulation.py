from algorithm import Path_finder
from rich import print
class Drone:
    def __init__(self, drone_id: int, start_zone: str):
        self.id = drone_id
        self.current_zone = start_zone
        self.path = []              # Zones to visit (excluding current)
        self.status = "waiting"     # waiting, flying, delivered
        self.next_zone = None   # For flying: destination zone
        self.current_connection = None  # For flying: connection name for output
class Simulation:
    def __init__(self, nb_drones, zones, connections, start_zone, end_zone):
        self.nb_drones = nb_drones
        self.zones = {z["name"]: z for z in zones}
        self.connections = {(c["from"], c["to"]): c for c in connections}
        self.start_zone = start_zone
        self.end_zone = end_zone
        self.drones = []
        self.turn = 0
        # Track current state
        self.drones_in_zone = {name: [] for name in self.zones}
        self.drones_in_conn = {(c["from"], c["to"]): 0 for c in connections}
        # Create drones
        for i in range(nb_drones):
            self.drones.append(Drone(i + 1, start_zone))
        self.drones_in_zone[start_zone] = list(range(1, nb_drones + 1))

    def assign_paths(self):
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

    def run(self):
        self.assign_paths()
        while not self.all_delivered():
            self.turn += 1
            self.process_turn()
        print(f"\nSimulation finished in {self.turn} turns")

    def print_with_colors(self, movement):
        pass

    def process_turn(self):
        # Reset connection usage for this turn
        for key in self.drones_in_conn:
            self.drones_in_conn[key] = 0
        
        # STEP 1: Arrivals (flying drones land)
        for drone in self.drones:
            # handle the case of the flying drone, means droen is in conn
            if drone.status == "flying":
                # Arrive at destination (SILENT - no output)
                self.drones_in_zone[drone.next_zone].append(drone.id)
                drone.current_zone = drone.next_zone
                drone.status = "waiting"
                # Remove from path (the zone we just arrived at)
                if drone.path and drone.path[0] == drone.next_zone:
                    drone.path.pop(0)
                # Clear flying info
                drone.next_zone = None
                drone.current_connection = None
        
        # STEP 2: Collect and execute movements
        movements = []

        for drone in self.drones:
            if drone.status != "waiting":
                continue
            if not drone.path:
                continue
            from_zone = drone.current_zone
            to_zone = drone.path[0]
            from_zone_instznce = self.zones[to_zone]
            conn_key = (from_zone, to_zone)
            conn_instance = self.connections.get(conn_key)

            if not conn_instance:
                continue

            # Check connection capacity
            if self.drones_in_conn[conn_key] >= conn_instance["max_link_capacity"]:
                continue  # Connection busy, drone waits

            # Check zone capacity (end zone has no limit)
            if to_zone != self.end_zone:
                if len(self.drones_in_zone[to_zone]) >= from_zone_instznce["max_drones"]:
                    continue  # Zone full, drone waits
            # ALL CHECKS PASSED - DRONE CAN MOVE
            self.drones_in_conn[conn_key] += 1
            # Remove from current zone
            self.drones_in_zone[from_zone].remove(drone.id)
            # Handle different zone types
            if from_zone_instznce["zone_type"] == "restricted":
                # 2-turn movement
                drone.status = "flying"
                drone.next_zone = to_zone
                drone.current_connection = f"{from_zone}-{to_zone}"
                movements.append(f"D{drone.id}-{drone.current_connection}")
            else:
                # Normal or priority - immediate arrival
                self.drones_in_zone[to_zone].append(drone.id)
                drone.current_zone = to_zone
                drone.path.pop(0)
                movements.append(f"D{drone.id}-{to_zone}")
                # Check if delivered
                if to_zone == self.end_zone:
                    drone.status = "delivered"
                    #self.drones_in_zone[to_zone].remove(drone.id)
        
        # STEP 3: Output
        if movements:
            for i in movements:


    def all_delivered(self):
        return all(d.status == "delivered" for d in self.drones)