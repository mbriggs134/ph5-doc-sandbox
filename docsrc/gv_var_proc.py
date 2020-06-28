#!/usr/bin/python
import re
import argparse
import os.path

VAR_REGEX = r'\s*//\s*#(\S*)=(\S*)' # ex: " // #name=value\n"

def find_var_pairs(filename, var_regex=VAR_REGEX):
    """
    Find name=value pairs inside a given file
    :param filename: filename for file to be scanned
    :return: dict with pairs or an empty dict if none are found
    """
    var_pairs = {}
    var_re = re.compile(var_regex)
    with open(filename, 'r') as f:
        for l in f:
            match = var_re.match(l)
            if match:
                name, val = match.groups()
                var_pairs.setdefault(name, val)
    return var_pairs

def get_formatted_lines(f, var_pairs):
    """
    Generator function for lines in file with each one being formatted with var_pairs
    This function does not support multi-line {format_vars}.
    Also escapes single '{' or '}' but no {formatt_vars} can be on the same line
    :param f: open file object
    :param var_pairs: dict of name, var pairs
    :return: yields line by line
    """
    l = next(f)
    while l:
        try:
            fmt_line = l.format(**var_pairs)
        except ValueError:
            l = l.replace('{', '{{').replace('}', '}}')
            fmt_line = l.format(**var_pairs)
        yield fmt_line
        l = next(f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Allow variables in txt using py format strings')
    parser.add_argument('input_filename', help='Input txt filename')
    parser.add_argument('output_filename', nargs='?',
                        help='Output txt filename (default: input-filled.ext)')
    args = parser.parse_args()
    if args.output_filename is None:
        base, ext = os.path.splitext(args.input_filename)
        args.output_filename = base+'-filled'+ext
    var_pairs = find_var_pairs(args.input_filename)
    if len(var_pairs) > 0:
        with open(args.input_filename, 'r') as in_f, \
                open(args.output_filename, 'w+') as out_f:
            for l in get_formatted_lines(in_f, var_pairs):
                out_f.writelines(l)
    else:
        print('No variables found.')

    print('{} written.'.format(args.output_filename))
