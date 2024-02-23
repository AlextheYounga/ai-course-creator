import re
from functools import lru_cache

# Shortcode attributes parsing


@lru_cache(maxsize=None)
def parse_attrs(text):
    named = {}
    numeric = []
    pattern = re.compile(
        r'([\w-]+)\s*=\s*"([^"]*)"(?:\s|$)|'
        r'([\w-]+)\s*=\s*\'([^\']*)\'(?:\s|$)|'
        r'([\w-]+)\s*=\s*([^\'"\s]+)(?:\s|$)|'
        r'"([^"]*)"(?:\s|$)|'
        r'\'([^\']*)\'(?:\s|$)|'
        r'(\S+)(?:\s|$)'
    )

    text = text.replace(u'\u00a0', ' ').replace(u'\u200b', ' ')

    for match in pattern.finditer(text):
        groups = match.groups()
        if groups[0]:
            named[groups[0].lower()] = groups[1]
        elif groups[2]:
            named[groups[2].lower()] = groups[3]
        elif groups[4]:
            named[groups[4].lower()] = groups[5]
        elif groups[6]:
            numeric.append(groups[6])
        elif groups[7]:
            numeric.append(groups[7])
        elif groups[8]:
            numeric.append(groups[8])

    return {'named': named, 'numeric': numeric}

# Generate a regex for finding shortcodes


def shortcode_regex(tag):
    return re.compile(
        r'\[(\[?)(' +
        tag +
        r')(?![\w-])([^\]\/]*(?:\/(?!\])[^\]\/]*)*?)(?:(\/)\]|\](?:([^\[]*(?:\[(?!\/\2\])[^‌​\[]*)*)(\[\/\2\]))?)(\]?)',
        re.DOTALL
    )

# Find the next matching shortcode


def find_next(tag, text, index=0):
    regex = shortcode_regex(tag)
    match = regex.search(text, index)
    if not match:
        return None

    result = {
        'index': match.start(),
        'content': match.group(0),
        'shortcode': from_match(match.groups()),
    }

    if match.group(1) == '[':
        result['content'] = result['content'][1:]
        result['index'] += 1

    if match.group(7) == ']':
        result['content'] = result['content'][:-1]

    return result

# Replace matching shortcodes in text


def replace(tag, text, callback):
    def replacer(match):
        left, right = match.group(1), match.group(7)
        if left == '[' and right == ']':
            return match.group(0)
        result = callback(from_match(match.groups()))
        return left + result + right if result or result == '' else match.group(0)

    return re.sub(shortcode_regex(tag), replacer, text)

# Generate a shortcode object from a regex match


def from_match(match):
    type = 'self-closing' if match[3] else 'closed' if match[5] else 'single'
    attrs = parse_attrs(match[2]) if match[2] else {'named': {}, 'numeric': []}
    return {
        'tag': match[1],
        'attrs': attrs,
        'type': type,
        'content': match[4] or '',
    }

# Generate a string from shortcode parameters


def shortcode_string(options):
    tag = options.get('tag', '')
    attrs = options.get('attrs', {})
    type = options.get('type', '')
    content = options.get('content', '')

    attrs_string = ''
    for name, value in attrs.get('named', {}).items():
        attrs_string += f' {name}="{value}"'
    for value in attrs.get('numeric', []):
        attrs_string += f' "{value}"'

    if type == 'self-closing':
        return f'[{tag}{attrs_string} /]'
    elif type == 'closed':
        return f'[{tag}{attrs_string}]{content}[/{tag}]'
    else:
        return f'[{tag}{attrs_string}]'
