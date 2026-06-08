import heapq

_TRAIT_TABLE = {
    "efficiency": {"multiplier": 10,   "exponent": 1.748, "cap": 215},
    "duration":   {"multiplier": 10,   "exponent": 1.7,   "cap": 235},
    "cost":       {"multiplier": 1000, "exponent": 3.4,   "cap": 5},
    "gain":       {"multiplier": 10,   "exponent": 1.8,   "cap": 200},
    "exp":        {"multiplier": 10,   "exponent": 1.8,   "cap": 200},
    "radar":      {"multiplier": 50,   "exponent": 2.5,   "cap": 999},
}


def _next_level_cost(trait_name: str, current_level: int) -> int:
    spec = _TRAIT_TABLE[trait_name]
    return int(spec["multiplier"] * ((current_level + 1) ** spec["exponent"]))


def _essence_to_next(trait_name: str, current_level: int, already_invested: int) -> int:
    return max(0, _next_level_cost(trait_name, current_level) - already_invested)


def allocate_essence(snapshot: dict, priorities) -> dict:
    pool = snapshot.get("essence", 0)
    if pool <= 0:
        return {}

    def _get_priority(name: str) -> float:
        if hasattr(priorities, name):
            return float(getattr(priorities, name, 1))
        if isinstance(priorities, dict):
            return float(priorities.get(name, 1))
        return 1.0

    slots = {}
    for name in _TRAIT_TABLE:
        entry = snapshot.get(name, {})
        if not entry.get("enabled", False):
            continue
        slots[name] = {
            "level": entry.get("current_level", 0),
            "invested": entry.get("invested", 0),
            "priority": _get_priority(name),
        }

    if not slots:
        return {}

    allocation = {name: 0 for name in slots}

    while pool > 0:
        heap = []
        for name, s in slots.items():
            cap = _TRAIT_TABLE[name]["cap"]
            if s["level"] >= cap:
                continue
            needed = _essence_to_next(name, s["level"], s["invested"])
            if needed == 0:
                s["level"] += 1
                s["invested"] = 0
                continue
            score = s["priority"] / needed
            heapq.heappush(heap, (-score, needed, name))

        if not heap:
            break

        _, needed, winner = heapq.heappop(heap)

        if needed <= pool:
            allocation[winner] += needed
            pool -= needed
            slots[winner]["level"] += 1
            slots[winner]["invested"] = 0
        else:
            allocation[winner] += pool
            slots[winner]["invested"] += pool
            pool = 0

    return {k: v for k, v in allocation.items() if v > 0}