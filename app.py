from datetime import datetime, date

from flask import Flask,render_template, request, redirect, url_for

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import asc
from sqlalchemy.exc import IntegrityError

from base import init_db
from base import Base
from base import session_scope

app = Flask(__name__)

class Task(Base):

    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    detail = Column(String)
    due = Column(DateTime, nullable=False)

    @classmethod
    def create(cls, title, detail, due):
        task = cls(
            title=title,
            detail=detail,
            due=due
        )
        try:
            with session_scope() as session:
                session.add(task)
            return task
        except IntegrityError:
            return False

    @classmethod
    def get(cls):
        with session_scope() as session:
            tasks = session.query(cls).order_by(asc(cls.due)).all()

        if tasks is None:
            return None
        return tasks

    @classmethod
    def get_by_id(cls, id):
        with session_scope() as session:
            task = session.query(cls).filter(cls.id == id).first()
        if task is None:
            return None
        return task

    @classmethod
    def delete(cls, id):
        with session_scope() as session:
            session.query(cls).filter(cls.id == id).delete()

    @classmethod
    def update(cls):
        with session_scope() as session:
            session.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        tasks = Task.get()
        return render_template('index.html', posts=tasks, today=date.today())
    else:
        title = request.form.get('title')
        detail = request.form.get('detail')
        due = request.form.get('due')
        due = datetime.strptime(due, '%Y-%m-%d')
        b_create = Task.create(title, detail, due)

        return redirect('/')

@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/detail/<int:id>')
def read(id):
    post = Task.get_by_id(id)
    return render_template('detail.html', post=post)

@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    post = Task.get_by_id(id)
    if request.method == 'GET':
        return render_template('update.html', post=post)
    else:
        post.title = request.form.get('title')
        post.detail = request.form.get('detail')
        post.due = datetime.strptime(request.form.get('due'), '%Y-%m-%d')
        Task.update()
        return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
    Task.delete(id)
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run()
