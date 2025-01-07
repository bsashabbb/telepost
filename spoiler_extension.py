import re

from markdown import Markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree


class SpoilerPattern(InlineProcessor):
    def __init__(self, pattern, md):
        super(SpoilerPattern, self).__init__(pattern, md)

    def handleMatch(self, m: re.Match[str], data: str) -> tuple[etree.Element | str | None, int | None, int | None]:
        span = etree.Element('span')
        span.set('class', 'spoiler')

        text = m.group(1)
        span.text = text

        return span, m.start(0), m.end(0)


class SpoilerExtension(Extension):
    def extendMarkdown(self, md: Markdown) -> None:
        md.inlinePatterns.register(SpoilerPattern(r'\|\|(.*?)\|\|', md), 'spoiler', 175)


def makeSpoilerExtension(*args, **kwargs):
    return SpoilerExtension(*args, **kwargs)
