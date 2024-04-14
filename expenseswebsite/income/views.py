from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Income, Source
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from userpreferences.models import UserPreference
from django.core.exceptions import ObjectDoesNotExist
import datetime 

def search_income(request):
    if request.method=='POST':
        search_str=json.loads(request.body).get('searchText','')   

        income=Income.objects.filter(
            amount__istartswith=search_str,owner=request.user) | Income.objects.filter(
            income_date__istartswith=search_str,owner=request.user) | Income.objects.filter(
            description__icontains=search_str,owner=request.user) | Income.objects.filter(
            source__name__icontains=search_str,owner=request.user)     
        
        data = []
        for income in income:
            data.append({
                'amount': income.amount,
                'income_date': income.income_date,
                'description': income.description,
                'source_name': income.source.name  
            })

        return JsonResponse(data, safe=False)
              

@login_required(login_url='/authentication/login')
def index(request):
    income = Income.objects.filter(owner=request.user)
    paginator = Paginator(income, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    try:
        user_preference = UserPreference.objects.get(user=request.user)
        currency = user_preference.currency
    except ObjectDoesNotExist:
        currency = None
    
    return render(request, 'income/index.html', {
        'income': income,  
        'page_obj': page_obj,
        'sources': Source.objects.all(),
        'currency': currency
    })

@login_required(login_url='/authentication/login')
def add_income(request):
    return handle_income(request, income_id=None)

@login_required(login_url='/authentication/login')
def income_edit(request, id):
    return handle_income(request, income_id=id)

def handle_income(request, income_id):
    sources = Source.objects.all()

    income = None
    
    if income_id:
        income = get_object_or_404(Income, pk=income_id, owner=request.user)

    if request.method == "POST":
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        income_date = request.POST.get('income_date')
        source_name = request.POST.get('source')
        source = get_object_or_404(Source, name=source_name)
        
        errors = []
        if not amount: errors.append('An amount is required')
        if not description: errors.append('A description is required')
        if not income_date: errors.append('A date is required')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            if not income:
                income = Income(owner=request.user)
            income.amount = amount
            income.description = description
            income.income_date = income_date
            income.source = source
            income.save()
            messages.success(request, 'Income saved successfully')
            return redirect('income')

    context = {
        'sources': sources,
        'values': income or request.POST,
        'income': income  
    }
    template = 'income/add_income.html' if not income_id else 'income/edit-income.html'
    return render(request, template, context)

def delete_income(request,id):
    income=Income.objects.get(pk=id)
    income.delete()
    messages.success(request,'Income deleted')
    return redirect('income')

def income_summary(request):
    todays_date=datetime.date.today()
    six_months_ago=todays_date-datetime.timedelta(days=30*6)
    income=Income.objects.filter(owner=request.user,
        income_date__gte=six_months_ago, income_date__lte=todays_date)
    finalrep = {}
    
    def get_source(income):
        return income.source
    source_list=list(set(map(get_source, income)))
    
    def get_income_source_amount(source):
        amount = 0
        filtered_by_source=income.filter(source=source)      
        for item in filtered_by_source:
            amount +=item.amount
        return amount
    
    for source in source_list:
        finalrep[str(source)] = get_income_source_amount(source)

    return JsonResponse({'income_source_data': finalrep}, safe=False)

def stats_view(request):
    return render(request,'income/income_stats.html')