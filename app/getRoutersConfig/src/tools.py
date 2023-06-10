import re

def separate_section(separator, content):
    if content == "":
        return []

    lines = re.split(separator, content, flags=re.M)

    if len(lines) == 1:
        msg = "Unexpected output data:\n{}".format(lines)
        raise ValueError(msg)

    lines.pop(0)

    if len(lines) % 2 != 0:
        msg = "Unexpected output data:\n{}".format(lines)
        raise ValueError(msg)

    lines_iter = iter(lines)

    try:
        new_lines = [line + next(lines_iter, '') for line in lines_iter]
    except TypeError:
        raise ValueError()
    return new_lines