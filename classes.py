from exceptions import Parsing_error
import re
import webcolors


class Zone():
    """Represents a zone in the drone network.

    A zone is a node in the graph with coordinates, type, color, and capacity.
    Zones can be start, end, or regular hubs with different movement costs.

    Attributes:
        name (str): Unique identifier for the zone.
        is_start (bool): True if this is the start zone.
        is_end (bool): True if this is the end zone.
        x (int): X-coordinate of the zone.
        y (int): Y-coordinate of the zone.
        attributes (str): Raw metadata string from the map file.
        zone_type (str): Type of zone (normal, restricted, priority, blocked).
        color (str | None): Visual color for terminal output.
        cost (int): Movement cost in turns (1 for normal, 2 for restricted).
        algo_cost (float): Cost used for pathfinding (priority zones get 0.9).
        max_drones (int): Maximum drones that can occupy this zone.
        connected_to (list[Zone]): List of adjacent zones (bidirectional).
    """
    def __init__(
        self,
        name: str,
        is_start: bool,
        is_end: bool,
        x: int,
        y: int,
        attributes: str,
    ) -> None:
        """Initialize a Zone instance.

        Args:
            name: Unique identifier for the zone.
            is_start: True if this is the start zone.
            is_end: True if this is the end zone.
            x: X-coordinate of the zone.
            y: Y-coordinate of the zone.
            attributes: Raw metadata string from the map file.
        """
        self.name = name
        self.is_start = is_start
        self.is_end = is_end
        self.x = x
        self.y = y
        self.attributes = attributes
        self.zone_type = "normal"
        self.color: str | None = None
        self.cost = 1
        self.algo_cost: float = 1.0
        self.max_drones = 1
        self.connected_to: list[Zone] = []

    def set_data(self, l_dx: int, number_of_drones: int) -> None:
        """Parse and validate zone metadata from the map file.

        Extracts and validates zone type, color, and max_drones from the
        attributes string. Raises Parsing_error for invalid metadata.

        Args:
            l_dx: Line number in the map file (for error reporting).
            number_of_drones: Total drones for start/end zone capacity override.

        Raises:
            Parsing_error: If metadata is invalid, duplicated, or unknown.
        """
        valid_zone_types = ["normal", "restricted", "priority", "blocked"]
        if self.attributes:
            splitted = (self.attributes).split()
            color_catched = False
            zone_type_catched = False
            max_drones_catched = False
            for i in splitted:
                attr_pattern = re.compile(r'^([a-z_]+)=([^=\s]+)$')
                valid_attribute = attr_pattern.match(i)
                if not valid_attribute:
                    msg = f"Not a valid metadata for zone, line {l_dx}"
                    raise Parsing_error(msg)
                key, val = valid_attribute.group(1), valid_attribute.group(2)
                if key == "color":
                    if color_catched:
                        raise Parsing_error(f"Duplicated meta data, line: {l_dx}")
                    if val == "rainbow":
                        self.color = val.lower()
                    else:
                        try:
                            webcolors.name_to_rgb(val)
                        except ValueError:
                            msg = f"{val} is not a valid color, line {l_dx}"
                            raise Parsing_error(msg)
                        self.color = val.lower()
                    color_catched = True
                elif key == "zone":
                    if zone_type_catched:
                        raise Parsing_error(f"Duplicated meta data, line: {l_dx}")
                    if val.lower() not in valid_zone_types:
                        msg = f"{val} is not a valid zone type, line {l_dx}"
                        raise Parsing_error(msg)
                    self.zone_type = val
                    if val == "restricted":
                        self.cost = 2
                        self.algo_cost = 2
                    elif val == "priority":
                        self.cost = 1
                        self.algo_cost = 0.9
                    elif val == "normal":
                        self.cost = 1
                        self.algo_cost = 1
                    elif val == "blocked":
                        pass
                    else:
                        raise Parsing_error(f"Unknown zone type, line {l_dx}")
                    zone_type_catched = True
                elif key == "max_drones":
                    if max_drones_catched:
                        raise Parsing_error(f"Duplicated meta data, line: {l_dx}")
                    try:
                        max_drones = int(val)
                        if self.is_start or self.is_end:
                            self.max_drones = number_of_drones
                        elif max_drones < 1:
                            msg = f"No drones provided, line: {l_dx}"
                            raise Parsing_error(msg)
                        else:
                            self.max_drones = max_drones
                    except ValueError:
                        msg = f"{val} is not a valid number, line: {l_dx}"
                        raise Parsing_error(msg)
                    max_drones_catched = True
                else:
                    raise Parsing_error(f"Unknown meta data, line: {l_dx}")
                if self.is_start or self.is_end:
                    self.max_drones = number_of_drones
        else:
            self.color = None
            self.zone_type = "normal"
            if self.is_start or self.is_end:
                self.max_drones = number_of_drones

    def get_dict(self) -> dict:
        """Convert Zone to a dictionary representation.

        Returns:
            dict: Zone data with name, coordinates, type, color, capacity,
                costs, connected zone names.
        """
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
            "algo_cost": self.algo_cost,
            "connected_to": [z.name for z in self.connected_to],
        }


class Conncetion():
    """Represents a bidirectional connection between two zones.

    Connections allow drones to move between zones. Each connection has a
    maximum capacity for simultaneous traversal.

    Attributes:
        zone_from (Zone): The source zone.
        zone_to (Zone): The destination zone.
        attributes (str): Raw metadata string from the map file.
        max_link_capacity (int): Maximum drones traversing simultaneously.
    """
    def __init__(self, zone_from: Zone, zone_to: Zone, attributes: str):
        """Initialize a Connection instance.

        Args:
            zone_from: The source zone.
            zone_to: The destination zone.
            attributes: Raw metadata string from the map file.
        """
        self.zone_from = zone_from
        self.zone_to = zone_to
        self.attributes = attributes
        self.max_link_capacity = 1

    def get_dict(self) -> dict:
        """Convert Connection to a dictionary representation.

        Returns:
            dict: Connection data with source, destination, and capacity.
        """
        return {
            "from": self.zone_from.name,
            "to": self.zone_to.name,
            "max_link_capacity": self.max_link_capacity,
        }


class Drone:
    """Represents a single drone in the simulation.

    Drones have an ID, current position, planned path, and status.
    Status can be: waiting, in_connection, or delivered.

    Attributes:
        id (int): Unique drone identifier.
        current_zone (str | None): Name of the zone the drone is in.
        path (list[str]): List of zones to visit (excluding current).
        status (str): Drone state: "waiting", "in_connection", "delivered".
        next_zone (str | None): Destination zone when in flight.
        current_connection (tuple | None): Connection being traversed.
    """
    def __init__(self, drone_id: int, start_zone: str):
        """Initialize a Drone instance.

        Args:
            drone_id: Unique identifier for the drone.
            start_zone: Name of the zone where the drone starts.
        """
        self.id = drone_id
        self.current_zone: str | None = start_zone
        self.path: list[str] = []
        self.status = "waiting"
        self.next_zone: str | None = None
        self.current_connection: tuple | None = None
