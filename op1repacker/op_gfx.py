import re
import os
import json

from svg.path import parse_path

# String to add to patched SVGs to help detect already patched files
PATCH_IDENTIFIER = '<!-- patched with op1repacker -->'


def get_full_match(pat):
    return pat.string[pat.start():pat.end()]


def round_coordinate(v):
    return round(v, 4)


def simple_delta_move(pat, delta):
    text = get_full_match(pat)
    match = pat.group(1)
    new = str(round_coordinate(float(match)+delta))
    text = text.replace(match, new)
    return text


def polyline_delta_move(pat, delta):
    text = get_full_match(pat)
    point_str = pat.group(1)
    points = ' '.join(point_str.split()).split(' ')
    new_point_str = ''

    for point in points:
        x, y = point.split(',')
        x = round_coordinate(float(x)+delta[0])
        y = round_coordinate(float(y)+delta[1])
        new_point_str += "{},{} ".format(x, y)

    new_point_str = new_point_str.strip()
    text = text.replace(point_str, new_point_str)
    return text


def move_imaginary(ima, delta):
    di = complex(round_coordinate(delta[0]), round_coordinate(delta[1]))
    return ima+di


def path_primitive_move(primitive, delta):
    primitive.start = move_imaginary(primitive.start, delta)
    primitive.end = move_imaginary(primitive.end, delta)
    if 'control' in dir(primitive):
        primitive.control = move_imaginary(primitive.control, delta)
    if 'control1' in dir(primitive):
        primitive.control1 = move_imaginary(primitive.control1, delta)
    if 'control2' in dir(primitive):
        primitive.control2 = move_imaginary(primitive.control2, delta)


def path_delta_move(pat, delta):
    text = get_full_match(pat)
    match = pat.group(1)
    path = parse_path(match)
    for primitive in path:
        path_primitive_move(primitive, delta)
    new_d = path.d()
    return text.replace(match, new_d)


def create_delta_move(delta, func):
    return lambda pat: func(pat, delta)


def move_all(data, delta):
    x, y = delta
    data = re.sub(r'<rect.*? x="(.*?)".*?/>', create_delta_move(x, simple_delta_move), data)
    data = re.sub(r'<rect.*? y="(.*?)".*?/>', create_delta_move(y, simple_delta_move), data)
    data = re.sub(r'x1="(.*?)"', create_delta_move(x, simple_delta_move), data)
    data = re.sub(r'x2="(.*?)"', create_delta_move(x, simple_delta_move), data)
    data = re.sub(r'y1="(.*?)"', create_delta_move(y, simple_delta_move), data)
    data = re.sub(r'y2="(.*?)"', create_delta_move(y, simple_delta_move), data)
    data = re.sub(r'cx="(.*?)"', create_delta_move(x, simple_delta_move), data)
    data = re.sub(r'cy="(.*?)"', create_delta_move(y, simple_delta_move), data)
    data = re.sub(r' d="(.*?)"', create_delta_move(delta, path_delta_move), data)
    data = re.sub(r' points="(.*?)"', create_delta_move(delta, polyline_delta_move), data)
    return data


def element_delta_move(pat, delta):
    text = get_full_match(pat)
    text = move_all(text, delta)
    return text


def move_element(data, tag, svg_id, delta):
    search = r'<' + tag + ' id="' + svg_id + '".*?/>'
    if tag == 'g':
        search = r'<' + tag + ' id="' + svg_id + '".*?/>.*?</g>'
    elem_data = re.sub(search, create_delta_move(delta, element_delta_move), data)
    return elem_data


def move_elements(data, elements, delta):
    for element in elements:
        data = move_element(data, element[0], element[1], delta)
    return data


def apply_patch(data, patch):
    for change in patch['changes']:
        if change['type'] == 'substitute':
            data = re.sub(change['find'], change['replace'], data)
        if change['type'] == 'move_all':
            data = move_all(data, change['delta'])
        if change['type'] == 'move_element':
            data = move_element(data, change['tag'], change['id'], change['delta'])
        if change['type'] == 'move_elements':
            data = move_elements(data, change['elements'], change['delta'])

    # Add the patch identifier to avoid double patching
    data = data + PATCH_IDENTIFIER

    return data


def is_patched(data):
    return PATCH_IDENTIFIER in data


def patch_image_file(fw_path, patch_file):
    # Read the patch file
    f = open(patch_file)
    patch_data = f.read()
    f.close()
    patch = json.loads(patch_data)

    # Read the original SVG
    target_file = os.path.join(fw_path, 'content', 'display', patch['file'])
    f = open(target_file)
    svg_data = f.read()
    f.close()

    if is_patched(svg_data):
        return False

    # Change the SVG data
    new_data = apply_patch(svg_data, patch)

    # Make sure the data got patched
    if new_data == svg_data:
        print('No changes made, patch already applied?')
        return False

    # Write the patched data to the SVG file
    f = open(target_file, 'w')
    f.write(new_data)
    f.close()

    return True
