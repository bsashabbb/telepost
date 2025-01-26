from markdown.inlinepatterns import SimpleTagPattern
from markdown.extensions import Extension

# Регулярные выражения для sub и sup
SUB_PATTERN = r'(\+)(.*?)(\+)'  # +текст+
SUP_PATTERN = r'(\^)(.*?)(\^)'  # ^текст^

class SubSupExtension(Extension):
    def extendMarkdown(self, md):
        # Добавляем обработку sub и sup
        md.inlinePatterns.register(SimpleTagPattern(SUB_PATTERN, 'sub'), 'sub', 175)
        md.inlinePatterns.register(SimpleTagPattern(SUP_PATTERN, 'sup'), 'sup', 176)

# Функция для создания расширения
def makeSubSupExtension(**kwargs):
    return SubSupExtension(**kwargs)