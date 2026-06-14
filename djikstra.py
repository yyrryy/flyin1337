import heapq
from typing import Optional


class Dijkstra:
    """Dijkstra pathfinding on the parsed zone graph."""

    def __init__(self, zones: list[dict]) -> None:
        """Initialize with the list of zone dicts from the parser.

        Args:
            zones: List of zone dictionaries from Data.get_dict()
        """
        self.zones: dict[str, dict] = {z["name"]: z for z in zones}

    def find_path(self, start: str, end: str) -> Optional[list[str]]:
        """Find the shortest path from start to end zone.

        Args:
            start: Name of the start zone.
            end: Name of the end zone.

        Returns:
            List of zone names from start to end, or None if no path exists.
        """
        distances: dict[str, float] = {name: float("inf") for name in self.zones}
        distances[start] = 0
        previous: dict[str, Optional[str]] = {name: None for name in self.zones}
        visited: set[str] = set()
        heap: list[tuple[float, str]] = [(0, start)]

        while heap:
            current_cost, current = heapq.heappop(heap)

            if current in visited:
                continue
            visited.add(current)

            if current == end:
                return self._reconstruct_path(previous, start, end)

            for neighbor_name in self.zones[current]["connected_to"]:
                if neighbor_name in visited:
                    continue
                neighbor = self.zones[neighbor_name]
                if neighbor["zone_type"] == "blocked":
                    continue
                new_cost = current_cost + neighbor["cost"]
                if new_cost < distances[neighbor_name]:
                    distances[neighbor_name] = new_cost
                    previous[neighbor_name] = current
                    heapq.heappush(heap, (new_cost, neighbor_name))

        return None

    def _reconstruct_path(
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

    def find_all_paths(self, start: str, end: str) -> list[list[str]]:
        """Find all simple paths from start to end using DFS.

        Args:
            start: Start zone name.
            end: End zone name.

        Returns:
            List of paths, each path is a list of zone names, sorted by cost.
        """
        all_paths: list[list[str]] = []
        self._dfs(start, end, [start], set([start]), all_paths)
        all_paths.sort(key=lambda p: self._path_cost(p))
        return all_paths

    def _dfs(
        self,
        current: str,
        end: str,
        path: list[str],
        visited: set[str],
        all_paths: list[list[str]]
    ) -> None:
        """Recursive DFS to find all simple paths.

        Args:
            current: Current zone name.
            end: Target zone name.
            path: Current path being explored.
            visited: Set of visited zone names in current path.
            all_paths: Accumulator for completed paths.
        """
        if current == end:
            all_paths.append(list(path))
            return
        for neighbor_name in self.zones[current]["connected_to"]:
            if neighbor_name in visited:
                continue
            neighbor = self.zones[neighbor_name]
            if neighbor["zone_type"] == "blocked":
                continue
            visited.add(neighbor_name)
            path.append(neighbor_name)
            self._dfs(neighbor_name, end, path, visited, all_paths)
            path.pop()
            visited.remove(neighbor_name)

    def _path_cost(self, path: list[str]) -> int:
        """Calculate total cost of a path.

        Args:
            path: List of zone names.

        Returns:
            Total turn cost of the path.
        """
        return sum(self.zones[zone]["cost"] for zone in path[1:])