from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)

# Путь к файлу с записями
DATA_FILE = 'entries.json'

# Функция загрузки записей из файла
def load_entries():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Функция сохранения записей в файл
def save_entries(entries):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

# Загружаем записи при старте
entries = load_entries()

# ------------------------------------------------------------
# ГЛАВНАЯ СТРАНИЦА (список записей)
@app.route('/')
def index():
    return render_template('index.html', entries=entries)

# ------------------------------------------------------------
# ПРОСМОТР ОДНОЙ ЗАПИСИ
@app.route('/entry/<int:entry_id>')
def detail(entry_id):
    entry = next((e for e in entries if e['id'] == entry_id), None)
    if entry is None:
        return "Запись не найдена", 404
    return render_template('detail.html', entry=entry)

# ------------------------------------------------------------
# ДОБАВЛЕНИЕ ЗАПИСИ
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        if title and content:
            # Генерируем новый ID
            new_id = max([e['id'] for e in entries], default=0) + 1
            
            # Создаём новую запись
            entry = {
                'id': new_id,
                'title': title,
                'content': content,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
            entries.append(entry)
            save_entries(entries)
        return redirect(url_for('index'))
    
    return render_template('add.html')

# ------------------------------------------------------------
# РЕДАКТИРОВАНИЕ ЗАПИСИ
@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit(entry_id):
    entry = next((e for e in entries if e['id'] == entry_id), None)
    if entry is None:
        return "Запись не найдена", 404
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        if title and content:
            entry['title'] = title
            entry['content'] = content
            save_entries(entries)
        return redirect(url_for('index'))
    
    return render_template('edit.html', entry=entry)

# ------------------------------------------------------------
# УДАЛЕНИЕ ЗАПИСИ
@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete(entry_id):
    global entries
    entries = [e for e in entries if e['id'] != entry_id]
    save_entries(entries)
    return redirect(url_for('index'))

# ------------------------------------------------------------
# ПОИСК ПО ЗАГОЛОВКУ
@app.route('/search')
def search():
    query = request.args.get('q', '').strip().lower()
    if query:
        filtered = [e for e in entries if query in e['title'].lower()]
    else:
        filtered = entries
    return render_template('index.html', entries=filtered)

# ------------------------------------------------------------
# ФИЛЬТР ЗА ПОСЛЕДНИЕ 7 ДНЕЙ
@app.route('/filter/week')
def filter_week():
    from datetime import datetime, timedelta
    week_ago = datetime.now() - timedelta(days=7)
    filtered = []
    for e in entries:
        try:
            entry_date = datetime.strptime(e['date'], '%Y-%m-%d %H:%M')
            if entry_date >= week_ago:
                filtered.append(e)
        except:
            pass
    return render_template('index.html', entries=filtered)

# ------------------------------------------------------------
# ЗАПУСК ПРИЛОЖЕНИЯ
if __name__ == '__main__':
    app.run(debug=True)