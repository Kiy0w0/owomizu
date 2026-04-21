   

def allocate_essence(input_data, prio_dict):

    traits = {
        "efficiency": {"inc": 10, "pow": 1.748, "base": 25, "upg": 1, "max": 215, "prio": 4},
        "duration":   {"inc": 10, "pow": 1.7,  "base": 0.5, "upg": 0.1, "max": 235, "prio": 2},
        "cost":       {"inc": 1000, "pow": 3.4, "base": 10, "upg": -1, "max": 5, "prio": 5},
        "gain":       {"inc": 10, "pow": 1.8,  "base": 0,  "upg": 25,  "max": 200, "prio": 4},
        "exp":        {"inc": 10, "pow": 1.8,  "base": 0,  "upg": 35,  "max": 200, "prio": 3},
        "radar":      {"inc": 50, "pow": 2.5,  "base": 0,  "upg": 0.00000004, "max": 999, "prio": 1}
    }
    for trait, prio in prio_dict.items():
        traits[trait]["prio"] = prio

    available_essence = input_data.get("essence", 0)

    """Fetch enabled traits"""
    enabled_traits = {
        t: data for t, data in input_data.items()
        if t in traits and data.get("enabled", False)
    }

    """
    allocation: future result,
    initialising with 0, will contain how much essence to allocate for all traits
    """
    allocation = {t: 0 for t in enabled_traits}

    """Contains a dict of current level of each enabled traits"""
    current_levels = {t: enabled_traits[t].get("current_level", 0) for t in enabled_traits}

    """Contains a dict of currently invested essense for each trait"""
    current_invested = {t: enabled_traits[t].get("invested", 0) for t in enabled_traits}

    """Essence from total available essence, which has yet to be distributed."""
    remaining = available_essence

    while remaining > 0:
        best_trait = None
        best_ratio = -1
        cost_for_best = None

        for t in allocation:
            lvl = current_levels[t]
            trait_data = traits[t]

            if lvl >= trait_data["max"]:

                continue

            next_level = lvl + 1

            """Total cost for next level is calculated with this equation"""
            full_cost = int(trait_data["inc"] * (next_level ** trait_data["pow"]))
            invested = current_invested.get(t, 0)

            """cost for next level"""
            required = max(0, full_cost - invested)

            if required == 0:

                current_levels[t] += 1
                current_invested[t] = 0
                continue

            benefit = trait_data["prio"]
            ratio = benefit / required if required > 0 else 0

            if required <= remaining and ratio > best_ratio:
                best_ratio = ratio
                best_trait = t
                cost_for_best = required

        if best_trait is not None:

            allocation[best_trait] += cost_for_best
            remaining -= cost_for_best
            """move the trait up by a level"""
            current_levels[best_trait] += 1
            """reset already invested amount to 0 (since we are at next level now)"""
            current_invested[best_trait] = 0
        else:

            best_trait = None
            best_ratio = -1

            for t in allocation:
                lvl = current_levels[t]
                trait_data = traits[t]

                if lvl >= trait_data["max"]:

                    continue

                next_level = lvl + 1
                full_cost = int(trait_data["inc"] * (next_level ** trait_data["pow"]))
                invested = current_invested.get(t, 0)
                required = max(0, full_cost - invested)

                if required <= 0:
                    continue

                benefit = trait_data["prio"]
                ratio = benefit / required if required > 0 else 0

                if ratio > best_ratio:
                    best_ratio = ratio
                    best_trait = t

            if best_trait is not None:
                allocation[best_trait] += remaining
                current_invested[best_trait] += remaining
                remaining = 0
            else:

                break

    return allocation