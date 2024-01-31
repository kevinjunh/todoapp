from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    date = db.Column(db.DateTime)
    priority = db.Column(db.String(10))
    completed = db.Column(db.Boolean, default=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref=db.backref('todos', lazy=True))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

# Show tasks
@app.route("/", methods=["GET", "POST"])
def home():
    todo_list = Todo.query.all()
    projects = Project.query.all()
    return render_template("index.html", todo_list=todo_list, projects=projects)

@app.route("/add_project", methods=["POST"])
def add_project():
    new_project_name = request.form.get('new_project')
    new_project = Project(name=new_project_name)
    db.session.add(new_project)
    db.session.commit()
    return redirect(url_for("home"))

# Add tasks
@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    priority = request.form.get("priority")
    
    date_str = request.form.get("date")
    date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else None

    project_id = request.form.get("project")

    if project_id == "new":
        new_project_name = request.form.get('new_project')
        existing_project = Project.query.filter_by(name=new_project_name).first()
        if existing_project:
            project = existing_project
        else:
            new_project = Project(name=new_project_name)
            db.session.add(new_project)
            db.session.commit()
            project = new_project
    else:
        project = Project.query.get(project_id)

    new_todo = Todo(title=title, priority=priority, date=date, project=project)

    db.session.add(new_todo)
    db.session.commit()

    return redirect(url_for("home"))

#complete tasks
@app.route("/complete/<int:todo_id>", methods=["POST"])
def complete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    if todo:
        todo.completed = not todo.completed
        db.session.commit()
    return redirect(url_for("home"))

# Delete tasks
@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))

# Edit tasks
@app.route("/edit/<int:todo_id>", methods=["GET", "POST"])
def edit(todo_id):
    todo = Todo.query.get(todo_id)
    if request.method == "POST":
        todo.title = request.form["title"]

        if "priority" in request.form:
            todo.priority = request.form["priority"]

        date_string = request.form["date"]
        todo.date = datetime.strptime(date_string, '%Y-%m-%d') if date_string else None

        project_id = request.form["project"]
        new_project_name = request.form.get('new_project')

        if project_id == "new" and new_project_name:
            existing_project = Project.query.filter_by(name=new_project_name).first()

            if existing_project:
                todo.project = existing_project
            else:
                new_project = Project(name=new_project_name)
                db.session.add(new_project)
                db.session.commit()
                todo.project = new_project
        else:
            todo.project = Project.query.get(project_id)

        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", todo=todo, projects=Project.query.all())

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
