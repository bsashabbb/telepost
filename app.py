import html
import os
import secrets
import sqlite3

import bleach
import markdown
from bleach.css_sanitizer import CSSSanitizer
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, validators

from color_text_extension import makeColorExtension
from custom_tags_extension import makeCustomTagsExtension
from quote_extension import makeQuoteExtension
from s_u_mark_md_extension import makeSUMarkExtension
from spoiler_extension import makeSpoilerExtension
from sub_sup_extension import makeSubSupExtension
from code_highlight_extension import makeCodeHighlightExtension


class PostForm(FlaskForm):
    title = StringField('Заголовок', [
        validators.Length(min=5, max=150, message="Заголовок должен содержать от 5 до 150 символов")
    ])
    content = TextAreaField('Содержание', [
        validators.Length(min=10, message="Содержание должно содержать не менее 10 символов")
    ])


# Путь к файлу с ключом (в корне проекта)
SECRET_KEY_FILE = '.secret_key'

# Генерация или загрузка ключа
if not os.path.exists(SECRET_KEY_FILE):
    # Генерируем новый ключ
    secret_key = secrets.token_hex(24)
    with open(SECRET_KEY_FILE, 'w') as f:
        f.write(secret_key)
    os.chmod(SECRET_KEY_FILE, 0o600)  # Права только для владельца
else:
    # Читаем существующий ключ
    with open(SECRET_KEY_FILE, 'r') as f:
        secret_key = f.read().strip()

app = Flask('TelePost')
app.config['SECRET_KEY'] = secret_key  # Используем сохранённый ключ
db_path = "articles.db"
ALLOWED_TAGS = {
    'p', 'strong', 'b', 'em', 's', 'u', 'a', 'ul',
    'ol', 'li', 'br', 'hr', 'blockquote', 'img', 'mark',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'pre', 'code', 'div', 'span', 'class',
    'details', 'summary', 'sup', 'sub', 'video', 'audio'
}
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['alt', 'src'],
    'span': ['style'],
    'code': ['lang'],
    '*': ['class']
}
CSS_SANITIZER = CSSSanitizer(
    allowed_css_properties=['color', 'background-color', 'display', 'padding']
)


# Функция для создания базы данных, если она ещё не существует
def create_db():
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        # Создаём таблицу для хранения постов
        c.execute(
            '''CREATE TABLE posts (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, author TEXT)''')
        conn.close()


# Главная страница с отображением списка публикаций
@app.route('/', methods=['GET', 'POST'])  # TODO: убрать IP адрес в post ответах
def index():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Запрос для получения заголовков постов
    c.execute('SELECT id, title, author FROM posts')
    all_posts = c.fetchall()
    conn.close()
    user_posts = []
    for post in all_posts:
        if post[2] == request.remote_addr:
            user_posts.append(post)
    posts = []
    for post in user_posts:
        if len(post[1]) > 50:
            new_title = post[1][:50] + '...'
            posts.append((post[0], new_title))
            continue
        posts.append((post[0], post[1]))
    if request.method == 'POST':
        return user_posts
    return render_template('index.html', posts=posts)


@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/api-docs')
def api_docs():
    return render_template('api-docs.html')


# Страница для просмотра конкретного поста по его ID
@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT title, content, author FROM posts WHERE id = ?', (post_id,))
    post = c.fetchone()
    conn.close()
    if request.method == 'POST':
        if post:
            return {
                "ok": True,
                "result": {
                    "title": post[0],
                    "content": post[1]
                }
            }
        else:
            return {
                "ok": False,
                "error_code": 404,
                "description": "Post Not Found"
            }, 404
    if post:
        stripped_content = post[1].strip()
        md_content = markdown.markdown(
            stripped_content,
            extensions=[
                'tables',
                'fenced_code',
                'codehilite',
                'nl2br',
                makeSUMarkExtension(),
                makeSpoilerExtension(),
                makeColorExtension(),
                makeSubSupExtension(),
                makeCustomTagsExtension(),
                makeQuoteExtension()
            ],
            extension_configs={
                'codehilite': {
                    'linenums': True,
                    'css_class': 'highlight'
                }
            }
        )
        linkify_content = bleach.linkify(md_content)
        esc_content = bleach.clean(linkify_content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES,
                                   css_sanitizer=CSS_SANITIZER)
        return render_template('post.html', post_id=post_id, title=post[0],
                               content=esc_content, author=post[2], user=request.remote_addr)
    else:
        return render_template('error.html', code=404, error='Post Not Found'), 404


