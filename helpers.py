import os
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

def userlogin_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/userlogin")
        
        return f(*args, **kwargs)
    return decorated_function

def adminlogin_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("admin_id") is None:
            return redirect("/adminlogin")
        
        return f(*args, **kwargs)
    return decorated_function


