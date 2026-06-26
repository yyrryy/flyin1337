import re
from classes import Zone, Conncetion
from exceptions import Parsing_error


class Parser():
    """Parser for drone network map files.

    Reads and validates map files, converting them into structured data
    containing zones, connections, and drone count. Ensures the map format
    complies with the specification.

    Attributes:
        nb_drones (int): Number of drones in the simulation.
        zones (list[Zone]): List of parsed Zone objects.
        connections (list[Connection]): List of parsed Connection objects.
    """
    def __init__(self) -> None:
        """Initialize an empty Parser instance."""
        self.nb_drones = 0
        self.zones: list[Zone] = []
        self.connections: list[Conncetion] = []

    def get_dict(self) -> dict:
        """Convert parsed data to a dictionary representation.

        Returns:
            dict: Contains nb_drones, zones, and connections as dictionaries.
        """
        return {
            "nb_drones": self.nb_drones,
            "zones": [i.get_dict() for i in self.zones],
            "connections": [i.get_dict() for i in self.connections],
        }

    def parse_data(self, file_content: list) -> None:
        """Parse the map file content into zones and connections.

        Validates the file format according to the specification, ensuring:
        - First non-comment line is nb_drones
        - Exactly one start_hub and one end_hub
        - All zones have unique names (no dashes or spaces)
        - All connections reference existing zones
        - No duplicate connections
        - At least one connection from start and one to end

        Args:
            file_content: List of lines from the map file.

        Raises:
            Parsing_error: If the file format is invalid, contains duplicates
                , or references non-existent zones.
        """
        # flags to track if we already got start and end zone
        # to avoid duplication
        has_content = False
        for line in file_content:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                has_content = True
                break
        if not has_content:
            raise Parsing_error("file contains only comments or is empty")

        start_flag = False
        end_flag = False
        start_connection_flag = False
        end_connection_flag = False
        nb_drones_found = False
        for l_dx, line in enumerate(file_content, start=1):
            raw_line = line.strip()
            # print('stripped_line 11', stripped_line)
            # Skip empty lines and comments
            if not raw_line or raw_line.startswith("#"):
                continue

            if '#' in raw_line:
                # stripped_line = stripped_line.split('#', 1)[0]
                stripped_line = ""
                for c in raw_line:
                    if c == '#':
                        break
                    stripped_line += c
                stripped_line = stripped_line.strip()
            else:
                stripped_line = raw_line
            nb_drones_pattern = r'^nb_drones:\s+([-?\d.]+)?$'
            start_hub_pattern = (
                r'^start_hub:\s+'
                r'([^\s]+)\s+(-?\d+)\s+(-?\d+)'
                r'(?:\s+\[([^\]]*)\])?$'
            )
            end_hub_pattern = (
                r'^end_hub:\s+'
                r'([^\s]+)\s+(-?\d+)\s+(-?\d+)'
                r'(?:\s+\[([^\]]*)\])?$'
            )
            hub_pattern = (
                r'^hub:\s+([^\s]+)\s+'
                r'(-?\d+)\s+(-?\d+)'
                r'(?:\s+\[([^\]]*)\])?$'
            )
            connection_pattern = (
                r'^connection:\s+'
                r'([^\s]+)(?:\s+\[([^\]]*)\])?$'
            )
            nb_drones_match = re.match(
                nb_drones_pattern, stripped_line, re.IGNORECASE
            )
            start = re.match(
                start_hub_pattern, stripped_line, re.IGNORECASE
            )
            end = re.match(
                end_hub_pattern, stripped_line, re.IGNORECASE
            )
            hub = re.match(
                hub_pattern, stripped_line, re.IGNORECASE
            )
            connection = re.match(
                connection_pattern, stripped_line, re.IGNORECASE
            )
            # print(" >>>>>>", nb_drones_match)
            # enforce the first line to be the number of drones
            if not nb_drones_found and not nb_drones_match:
                msg = "the first not commented line should be the number of drones"
                raise Parsing_error(msg)
            # skip empty lines
            if nb_drones_match:
                # print("driones fpund")
                if nb_drones_found:
                    raise Parsing_error(f"duplicated data. line {l_dx}")
                nbr_of_drones = 0
                try:
                    nbr_of_drones = int(nb_drones_match.group(1))
                    if nbr_of_drones <= 0:
                        msg = "Number of drones must be a positive integer"
                        raise Parsing_error(msg)
                except ValueError:
                    msg = f"{nb_drones_match.group(1)} isn't a valid integer"
                    msg += f", line: {l_dx}"
                    raise Parsing_error(msg)
                self.nb_drones = nbr_of_drones
                nb_drones_found = True
            elif start:
                name = start.group(1)
                if "-" in name or " " in name:
                    msg = f"Zone name can't have dashes or spaces, line:{l_dx}"
                    raise Parsing_error(msg)
                if start_flag:
                    message = f"{name} already existed, Error in line {l_dx}"
                    raise Parsing_error(message)
                start_flag = True
                try:
                    x = int(start.group(2))
                except ValueError:
                    raise Parsing_error(f'{x} is not a valid coordination')
                try:
                    y = int(start.group(3))
                except ValueError:
                    raise Parsing_error(f'{y} is not a valid coordination')
                attributes = start.group(4)
                zone = Zone(name, True, False, x, y, attributes)
                zone.set_data(l_dx, nbr_of_drones)
                self.zones.append(zone)
                self.start = (x, y)
            elif end:
                name = end.group(1)
                if "-" in name or " " in name:
                    msg = f"Zone name can't have dashes or spaces, line:{l_dx}"
                    raise Parsing_error(msg)
                if end_flag:
                    message = f"{name} already existed, Error in line {l_dx}"
                    raise Parsing_error(message)
                end_flag = True
                try:
                    x = int(end.group(2))
                except ValueError:
                    raise Parsing_error(f'{x} is not a valid coordination')
                try:
                    y = int(end.group(3))
                except ValueError:
                    raise Parsing_error(f'{y} is not a valid coordination')
                attributes = end.group(4)
                zone = Zone(name, False, True, x, y, attributes)
                zone.set_data(l_dx, nbr_of_drones)
                self.zones.append(zone)
                self.end = (x, y)
            elif hub:
                name = hub.group(1)
                if "-" in name or " " in name:
                    msg = f"Zone name can't have dashes or spaces, line:{l_dx}"
                    raise Parsing_error(msg)
                try:
                    x = int(hub.group(2))
                except ValueError:
                    raise Parsing_error(f'{x} is not a valid coordination')
                try:
                    y = int(hub.group(3))
                except ValueError:
                    raise Parsing_error(f'{y} is not a valid coordination')
                attributes = hub.group(4)
                zone_exist = next(
                    (
                        z for z in self.zones if z.name == name
                    ), None
                )
                if zone_exist:
                    msg = f"Zone {name} already exists, line {l_dx}"
                    raise Parsing_error(msg)
                zone = Zone(name, False, False, x, y, attributes)
                zone.set_data(l_dx, nbr_of_drones)
                self.zones.append(zone)
            elif connection:
                zones = connection.group(1)
                splitted = zones.split("-")
                if not len(splitted) == 2:
                    raise Parsing_error(f"Not valid connection, line: {l_dx}")
                zone_from = splitted[0]
                zone_to = splitted[1]
                attributes = connection.group(2)
                zone_from_instence = next((
                    z for z in self.zones if z.name == zone_from), None
                )
                if not zone_from_instence:
                    message = f"Zone {zone_from} does not exist, line {l_dx}"
                    raise Parsing_error(message)
                zone_to_instence = next((
                    z for z in self.zones if z.name == zone_to), None
                )
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
                expected = (
                    "expected: \n"
                    "nb_drones: (positive integer)\n"
                    "start_hub: (name) (x) (y) [optional metadata]\n"
                    "hub: (name) (x) (y) [optional metadata]\n"
                    "end_hub: (name) (x) (y) [optional metadata]\n"
                    "connection: (zone_from)-(zone_target)[optional metadata]\n"
                    "Ordering is not important\n"
                    "white spaces are allowed"
                )
                raise Parsing_error(f"Invalid format, line: {l_dx}, {expected}")
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
        l_dx: int
    ) -> Conncetion:
        """Create a bidirectional connection between two zones.

        Validates that the connection doesn't already exist (in either direction),
        adds the connection to both zones' adjacency lists, and parses any
        connection metadata.

        Args:
            zone_from_instence: The source Zone object.
            zone_to_instence: The destination Zone object.
            attributes: Metadata string (e.g., "max_link_capacity=5").
            l_dx: Line number for error reporting.

        Returns:
            The created Connection object.

        Raises:
            Parsing_error: If the connection already exists or if metadata is invalid.
        """
        one_ways_duplicate = next(
            (
                connection for connection in self.connections
                if (
                    connection.zone_from == zone_from_instence
                    and connection.zone_to == zone_to_instence
                    )
            ),
            None
        )
        if one_ways_duplicate:
            msg = f"Duplicated connection {zone_from_instence.name}"
            msg += f" and {zone_to_instence.name}, line {l_dx}"
            raise Parsing_error(msg)
        # else means there is zone from and zone to
        else:
            zone_from_instence.connected_to.append(zone_to_instence)
            # bidirectional connection
            # zone_to_instence.connected_to.append(zone_from_instence)
            connection_instence = Conncetion(
                zone_from_instence,
                zone_to_instence,
                attributes
            )
            # connection_instence.data[""]
            if attributes:
                attr_pattern = re.compile(r'(\w+)=([^=\s\]]+)$')
                valid_attribute = attr_pattern.match(attributes)
                expected = "max_link_capacity is expected"
                if not valid_attribute:
                    msg = f"Invalid metadata for connection, line {l_dx}, {expected}"
                    raise Parsing_error(msg)
                key, val = valid_attribute.group(1), valid_attribute.group(2)
                if key.lower() == "max_link_capacity":
                    try:
                        capacity = int(val)
                        if capacity < 1:
                            msg = "max_link_capacity must be a positive"
                            msg += f" integer, line {l_dx}"
                            raise Parsing_error(msg)
                        connection_instence.max_link_capacity = capacity
                    except ValueError:
                        msg = "Invalid max_link_capacity value"
                        msg += f" '{val}', line {l_dx}"
                        raise Parsing_error(msg)
                else:
                    msg = f"Invalid metadata for connection, line {l_dx}, {expected}"
                    raise Parsing_error(msg)
                    # Add other connection attributes here if needed
            # else, means no attributes providedm do the defaults:
            else:
                connection_instence.max_link_capacity = 1
            return connection_instence
