from markdown import Markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import SimpleTagPattern

HIGHLIGHT_RE = r'(==)(.*?)(==)'
UNDERLINE_RE = r'(~)(.*?)(~)'
STRIKETHROUGH_RE = r'(~~)(.*?)~~'


class SUMarkMDExtension(Extension):
    def extendMarkdown(self, md: Markdown) -> None:
        md.inlinePatterns.register(SimpleTagPattern(HIGHLIGHT_RE, 'mark'), 'highlight', 175)
        md.inlinePatterns.register(SimpleTagPattern(UNDERLINE_RE, 'u'), 'underline', 175)
        md.inlinePatterns.register(SimpleTagPattern(STRIKETHROUGH_RE, 's'), 'strikethrough', 176)

def makeSUMarkExtension(*args, **kwargs):
    return SUMarkMDExtension(*args, **kwargs)
