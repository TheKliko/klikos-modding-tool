def hex_to_rgb(color: str) -> tuple[int,int,int]:
    if color.startswith('#'):
        color = color.lstrip('#')

    if len(color) == 7:
        color = color[:6]
    elif len(color) == 4:
        color = color[:3]
    
    if len(color) == 3:
        color = f"{color[0]*2}{color[1]*2}{color[2]*2}"

    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    
    return (r, g, b)