import django_filters
from django import forms
from .models import *

class DateInput(forms.DateInput):
    input_type = 'date'

class applyLeaveFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(widget=DateInput(attrs={'type': 'date'}))
    end_date = django_filters.DateFilter(widget=DateInput(attrs={'type': 'date'}))
    class Meta:
        model = Apply_Leave
        fields = ['start_date', 'end_date', 'trooper']
        exclude = ['current_leave', 'half_day', 'half_day_bool', 'commander']


    def __init__(self, *args, user=None, **kwargs):
            super(applyLeaveFilter, self).__init__(*args, **kwargs)

            if user:
                self.filters['trooper'].queryset = Trooper.objects.filter(commander=user)

class currentLeaveFilter(django_filters.FilterSet):
    class Meta:
        model = Current_Leave
        fields = ['number_of_leaves','leave_type','trooper']
        exclude = ['remarks', 'commander']

    def __init__(self, *args, user=None, **kwargs):
            super(currentLeaveFilter, self).__init__(*args, **kwargs)

            if user:
                self.filters['trooper'].queryset = Trooper.objects.filter(commander=user)
                self.filters['leave_type'].queryset = Leave_Type.objects.filter(commander=user)


class peakSecureFilter(django_filters.FilterSet):

    class Meta:
        model = Main_Duty_Time
        fields = {
             'duty_date': ['gte', 'lte']
        }

    def __init__(self, *args, user=None, **kwargs):
        super(peakSecureFilter, self).__init__(*args, **kwargs)

        if user:
            self.filters['duty_date__gte'].queryset = Duty_Date.objects.filter(commander=user)
            self.filters['duty_date__lte'].queryset = Duty_Date.objects.filter(commander=user)
    