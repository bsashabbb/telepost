import re

from markdown import Markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

class UrlPreprocessor(Preprocessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_pattern = re.compile(
            r'(?:'
            r'https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}'
            r'|'
            r'www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}'
            r'|'
            r'https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}'
            r'|'
            r'www\.[a-zA-Z0-9]+\.[^\s]{2,}'
            r'|'
            r'https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*\.[^\s]{2,}'
            r')'
        )

    def find_urls(self, text):
        return [match.group(0) for match in self.url_pattern.finditer(text)]

    def is_markdon_link(self, text, url):
        for match in re.finditer(re.escape(url), text):
            position = match.start()

            bracket_start = text.rfind('[', 0, position)
            if bracket_start == -1:
                continue

            bracket_end = text.find(']', bracket_start, position)
            if bracket_end == -1:
                continue

            paren_start = text.find('(', bracket_end + 1)
            if bracket_start == -1 or paren_start > position:
                continue

            paren_start = text.find(')', paren_start + 1)
            if bracket_start == -1:
                continue

            return True

        return False

    def create_anchor_tag(self, url):
        if url.startswith('www.') and not self.is_markdon_link(self._current_line, url):
            url = 'https://' + url
        return f'<a href="{url}">{url}</a>'

    def run(self, lines: list[str]) -> list[str]:
        new_lines = []
        for line in lines:
            self._current_line = line
            urls = self.find_urls(line)
            for url in urls:
                if not self.is_markdon_link(line, url):
                    line = line.replace(url, self.create_anchor_tag(url))
            new_lines.append(line)
        return new_lines


class UrlExtension(Extension):
    def extendMarkdown(self, md: Markdown) -> None:
        md.preprocessors.register(UrlPreprocessor(md), 'url', 25)


def makeURLExtension(*args, **kwargs):
    return UrlExtension(*args, **kwargs)
