from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

class CodeBlockPreprocessor(Preprocessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.in_code_block = False
        self.code_lines = []
        self.language = None

    def _highlight_code(self):
        """Highlight the code block using Pygments."""
        try:
            lexer = get_lexer_by_name(self.language, stripall=True)
        except ClassNotFound:
            lexer = TextLexer()  # Fallback to plain text if language is not found

        formatter = HtmlFormatter()
        return highlight("\n".join(self.code_lines), lexer, formatter)

    def _reset_code_block(self):
        """Reset the code block state."""
        self.in_code_block = False
        self.code_lines = []
        self.language = None

    def run(self, lines):
        new_lines = []

        for line in lines:
            if line.startswith("```"):
                if self.in_code_block:
                    # End of code block, highlight the code
                    highlighted_code = self._highlight_code()
                    new_lines.append(highlighted_code)
                    self._reset_code_block()
                else:
                    # Start of code block, extract language
                    self.in_code_block = True
                    self.language = line[3:].strip() or "text"
            elif self.in_code_block:
                # Inside a code block, collect lines
                self.code_lines.append(line)
            else:
                # Outside a code block, add line as is
                new_lines.append(line)

        return new_lines

class CodeHighlightExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(CodeBlockPreprocessor(), 'code_highlight', 25)

def makeCodeHighlightExtension():
    return CodeHighlightExtension()