import django.db.utils
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, hashers, login
from django.contrib import messages
from django.utils.datastructures import MultiValueDictKeyError
from django.conf import settings
from .models import BankUser

import random
from string import ascii_lowercase


# Create your views here.
def login_page(request: HttpRequest):
    if 'sessionid' in request.COOKIES.keys() and request.COOKIES['sessionid'] in settings.VALID_SESSION_IDS:
        return HttpResponseRedirect("/dashboard")

    if request.POST:
        post = request.POST

        try:
            username = post["username"]
            passwd = post["password"]

        except MultiValueDictKeyError as e:
            messages.add_message(request, messages.ERROR, f"Missing value {e}")
            messages.get_messages(request)
            return render(request, "login.html")

        try:
            user = BankUser.objects.get(username=username)
            salt = user.salt

            hashed = hashers.make_password(passwd, salt)

            if user.password == hashed:
                session_id = ''.join([random.choice(ascii_lowercase) for _ in range(64)])
                settings.VALID_SESSION_IDS.append(session_id)
                response = HttpResponseRedirect("/dashboard")
                response.set_cookie("username", username)
                response.set_cookie("sessionid", session_id)
                return response
        except Exception as e:
            messages.add_message(request, messages.ERROR, f"Missing value {e}")
            messages.get_messages(request)
            return render(request, "login.html")

    return render(request, "login.html")


def signup_page(request):
    if 'sessionid' in request.COOKIES.keys() and request.COOKIES['sessionid'] in settings.VALID_SESSION_IDS:
        return HttpResponseRedirect("/dashboard")

    if request.POST:
        post = request.POST

        try:
            username = post["username"]
            f_name = post["firstName"]
            s_name = post["secondName"]
            email = post["emailAddress"]
            passwd = post["password"]
            passwd_cnfrm = post["passwordConfirm"]

        except MultiValueDictKeyError as e:
            messages.add_message(request, messages.ERROR, f"Missing value {e}")
            messages.get_messages(request)
            return render(request, "signup.html")

        if passwd == passwd_cnfrm:
            salt = ''.join([random.choice(ascii_lowercase) for _ in range(16)])
            hashed = hashers.make_password(passwd, salt=salt)
            acc_no = random.randint(10000000, 99999999)
            try:
                user = BankUser(username=username, first_name=f_name, second_name=s_name, password=hashed, salt=salt,
                                email=email, account_number=acc_no)
                user.save()
            except django.db.utils.IntegrityError:
                messages.add_message(request, messages.ERROR, "User like this was already created")
            except Exception as e:
                messages.add_message(request, messages.ERROR, f"Unknown exception: {e}")
            else:
                messages.add_message(request, messages.INFO, "User created successfully")

    messages.get_messages(request)
    return render(request, "signup.html")


def logout(request: HttpRequest):
    session_id = request.COOKIES["sessionid"]
    index = settings.VALID_SESSION_IDS.index(session_id)
    del settings.VALID_SESSION_IDS[index]
    response = HttpResponseRedirect('/')
    response.delete_cookie("sessionid")
    return response
