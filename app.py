from flask import Flask, request, jsonify, render_template
import sqlite3
import os
import yaml
from datetime import datetime

app = Flask(__name__)
DB_PATH = "/data/db/favs.db"

# Inicializar banco
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.execute('''CREATE TABLE IF NOT EXISTS favorites
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 title TEXT, url TEXT UNIQUE, timestamp TEXT,
                 category TEXT DEFAULT 'Sem Categoria', tags TEXT,
                 video_links TEXT)''')
conn.commit()

@app.route('/save', methods=['POST'])
def save_fav():
    data = request.json
    url = data['url']
    title = data['title']
    timestamp = data['timestamp']
    video_links = ','.join(data['direct_links']) if data['direct_links'] else ''

    try:
        conn.execute('INSERT INTO favorites (title, url, timestamp, video_links) VALUES (?, ?, ?, ?)',
                     (title, url, timestamp, video_links))
        conn.commit()
        return jsonify({"status": "success", "message": f"Link salvo: {title}"})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Link já existe!"})

@app.route('/')
def index():
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('SELECT * FROM favorites')
    favorites = cur.fetchall()
    # Estatísticas básicas
    stats = {
        'total': len(favorites),
        'by_category': dict(conn.execute('SELECT category, COUNT(*) FROM favorites GROUP BY category').fetchall())
    }
    return render_template('index.html', favorites=favorites, stats=stats)

@app.route('/update/<int:id>', methods=['POST'])
def update_fav(id):
    data = request.form
    category = data.get('category', 'Sem Categoria')
    tags = data.get('tags', '')
    conn.execute('UPDATE favorites SET category = ?, tags = ? WHERE id = ?', (category, tags, id))
    conn.commit()
    return jsonify({"status": "success", "message": "Atualizado!"})

@app.route('/delete/<int:id>', methods=['POST'])
def delete_fav(id):
    conn.execute('DELETE FROM favorites WHERE id = ?', (id,))
    conn.commit()
    return jsonify({"status": "success", "message": "Deletado!"})

@app.route('/export/<format>')
def export_favs(format):
    conn.row_factory = sqlite3.Row
    favorites = conn.execute('SELECT * FROM favorites').fetchall()
    data = [{'id': f['id'], 'title': f['title'], 'url': f['url'], 'timestamp': f['timestamp'],
             'category': f['category'], 'tags': f['tags'], 'video_links': f['video_links'].split(',') if f['video_links'] else []}
            for f in favorites]
    
    if format == 'yaml':
        with open('/data/export.yaml', 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, allow_unicode=True)
        return jsonify({"status": "success", "message": "Exportado como YAML!"})
    elif format == 'html':
        with open('/data/export.html', 'w', encoding='utf-8') as f:
            f.write('<html><body><ul>' + ''.join(f'<li><a href="{f["url"]}">{f["title"]}</a> - {f["category"]} - {f["tags"]}</li>' for f in data) + '</ul></body></html>')
        return jsonify({"status": "success", "message": "Exportado como HTML!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)