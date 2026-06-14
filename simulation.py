from classes import Drone, DroneStatus
from algorithm import Path_finder


class Simulation():
    def __init__(self, nb_drones: int, zones: list[dict], connections: list[dict], start_zone: str, end_zone: str):
        self.nb_drones = nb_drones
        self.zones = zones
        self.connections = connections
        self.start_zone = start_zone
        self.end_zone = end_zone
        self.drones = []
        self.turn = 0
        self.drones_in_zone = {z["name"]: [] for z in zones}
        self.drones_in_connection = {(c["from"], c["to"]): [] for c in connections}

    def create_drones(self) -> list[Drone]:
        drones = [Drone(i + 1, self.start_zone) for i in range(self.nb_drones)]
        self.drones = drones
        self.drones_in_zone[self.start_zone] = [d.id for d in drones]

    def assign_paths(self) -> None:
        for i in self.drones:
            pathfinder = Path_finder(self.zones, self.connections)
            all_paths = pathfinder.find_all_paths(self.start_zone,
                                                  self.end_zone,
                                                  paths_needed=self.nb_drones)
            if len(all_paths) == 0:
                raise ValueError("No path found in this graph")
            for i, drone in enumerate(self.drones):
                path_index = i % len(all_paths)  # ← round-robin
                full_path = all_paths[path_index]
                drone.path = full_path[1:] if len(full_path) > 1 else []

    def run(self) -> None:
        self.create_drones()
        self.assign_paths()
        while not all(drone.status == DroneStatus.DELIVERED
                      for drone in self.drones):
            self.turn += 1
            self.process_turn()

    def process_turn(self) -> None:
        movements_this_turn = []
        
        # STEP 1: Process arriving drones (MOVING → WAITING)
        for drone in self.drones:
            if drone.status == DroneStatus.MOVING:
                # Decrement counter
                drone.turns_remaining -= 1
                
                if drone.turns_remaining == 0:
                    # ARRIVAL at restricted zone - SILENT (no output)
                    target = drone.target_zone
                    
                    # Check if destination has capacity? PDF says: "Cannot wait on connection"
                    # So capacity must have been checked BEFORE starting the move
                    
                    # Add to zone
                    self.drones_in_zone[target].append(drone.id)
                    drone.current_zone = target
                    drone.status = DroneStatus.WAITING
                    
                    # Remove from path (the zone we just arrived at)
                    if drone.path and drone.path[0] == target:
                        drone.path.pop(0)
                    
                    # Remove from connection tracking
                    conn_key = (drone.current_connection[0], drone.current_connection[1])
                    if drone.id in self.drones_in_connection.get(conn_key, []):
                        self.drones_in_connection[conn_key].remove(drone.id)
                    
                    # Check if delivered
                    if target == self.end_zone:
                        drone.status = DroneStatus.DELIVERED
                        self.drones_in_zone[target].remove(drone.id)
                
                # MOVING drones cannot move again this turn, so skip the rest of the loop
                continue
            
            # STEP 2: Process WAITING drones that want to move
            if drone.status == DroneStatus.WAITING and drone.path:
                current_zone = drone.current_zone
                next_zone = drone.path[0]
                
                if self.can_move(drone, current_zone, next_zone):
                    movements_this_turn.append(self.move_drone(drone, current_zone, next_zone))
        
        # STEP 3: Output
        if movements_this_turn:
            print(*movements_this_turn)

    def can_move(self, drone: Drone, from_zone: str, to_zone: str) -> bool:
        connection = next((c for c in self.connections
                           if (c["from"] == from_zone
                               and c["to"] == to_zone)), None)
        max_conn_capacity = connection["max_link_capacity"]
        to_zone_instence = next(z for z in self.zones if z["name"] == to_zone)
        max_drones_in_next_zone = to_zone_instence["max_drones"]
        drones_in_next_zone = len(self.drones_in_zone[to_zone])
        drones_in_connection = len(self.drones_in_connection[(from_zone,
                                                              to_zone)])
        if drones_in_connection == max_conn_capacity:
            return False
        if not to_zone_instence['is_end']:
            if drones_in_next_zone == max_drones_in_next_zone:
                return False
        return True

    def move_drone(self, drone: Drone, from_zone: str, to_zone: str) -> str:
        to_zone_instence = next(z for z in self.zones if z["name"] == to_zone)
        if to_zone_instence['zone_type'] == 'restricted':
            drone.status = DroneStatus.MOVING
            drone.turns_remaining = 1
            drone.target_zone = to_zone
            drone.current_connection = (from_zone, to_zone)  # ← ADD THIS
            self.drones_in_connection[(from_zone, to_zone)].append(drone.id)
            # Don't pop path yet! Keep it for arrival
            return f"D{drone.id}-{from_zone}-{to_zone}"
        drone.current_zone = to_zone
        drone.path.pop(0)
        self.drones_in_zone[from_zone].remove(drone.id)
        self.drones_in_zone[to_zone].append(drone.id)
        if drone.id in self.drones_in_connection[(from_zone, to_zone)]:
            self.drones_in_connection[(from_zone, to_zone)].remove(drone.id)
        if to_zone == self.end_zone:
            drone.status = DroneStatus.DELIVERED
        return f"D{drone.id}-{to_zone}"
