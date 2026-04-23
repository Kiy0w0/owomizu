import random
import string

keyboard_neighbors = {
    'a': ['q', 'w', 's'], 'b': ['v', 'n'], 'c': ['x', 'v'], 'd': ['s', 'f'],
    'e': ['w', 'r'], 'f': ['d', 'g'], 'g': ['f', 'h'], 'h': ['g', 'j'],
    'i': ['u', 'o'], 'j': ['h', 'k'], 'k': ['j', 'l'], 'l': ['k'],
    'm': ['n'], 'n': ['b', 'm'], 'o': ['i', 'p'], 'p': ['o'],
    'q': ['w', 'a'], 'r': ['e', 't'], 's': ['a', 'd'], 't': ['r', 'y'],
    'u': ['y', 'i'], 'v': ['c', 'b'], 'w': ['q', 'e'], 'x': ['z', 'c'],
    'y': ['t', 'u'], 'z': ['x']
}


def _swap_letter(word):
    if len(word) < 2:
        return word
    idx = random.randint(0, len(word) - 2)
    return word[:idx] + word[idx + 1] + word[idx] + word[idx + 2:]


def _replace_with_neighbor(word):
    idx = random.randint(0, len(word) - 1)
    letter = word[idx].lower()
    if letter in keyboard_neighbors:
        return word[:idx] + random.choice(keyboard_neighbors[letter]) + word[idx + 1:]
    return word


def _double_letter(word):
    parts = word.split(" ", 1)
    fw = parts[0]
    idx = random.randint(0, len(fw) - 1)
    fw = fw[:idx] + fw[idx] + fw[idx] + fw[idx + 1:]
    return fw + (" " + parts[1] if len(parts) > 1 else "")


def _one_out(word):
    if len(word) < 2:
        return word
    idx = random.randint(0, len(word) - 1)
    return word[:idx] + word[idx + 1:]


def _add_end_noise(word):
    return word + random.choice(string.ascii_lowercase)


_TYPO_TABLE = [
    (40, _replace_with_neighbor),
    (20, _swap_letter),
    (25, _one_out),
    (10, _double_letter),
    (5,  _add_end_noise),
]


def misspell_word(word: str) -> str:
    roll = random.randint(1, 100)
    cumulative = 0
    for weight, fn in _TYPO_TABLE:
        cumulative += weight
        if roll <= cumulative:
            return fn(word)
    return _replace_with_neighbor(word)


def should_misspell(settings_dict: dict) -> bool:
    cnf = settings_dict.get("misspell", {})
    if not cnf.get("enabled", False):
        return False
    freq = cnf.get("frequencyPercentage", 1)
    return random.randint(1, 100) <= freq