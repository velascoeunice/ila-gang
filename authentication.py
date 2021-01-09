import database as db
from flask import session

def login(username, password):
    is_valid_login = False
    user=None
    temp_user = db.get_user(username)
    if(temp_user != None):
        if(temp_user["password"]==password):
            is_valid_login=True
            user={"username":username,
                  "first_name":temp_user["first_name"],
                  "last_name":temp_user["last_name"]}

    return is_valid_login, user

def change_password_verification(oldpass, newpass, confirmpass):
    is_correct_oldpass = False
    is_same_newpasses = False
    is_valid_changepass = False
    temp_user = db.get_user(session["user"]["username"])
    if(oldpass == temp_user["password"]):
        is_correct_oldpass = True
    if(newpass == confirmpass):
        is_same_newpasses = True

    if is_correct_oldpass and is_same_newpasses:
        is_valid_changepass = True

    return is_valid_changepass, is_correct_oldpass, is_same_newpasses
