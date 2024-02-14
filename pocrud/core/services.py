import django_tables2 as tables
from .models import Trooper, Apply_Leave, Current_Leave, Leave_Type, Main_Duty_Time, Main_Duty, Additional_Duty, Additional_Duty_Time, Duty_Date
from .tables import TrooperMainDutyTable, MainDutyTable, TrooperAdditionalDutyTable, AdditionalDutyTable, LeaveTypeTable, ApplyLeaveTable, TrooperTable, CurrentLeaveTable, PeakSecureTable
from collections import defaultdict
import datetime

class TrooperService():

    @staticmethod
    def create_peak_secure_table(user, filtered_data):

        if not filtered_data:
            main_duty = Main_Duty_Time.objects.filter(commander=user).values()
        else:
            main_duty = filtered_data.values()
       
        peak_secure = []
        seen_trooper = {}
        seen_peak = defaultdict(list)
        seen_secure = defaultdict(list)

        for duty in main_duty:
            trooper = Trooper.objects.get(id=duty['trooper_id'])
            duty_date = Duty_Date.objects.get(id=duty['duty_date_id'])
            temp_dict = defaultdict()
            peak = 0
            secure = 0

            if trooper not in seen_peak[duty_date] and duty['start_time'] >= datetime.time(6,0,0) and duty['end_time'] <= datetime.time(10,0,0):
                peak = 1
                seen_peak[duty_date].append(trooper)
            if trooper not in seen_secure[duty_date] and duty['end_time'] == datetime.time(22,0,0):
                secure = 1
                seen_secure[duty_date].append(trooper)
            if peak == 0 and secure == 0:
                continue
            if trooper in seen_trooper:
                index = seen_trooper[trooper]
                peak_secure[index]['peak'] += peak
                peak_secure[index]['secure'] += secure
            else:
                temp_dict['trooper'] = trooper 
                temp_dict['peak'] = peak
                temp_dict['secure'] = secure
                seen_trooper[trooper] = len(peak_secure)
                peak_secure.append(temp_dict)


        peak_secure_table = PeakSecureTable(peak_secure)
        return peak_secure_table
        
    @staticmethod
    def retrieve_all_trooper():
        #Getting all troopers data
        trooper_data = Trooper.objects.all()
        trooper_list = []

        for trooper in trooper_data:
            rank_name = f'{trooper.rank} {trooper.first_name} {trooper.last_name}'
            trooper_list.append((rank_name, trooper.id))
        
        return trooper_list
    
    @staticmethod
    def retrieve_available_trooper(user, duty_date):
        trooper_data = Trooper.objects.filter(commander=user)
        trooper_list = []

        leave_data = Apply_Leave.objects.filter(commander=user)
        trooper_on_leave = {}

        for leave in leave_data:
            if leave.start_date <= duty_date <= leave.end_date:
                trooper_on_leave[leave.trooper] = leave.trooper

        for trooper in trooper_data:

            #Exclude troopers that are unavailable due to leave
            if trooper not in trooper_on_leave:
                rank_name = f'{trooper.rank} {trooper.first_name} {trooper.last_name}'
                trooper_list.append((rank_name, trooper.id))

        return trooper_list

    @staticmethod
    def create_trooper_table(user):
        #filter all trooper data based on user logged in
        trooper_data = list(Trooper.objects.filter(commander=user).values())

        main_data = []

        for dic in trooper_data:
            temp_dic = defaultdict(lambda:('-'))

            temp_dic['id'] = dic['id']
            temp_dic['rank'] = dic['rank']
            temp_dic['first_name'] = dic['first_name']
            temp_dic['last_name'] = dic['last_name']
            temp_dic['initial'] = dic['initial']

            main_data.append(temp_dic)
            
        trooper_table = TrooperTable(main_data)

        return trooper_table
    
    @staticmethod
    def create_leave_type_table(user):
        leave_type_data = Leave_Type.objects.filter(commander=user).values()

        main_data = []

        for dic in leave_type_data:
            temp_dic = defaultdict(lambda:('-'))

            temp_dic['id'] = dic['id']
            temp_dic['leave_type'] = dic['leave_type']

            main_data.append(temp_dic)

        leave_type_table = LeaveTypeTable(main_data)

        return leave_type_table
    
    @staticmethod
    def create_current_leave_table(user, filtered_data):
        if not filtered_data:
            leave_data = Current_Leave.objects.filter(commander=user).values()
        else:
            leave_data = filtered_data.values()
        

        main_data = []

        for dic in leave_data:
            temp_dic = defaultdict(lambda:('-'))

            trooper = Trooper.objects.get(id=dic['trooper_id'])
            leave_type = Leave_Type.objects.get(id=dic['leave_type_id'])
            
            temp_dic['id'] = dic['id']
            temp_dic['trooper'] = trooper
            temp_dic['leave_type'] = leave_type
            temp_dic['number_of_leaves'] = dic['number_of_leaves']
            temp_dic['remarks'] = dic['remarks']

            main_data.append(temp_dic)

        leave_table = CurrentLeaveTable(main_data)
        return leave_table      

    @staticmethod
    def create_apply_leave_table(user, filtered_data):
        if not filtered_data:
            leave_data = Apply_Leave.objects.filter(commander=user).values()
        else:
            leave_data = filtered_data.values()

        main_data = []

        for dic in leave_data:
            temp_dic = defaultdict(lambda:('-'))

            trooper = Trooper.objects.get(id=dic['trooper_id'])
            current_leave = Current_Leave.objects.get(id=dic['current_leave_id'])
            
            temp_dic['id'] = dic['id']
            temp_dic['trooper'] = trooper
            temp_dic['start_date'] = dic['start_date']
            temp_dic['end_date'] = dic['end_date']
            temp_dic['half_day'] = dic['half_day']
            days = (dic['end_date'] - dic['start_date']).days
            if dic['half_day_bool'] == 'YES':
                temp_dic['days'] = days + 0.5
            else:
                temp_dic['days'] = days + 1
           
            temp_dic['leave_type'] = current_leave.leave_type

            main_data.append(temp_dic)

        leave_table = ApplyLeaveTable(main_data)
        
        return leave_table

    
