import markdown
from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
import re
import xml.etree.ElementTree as ET

# Регулярное выражение для цитат
QUOTE_PATTERN = r'^>\s+(.*)$'  # Пример: > Это цитата

class QuoteProcessor(BlockProcessor):
    def test(self, parent, block):
        # Проверяем, начинается ли блок с '>'
        return block.startswith('>')

    def run(self, parent, blocks):
        # Обрабатываем все строки, начинающиеся с '>'
        quote_lines = []
        while blocks and blocks[0].startswith('>'):
            # Убираем только первый '>' и лишние пробелы
            line = blocks.pop(0).lstrip('>').strip()
            quote_lines.append(line)

        # Если нет строк для цитаты, выходим
        if not quote_lines:
            return False

        # Создаем HTML-элемент для цитаты
        blockquote = ET.SubElement(parent, 'blockquote')
        blockquote.set('class', 'custom-quote')

        # Добавляем текст цитаты
        quote_text = ET.SubElement(blockquote, 'div')
        quote_text.set('class', 'quote-text')
        quote_text.text = '\n'.join(quote_lines)  # Сохраняем переносы строк

        return True

class QuoteExtension(Extension):
    def extendMarkdown(self, md):
        # Удаляем встроенный процессор цитат
        md.parser.blockprocessors.deregister('quote')
        # Добавляем наш кастомный процессор цитат
        md.parser.blockprocessors.register(
            QuoteProcessor(md.parser),
            'custom_quote_processor',
            70  # Приоритет (можно настроить)
        )

# Функция для создания расширения
def makeQuoteExtension(**kwargs):
    return QuoteExtension(**kwargs)
