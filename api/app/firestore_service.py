import firebase_admin
from firebase_admin import credentials, firestore


project_id = "todosproyectpm"
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
  'projectId': project_id,
})
db = firestore.client()

def get_users():
    return db.collection("users").get()

def get_user(user_id):
    #return db.collection("users").document(user_id).get()
    return db.document(f"users/{user_id}").get()


def get_todos(user_id):
#    return db.collection("users").document(user_id)
    return db.collection(f"users/{user_id}/todos").get()

def user_put(user_data):
    user_ref = db.document(f"users/{user_data.username}")
    user_ref.set({"password": user_data.password,
                 "email":user_data.email})

def put_todo(user_id, title,  description, priority, deadline):
    todos_collection_ref = db.collection(f"users/{user_id}/todos")
    todos_collection_ref.add({ 
                               "title": title,
                               "description":description,
                               "priority": priority,
                               "deadline": deadline,
                               "status": "To Do",
                            })

def delete_todo(user_id, todo_id):
    todo_ref = _get_todo_ref(user_id, todo_id)

    if (todo_ref.get().exists):
        todo_ref.delete()
        return True
    else:
        return False

def update_todo(user_id, todo_id, status):
    todo_ref = _get_todo_ref(user_id, todo_id)
    todo_ref.update({ "status": status })

def _get_todo_ref(user_id, todo_id):
    return db.document(f"users/{user_id}/todos/{todo_id}")

def update_todo_all(user_id, todo_id, status, title, description, priority, deadline):
    todo_ref = _get_todo_ref(user_id, todo_id)
    todo_ref.update({ "status": status,
                      "title" : title,
                      "description" : description, 
                      "priority" : priority,
                      "deadline" : deadline
                      
                    })
