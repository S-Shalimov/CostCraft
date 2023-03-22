import math
from decimal import Decimal
import ezdxf


def get_line_length(*coords):
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

def get_arc_length(arc):
    PI = 3.1415926535
    radius = arc.dxfattribs()['radius']
    angle = abs(arc.dxfattribs()['end_angle'] - arc.dxfattribs()['start_angle'])
    length_arc = (PI * radius * angle) / 180 / 1000
    return round(length_arc, 2)

def get_item_quantity(obj, unit):
    if unit == 'м²':
        item_points = tuple((coord[0], coord[1]) for coord in obj['entity'].get_points())
        item_quantity = get_area(item_points)
    elif unit == 'м':
        if isinstance(obj['entity'], ezdxf.entities.arc.Arc):
            item_quantity = get_arc_length(obj['entity'])
        elif isinstance(obj['entity'], (ezdxf.entities.line.Line, ezdxf.entities.lwpolyline.LWPolyline)):
            item_points = tuple((coord[0], coord[1]) for coord in obj['entity'].get_points())
            item_quantity = get_line_length(item_points)
        else:
            raise TypeError('Unknown object: {}'.format(type(obj['entity'])))

    elif unit == 'шт':
        item_quantity = 1
    else:
        #TODO: обработать, вывести пользователю
        raise TypeError('Unknown unit: {}'.format(unit))
    return item_quantity



