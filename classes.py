from exceptions import Parsing_error
import re
import webcolors


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
        self.color: str | None = None
        self.cost = 1
        self.algo_cost: float = 1.0
        self.max_drones = 1
        self.connected_to: list[Zone] = []

    def set_data(self, l_dx: int, number_of_drones: int) -> None:
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
    def __init__(self, zone_from: Zone, zone_to: Zone, attributes: str):
        self.zone_from = zone_from
        self.zone_to = zone_to
        self.attributes = attributes
        self.max_link_capacity = 1

    def get_dict(self) -> dict:
        return {
            "from": self.zone_from.name,
            "to": self.zone_to.name,
            "max_link_capacity": self.max_link_capacity,
        }


class Drone:
    def __init__(self, drone_id: int, start_zone: str):
        self.id = drone_id
        self.current_zone: str | None = start_zone
        self.path: list[str] = []
        self.status = "waiting"
        self.next_zone: str | None = None
        self.current_connection: tuple | None = None
