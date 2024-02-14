from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from .forms import RegisterUserForm, LoginForm, RegisterTrooperForm, RegisterLeaveForm, ManageCurrentLeaveForm, ApplyLeaveForm, RegisterMainDuty, SelectDuty, CreateMainDutyForm, CreateAdditionalDutyForm, RegisterAdditionalDuty, RegisterLeaveTypeForm, ManageApplyLeaveForm, UserProfileForm, UserPasswordForm
from .models import Trooper, Current_Leave, Apply_Leave, Duty_Date, Main_Duty_Time, Main_Duty, Additional_Duty, Additional_Duty_Time, Leave_Type
from django_tables2 import RequestConfig
from django.core.exceptions import ValidationError
from django.contrib import messages
import datetime
from .services import TrooperService, MainDutyService, AdditionalDutyService
from collections import defaultdict
from decimal import Decimal
from .filters import *
from .tables import StrengthTable

@login_required(login_url='/login_user')
def index(request):
    user = User.objects.get(id=request.user.id)
    today = datetime.datetime.now().strftime('%d/%m/%Y')

    """ 
    Getting total strength section.

    Getting total strength for the day by separating troopers who are on leave and those who are not. Those who are on absent will have the reason and end date attached beside their name 
    
    """

    all_troopers = Trooper.objects.filter(commander=user)
    all_leaves = Apply_Leave.objects.filter(commander=user, start_date__gte=datetime.datetime.now(), end_date__lte=datetime.datetime.now())
    troopers = []
    for trooper in all_troopers:
        troopers.append(str(trooper))

    absent = []
    absent_troopers = []
    for leave in all_leaves:
        temp_dict = {}
        temp_dict['name'] = f'{str(leave.trooper)} [{str(leave.current_leave.leave_type)} TILL {leave.end_date}]'
        absent_troopers.append(str(leave.trooper))
        absent.append(temp_dict)
    
    present = []
    for trooper in troopers:
        if trooper not in absent_troopers:
            temp_dict = {}
            temp_dict['name'] = trooper
            present.append(temp_dict)

    absent_table = StrengthTable(absent)
    present_table = StrengthTable(present)

    #Calculating strength for all, present and absent troopers
    total_strength = len(all_troopers)
    present_strength = len(present)
    absent_strength = len(absent)

    """ Peak & Secure Table Section """

    queryset = Main_Duty_Time.objects.filter(commander=user)
    
    leave_filter = peakSecureFilter(request.GET, queryset=queryset, user=user)

    peak_secure_table = TrooperService.create_peak_secure_table(user, leave_filter.qs)

    context = {'today':today, 'total_strength':total_strength, 'present_strength':present_strength, 'absent_strength':absent_strength, 'absent':absent, 'present':present, 'absent_table':absent_table, 'present_table':present_table, 'peak_secure_table':peak_secure_table, 'leave_filter': leave_filter}

    return render(request, 'index.html', context=context)

def trooper_duty_chart(request):
    user = User.objects.get(id=request.user.id)
    startdate = request.GET.get('startdate', None)
    enddate = request.GET.get('enddate', None)

    trooper_query = Trooper.objects.filter(commander=user)
    troopers = []
    hours = []
    for trooper in trooper_query:         

        if startdate and enddate:       
            duty_dates = Duty_Date.objects.filter(date__gte=startdate, date__lte=enddate).values('id')
            all_main_duty = Main_Duty_Time.objects.filter(trooper=trooper.id, duty_date__in=duty_dates)
        else:
            all_main_duty = Main_Duty_Time.objects.filter(trooper=trooper.id)
        hours_done = 0
        seen = {}
        for main_duty in all_main_duty:
            if (main_duty.start_time, main_duty.end_time, main_duty.duty_date) not in seen:
                if main_duty.start_time < main_duty.end_time:
                    duration = int((datetime.datetime.combine(datetime.datetime.today(), main_duty.end_time) - datetime.datetime.combine(datetime.datetime.today(), main_duty.start_time)).total_seconds() / 3600)
                else:
                    duration = int((datetime.datetime.combine(datetime.datetime.today() + datetime.timedelta(days=1), main_duty.end_time) - datetime.datetime.combine(datetime.datetime.today(), main_duty.start_time)).total_seconds() / 3600)
                hours_done += duration
            seen[(main_duty.start_time, main_duty.end_time, main_duty.duty_date)] = True

        troopers.append(str(trooper))
        hours.append(hours_done)

    return JsonResponse(data = {
        'labels': troopers,
        'data': hours,
    })


