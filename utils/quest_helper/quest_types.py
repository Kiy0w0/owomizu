_ANIMAL_RANKS = [
    "common", "uncommon", "rare", "epic", "special",
    "mythical", "gem", "legendary", "fabled", "distorted", "hidden",
]

QUEST_IDS = {
    "receive an action from a friend": {"id": "action_receive", "helpable": True},
    "receive curses": {"id": "curse", "helpable": True},
    "receive prayers": {"id": "prayer", "helpable": True},
    "receive cookies": {"id": "cookie", "helpable": True},
    "battle with a friend": {"id": "battle_friend", "helpable": True},
    "earn battle xp": {"id": "battle_xp", "helpable": False},
    "gamble your cowoncy": {"id": "gamble", "helpable": False},
    "defeat bosses": {"id": "boss", "helpable": False},
    "send an action to a friend": {"id": "action_send", "helpable": False},
    "manually hunt": {"id": "hunt", "helpable": False},
    "battle": {"id": "battle", "helpable": False},
    "say owo": {"id": "owo", "helpable": False},
}

for _rank in _ANIMAL_RANKS:
    QUEST_IDS[f"find {_rank} animals"] = {"id": f"find_animal_{_rank}", "helpable": False}


def get_quest_id(title: str) -> str | None:
    return (QUEST_IDS.get(title.lower()) or {}).get("id")


def is_helpable(title: str) -> bool:
    return QUEST_IDS.get(title.lower(), {}).get("helpable", False)
