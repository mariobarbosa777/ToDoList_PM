from flask import request, redirect, render_template, session, url_for, flash
import unittest

from flask_login import login_required, current_user, login_user, logout_user
from flask import jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash


from app import create_app
from app.models import UserModel, UserData

from app.firestore_service import update_todo, get_todos, put_todo, delete_todo
from app.firestore_service import get_user, user_put, update_todo_all


app = create_app()

# Response function
def make_response(error: bool, message: str, status: int, data={}):
    """
    Create a homogenized response
    Params:
    - error: bool, The status of error
    - message: str, A message to user for operation status
    - status: int, HTTP status code
    """
    res = jsonify({'error': error, 'message': message, 'data': data})
    return res, status


@app.errorhandler(404)
def not_found(error):
    message = "This Page Does Not Exists "
    return make_response(error=True, message=message, status=404)

@app.errorhandler(500)
def server_error(error):
    message = "Server Error"
    return make_response(error=True, message=message, status=500)

@app.route('/')
def index():
    message = "This Page Does Not Exists "
    return make_response(error=True, message=message, status=404)

# @app.route('/hello', methods=['GET','POST'])
# @login_required
# def hello():
#     username = current_user.id
#     todo_form = Todoform()
#     delete_form = DeleteTodoForm()
#     update_form = UpdateTodoForm()

#     context = {
#         'todos': get_todos(user_id = username),
#         'username': username,
#         'todo_form': todo_form,
#         "delete_form" : delete_form,
#         "update_form" : update_form
#     }

#     if todo_form.validate_on_submit():

#         put_todo (user_id = username, title= todo_form.title.data,
#                                       description = todo_form.description.data,
#                                       priority  = todo_form.priority.data,
#                                       deadline = str(todo_form.deadline.data))
#         flash("Tarea Creada con éxito")

#         return redirect(url_for("hello"))


#     return render_template('hello.html', **context)


# @app.route("/todos/delete/<todo_id>",methods=['POST'])
# def delete(todo_id):
#     user_id = current_user.id
#     delete_todo (user_id=user_id, todo_id=todo_id)

#     return redirect(url_for("hello"))

# @app.route("/todos/update/<todo_id>/<int:done>",methods=['GET','POST'])
# def update(todo_id, done):
#     user_id = current_user.id
#     print(done)
#     update_todo (user_id=user_id, todo_id=todo_id, status=done)

#     return redirect(url_for("hello"))


@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        body = request.get_json()

        email = body["email"]
        username = body["username"]
        password = body["password"]

        user_doc = get_user(username)

        if user_doc.to_dict() is None:
            password_hash = generate_password_hash(password)
            user_data = UserData(username,password_hash,email)
            user_put(user_data)

            session['username'] = username

            return make_response(error=False, message="User created", status=201)

        else: 
            return make_response(error=True, message="User already exist", status=400)

    except (KeyError, TypeError):
        # If invalid body schema
        message = 'username, email and password are needed'
        return make_response(error=True, message=message, status=400)

    except Exception:
        # Return a 500 error if something went wrong
        return make_response(error=True, message='Server serror', status=500)



@app.route('/api/login', methods=['POST'])
def login():
    try:
        body = request.get_json()
        username = body["username"]
        password = body["password"]

        user_doc = get_user(username)

        

        if user_doc.to_dict() is not  None:
            password_from_db = user_doc.to_dict()["password"]

            if check_password_hash(password_from_db,password):
                
                session['username'] = username

                todo_list = get_todos(user_id = username)

                all_todo_dict = { "username": username }

                todo_array = []                
                for todo in todo_list:
                    todo_elements=todo.to_dict()
                    todo_elements["id"] = todo.id
                    todo_array.append(todo_elements)

                
                all_todo_dict["todos"] = todo_array 
                
                

                return make_response(error=False, message="Successful Login", status=201, data=all_todo_dict)
            else:
                return make_response(error=True, message="Password is Wrong", status=400)
        else: 
            return make_response(error=True, message="User does not exits", status=400)

    except (KeyError, TypeError):
        # If invalid body schema
        message = 'username and password are needed'
        return make_response(error=True, message=message, status=400)

    except Exception:
        # Return a 500 error if something went wrong
        return make_response(error=True, message='Server serror', status=500)


@app.route('/api/logout', methods=['POST'])
def logout():
    try: 
        body = request.get_json()
        username = body["username"]

        session.pop('username')

        return make_response(error=False, message=f"Close session for  {username}", status=200)

    
    except (KeyError, TypeError):
        # If invalid body schema
        message = 'No posible to Logout'
        return make_response(error=True, message=message, status=400)

    except Exception:
        # Return a 500 error if something went wrong
        return make_response(error=True, message='Server error', status=500)