def daily_leaves_chart(request):
    user = User.objects.get(id=request.user.id)
    hashmap = defaultdict(int)

    applied_leave = Apply_Leave.objects.filter(commander=user)

    for leave in applied_leave:
        days_absent = (leave.end_date - leave.start_date).days 

        if days_absent == 0:
            hashmap[leave.start_date] += 1
        else:
            for days in range(days_absent):
                hashmap[leave.start_date + datetime.timedelta(days)] += 1

    return JsonResponse(data = {
        'labels': list(hashmap.keys()),
        'data': list(hashmap.values()),
    })

def most_leaves_chart(request):
    user = User.objects.get(id=request.user.id)
    hashmap = defaultdict(int)
    troopers = Trooper.objects.filter(commander=user)
    for trooper in troopers:
        leaves = Apply_Leave.objects.filter(trooper=trooper.id)
        for leave in leaves:
            hashmap[str(trooper)] += (leave.end_date - leave.start_date).days + 1
    return JsonResponse(data = {
        'labels': list(hashmap.keys()),
        'data': list(hashmap.values()),
    })
    
def login_user(request):
    form = LoginForm()
    context = {'form': form}
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request,'Incorrect login credentials. Please try again.')

    return render(request, 'login_user.html', context=context)
 
def logout_user(request):

    logout(request)
    return redirect('login_user')

def register(request):
    form = RegisterUserForm()
    context = {'form': form}
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = RegisterUserForm()
    return render(request, 'register.html', context=context)

@login_required(login_url='/login_user')
def profile(request):
    user = User.objects.get(id=request.user.id)
    form = UserProfileForm(instance=user)
    context = {'form':form, 'user_email':user.email}
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user.username = data['username']
            user.save()
            messages.success(request, 'Username changed successfully.')
            return redirect('index')
        else:
            messages.error(request, 'Username already exist. Kindly enter another username.')
    return render(request, 'profile.html', context=context)

@login_required(login_url='/login_user')
def change_password(request):
    user = User.objects.get(id=request.user.id)
    form = UserPasswordForm(instance=user)
    context = {'form':form, 'user_email':user.email}
    if request.method == 'POST':
        form = UserPasswordForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if user.check_password(data['old_password']):
                if data['new_password1'] == data['new_password2']:
                    user.set_password(data['new_password1'])
                    user.save()
                    messages.success(request,'Password changed successfully. Please login with your new password.')
                    return redirect('index')
                else:
                    messages.error(request,'New passwords does not match.')
            else:
                messages.error(request,'Old password is incorrect.')
    return render(request, 'change_password.html', context=context)

@login_required(login_url='/login_user')
def manage_trooper(request):
    form = RegisterTrooperForm()
    user = User.objects.get(id=request.user.id)
    table = TrooperService.create_trooper_table(user)
    context = {'form':form, 'table': table}
    if request.method == 'POST':
        form = RegisterTrooperForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            trooper = Trooper(
                rank = data['rank'],
                first_name = data['first_name'].upper(),
                last_name = data['last_name'].upper(),
                initial = data['initial'].upper(),
                commander = user
            )
            trooper.save()
            return redirect('manage_trooper')
    else:
        form = RegisterTrooperForm()
    return render(request, 'trooper/manage_trooper.html', context=context)

