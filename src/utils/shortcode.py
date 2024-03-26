import re
from functools import lru_cache

# Shortcode attributes parsing


class Shortcode:
    @staticmethod
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
    @staticmethod
    def shortcode_regex(tag):
        pattern = (
            r'\[(\[?)(' +
            re.escape(tag) +
            r')(?![\w-])([^\]/]*(?:/(?!\])[^\/]*)*?)(?:(/)\]|](?:([^\[]*(?:\[(?!/\2\])[^[]*)*)(\[/\2\]))?)(\]?)'
        )
        return re.compile(pattern, re.IGNORECASE)

    # Find the next matching shortcode

    @staticmethod
    def find_next(tag, text, index=0):
        """
        Find the next matching shortcode in the text starting from the given index.

        Args:
            tag (str): The shortcode tag to search for.
            text (str): The text in which to search for the shortcode.
            index (int, optional): The index in the text from which to start the search. Defaults to 0.

        Returns:
            dict or None: A dictionary containing the index where the shortcode is found,
                        the matched content, and the shortcode object. Returns None if no match is found.
        """
        # Generate the regular expression for the given tag
        regex = Shortcode.shortcode_regex(tag)

        # Search for the next match in the text starting from the given index
        match = regex.search(text, index)

        # Return None if no match is found
        if match is None:
            return None

        # Check if the match is an escaped shortcode, and if so, recurse to find the next one
        if match.group(1) == '[' and match.group(7) == ']':
            return Shortcode.find_next(tag, text, match.end())

        result = {
            'index': match.start(),
            'content': match.group(0),
            'shortcode': Shortcode.from_match(match.groups())
        }

        # Adjust the content and index if the shortcode is preceded by '['
        if match.group(1):
            result['content'] = result['content'][1:]
            result['index'] += 1

        # Adjust the content if the shortcode is followed by ']'
        if match.group(7):
            result['content'] = result['content'][:-1]

        return result


    # Replace matching shortcodes in text


    @staticmethod
    def replace(tag, text, callback):
        def replacer(match):
            left, right = match.group(1), match.group(7)
            if left == '[' and right == ']':
                return match.group(0)
            result = callback(Shortcode.from_match(match.groups()))
            return left + result + right if result or result == '' else match.group(0)

        return re.sub(Shortcode.shortcode_regex(tag), replacer, text)


    # Generate a shortcode object from a regex match


    @staticmethod
    def from_match(match):
        """
        Create a shortcode object from the regular expression match.

        Args:
            match (tuple): The match groups from the regular expression match.

        Returns:
            dict: A dictionary representing the shortcode with its tag, attributes, type, and content.
        """
        tag, attr_string, self_closing, content, closing_tag = match[1], match[2], match[3], match[4], match[5]
        type = 'single'

        if self_closing:
            type = 'self-closing'
        elif closing_tag:
            type = 'closed'

        attrs = Shortcode.parse_attrs(attr_string)

        return {
            'tag': tag,
            'attrs': attrs,  # Attributes are now parsed into a dictionary
            'type': type,
            'content': content
        }

    # Generate a string from shortcode parameters

    @staticmethod
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
