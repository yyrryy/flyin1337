import heapq
from typing import Optional
import random


class Path_finder:
    def __init__(self, zones: list[dict], connections: list[dict]) -> None:
        """Initialize with the list of zone dicts from the parser.

        Args:
            zones: List of zone dictionaries from Data.get_dict()
        """
        self.zones: dict[str, dict] = {zone["name"]: zone for zone in zones}
        self.connections: dict[str, dict] = connections

    def find_path(self, start: str, end: str) -> Optional[list[str]]:
        costs = {name: float("inf") for name in self.zones}
        costs[start] = 0
        previous = {name: None for name in self.zones}
        visited = set()
        # (cost, is_priority, zone_name) - is_priority=0 means priority zone (higher priority in heap)
        heap = [(0, 1, start)]  # lower is_priority = better (0 for priority, 1 for normal)

        while heap:
            current_cost, current_priority_flag, current_name = heapq.heappop(heap)

            if current_name in visited:
                continue
            visited.add(current_name)

            if current_name == end:
                return self.build_path(previous, start, end)

            for neighbor_name in self.zones[current_name]["connected_to"]:
                if neighbor_name in visited:
                    continue
                neighbor = self.zones[neighbor_name]
                if neighbor["zone_type"] == "blocked":
                    continue
                new_cost = current_cost + neighbor["cost"]
                if new_cost < costs[neighbor_name]:
                    costs[neighbor_name] = new_cost
                    previous[neighbor_name] = current_name
                    # Priority flag: 0 for priority zones (higher priority), 1 for normal
                    priority_flag = 0 if neighbor["zone_type"] == "priority" else 1
                    heapq.heappush(heap, (new_cost, priority_flag, neighbor_name))
                elif new_cost == costs[neighbor_name]:
                    # Same cost - prefer priority zones
                    existing_is_priority = (self.zones[neighbor_name]["zone_type"] == "priority")
                    new_is_priority = (neighbor["zone_type"] == "priority")
                    if new_is_priority and not existing_is_priority:
                        costs[neighbor_name] = new_cost
                        previous[neighbor_name] = current_name
                        priority_flag = 0 if neighbor["zone_type"] == "priority" else 1
                        heapq.heappush(heap, (new_cost, priority_flag, neighbor_name))

        return None
    def find_path2(self, start: str, end: str) -> Optional[list[str]]:
        costs = {name: float("inf") for name in self.zones}
        costs[start] = 0
        previous = {name: None for name in self.zones}
        visited = set()
        heap = [(0, 1, start)]

        while heap:
            current_cost, current_priority_flag, current_name = heapq.heappop(heap)

            if current_name in visited:
                continue
            visited.add(current_name)

            if current_name == end:
                return self.build_path(previous, start, end)

            # SHUFFLE NEIGHBORS FOR DIFFERENT PATHS
            neighbors = list(self.zones[current_name]["connected_to"])
            random.shuffle(neighbors)

            for neighbor_name in neighbors:
                if neighbor_name in visited:
                    continue
                neighbor = self.zones[neighbor_name]
                if neighbor["zone_type"] == "blocked":
                    continue
                new_cost = current_cost + neighbor["cost"]
                if new_cost < costs[neighbor_name]:
                    costs[neighbor_name] = new_cost
                    previous[neighbor_name] = current_name
                    priority_flag = 0 if neighbor["zone_type"] == "priority" else 1
                    heapq.heappush(heap, (new_cost, priority_flag, neighbor_name))
                elif new_cost == costs[neighbor_name]:
                    existing_is_priority = (self.zones[neighbor_name]["zone_type"] == "priority")
                    new_is_priority = (neighbor["zone_type"] == "priority")
                    if new_is_priority and not existing_is_priority:
                        costs[neighbor_name] = new_cost
                        previous[neighbor_name] = current_name
                        priority_flag = 0 if neighbor["zone_type"] == "priority" else 1
                        heapq.heappush(heap, (new_cost, priority_flag, neighbor_name))

        return None

    def build_path(
        self,
        previous: dict[str, Optional[str]],
        start: str,
        end: str
    ) -> list[str]:
        
        """Reconstruct path from previous dict.

        Args:
            previous: Dict mapping each zone to the zone it was reached from.
            start: Start zone name.
            end: End zone name.

        Returns:
            Ordered list of zone names from start to end.
        """
        path: list[str] = []
        current: Optional[str] = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        return path

    def find_all_paths(self, start: str, end: str, paths_needed: int) -> list[list[str]]:
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
            
            # Explore neighbors (reverse order to maintain same order as recursion)
            for neighbor_name in reversed(self.zones[current]["connected_to"]):
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
            Total turn cost of the path.
        """
        return sum(self.zones[zone_name]["cost"] for zone_name in path[1:])