def update_trooper(request, trooper_id):
    selected_trooper = Trooper.objects.get(id=trooper_id)
    form = RegisterTrooperForm(instance=selected_trooper)

    context = {'form':form, 'trooper_id':trooper_id}

    if request.method =='POST':
        form = RegisterTrooperForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            selected_trooper.rank = data['rank']
            selected_trooper.first_name = data['first_name'].upper()
            selected_trooper.last_name = data['last_name'].upper()
            selected_trooper.initial = data['initial'].upper()  
            selected_trooper.save()
            return redirect('manage_trooper')
    return render(request, 'trooper/update_trooper.html', context=context)

@login_required(login_url='/login_user')
def manage_leave_type(request):
    user = User.objects.get(id=request.user.id)
    table = TrooperService.create_leave_type_table(user)
    form = RegisterLeaveTypeForm()
    context =  {'form':form, 'table': table}

    if request.method == 'POST':
        form = RegisterLeaveTypeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            new_leave_type = Leave_Type(
                #Convert all leave types to upper case to ensure data integrity
                leave_type = data['leave_type'].upper(),
                commander = user
            )
            try:
                new_leave_type.full_clean()
                new_leave_type.save()
            except ValidationError:
                messages.error(request,'Leave type already exist.')
            return redirect('manage_leave_type')
    return render(request, 'trooper/manage_leave_type.html', context=context)

def delete_leave_type(request, leave_type_id):
    leave_type = Leave_Type.objects.get(id=leave_type_id)
    leave_type.delete()

    return redirect('manage_leave_type')

