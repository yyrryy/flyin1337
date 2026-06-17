from exceptions import Parsing_error
import re
import webcolors
from typing import Optional, Literal
from dataclasses import dataclass
from enum import Enum


class Zone():
    def __init__(
        self,
        name: str,
        is_start: bool,
        is_end: bool,
        x: int,
        y: int,
        attributes: str,
    ) -> None:
        self.name = name
        self.is_start = is_start
        self.is_end = is_end
        self.x = x
        self.y = y
        self.attributes = attributes
        self.zone_type = "normal"
        self.color = None
        self.cost = 1
        self.max_drones = 1
        self.connected_to = []
        self.data = {
            "name": self.name,
            "cost": self.cost,
            "x": self.x,
            "y": self.y,
            "connected_to": self.connected_to
        }

    def set_data(self, l_dx, number_of_drones):
        # we need number of drones to make sure start and end well accept them
        valid_zone_types = ["normal", "restricted", "priority", "blocked"]
        if self.attributes:
            splitted = (self.attributes).split()
            for i in splitted:
                attr_pattern = re.compile(r'^([a-z_]+)=([^=\s]+)$')
                valid_attribute = attr_pattern.match(i)
                if not valid_attribute:
                    raise Parsing_error(f"Not a valid attribute, line {l_dx}")
                key, val = valid_attribute.group(1), valid_attribute.group(2)
                if key == "color":
                    if val == "rainbow":
                        self.color = val.lower()
                    else:
                        try:
                            webcolors.name_to_rgb(val)
                        except ValueError:
                            raise Parsing_error(f"{val} is not a valid color, line {l_dx}")
                        self.color = val.lower()

                elif key == "zone":
                    if val.lower() not in valid_zone_types:
                        raise Parsing_error(f"{val} is not a valid zone type, line {l_dx}")
                    self.zone_type = val
                    if val == "restricted":
                        self.cost = 2
                    elif val == "blocked":
                        self.cost = 0
                elif key == "max_drones":
                    try:
                        max_drones = int(val)
                        if max_drones < 1:
                            raise Parsing_error(f"max_drones must be at least 1, line: {l_dx}")
                        # if self.is_start and max_drones < number_of_drones:
                        #     raise Parsing_error(f"start zone must accept all drones, line: {l_dx}")
                        # if self.is_end and max_drones < number_of_drones:
                        #     raise Parsing_error(f"end zone must accept all drones, line: {l_dx}")
                        if self.is_start or self.is_end:
                            self.max_drones = number_of_drones
                        else:
                            self.max_drones = max_drones
                    except ValueError:
                        raise Parsing_error(f"{val} is not a valid number, line: {l_dx}")       
                if self.is_start or self.is_end:
                    self.max_drones = number_of_drones
        else:
            # if self.is_start:
            #     raise Parsing_error(f"start zone must accept all drones, line: {l_dx}")
            # if self.is_end:
            #     raise Parsing_error(f"end zone must accept all drones, line: {l_dx}")
            self.color = None
            self.zone_type = "normal"
            if self.is_start or self.is_end:
                self.max_drones = number_of_drones

    def get_dict(self) -> dict:
        return {
            "name": self.name,
            "is_start": self.is_start,
            "is_end": self.is_end,
            "x": self.x,
            "y": self.y,
            "zone_type": self.zone_type,
            "color": self.color,
            "max_drones": self.max_drones,
            "cost": self.cost,
            "connected_to": [z.name for z in self.connected_to],
        }
 

class Conncetion():
    def __init__(self, zone_from: Zone, zone_to: Zone, attributes: dict):
        self.zone_from = zone_from
        self.zone_to = zone_to
        self.attributes = attributes
        self.max_link_capacity = 1
        self.data = {}

    def get_dict(self) -> dict:
        return {
            "from": self.zone_from.name,
            "to": self.zone_to.name,
            "max_link_capacity": self.max_link_capacity,
        }

class DroneStatus(Enum):
    WAITING = "waiting"
    MOVING = "moving"
    FINISHED = "finished"  # Added this line
    DELIVERED = "delivered"  # Keep for backward compatibility


class Drone:
    def __init__(self, drone_id: int, start_zone: str):
        self.id = drone_id
        self.current_zone = start_zone
        self.path = []              # List of zones to visit (excluding current)
        self.status = DroneStatus.WAITING     # "waiting", "flying", "delivered"
        self.target_zone = None     # For flying: where drone is going
        self.turns_remaining = 0    # For flying: turns until arrival


class ZoneState:
    """Tracks dynamic state of a zone during simulation."""

    def __init__(self, zone_data: dict):
        self.name = zone_data["name"]
        self.max_drones = zone_data["max_drones"]
        self.zone_type = zone_data["zone_type"]
        self.current_drones: list[int] = []  # Drone IDs currently in zone
        self.incoming_drones: list[int] = []  # Drones arriving this turn

    def can_enter(self, drone_id: int) -> bool:
        """Check if a drone can enter this zone."""
        if self.zone_type == "blocked":
            return False
        occupied = len(self.current_drones) + len(self.incoming_drones)
        return occupied < self.max_drones

    def add_incoming(self, drone_id: int) -> None:
        """Schedule a drone to arrive this turn."""
        self.incoming_drones.append(drone_id)

    def commit_arrivals(self) -> None:
        """Move incoming drones to current."""
        self.current_drones.extend(self.incoming_drones)
        self.incoming_drones.clear()

    def remove_drone(self, drone_id: int) -> None:
        """Remove a drone that is leaving."""
        if drone_id in self.current_drones:
            self.current_drones.remove(drone_id)


class ConnectionState:
    """Tracks dynamic state of a connection during simulation."""

    def __init__(self, from_zone: str, to_zone: str, max_capacity: int):
        self.from_zone = from_zone
        self.to_zone = to_zone
        self.max_capacity = max_capacity
        self.current_usage: int = 0  # Drones currently traversing
        self.reserved_for_next: list[int] = []  # Drones that will start traversing

    def can_traverse(self, drone_id: int) -> bool:
        """Check if a drone can start traversing this connection."""
        return self.current_usage + len(self.reserved_for_next) < self.max_capacity

    def reserve(self, drone_id: int) -> None:
        """Reserve the connection for a drone starting this turn."""
        self.reserved_for_next.append(drone_id)

    def commit_reservations(self) -> None:
        """Move reservations to current usage."""
        self.current_usage += len(self.reserved_for_next)
        self.reserved_for_next.clear()

    def release(self, drone_id: int) -> None:
        """Release connection when drone finishes traversing."""
        self.current_usage -= 1