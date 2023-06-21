#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

def align_tabs(str, min_size=1):
    lines = str.split("\n")

    while True:
        found = False

        max_tab_offset = -1
        for line in lines:
            index = line.find('\t')
            if index != -1: found = True
            max_tab_offset = max(max_tab_offset, index)

        new_lines = []
        for line in lines:
            index = line.find('\t')
            if index == -1:
                new_lines.append(line)
                continue
            difference = (max_tab_offset + min_size - index)
            new_lines.append(line.replace('\t', " "*difference, 1))
        lines = new_lines

        if not found:
            break

    return '\n'.join(lines)

def format_dhm(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if d > 0:
        return f'{d:d}d,{h:02d}h:{m:02d}m'
    else:
        return f'{h:02d}h:{m:02d}m'

def format_dhms(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if d > 0:
        return f'{d:d}d,{h:02d}h:{m:02d}m'
    elif h > 0:
        return f'{h:02d}h:{m:02d}m'
    else:
        return f'{m:02d}m:{s:02d}s'

def make_psep(x=None, sep_char='-', width=80):
    w = width
    if x is None:
        return (sep_char * w)
    else:
        s = " " + x.strip() + " "
        d = (w - len(s)) // 2
        return (sep_char * d + s + sep_char * d)

def pprint(x, long=True, indent=4, limit_lines=None):
    import json
    if long:
        str = json.dumps(x, indent=4)
        if limit_lines is None:
            print(str)
        else:
            lines = str.split('\n')
            for i in range(0, min(len(lines), limit_lines)):
                print(lines[i])
            if i != len(lines):
                print('...')
    else:
        import pprint

        pp = pprint.PrettyPrinter(indent=indent, compact=not long)
        return pp.pprint(x)

def psep(x=None, sep_char="-", width=80):
    print(make_psep(x, sep_char, width))

def lookahead(iterable):
    it = iter(iterable)
    last = next(it)
    for val in it:
        yield last, True
        last = val
    yield last, False