@login_required(login_url='/login_user')    
def manage_leave(request):
    user = User.objects.get(id=request.user.id)
    form = RegisterLeaveForm(instance=user)
    queryset = Current_Leave.objects.filter(commander=user)
    leave_filter = currentLeaveFilter(request.GET, queryset=queryset, user=user)

    table = TrooperService.create_current_leave_table(user, leave_filter.qs)
    table.paginate(page=request.GET.get("page", 1), per_page=5)
    table.template_name = 'django_tables2/bootstrap5-responsive.html'   
    RequestConfig(request).configure(table)

    context = {'form':form, 'table':table, 'leave_filter': leave_filter}

    if request.method == 'POST':
        form = RegisterLeaveForm(instance=user, data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            trooper_id = request.POST.get('trooper', None)
            leave_type_id = request.POST.get('leave_type', None)
            trooper_selected = Trooper.objects.get(id=trooper_id)
            leave_type_selected = Leave_Type.objects.get(id=leave_type_id)
            new_leave = Current_Leave(
                number_of_leaves = data['number_of_leaves'],
                remarks = data['remarks'],
                leave_type = leave_type_selected,
                trooper = trooper_selected,
                commander = user
            )
            try:
                new_leave.full_clean()
                new_leave.save()
            except ValidationError:
                messages.error(request,'Leave type already exist for the selected trooper.')

            return redirect('manage_leave')

    return render(request, 'trooper/manage_leave.html', context=context)


def update_current_leave(request, current_leave_id):
    selected_leave = Current_Leave.objects.get(id=current_leave_id)
    form = ManageCurrentLeaveForm(instance=selected_leave)
    trooper_id = selected_leave.trooper.id

    context = {'leave':selected_leave, 'form':form, 'trooper_id':trooper_id}
    
    if request.method == 'POST':
        form = ManageCurrentLeaveForm(request.POST, instance=selected_leave)
        if form.is_valid():
            data = form.cleaned_data
            if data['number_of_leaves'] < 0:
                messages.error(request, 'Number of leaves cannot be less than 0.')
                return redirect('manage_leave')
            selected_leave.trooper = data['trooper']
            selected_leave.leave_type = data['leave_type']
            selected_leave.number_of_leaves = data['number_of_leaves']
            selected_leave.remarks = data['remarks']
            selected_leave.save()

            return redirect('manage_leave')

    return render(request, 'trooper/update_current_leave.html', context=context)

def delete_current_leave(request, current_leave_id):
    leave = Current_Leave.objects.get(id=current_leave_id)
    leave.delete()

    return redirect('manage_leave')
 
@login_required(login_url='/login_user')
def apply_leave(request):
    user = User.objects.get(id=request.user.id)
    leave_form = ApplyLeaveForm(instance=user, initial={'start_date':datetime.datetime.now(),'end_date':datetime.datetime.now()})

    queryset = Apply_Leave.objects.filter(commander=user)
    leave_filter = applyLeaveFilter(request.GET, queryset=queryset, user=user)

    table = TrooperService.create_apply_leave_table(user, leave_filter.qs)
    table.paginate(page=request.GET.get("page", 1), per_page=5)
    table.template_name = 'django_tables2/bootstrap5-responsive.html'
    RequestConfig(request).configure(table)

    context = {'leave_form': leave_form, 'table':table, 'leave_filter': leave_filter}  
    
    if request.method == 'POST':

        form = ApplyLeaveForm(instance=user, data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            days_selected = (data['end_date'] - data['start_date']).days + 1 

            remaining_leave = data['current_leave'].number_of_leaves - days_selected

            #Validation to ensure that half day date is in between the selected dates of leave
            if (data['half_day_bool'] and data['half_day']) and not(data['start_date'] <= data['half_day'] <= data['end_date']):
                messages.error(request,f'Date selected for half day is not in between the start and end dates.')
                return redirect('apply_leave')

            #Validation for half_day_bool (if user selects "YES" for half_day_bool, they must have a half day date)
            if data['half_day_bool'] == 'YES' and not data['half_day']:
                messages.error(request,f'Please select the half day date.')
                return redirect('apply_leave')
        
            if data['half_day_bool'] == 'YES':
                if remaining_leave == -0.5:
                    remaining_leave = 0
                else:
                    remaining_leave = data['current_leave'].number_of_leaves - Decimal(0.5)
            
            if remaining_leave < 0:
                messages.error(request,f'Dates selected exceeds the number of leaves {data["trooper"]} owns.')
                return redirect('apply_leave')
            
            new_leave = Apply_Leave(
                start_date = data['start_date'],
                end_date = data['end_date'],
                half_day_bool = data['half_day_bool'],
                half_day = data['half_day'],
                trooper = data['trooper'],
                current_leave = data['current_leave'],
                commander = user
            )
            try:
                new_leave.full_clean()
                new_leave.save()
                #Reduce the number of leaves in current leave object
                data['current_leave'].number_of_leaves = remaining_leave
                data['current_leave'].save()
            except ValidationError as error:
                messages.error(request, ' '.join(error.messages))

            return redirect('apply_leave')

    return render(request, 'trooper/apply_leave.html', context)
    
# AJAX to create dependent dropdown list for leave
def load_leaves(request):
    trooper_id = request.GET.get('trooper_id')

    if trooper_id:
        trooper = Trooper.objects.get(id=trooper_id)
        trooper_leaves = Current_Leave.objects.filter(trooper = trooper)
        return render(request, 'trooper/load_leaves.html', {'leave': trooper_leaves})
    
    return render(request, 'trooper/load_leaves.html') 

def update_apply_leave(request, apply_leave_id):
    selected_leave = Apply_Leave.objects.get(id=apply_leave_id)
    form = ManageApplyLeaveForm(instance=selected_leave)
    trooper_id = selected_leave.trooper.id

    context = {'leave':selected_leave, 'form':form, 'trooper_id':trooper_id}

    if request.method == 'POST':
        form = ManageApplyLeaveForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            current_leave = selected_leave.current_leave
 
            #Validation to ensure that half day date is in between the selected dates of leave
            if (data['half_day_bool'] and data['half_day']) and not(data['start_date'] <= data['half_day'] <= data['end_date']):
                messages.error(request,f'Date selected for half day is not in between the start and end dates.')
                return render(request, 'trooper/update_apply_leave.html', context=context)
            
            #Validation for half_day_bool (if user selects "YES" for half_day_bool, they must have a half day date)
            if data['half_day_bool'] == 'YES' and not data['half_day']:
                messages.error(request,f'Please select the half day date.')
                return render(request, 'trooper/update_apply_leave.html', context=context)
        
            #Refund previously applied leaves based on half day bool
            if selected_leave.half_day_bool == 'YES':
                prev_leave_days = (selected_leave.end_date - selected_leave.start_date).days + 0.5
            else:
                prev_leave_days = (selected_leave.end_date - selected_leave.start_date).days + 1
            
            if data['half_day_bool'] == "YES":
                days_selected = (data['end_date'] - data['start_date']).days + 0.5
            else:
                days_selected = (data['end_date'] - data['start_date']).days + 1 
                #Remove the half day date selected if it exist (in the event the user forgets)
                data['half_day'] = None

            # Condition that executes when the user would like to change the leave (current_leave object) they are currently using 
            if current_leave.leave_type != data['current_leave'].leave_type:

                if data['current_leave'].number_of_leaves < days_selected:
                    messages.error(request,f'{data["trooper"]} does not have enough {data["current_leave"].leave_type} leaves to apply.')
                    return render(request, 'trooper/update_apply_leave.html', context=context)
                
                else:
                    #Reimburse the previously applied leave to the old current_leave object
                    current_leave.number_of_leaves += Decimal(prev_leave_days)
                    current_leave.save()

                    remaining_leave = (data['current_leave'].number_of_leaves) - Decimal(days_selected)

                    try:

                        selected_leave.start_date = data['start_date']
                        selected_leave.end_date = data['end_date']

                        #Replace the old current leave object with the new object
                        selected_leave.current_leave = data['current_leave']
                        selected_leave.trooper = data['trooper']
                        selected_leave.half_day_bool = data['half_day_bool']
                        selected_leave.half_day = data['half_day']
                        selected_leave.save()

                        #Deduct number of leaves from the new current leave object and save it
                        data['current_leave'].number_of_leaves = remaining_leave
                        data['current_leave'].save()
                    except ValidationError as error:
                        messages.error(request, ' '.join(error.messages))

                    return redirect('apply_leave')
                
            # Condition that executes when the user uses the same leave 
            else:      
                #Add the number of leaves selected trooper has with the previously selected leave to get the total original amount before this selected applied leave was applied
                remaining_leave = current_leave.number_of_leaves + Decimal(prev_leave_days) - Decimal(days_selected)

                if remaining_leave < 0:
                    messages.error(request,f'Dates selected exceeds the number of leaves {data["trooper"]} owns.')
                    return redirect('apply_leave')
                try: 
                    selected_leave.start_date = data['start_date']
                    selected_leave.end_date = data['end_date']
                    selected_leave.trooper = data['trooper']
                    selected_leave.half_day_bool = data['half_day_bool']
                    selected_leave.half_day = data['half_day']
                    selected_leave.save()

                    #Modify the number of leaves in current leave object
                    current_leave.number_of_leaves = remaining_leave
                    current_leave.save()
                except ValidationError as error:
                    messages.error(request, ' '.join(error.messages))

                return redirect('apply_leave')

    return render(request, 'trooper/update_apply_leave.html', context=context)


def delete_apply_leave(request, apply_leave_id):
    applied_leave = Apply_Leave.objects.get(id=apply_leave_id)
    current_leave = applied_leave.current_leave
    
    if applied_leave.half_day_bool == 'YES':
        days_applied = (applied_leave.end_date - applied_leave.start_date).days + 0.5
    else:
        days_applied = (applied_leave.end_date - applied_leave.start_date).days + 1
    applied_leave.delete()

    # reimburse the applied number of leaves 
    current_leave.number_of_leaves += Decimal(days_applied)
    current_leave.save()
    return redirect('apply_leave')

@login_required(login_url='/login_user')
def create_main_duty(request):
    user = User.objects.get(id=request.user.id)
    form = CreateMainDutyForm()
    table = MainDutyService.create_table(user)
    context = {'form':form, 'table': table}
    if request.method == 'POST':
        form = CreateMainDutyForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            new_duty = Main_Duty(
                name = data['name'].upper(),
                commander = user
            )
            new_duty.save()
            return redirect('create_main_duty')
        
    return render(request, 'duty/create_main_duty.html', context)

def delete_main_duty(request, main_duty_id):
    main_duty = Main_Duty.objects.get(id=main_duty_id)
    main_duty.delete()

    return redirect('create_main_duty')

@login_required(login_url='/login_user')
def create_additional_duty(request):
    user = User.objects.get(id=request.user.id)
    form = CreateAdditionalDutyForm()
    table = AdditionalDutyService.create_table(user)
    context = {'form':form, 'table': table}
    if request.method == 'POST':
        form = CreateAdditionalDutyForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            new_duty = Additional_Duty(
                name = data['name'].upper(),
                commander = user
            )
            new_duty.save()
            return redirect('create_additional_duty')
        
    return render(request, 'duty/create_additional_duty.html', context)

def delete_additional_duty(request, additional_duty_id):
    additional_duty = Additional_Duty.objects.get(id=additional_duty_id)
    additional_duty.delete()

    return redirect('create_additional_duty')

@login_required(login_url='/login_user')
def select_duty(request):
    user = User.objects.get(id=request.user.id)
    form = SelectDuty(initial={'date':datetime.datetime.now()})
    context = {'form':form}
    if request.method == 'POST':
        form = SelectDuty(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            date_selected = data['date']
            if not Duty_Date.objects.filter(date=date_selected):
                new_duty = Duty_Date(
                    date=date_selected, 
                    commander=user)
                new_duty.save()
            
            date = Duty_Date.objects.get(date=date_selected)
            request.session['duty_date_id'] = date.id
            return redirect('plan_duty')
        
    return render(request, 'duty/select_duty.html', context=context) 

def plan_duty(request):
    user = User.objects.get(id=request.user.id)
    duty_date_id = request.session['duty_date_id']
    if not (duty_date_id):
        return redirect('select_duty')
    
    duty_date = Duty_Date.objects.get(id=duty_date_id).date

    """ DATA RETRIEVAL SECTION """
    trooper_list = TrooperService.retrieve_available_trooper(user, duty_date)

    #Retrieving duty list and columns
    main_duty_list, MAIN_DUTY_COLS = MainDutyService.retrieve_duty(user)
    additional_duty_list, ADDITIONAL_DUTY_COLS = AdditionalDutyService.retrieve_duty(user)

    """ FORMS SECTION """
    main_duty_form = RegisterMainDuty()
    additional_duty_form = RegisterAdditionalDuty()

    """ TABLES SECTION """
    main_duty_table = MainDutyService.create_duty_table(user, duty_date_id, MAIN_DUTY_COLS)
    addiional_duty_table = AdditionalDutyService.create_duty_table(user, duty_date_id, ADDITIONAL_DUTY_COLS)
    
    context = {'main_duty_table':main_duty_table, 'troopers':trooper_list, 'duty_date':duty_date,
               'main_duty_form': main_duty_form, 'additional_duty_form': additional_duty_form, 'main_duty_list':main_duty_list, 'additional_duty_list':additional_duty_list, 'addiional_duty_table':addiional_duty_table}

    #Sorting the tables
    RequestConfig(request).configure(main_duty_table)
    RequestConfig(request).configure(addiional_duty_table)

    return render(request, 'duty/plan_duty.html', context=context)

def add_main_duty(request):
    user = User.objects.get(id=request.user.id)
    duty_date_id = request.session['duty_date_id']
    if request.method == 'POST':
        form = RegisterMainDuty(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            trooper_id = request.POST.get('trooper', None)
            main_duty_id = request.POST.get('main_duty', None)
            main_duty_selected = Main_Duty.objects.get(id=main_duty_id)
            trooper_selected = Trooper.objects.get(id=trooper_id)
            selected_duty_date = Duty_Date.objects.get(id=duty_date_id)

            #Check for night duty
            if data['start_time'] < data['end_time']:
                hours = int((datetime.datetime.combine(datetime.datetime.today(), data['end_time']) - datetime.datetime.combine(datetime.datetime.today(), data['start_time'])).total_seconds() / 3600)
            else:
                hours = int((datetime.datetime.combine(datetime.datetime.today() + datetime.timedelta(days=1), data['end_time']) - datetime.datetime.combine(datetime.datetime.today(), data['start_time'])).total_seconds() / 3600)
            
            original_start_time = data['start_time']

            for h in range(hours):
                start_time = (datetime.datetime.combine(datetime.datetime.today(), original_start_time) + datetime.timedelta(hours=h)) 
                end_time = (datetime.datetime.combine(datetime.datetime.today(), original_start_time) + datetime.timedelta(hours=h+1)) 
                new_duty_time = Main_Duty_Time(
                    start_time = start_time,
                    end_time = end_time,
                    main_duty = main_duty_selected,
                    trooper = trooper_selected,
                    duty_date = selected_duty_date,
                    commander = user
                )
                try:
                    new_duty_time.full_clean()
                    new_duty_time.save()
                #if user tries to insert duty time that already exist, replace the old duty trooper with new one.    
                except ValidationError:
                    old_duty_time = Main_Duty_Time.objects.get(start_time=start_time, end_time=end_time, main_duty=main_duty_selected, duty_date=selected_duty_date)
                    old_duty_time.trooper = trooper_selected
                    old_duty_time.save()

            
            return redirect('plan_duty')


def add_additional_duty(request):
    user = User.objects.get(id=request.user.id)
    duty_date_id = request.session['duty_date_id']
    if request.method == 'POST':
        form = RegisterAdditionalDuty(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            trooper_id = request.POST.get('trooper', None)
            additional_duty_id = request.POST.get('additional_duty', None)
            additional_duty_selected = Additional_Duty.objects.get(id=additional_duty_id)
            trooper_selected = Trooper.objects.get(id=trooper_id)
            selected_duty_date = Duty_Date.objects.get(id=duty_date_id)

            new_duty_time = Additional_Duty_Time(
                time_of_day = data['time_of_day'],
                add_duty = additional_duty_selected,
                trooper = trooper_selected,
                duty_date = selected_duty_date,
                commander = user
            )
            try:
                new_duty_time.full_clean()
                new_duty_time.save()
            except ValidationError:
                messages.error(request,'Start Time, End Time and Main Duty record already exist.')

            return redirect('plan_duty')
    
def delete_trooper_main_duty(request, duty_ids):
    for id in duty_ids:
        duty = Main_Duty_Time.objects.get(id=id)
        duty.delete()
    return redirect('plan_duty')

def delete_trooper_additional_duty(request, duty_id):
    duty = Additional_Duty_Time.objects.get(id=duty_id)
    duty.delete()
    return redirect('plan_duty')

def delete_trooper(request, trooper_id):
    trooper = Trooper.objects.get(id=trooper_id)
    trooper.delete()
    return redirect('manage_trooper')

def delete_multiple_main_duties(request):
    if request.method == "POST":
        #pk refers to primary keys (id)
        selected_pks = request.POST.getlist("selection")
        pks = []
        for pk in selected_pks:
            #convert the string representation of list back to a list using slicing (start from 1 and end before -1 to ignore the brackets)
            res = list(map(int, pk[1:-1].split(',')))
            pks.extend(res)
        for pk in pks:
            duty = Main_Duty_Time.objects.get(id=pk)
            duty.delete()
    return redirect('plan_duty')


