import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# This handles the database automatically on deployment
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///planora.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)
    priority = db.Column(db.Integer, default=1)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    tasks = Task.query.order_by(Task.priority.desc()).all()
    total = len(tasks)
    completed = len([t for t in tasks if t.done])
    progress = (completed / total * 100) if total > 0 else 0
    remaining = total - completed
    return render_template('index.html', tasks=tasks, progress=progress, remaining=remaining)

@app.route('/add', methods=['POST'])
def add_task():
    content = request.form.get('content')
    priority = int(request.form.get('priority', 0))
    if content:
        new_task = Task(content=content, priority=priority)
        db.session.add(new_task)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/toggle/<int:task_id>')
def toggle(task_id):
    task = Task.query.get(task_id)
    if task:
        task.done = not task.done
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/clear')
def clear_completed():
    Task.query.filter_by(done=True).delete()
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
