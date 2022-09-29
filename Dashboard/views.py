from django.contrib import messages
from django.db.models import F
from django.http import HttpRequest, HttpResponseForbidden
from django.shortcuts import render
from django.conf import settings
from Auth.models import BankUser
from django.utils.datastructures import MultiValueDictKeyError


# Create your views here.
def dashboard(request: HttpRequest):
    if "sessionid" not in request.COOKIES.keys() or request.COOKIES["sessionid"] not in settings.VALID_SESSION_IDS:
        return HttpResponseForbidden()
    username = request.COOKIES["username"]
    user = BankUser.objects.get(username=username)
    context = {
        "name": user.first_name,
        "last_name": user.second_name,
        "balance": user.balance,
        "account_number": user.account_number
    }
    return render(request, "dashboard.html", context=context)


def transfer(request: HttpRequest):
    if "sessionid" not in request.COOKIES.keys() or request.COOKIES["sessionid"] not in settings.VALID_SESSION_IDS:
        return HttpResponseForbidden()
    username = request.COOKIES["username"]
    user = BankUser.objects.get(username=username)
    if request.POST:
        try:
            post = request.POST
            account_number = post["account_number"]

            if int(account_number) == user.account_number:
                messages.add_message(request, messages.ERROR, "You can't transfer funds to yourself")
                messages.get_messages(request)
                return render(request, "transfer.html", context={"balance": user.balance})

            transfer_amount = float(post["transfer_amount"])

        except MultiValueDictKeyError as e:
            messages.add_message(request, messages.ERROR, f"Missing value {e}")
            messages.get_messages(request)
            return render(request, "transfer.html", context={"balance": user.balance})

        try:
            user_to = BankUser.objects.get(account_number=account_number)

            if user.balance >= transfer_amount:
                balance_to_show = user.balance - transfer_amount

                user.balance = F('balance') - transfer_amount
                user.save()

                user_to.balance = F('balance') + transfer_amount
                user_to.save()

                messages.add_message(request, messages.INFO, "Transfer ordered successfully")
                messages.get_messages(request)

                return render(request, "transfer.html", context={"balance": balance_to_show})
            else:
                messages.add_message(request, messages.WARNING, "You don't have sufficient funds to order this transfer")
                messages.get_messages(request)
                return render(request, "transfer.html", context={"balance": user.balance})

        except Exception as e:
            raise e

    context = {
        "balance": user.balance
    }
    return render(request, "transfer.html", context=context)