@app.route('/api/todos_list', methods=['POST'])
def todo_list():
    try: 

        body = request.get_json()
        username = body["username"]
        todo_list = get_todos(user_id = username)

        todo_list = get_todos(user_id = username)

        all_todo_dict = { "username": username }

        todo_array = []                
        for todo in todo_list:
            todo_elements=todo.to_dict()
            todo_elements["id"] = todo.id
            todo_array.append(todo_elements)

        
        all_todo_dict["todos"] = todo_array 

        return make_response(error=False, message="To Do list get", status=200, data=all_todo_dict)

   
    except (KeyError, TypeError):
        # If invalid body schema
        message = 'No Complete data'
        return make_response(error=True, message=message, status=400)

    except Exception:
        # Return a 500 error if something went wrong
        return make_response(error=True, message='Server error', status=500)


@app.route('/api/add_todo', methods=['POST'])
def add_todo_list():

    try: 

        body = request.get_json()
        username = body["username"]
        title = body["title"]
        description = body["description"]
        priority = body["priority"]
        deadline = body["deadline"]


        put_todo (user_id = username,   title = title,
                                        description = description,
                                        priority  = priority,
                                        deadline = deadline)


        return make_response(error=False, message="Todo added", status=201)
        
    except (KeyError, TypeError):
        # If invalid body schema
        message = 'No Complete data to add ToDo'
        return make_response(error=True, message=message, status=400)

    except Exception:
        # Return a 500 error if something went wrong
        return make_response(error=True, message='Server error', status=500)


@app.route('/api/delete_todo', methods=['DELETE'])
def delete_todo_list():
    try:

        body = request.get_json()
        username = body["username"]
        todo_id = body["todo_id"]

        delete_action = delete_todo(user_id = username, todo_id = todo_id)

        if delete_action == True :
            return make_response(error=False, message="Todo deleted", status=200)
        else :
            return make_response(error=True, message="Todo Id does not exists", status=400)
        
    except (KeyError, TypeError):
        # If invalid body schema
        message = 'No Complete data to Delete ToDo'
        return make_response(error=True, message=message, status=400)

    except Exception:
        # Return a 500 error if something went wrong
        return make_response(error=True, message='Server error', status=500)


@app.route('/api/get_todos_list', methods=['GET'])
def get_todos_list():  
    try: 

        body = request.get_json()
        username = body["username"]

        todo_list = get_todos(user_id = username)

        all_todo_dict=[]
        for todo in todo_list:
            todo_elements=todo.to_dict()
            todo_elements["id"] = todo.id
            all_todo_dict.append(todo_elements)

        return make_response(error=False, message="To Do list get", status=200, data=all_todo_dict)

    except (KeyError, TypeError):
        # If invalid body schema
        message = 'No Complete data to Delete ToDo'
        return make_response(error=True, message=message, status=400)

    except Exception:
        # Return a 500 error if something went wrong
        return make_response(error=True, message='Server error', status=500)

@app.route('/api/update_status_todo', methods=['POST'])
def update_status():
    try: 

        body = request.get_json()
        username = body["username"]
        todo_id = body["todo_id"]
        status = body["status"]

        update_todo (user_id=username, todo_id=todo_id, status=status)


        return make_response(error=False, message="To do status Update", status=200)
    

    except (KeyError, TypeError):
        # If invalid body schema
        message = 'No Complete data to update status ToDo'
        return make_response(error=True, message=message, status=400)

    except Exception:
        # Return a 500 error if something went wrong
        return make_response(error=True, message='Server error', status=500)

@app.route('/api/update_todo', methods=['POST'])
def update_all_status():
    try: 
        
        body = request.get_json()
        username = body["username"]
        todo_id = body["todo_id"]
        title = body["title"]
        description = body["description"]
        priority = body["priority"]
        deadline = body["deadline"]
        status = body["status"]

        update_todo_all (user_id=username, todo_id=todo_id, status=status,
                                                            title = title,
                                                            description = description,
                                                            priority  = priority,
                                                            deadline = deadline)


        return make_response(error=False, message="To do Update", status=200)

    except (KeyError, TypeError):
        # If invalid body schema
        message = 'No Complete data to update ToDo'
        return make_response(error=True, message=message, status=400)

    except Exception:
        # Return a 500 error if something went wrong
        return make_response(error=True, message='Server error', status=500)

