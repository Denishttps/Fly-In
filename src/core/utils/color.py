import webcolors


def set_color(text: str, color: str) -> str:
    try:
        hex_color = webcolors.name_to_hex(color)
        return f"[{hex_color}]{text}[/{hex_color}]"
    except ValueError:
        return text
