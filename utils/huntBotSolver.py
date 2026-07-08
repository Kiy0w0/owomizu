import io
import asyncio
import base64

try:
    import numpy as np
except ImportError:
    np = None

try:
    from PIL import Image
except ImportError:
    Image = None

priority_groups = [
    list("abdegkmpqstvwxyz"),
    list("fho"),
    list("cnru"),
    list("jl"),
    list("i"),
]

_encoded_templates = {
    "a": "iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAARElEQVQoFWN0mv3/PwOJgIlE9WDlZGliJNYmZG+QZxOyCcTaSpZNZGliQXbSvlRGnAGD7A2ybGJENgHZVnxssmwiSxMARF4PhclsgWMAAAAASUVORK5CYII=",
    "b": "iVBORw0KGgoAAAANSUhEUgAAAA0AAAASCAYAAACAa1QyAAAAO0lEQVQoFWN0mv3/PwMU7EtlZASx8dFM+CRxyQ1yTYzIAYHLD+ji9PMTC7LV+OIJ2Rv0c96oTdD4oV9AAAB/TQsAYy1MLwAAAABJRU5ErkJggg==",
    "c": "iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAALklEQVQoFWN0mv3/PwOJgIlE9WDlZGliQbZpXyojIzIfF5tym2AmEwocsmwiSxNKQMCchy1AkJ1Mlk2MyCbAbCJEk2UTWZoA7Z4N1XlVX20AAAAASUVORK5CYII=",
    "d": "iVBORw0KGgoAAAANSUhEUgAAAA0AAAASCAYAAACAa1QyAAAAOUlEQVQoFWNkIBI4zf7/H6aUCcYghR7kmhiRPUisv+jnJxZkJ+1LZWRE5iOzkb1BP+cNR5sGeYoAAJVGDLX7Igd2AAAAAElFTkSuQmCC",
    "e": "iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAAP0lEQVQoFWN0mv3/PwOJgIlE9WDlZGliQbZpXyojIzIfmY3sDbJsGtUEDU5G5KBEDmJ8bPqFHtEpAtm59HMe/WwCAJ8UCwJWTpYsAAAAAElFTkSuQmCC",
    "f": "iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAAMUlEQVQoFWN0mv3/PwOJgIlE9WDlZGliQbZpXyojIzIfF5ssmxhHd0AQ5XFQgCB7YzgGBAAHzQyqIIdwIAAAAABJRU5ErkJggg==",
    "g": "iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAAR0lEQVQoFWN0mv3/PwOJgIlE9WDlZGliQbZpXyojIzIfF5tym2AmEwocsmwiSxNKQMCchy1AkJ1Mlk2MyCbAbCJEk2UTWZoA7Z4N1XlVX20AAAAASUVORK5CYII=",
    "h": "iVBORw0KGgoAAAANSUhEUgAAAA0AAAASCAYAAACAa1QyAAAAPUlEQVQoFWN0mv3/PwMU7EtlZAQxCYkxwTSQQo9qgobWIA8IRuTYJzaC6ecnACGvDc/Z7HB/AAAAAElFTkSuQmCC",
    "i": "iVBORw0KGgoAAAANSUhEUgAAAAkAAAANCAYAAAB7AEQGAAAAIklEQVQYGWNkQAJOs///h3H3pTIywthMMAY+elQRw2AMAgBW+wQa/q56owAAAABJRU5ErkJggg==",
    "j": "iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAAN0lEQVQoFWNkIBI4zf7/H6aUCcYghR7VBA0tsgKCBTn896UyMhIT9GTZxIhsEzG2gNSQZRNZmgAmfgnRpvfItgAAAABJRU5ErkJggg==",
    "k": "iVBORw0KGgoAAAANSUhEUgAAAAwAAAANCAYAAACdKY9CAAAAaklEQVQoFYWR0Q3AIAhES0frLp2qu3Q1zSW95rhA8EeU94BoXM9ax7feO4Kx7+ROT1RnwsiNgsKj4DBGbjtUcNuhg0vBYUC60kgTDDEJWkljLVQKeA3/RErBgBU7kPnUwWFAfvcLnmBFlzY0ejHPkHfW8AAAAABJRU5ErkJggg==",
    "l": "iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAAL0lEQVQoFWN0mv3/PwMU7EtlZISx8dFM+CRxyY1qgobMIA8IRuQUgSsy0cXp5ycAj5sG9B8JGsEAAAAASUVORK5CYII=",
    "m": "iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAAMElEQVQoFWN0mv3/PwOJgIlE9WDllGval8rICMLItmMTo9wmZBvwsUdtgoYO/QICANPkB4nFxDDlAAAAAElFTkSuQmCC",
    "n": "iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAAL0lEQVQoFWN0mv3/PwOJgIlE9WDlZGliQbZpXyojIzIfmY3sDbJsGtUEDc5BHhAAj7kG91sA1sEAAAAASUVORK5CYII=",
    "o": "iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAAN0lEQVQoFWN0mv3/PwOJgIlE9WDlZGliQbZpXyojIzIfmY3sDbJsGtUEDU5G5KBEDmJ8bPqFHtEpAtm59HMe/WwCAJ8UCwJWTpYsAAAAAElFTkSuQmCC",
    "p": "iVBORw0KGgoAAAANSUhEUgAAAA0AAAASCAYAAACAa1QyAAAAQklEQVQoFWN0mv3/PwOJgIlE9WDlZGliQbZpXyojIzIfmY3sDbJsGtUEDU5G5KBEDmJ8bPqFHtEpAtm59HMe/WwCAJ8UCwJWTpYsAAAAAElFTkSuQmCC",
    "q": "iVBORw0KGgoAAAANSUhEUgAAAA0AAAASCAYAAACAa1QyAAAATUlEQVQoFWN0mv3/PwOJgIlE9WDlZGliQbZpXyojIzIfmY3sDbJsGtUEDU5G5KBEDmJ8bPqFHtYUgOxkbKmELOcRtAkWIMg2kmUTWZoAQwMR2VhDl78AAAAASUVORK5CYII=",
    "r": "iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAALUlEQVQoFWN0mv3/PwOJgIlE9WDlZGliQbZpXyojIzIfF5ssm0Y1QYNzkAcEACCxBBxWW3qwAAAAAElFTkSuQmCC",
    "s": "iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAANElEQVQoFWN0mv3/PwOJgIlE9WDlZGliQbZpXyojIzIfF5ssmxgHd0AQ5XFQgCB7YzgGBAAHzQyqIIdwIAAAAABJRU5ErkJggg==",
    "t": "iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAALUlEQVQoFWN0mv3/PwOJgIlE9WDlZGlixGYTspP3pTJiqCHLplFN0KAe5AEBAKu7BvTrMd81AAAAAElFTkSuQmCC",
    "u": "iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAAMUlEQVQoFWN0mv3/PwMU7EtlZISx0WlkdUzoksTwRzVBQ2mQBwQjckwTE7EgNfTzE9YEiuxkbImYfs6jn00ArlAN2LER5EoAAAAASUVORK5CYII=",
    "v": "iVBORw0KGgoAAAANSUhEUgAAAAwAAAANCAYAAACdKY9CAAAAd0lEQVQoFYWQAQ6AIAxEi6PpKm6lqzgbesRnygVNJMGW3gcaG7XWmLfre8WvDacoiXsdaxTyHJc9Hs70BlDPZNUmd82EnGPQbnARoEfxihpljRzBMO0EAl0EEeH/plG6M3XFjLUbcgGiPwVO9+NGZIhgXQ8qurOf2/xoPJiVt3kCPwGLgnhJFhDySgAAAABJRU5ErkJggg==",
    "w": "iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAALUlEQVQoFWN0mv3/PwMU7EtlZAQxCYkxwTSQQo9qgobWIA8IRuTYJzaC6ecnACGvDc/Z7HB/AAAAAElFTkSuQmCC",
    "x": "iVBORw0KGgoAAAANSUhEUgAAAAwAAAANCAYAAACdKY9CAAAAgklEQVQoFZWSiw2AIAxEi6PpKm6lqzgbesRnygVNJMGW3gcaG7XWmLfre8WvDacoiXsdaxTyHJc9Hs70BlDPZNUmd82EnGPQbnARoEfxihpljRzBMO0EAl0EEeH/plG6M3XFjLUbcgGiPwVO9+NGZIhgXQ8qurOf2/xoPJiVt3kCPwGLgnhJFhDySgAAAABJRU5ErkJggg==",
    "y": "iVBORw0KGgoAAAANSUhEUgAAAA0AAAASCAYAAACAa1QyAAAAPklEQVQoFWN0mv3/PwMU7EtlZISx0WlkdUzoksTwRzVBQ2mQBwQjckwTE7EgNfTzE9YEiuxkbImYfs6jn00ArlAN2LER5EoAAAAASUVORK5CYII=",
    "z": "iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAAT0lEQVQoFWN0mv3/PwOJgIlE9WDlZGliJGQTuvP3pTIy4tWETQPIEpyacGnAqQmfBqyaCGnA0ESMBhRNxGqAa0LXAJLABxhJ1QAyjKwUAQA6fySifLwVygAAAABJRU5ErkJggg==",
}


