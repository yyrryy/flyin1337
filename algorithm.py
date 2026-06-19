from exceptions import Algo_error


class Path_finder:
    def __init__(
            self,
            zones: list[dict],
            connections: list[dict]
    ) -> None:
        """Initialize with the list of zone dicts from the parser.

        Args:
            zones: List of zone dictionaries from Data.get_dict()
        """
        self.zones: dict[str, dict] = {zone["name"]: zone for zone in zones}
        self.connections: list[dict] = connections

    def find_all_paths(
            self,
            start: str,
            end: str,
            paths_needed: int
    ) -> list[list[str]]:
        """Find all simple paths from start to end using iterative DFS.

        Args:
            start: Start zone name.
            end: End zone name.
            paths_needed: Maximum number of paths to find.

        Returns:
            List of paths, each path is a list of zone names, sorted by cost.
        """
        all_paths: list[list[str]] = []
        # Stack holds tuples of (current_node, path_so_far, visited_set)
        # Using list of tuples instead of recursion
        stack = [(start, [start], {start})]
        while stack and len(all_paths) < paths_needed:
            # print("stack>>", stack)
            current, path, visited = stack.pop()
            if current == end:
                all_paths.append(list(path))
                continue
            for neighbor_name in self.zones[current]["connected_to"]:
                if neighbor_name in visited:
                    continue
                neighbor = self.zones[neighbor_name]
                if neighbor["zone_type"] == "blocked":
                    continue
                # Create new path and visited set (no mutations!)
                new_path = path + [neighbor_name]
                new_visited = visited | {neighbor_name}
                stack.append((neighbor_name, new_path, new_visited))
            # print('path >>', path)
        # Sort by cost (cheapest first)
        if not all_paths:
            raise Algo_error("No path in this map")
        paths_with_cost = {}
        for path in all_paths:
            paths_with_cost[tuple(path)] = self._path_cost(path)
        min_cost = min(value for value in paths_with_cost.values())
        with open('paths.txt', 'w') as f:
            print(paths_with_cost, file=f)
        best_paths = []
        for key, value in paths_with_cost.items():
            if value == min_cost:
                best_paths.append(list(key))
        # all_paths.sort(key=lambda p: (self._path_cost(p), len(p)))
        # print('all_paths >>', all_paths)
        return best_paths

    def _path_cost(self, path: list[str]) -> int:
        """Calculate total cost of a path.
        Args:
            path: List of zone names (clean strings, no metadata).

        Returns:
            Total turn algo cost of the path.
        """
        return sum(
            self.zones[zone_name]["algo_cost"]
            for zone_name in path[1:]
        )
