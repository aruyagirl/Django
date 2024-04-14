from django.shortcuts import render, redirect
import os
import json
from django.conf import settings
from .models import UserPreference
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    currency_data = []
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')

    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            for k, v in data.items():
                currency_data.append({'name': k, 'value': v})
    except FileNotFoundError:
        messages.error(request, 'Currency data file not found.')
        return redirect('preferences') 

    user_preferences = UserPreference.objects.filter(user=request.user).first()

    if request.method == 'POST':
        currency = request.POST.get('currency')
        if currency:
            if user_preferences:
                user_preferences.currency = currency
                user_preferences.save()
            else:
                UserPreference.objects.create(user=request.user, currency=currency)
            messages.success(request, 'Changes saved')
        else:
            messages.error(request, 'No currency selected.')

    user_currency = None
    if user_preferences:
        user_currency = user_preferences.currency

    return render(request, 'preferences/index.html', {
        'currencies': currency_data,
        'user_currency': user_currency
    })
