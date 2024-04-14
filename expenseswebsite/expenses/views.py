from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Expense, Category
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse
from userpreferences.models import UserPreference
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.db.models import Sum
import tempfile
import datetime, csv, xlwt

def search_expenses(request):
    if request.method=='POST':
        search_str=json.loads(request.body).get('searchText','')   

        expenses=Expense.objects.filter(
            amount__istartswith=search_str,owner=request.user) | Expense.objects.filter(
            expense_date__istartswith=search_str,owner=request.user) | Expense.objects.filter(
            description__icontains=search_str,owner=request.user) | Expense.objects.filter(
            category__name__icontains=search_str,owner=request.user)     
        
        data = []
        for expense in expenses:
            data.append({
                'amount': expense.amount,
                'expense_date': expense.expense_date,
                'description': expense.description,
                'category_name': expense.category.name  
            })

        return JsonResponse(data, safe=False)
              

@login_required(login_url='/authentication/login')
def index(request):
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    try:
        user_preference = UserPreference.objects.get(user=request.user)
        currency = user_preference.currency
    except ObjectDoesNotExist:
        currency = None
    
    return render(request, 'expenses/index.html', {
        'expenses': expenses,  
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'currency': currency
    })

@login_required(login_url='/authentication/login')
def add_expense(request):
    return handle_expense(request, expense_id=None)

@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    return handle_expense(request, expense_id=id)

def handle_expense(request, expense_id):
    categories = Category.objects.all()
    expense = None
    
    if expense_id:
        expense = get_object_or_404(Expense, pk=expense_id, owner=request.user)

    if request.method == "POST":
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        expense_date = request.POST.get('expense_date')
        category_name = request.POST.get('category')
        category = get_object_or_404(Category, name=category_name)
        
        errors = []
        if not amount: errors.append('An amount is required')
        if not description: errors.append('A description is required')
        if not expense_date: errors.append('A date is required')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            if not expense:
                expense = Expense(owner=request.user)
            expense.amount = amount
            expense.description = description
            expense.expense_date = expense_date
            expense.category = category
            expense.save()
            messages.success(request, 'Expense saved successfully')
            return redirect('expenses')

    context = {
        'categories': categories,
        'values': expense or request.POST,
        'expense': expense  # For editing
    }
    template = 'expenses/add_expense.html' if not expense_id else 'expenses/edit-expense.html'
    return render(request, template, context)

def delete_expense(request,id):
    expense=Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request,'Expense deleted')
    return redirect('expenses')

def expense_summary(request):
    todays_date=datetime.date.today()
    six_months_ago=todays_date-datetime.timedelta(days=30*6)
    expenses=Expense.objects.filter(owner=request.user,
        expense_date__gte=six_months_ago, expense_date__lte=todays_date)
    finalrep = {}
    
    def get_category(expense):
        return expense.category
    category_list=list(set(map(get_category, expenses)))
    
    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category=expenses.filter(category=category)      
        for item in filtered_by_category:
            amount +=item.amount
        return amount
    
    for category in category_list:
        finalrep[str(category)] = get_expense_category_amount(category)

    return JsonResponse({'expense_category_data': finalrep}, safe=False)

def stats_view(request):
    return render(request,'expenses/stats.html')

def export_csv(request):
    response=HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment; filename = Expenses'+str(datetime.datetime.now())+'.csv'
    
    writer=csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category','Date'])
    
    expenses = Expense.objects.filter(owner=request.user)
    
    for expense in expenses:
        writer.writerow([expense.amount, expense.description, expense.category, expense.expense_date])
        
    return response

def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Dsiposition'] = 'attachment; filename = Expenses' + str(datetime.datetime.now())+'.xls'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    
    columns = ['Amount', 'Description', 'Category','Date']
    
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    
    font_style = xlwt.XFStyle()
    
    rows=Expense.objects.filter(owner=request.user).values_list('amount', 'description', 'category', 'expense_date')
    
    for row in rows:
        row_num +=1
        
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
            
    wb.save(response)
    
    return response
    
    
        
    
    
    

            
    

