import webcolors


def rgb_to_hex_bytes(rgb: tuple[int, int, int]) -> str:
    return f"#{bytes(rgb).hex()}"


def set_color(text: str, colors: tuple[str | None, str | None]) -> str:
    c1, c2 = colors
    if not (c1 or c2):
        return text

    if not c1:
        c1 = c2

    if not c2:
        c2 = c1

    try:
        color1 = webcolors.name_to_rgb(c1)
        color2 = webcolors.name_to_rgb(c2)

        color = tuple((a + b) // 2 for a, b in zip(color1, color2))
    except Exception:
        color = (255, 255, 255)
    color = rgb_to_hex_bytes(color)
    return f"[{color}]{text}[/{color}]"
