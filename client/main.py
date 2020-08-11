from  flask import Flask, render_template, flash, url_for, redirect, session
from flask_bootstrap import Bootstrap
import requests
from config import Config

from forms import SignUpForm, LoginForm, Todoform, EditTodoForm, DeleteTodoForm
 
from  flask_csv import send_csv

import datetime


API_SIGNIN = "https://todosproyectpm.ue.r.appspot.com/api/signup"
API_LOGIN = "https://todosproyectpm.ue.r.appspot.com/api/login"
API_LOGOUT = "https://todosproyectpm.ue.r.appspot.com/api/logout"
API_GET_TODOS = "https://todosproyectpm.ue.r.appspot.com/api/todos_list"
API_ADD_TODO = "https://todosproyectpm.ue.r.appspot.com/api/add_todo"
API_EDIT_TODO ="https://todosproyectpm.ue.r.appspot.com/api/update_todo"
API_DELETE_TODO = "https://todosproyectpm.ue.r.appspot.com/api/delete_todo"

def create_app():
    app = Flask(__name__)
    bootstrap = Bootstrap(app)
    app.config.from_object(Config)
    return app

app = create_app()

@app.errorhandler(404)
def not_found(error):
    context = {
        "error" : error
    }

    return render_template("404.html", **context)

@app.errorhandler(500)
def server_error(error):
    context = {
        "error" : error
    }

    return render_template("500.html", **context)


@app.route("/signup", methods=["GET","POST"])
def signup():

    signup_form = SignUpForm()
    context = {
        "signup_form" : signup_form
    }

    if signup_form.validate_on_submit():

        email = signup_form.email.data
        username = signup_form.username.data
        password = signup_form.password.data
        confirm = signup_form.confirm.data

        if password != confirm:
            flash("Las contraseñas no coinciden")
            return redirect(url_for("signup"))

        params = {
                    "username" : username,
                    "email" : email,
                    "password" : password,
                 }

        api_response = requests.post(API_SIGNIN, json= params)
        body = api_response.json()
        if api_response.status_code == 201:
            session['username'] = username
            flash("Usuario creado con éxito")
            return redirect(url_for("index"))
        else:
            flash(str(body["message"]))

    
    return render_template("signup.html", **context)


@app.route("/login", methods=["GET","POST"])
def login():

    if  not 'username' in session:

        login_form = LoginForm()
        context = {
            "login_form": login_form 
        }
        
        if login_form.validate_on_submit():

            username = login_form.username.data
            password = login_form.password.data

            params = {
                "username" : username,
                "password" : password,
            }

            api_response = requests.post(API_LOGIN, json= params)
            body = api_response.json()

            if api_response.status_code == 201:
                session['username'] = username
                flash(f"Sesión iniciada correctamente, {str(username).title()} ")
                return redirect(url_for("index"))

            else:
                flash(str(body["message"]))



        return render_template("login.html", **context)
    
    else:
        flash(f"Ya has iniciado sesión")
        return redirect(url_for("index"))



@app.route("/logout", methods=["GET","POST"])
def logout():

    try:
        username = session['username']
        params = { "username" : username}

        api_response = requests.post(API_LOGOUT, json= params)
        body = api_response.json()

        print(api_response.status_code)

        if api_response.status_code == 400:
            session.pop('username')
            flash("Sesión Cerrada")
            return redirect(url_for("login"))
        else:
            flash(str(body["message"]))

        return redirect(url_for("index"))

    except (KeyError, TypeError):
        flash("No has iniciado sesión")
        return redirect(url_for("login"))


@app.route("/", methods=["GET","POST"])
def index():

    if 'username' in session:
        
        params = {
            "username" : session['username']
        }

        api_response = requests.post(API_GET_TODOS, json= params)
        body = api_response.json()

         
        todo_form = Todoform( prefix = "todo_add")

        edit_todo_forms = []
        delete_todo_forms = []
        for index, todo in enumerate(body["data"]["todos"]) : 

            deadline = todo["deadline"]

            if todo["deadline"] != "None":
                deadline = datetime.datetime.strptime(todo["deadline"],"%Y-%m-%d")
            else :
                deadline = None

            todo_dict = { 
                "title" : todo["title"],
                "description" : todo["description"],
                "priority": todo["priority"],
                "deadline": deadline,
                "status" : todo["status"],
                "todo_id" : todo["id"]
            }

            edit_todo_forms.append(EditTodoForm( prefix = f"todo_edit{index}",
                                                 data =  todo_dict ))

            delete_dict = {
                "todo_id" : todo["id"]
            }

            delete_todo_forms.append(DeleteTodoForm( prefix = f"todo_delete{index}",
                                                     data = delete_dict ))


        context = {
            "username" : session['username'],
            "todo_form" : todo_form,
            "todos" : body["data"]["todos"],
            "edit_forms" : edit_todo_forms,
            "delete_forms" : delete_todo_forms,
            "index" : 0,
        }

        
        if todo_form.validate_on_submit():

            params = {
                "username" : session['username'],
                "title" : todo_form.title.data,
                "description" : todo_form.description.data,
                "priority" : todo_form.priority.data,
                "deadline" : str(todo_form.deadline.data)
            }

            api_response = requests.post(API_ADD_TODO, json= params)
            body = api_response.json()

            if api_response.status_code == 201:
                flash("Tarea Creada con éxito")
                return redirect(url_for("index"))

            else:
                flash("Error creando tarea intente nuevamente")
                flash(str(body["message"]))


            return redirect(url_for("index"))

        for edit_form in edit_todo_forms:

            if edit_form.validate_on_submit():

                params = {
                    "username" : session['username'],
                    "title" : edit_form.title.data,
                    "description" : edit_form.description.data,
                    "priority" : edit_form.priority.data,
                    "deadline" : str(edit_form.deadline.data),
                    "status" : edit_form.status.data,
                    "todo_id": edit_form.todo_id.data,
                }

                api_response = requests.post(API_EDIT_TODO, json= params)
                body = api_response.json()

                if api_response.status_code == 200:
                    flash("Tarea editada con éxito")
                    return redirect(url_for("index"))

                else:
                    flash("Error editando tarea intente nuevamente")
                    flash(str(body["message"]))


        for delete_form in delete_todo_forms:
            if delete_form.validate_on_submit():
                params = {
                    "username" : session['username'],
                    "todo_id": delete_form.todo_id.data,
                }

                
                api_response = requests.delete(API_DELETE_TODO, json = params)
                body = api_response.json()

                if api_response.status_code == 200:
                    flash("Tarea eliminada")
                    return redirect(url_for("index"))

                else:
                    flash("Error eliminando tarea intente nuevamente")
                    flash(str(body["message"]))


        return render_template("index.html", **context)


    
    else:
        flash("No has iniciado sesión")
        return redirect(url_for("login"))


@app.route("/download")
def download():

    params = {
        "username" : session['username']
    }

    api_response = requests.post(API_GET_TODOS, json= params)
    body = api_response.json()
    data = body["data"]["todos"]

    return send_csv(data,"My_todo_lits.csv", ["title","description","deadline","priority","status","id"])




if __name__ == '__main_':
    app.run(debug=True, port=5001)

    