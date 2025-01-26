from markdown import Markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
import xml.etree.ElementTree as etree
import re


class ColorPattern(Pattern):
    COLOR_RE = re.compile(r'\[color:(.+?)\]')
    COLOR_FG_BG_RE = re.compile(r'\[color:(.*?):(.*?) (.*?)\]')

    def handleMatch(self, m: re.Match[str]) -> etree.Element | str:
        math_fg_bg = self.COLOR_FG_BG_RE.match(m.string[m.start():])
        if math_fg_bg:
            fg_color = math_fg_bg.group(1).strip()
            bg_color = math_fg_bg.group(2).strip()
            text = math_fg_bg.group(3).strip()
            span = etree.Element('span')
            style = ''
            if fg_color:
                style += f'color:{fg_color};'
            if bg_color:
                style += f'background-color:{bg_color};'
            style += 'display:inline-block;padding:0.2em;'
            span.set('style', style)
            span.text = text
            return span
        else:
            match_color = self.COLOR_RE.match(m.string[m.start():])
            if match_color:
                color = match_color.group(1).strip()
                text = m.string[m.end():].strip()
                end_index = m.end()
                while m.string[end_index] != '[':
                    end_index += 1
                    if end_index == len(m.string):
                        break
                text = m.string[m.end():end_index].strip()
                span = etree.Element('span')
                span.set('style', f'color: {color}; display: inline-block; padding: 0 0.2em')
                span.text = text
                return span
            else:
                return None


class ColorExtension(Extension):
    def extendMarkdown(self, md: Markdown) -> None:
        color_pattern = ColorPattern(r'\[color:.+?\]')
        md.inlinePatterns.register(color_pattern, 'color', 175)


def makeColorExtension(**kwargs):
    return ColorExtension(**kwargs)