@app.route('/raw/<int:post_id>')
def raw_post(post_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT title, content, author FROM posts WHERE id = ?', (post_id,))
    post = c.fetchone()
    conn.close()
    if post:
        return f'<pre>{html.escape(post[1])}</pre>'
    else:
        return render_template('error.html', code=404, error='Post Not Found'), 404


# Страница для создания нового поста
@app.route('/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author_ip = request.remote_addr  # Получаем IP-адрес

        if not title or len(title) < 5:
            return {
                "ok": False,
                "error_code": 400,
                "description": "Title must be at least 5 characters long"
            }, 400
        if not content or len(content) < 10:
            return {
                "ok": False,
                "error_code": 400,
                "description": "Content must be at least 10 characters long"
            }, 400

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('INSERT INTO posts (title, content, author) VALUES (?, ?, ?)', (title, content, author_ip))
        post_id = c.lastrowid
        conn.commit()
        conn.close()
        return redirect(url_for('post', post_id=post_id))

    form = PostForm()
    return render_template('new_post.html', form=form)


# Страница для редактирования поста
@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT title, content, author FROM posts WHERE id = ?', (post_id,))
    post = c.fetchone()
    # Обработка POST-запроса для сохранения изменений
    if request.method == 'POST':
        if post:
            if post[2] == request.remote_addr:
                title = request.form['title']
                content = request.form['content']
                if not title or len(title) < 5:
                    return {
                        "ok": False,
                        "error_code": 400,
                        "description": "Title must be at least 5 characters long"
                    }, 400
                if not content or len(content) < 10:
                    return {
                        "ok": False,
                        "error_code": 400,
                        "description": "Content must be at least 10 characters long"
                    }, 400
                # Обновляем пост в базе данных
                c.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', (title, content, post_id))
                conn.commit()
                conn.close()
                return redirect(url_for('post', post_id=post_id))
            else:
                return {
                    "ok": False,
                    "error_code": 403,
                    "description": "You are not authorized to edit this post"
                }, 403
        else:
            return {
                "ok": False,
                "error_code": 404,
                "description": "Post Not Found"
            }, 404
    conn.close()
    # Если метод GET, показываем форму редактирования с текущими данными поста
    if post:
        if post[2] == request.remote_addr:
            form = PostForm(title=post[0], content=post[1])
            return render_template('edit_post.html', post_id=post_id, title=post[0], content=post[1], form=form)
        else:
            return render_template('error.html', code=403, error='You are not authorized to edit this post'), 403
    else:
        return render_template('error.html', code=404, error='Post Not Found'), 404


@app.route('/delete/<int:post_id>', methods=['GET', 'POST'])
def delete_post(post_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT title, content, author FROM posts WHERE id = ?', (post_id,))
    post = c.fetchone()

    if not post:
        conn.close()
        return render_template('error.html', code=404, error='Post Not Found'), 404

    if request.method == 'POST':
        # Проверяем, что IP-адрес пользователя совпадает с автором поста
        if post[2] == request.remote_addr:
            # Удаляем пост
            c.execute('DELETE FROM posts WHERE id = ?', (post_id,))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        else:
            conn.close()
            return {
                "ok": False,
                "error_code": 403,
                "description": "You are not authorized to delete this post"
            }, 403

    # Если метод GET, показываем страницу подтверждения
    conn.close()
    return render_template('delete.html', post_id=post_id, title=post[0])


if __name__ == '__main__':
    create_db()
    app.run(host='0.0.0.0', port=5000)
