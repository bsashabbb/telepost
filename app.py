from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
db_path = "articles.db"


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
@app.route('/')
def index():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Запрос для получения заголовков постов
    c.execute('SELECT id, title FROM posts')
    posts = c.fetchall()
    conn.close()
    return render_template('index.html', posts=posts)


# Страница для просмотра конкретного поста по его ID
@app.route('/post/<int:post_id>')
def post(post_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT title, content, author FROM posts WHERE id = ?', (post_id,))
    post = c.fetchone()
    conn.close()
    if post:
        return render_template('post.html', post_id=post_id, title=post[0], content=post[1], author=post[2])
    else:
        return 'Post not found', 404


# Страница для создания нового поста
@app.route('/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author_ip = request.remote_addr  # Получаем IP-адрес

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('INSERT INTO posts (title, content, author) VALUES (?, ?, ?)', (title, content, author_ip))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('new_post.html')


# Страница для редактирования поста
@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Обработка POST-запроса для сохранения изменений
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        # Обновляем пост в базе данных
        c.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', (title, content, post_id))
        conn.commit()
        conn.close()
        return redirect(url_for('post', post_id=post_id))
    # Если метод GET, показываем форму редактирования с текущими данными поста
    c.execute('SELECT title, content FROM posts WHERE id = ?', (post_id,))
    post = c.fetchone()
    conn.close()
    if post:
        return render_template('edit_post.html', post_id=post_id, title=post[0], content=post[1])
    else:
        return 'Post not found', 404


# Операция для удаления поста
@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Удаляем пост по его ID
    c.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    create_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
