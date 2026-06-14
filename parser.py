import re
from classes import Zone, Conncetion
from exceptions import Parsing_error


class Parser():
    def __init__(self) -> None:
        self.nb_drones = 0
        self.start = (0, 0)
        self.end = (0, 0)
        self.zones = []
        self.connections = []

    def get_dict(self) -> dict:
        return {
            "nb_drones": self.nb_drones,
            "zones": [i.get_dict() for i in self.zones],
            "connections": [i.get_dict() for i in self.connections],
        }

    def parse_data(self, file_content):
        # #if True then it has already parsed else not parsed
        start_flag = False
        end_flag = False
        # flag to track if there is atleast a connection from start 
        start_connection_flag = False
        # flag to track if there is atleast a connection to end 
        end_connection_flag = False
        # l_dx = line index
        for l_dx, line in enumerate(file_content):
            stripped_line = line.strip()
            # Skip empty lines and comments
            if not stripped_line or stripped_line.startswith("#"):
                continue
            l_dx += 1
            # start hub pattern
            # the start flag to  catch the start hub parsing
            nb_drones_pattern = r'^nb_drones:\s+([\d.]+)?'
            start_hub_pattern = r'^start_hub:\s+([\w-]+)\s+([-?\d+]+)\s+([-?\d+]+)(?:\s+\[([^\]]*)\])?'
            end_hub_pattern = r'^end_hub:\s+([\w-]+)\s+([-?\d+]+)\s+([-?\d+]+)(?:\s+\[([^\]]*)\])?'
            hub_pattern = r'^hub:\s+([\w-]+)\s+([-?\d+]+)\s+([-?\d+]+)(?:\s+\[([^\]]*)\])?'
            connection_pattern = r'^connection:\s+([\w-]+)(?:\s+\[([^\]]*)\])?'
            nb_drones_match = re.match(nb_drones_pattern, stripped_line)
            start = re.match(start_hub_pattern, stripped_line)
            end = re.match(end_hub_pattern, stripped_line)
            hub = re.match(hub_pattern, stripped_line)
            connection = re.match(connection_pattern, stripped_line)
            # enforce the first line to be the number of drones
            if l_dx == 1 and not nb_drones_match:
                raise Parsing_error("the first line should be the number of drones")
            # skip empty lines
            if nb_drones_match:
                try:
                    number_of_drones = int(nb_drones_match.group(1))
                except ValueError:
                    raise Parsing_error(f"{number_of_drones} is not a valid number, line: {l_dx}")
                self.nb_drones = number_of_drones
            elif start:
                name = start.group(1)
                if "-" in name or " " in name:
                    raise Parsing_error(f"Zone name cannot contain dashes or spaces, line: {l_dx}")
                if start_flag:
                    message = f"{name} already existed, Error in line {l_dx}"
                    raise Parsing_error(message)
                start_flag = True
                x = int(start.group(2))
                y = int(start.group(3))
                attributes = start.group(4)
                zone = Zone(name, True, False, x, y, attributes)
                zone.set_data(l_dx, number_of_drones)
                self.zones.append(zone)
                self.start = (x, y)
            elif end:
                name = end.group(1)
                if "-" in name or " " in name:
                    raise Parsing_error(f"Zone name cannot contain dashes or spaces, line: {l_dx}")
                if end_flag:
                    message = f"{name} already existed, Error in line {l_dx}"
                    raise Parsing_error(message)
                end_flag = True
                x = int(end.group(2))
                y = int(end.group(3))
                attributes = end.group(4)
                zone = Zone(name, False, True, x, y, attributes)
                zone.set_data(l_dx, number_of_drones)
                self.zones.append(zone)
                self.end = (x, y)
            elif hub:
                name = hub.group(1)
                if "-" in name or " " in name:
                    raise Parsing_error(f"Zone name cannot contain dashes or spaces, line: {l_dx}")
                x = int(hub.group(2))
                y = int(hub.group(3))
                attributes = hub.group(4)
                zone = Zone(name, False, False, x, y, attributes)
                zone.set_data(l_dx, number_of_drones)
                self.zones.append(zone)
            elif connection:
                zones = connection.group(1)
                splitted = zones.split("-")
                if len(splitted) > 2:
                    raise Parsing_error(f"Not valid connection, line: {l_dx}")
                zone_from = splitted[0]
                zone_to = splitted[1]
                attributes = connection.group(2)
                zone_from_instence = next((z for z in self.zones if z.name == zone_from), None)
                if not zone_from_instence:
                    message = f"Zone {zone_from} does not exist, line {l_dx}"
                    raise Parsing_error(message)
                # if there is zone from the proceed with the remain logic
                zone_to_instence = next((z for z in self.zones if z.name == zone_to), None)
                if not zone_to_instence:
                    message = f"Zone {zone_to} does not exist, line {l_dx}"
                    raise Parsing_error(message)
                if zone_to_instence.is_end:
                    end_connection_flag = True
                if zone_from_instence.is_start:
                    start_connection_flag = True
                cretaed_connections = self.create_connection(
                    zone_from_instence,
                    zone_to_instence,
                    attributes,
                    l_dx
                )
                self.connections.append(cretaed_connections)
            else:
                raise Parsing_error(f"Unkown data, line: {l_dx}")
        if not start_flag:
            raise Parsing_error("start hub does not exist")
        if not end_flag:
            raise Parsing_error("end hub does not exist")
        if not start_connection_flag:
            raise Parsing_error("there is no connection from the start zone")
        if not end_connection_flag:
            raise Parsing_error("there is no connection to the end zone")

    def create_connection(
        self,
        zone_from_instence: Zone,
        zone_to_instence: Zone,
        attributes: str,
        l_dx
    ) -> Conncetion:
        # start -> zone1
        # zone1 -> start
        # tow_ways_duplicate = next(
        #     (connection for connection in self.connections if (connection.zone_from == zone_to_instence and connection.zone_to == zone_from_instence)),
        #     None
        # )
        # start -> zone1
        # start -> zone1
        one_ways_duplicate = next(
            (connection for connection in self.connections if (connection.zone_from == zone_from_instence and connection.zone_to == zone_to_instence)),
            None
        )
        # if tow_ways_duplicate:
        #     raise Parsing_error(f"Duplicate connection between {zone_from_instence.name} and {zone_to_instence.name}, line {l_dx}")
        if one_ways_duplicate:
            raise Parsing_error(f"the connection between {zone_from_instence.name} and {zone_to_instence.name} already exist, line {l_dx}")
        # else means there is zone from and zone to
        else:
            zone_from_instence.connected_to.append(zone_to_instence)
            # bidirectional connection
            # zone_to_instence.connected_to.append(zone_from_instence)
            connection_instence = Conncetion(zone_from_instence, zone_to_instence, attributes)
            # connection_instence.data[""]
            if attributes:
                attr_pattern = re.compile(r'(\w+)=([^=\s\]]+)')
                valid_attribute = attr_pattern.match(attributes)
                if not valid_attribute:
                    raise Parsing_error(f"Not a valid attribute, line {l_dx}")
                key, val = valid_attribute.group(1), valid_attribute.group(2)
                if key == "max_link_capacity":
                    try:
                        capacity = int(val)
                        if capacity < 1:
                            raise Parsing_error(f"max_link_capacity must be a positive integer, line {l_dx}")
                        connection_instence.max_link_capacity =capacity
                    except ValueError:
                        raise Parsing_error(f"Invalid max_link_capacity value '{val}', line {l_dx}")
                    # Add other connection attributes here if needed
            # else, means no attributes providedm do the defaults:
            else:
                connection_instence.max_link_capacity = 1
            return connection_instence

