import math


def get_length(*coords):
    length = 0.0
    coords = coords[0]
    for point in range(len(coords) - 1):
        x1, y1 = coords[point]
        x2, y2 = coords[point + 1]
        dx = x2 - x1
        dy = y2 - y1
        length += math.sqrt(dx**2 + dy**2)
    return round((length / 1000), 2)

def get_area(*coords):
    coords = list(*coords) + [coords[0][0]]
    area = 0.0
    for point in range(len(coords) - 1):
        area += coords[point][0] * coords[point + 1][1] - coords[point + 1][0] * coords[point][1]
    return abs(round((area / 2 / 1000000), 2))

def get_item_entity(obj, unit):
    if 'м' in unit:
        # TODO: добавить проверку на lwpolyline
        item_points = tuple((coord[0], coord[1]) for coord in obj['entity'].get_points())
        if unit == 'м²':
            item_quantity = round(get_area(item_points), 2)
        if unit == 'м':
            item_quantity = round(get_length(item_points), 2)
    elif unit == 'шт':
        item_quantity = 1
    else:
        raise TypeError('Unknown unit: {}'.format(unit))
    return item_quantity



