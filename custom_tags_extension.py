import markdown
from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
import re
import xml.etree.ElementTree as ET  # Используем стандартный модуль ElementTree

# Список допустимых имен тегов
VALID_TAGS = {
    'note', 'warning', 'info', 'tip', 'error', 'success', 'important',
    'code', 'lightbulb', 'pencil', 'plain'  # Добавили 'plain'
}

# Регулярное выражение для кастомных тегов
CUSTOM_TAG_PATTERN = r'^!!!(\w+)\s+(.*)$'  # Пример: !!!note Это заметка


class CustomTagProcessor(BlockProcessor):
    def test(self, parent, block):
        # Проверяем, начинается ли блок с !!!
        return re.match(CUSTOM_TAG_PATTERN, block)

    def run(self, parent, blocks):
        # Обрабатываем блок
        block = blocks.pop(0)
        match = re.match(CUSTOM_TAG_PATTERN, block)
        if not match:
            return False

        # Получаем имя тега и текст
        tag_name = match.group(1).lower()  # Имя тега (note, warning, info и т.д.)
        text = match.group(2).strip()  # Текст внутри тега

        # Проверяем, допустимо ли имя тега
        if tag_name not in VALID_TAGS:
            # Если тег недопустим, добавляем текст как обычный параграф
            p = ET.SubElement(parent, 'p')
            p.text = block  # Оставляем весь блок как текст
            return True

        # Создаем HTML-элемент
        div = ET.SubElement(parent, 'div')
        div.set('class', f'custom-tag {tag_name}')
        div.text = text

        return True


class CustomTagsExtension(Extension):
    def extendMarkdown(self, md):
        # Добавляем обработку кастомных тегов
        md.parser.blockprocessors.register(
            CustomTagProcessor(md.parser),
            'custom_tag_processor',
            175
        )


# Функция для создания расширения
def makeCustomTagsExtension(**kwargs):
    return CustomTagsExtension(**kwargs)