def _decode_template(b64_string):
    return Image.open(io.BytesIO(base64.b64decode(b64_string)))


def _build_checks():
    checks = []
    for group in priority_groups:
        for letter in group:
            if letter in _encoded_templates:
                img = _decode_template(_encoded_templates[letter])
                checks.append((img, img.size, letter))
    return checks


async def solveHbCaptcha(captcha_url, session):
    if np is None or Image is None:
        return ""

    checks = _build_checks()

    try:
        async with session.get(captcha_url) as resp:
            if resp.status == 200 and "image" in resp.headers.get("Content-Type", ""):
                large_image = Image.open(io.BytesIO(await resp.read()))
                large_array = np.array(large_image)
            else:
                return ""
    except Exception:
        return ""

    matches = []
    for img, (small_w, small_h), letter in checks:
        small_array = np.array(img)
        mask = small_array[:, :, 3] > 0

        for y in range(large_array.shape[0] - small_h + 1):
            for x in range(large_array.shape[1] - small_w + 1):
                segment = large_array[y : y + small_h, x : x + small_w]
                try:
                    if np.array_equal(segment[mask], small_array[mask]):
                        if not any(
                            (m[0] - small_w < x < m[0] + small_w)
                            and (m[1] - small_h < y < m[1] + small_h)
                            for m in matches
                        ):
                            matches.append((x, y, letter))
                except Exception:
                    continue

    matches = sorted(matches, key=lambda tup: tup[0])
    return "".join([i[2] for i in matches])