class MainDutyService():

    @staticmethod
    def create_table(user):
        #data for all created main duty
        main_duty_data = Main_Duty.objects.filter(commander=user).values()

        main_data = []

        for dic in main_duty_data:
            temp_dic = defaultdict(lambda:('-'))

            temp_dic['id'] = dic['id']
            temp_dic['duty'] = dic['name']

            main_data.append(temp_dic)

        main_duty_table = MainDutyTable(main_data)

        return main_duty_table


    @staticmethod
    def retrieve_duty(user):             
        main_duty_data = Main_Duty.objects.filter(commander=user).values()
        
        #Used to display all types of duties that were created
        main_duty_list = []

        #Used to created additional columns (duties created by user) for the main duty table
        MAIN_DUTY_COLS = [] 

        for main_duty in main_duty_data:
            main_duty_list.append((main_duty['name'], main_duty['id']))
            MAIN_DUTY_COLS.append((main_duty['name'], tables.Column()))

        return (main_duty_list, MAIN_DUTY_COLS)
    
    @staticmethod
    def create_duty_table(user, duty_date_id, MAIN_DUTY_COLS):
        selected_main_duty = Main_Duty_Time.objects.filter(commander=user, duty_date=duty_date_id).values()
        main_data = []
        main_duplicates = {}
        for dic in selected_main_duty:       

            main_duty = Main_Duty.objects.get(id=dic['main_duty_id']).name
            trooper = Trooper.objects.get(id=dic['trooper_id'])

            hours = int((datetime.datetime.combine(datetime.datetime.today(), dic['end_time']) - datetime.datetime.combine(datetime.datetime.today(), dic['start_time'])).total_seconds() / 3600)
            start = dic['start_time']
            for h in range(hours):
                temp_dict = defaultdict(lambda:('-'))
                start_time = (datetime.datetime.combine(datetime.datetime.today(), start) + datetime.timedelta(hours=h)).strftime('%H:%M')
                end_time = (datetime.datetime.combine(datetime.datetime.today(), start) + datetime.timedelta(hours=h+1)).strftime('%H:%M')
                temp_dict['start'] = start_time
                temp_dict['end'] = end_time
                    
                temp_dict['id'] = [dic['id']]

                #grouping common start and end time together
                if start_time in main_duplicates:
                    index = main_duplicates[start_time]
                    main_data[index][main_duty] = (trooper.initial)
                    main_data[index]['id'].append(dic['id'])
                else:
                    temp_dict[main_duty] = (trooper.initial)
                    main_data.append(temp_dict)
                    main_duplicates[start_time] = len(main_data) - 1

        trooper_main_duty_table = TrooperMainDutyTable(main_data, extra_columns=MAIN_DUTY_COLS)

        return trooper_main_duty_table
    

class AdditionalDutyService():

    @staticmethod
    def create_table(user):
        #data for all created additional duty
        additional_duty_data = Additional_Duty.objects.filter(commander=user).values()

        main_data = []

        for dic in additional_duty_data:
            temp_dic = defaultdict(lambda:('-'))

            temp_dic['id'] = dic['id']
            temp_dic['duty'] = dic['name']

            main_data.append(temp_dic)

        additional_duty_table = AdditionalDutyTable(main_data)

        return additional_duty_table

    @staticmethod
    def retrieve_duty(user):
        additional_duty_data = Additional_Duty.objects.filter(commander=user).values()

        additional_duty_list = []

        ADDITIONAL_DUTY_COLS = []

        for additional_duty in additional_duty_data:
            additional_duty_list.append((additional_duty['name'], additional_duty['id']))
            ADDITIONAL_DUTY_COLS.append((additional_duty['name'], tables.Column()))

        return (additional_duty_list, ADDITIONAL_DUTY_COLS)
    
    @staticmethod
    def create_duty_table(user, duty_date_id, ADDITIONAL_DUTY_COLS):

        selected_additional_duty = Additional_Duty_Time.objects.filter(commander=user, duty_date=duty_date_id).values()
        additional_data = []

        for dict in selected_additional_duty:
            temp_dict = defaultdict(lambda:('-'))

            additional_duty = Additional_Duty.objects.get(id=dict['add_duty_id']).name
            trooper = Trooper.objects.get(id=dict['trooper_id'])

            temp_dict[additional_duty] = trooper.initial
            temp_dict['time_of_day'] = dict['time_of_day']
            temp_dict['id'] = dict['id']

            additional_data.append(temp_dict)

        trooper_addiional_duty_table = TrooperAdditionalDutyTable(additional_data, extra_columns=ADDITIONAL_DUTY_COLS)

        return trooper_addiional_duty_table