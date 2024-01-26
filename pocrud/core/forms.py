
from django.contrib.auth.models import User 
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Trooper, Apply_Leave, Leave_Type, Current_Leave, Main_Duty, Additional_Duty

class RegisterUserForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class ResetUserPasswordForm(forms.Form):
    email = forms.CharField()

class UserProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username','first_name', 'last_name']

class UserPasswordForm(forms.ModelForm):
    old_password = forms.CharField(label='Old Password')
    new_password1 = forms.CharField(label='New Password')
    new_password2 = forms.CharField(label='Confirm New Password')

    class Meta:
        model = User
        fields = []
        widgets = {
            'old_password': forms.widgets.PasswordInput(),
            'new_password1': forms.widgets.PasswordInput(),
            'new_password2': forms.widgets.PasswordInput(),
        }

class RegisterTrooperForm(forms.ModelForm):
    RANK_CHOICES = (
        ('REC', 'Recruit (REC)'),
        ('PTE', 'Private (PTE)'),
        ('LCP', 'Lance Corporal (LCP)'),
        ('CPL', 'Corporal (CPL)'),
        ('CFC', 'Corporal First Class (CFC)'),
        ('3SG', '3rd Sergeant (3SG)')
    ) 
    rank = forms.ChoiceField(choices=RANK_CHOICES)
    first_name = forms.CharField()
    last_name = forms.CharField(required=False)
    
    class Meta:
        model = Trooper
        fields = '__all__'
        exclude = ('commander',)

class RegisterLeaveTypeForm(forms.Form):
    leave_type = forms.CharField()

class RegisterLeaveForm(forms.ModelForm):

    class Meta:
        model = Current_Leave
        fields = ['trooper', 'leave_type', 'number_of_leaves', 'remarks']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            #Ensure that the user is viewing troopers and leave types that are created by him and not other users.
            self.fields['trooper'].queryset = Trooper.objects.filter(commander=self.instance)
            self.fields['leave_type'].queryset = Leave_Type.objects.filter(commander=self.instance)
    
class ManageCurrentLeaveForm(forms.ModelForm):

    class Meta:
        model = Current_Leave
        fields = ['trooper', 'leave_type', 'number_of_leaves', 'remarks']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['trooper'].queryset = Trooper.objects.filter(commander=self.instance.commander)
            self.fields['leave_type'].queryset = Leave_Type.objects.filter(commander=self.instance.commander)

class ApplyLeaveForm(forms.ModelForm):
    half_day_bool = forms.ChoiceField(choices=(('NO', 'NO'),('YES', 'YES')))

    class Meta:
        model = Apply_Leave
        fields = ['start_date', 'end_date', 'trooper', 'current_leave', 'half_day']
        widgets = {
            'start_date': forms.widgets.DateInput(attrs={'type': 'date'}),
            'end_date': forms.widgets.DateInput(attrs={'type': 'date'}),
            'half_day': forms.widgets.DateInput(attrs={'type': 'date'})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['current_leave'].queryset = Leave_Type.objects.none()
        if self.instance:
            self.fields['trooper'].queryset = Trooper.objects.filter(commander=self.instance)
        
        if 'trooper' in self.data:
            try:
                trooper_id = int(self.data.get('trooper'))
                self.fields['current_leave'].queryset = Current_Leave.objects.filter(trooper = trooper_id)
              
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore
   
class ManageApplyLeaveForm(forms.ModelForm):
    half_day_bool = forms.ChoiceField(choices=(('NO', 'NO'),('YES', 'YES')))

    class Meta:
        model = Apply_Leave
        fields = ['trooper', 'current_leave', 'start_date', 'end_date', 'half_day']
        widgets = {
            'start_date': forms.widgets.DateInput(attrs={'type': 'date'}),
            'end_date': forms.widgets.DateInput(attrs={'type': 'date'}),
            'half_day': forms.widgets.DateInput(attrs={'type': 'date'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id != None:
            self.fields['current_leave'].queryset = Current_Leave.objects.filter(trooper = self.instance.trooper)
            self.fields['trooper'].queryset = Trooper.objects.filter(commander=self.instance.commander)

class CreateMainDutyForm(forms.ModelForm):
     class Meta:
        model = Main_Duty
        fields = ['name']

class CreateAdditionalDutyForm(forms.ModelForm):
     class Meta:
        model = Additional_Duty
        fields = ['name']

class SelectDuty(forms.Form):
    date = forms.DateField()

class RegisterMainDuty(forms.Form):
    start_time = forms.TimeField()
    end_time = forms.TimeField()

class RegisterAdditionalDuty(forms.Form):
    TIMES_OF_DAY = (
        ('Morning', 'Morning'),
        ('Afternoon', 'Afternoon'),
        ('Night', 'Night'),
        ('Whole', 'Whole')
    ) 
    time_of_day = forms.ChoiceField(choices=TIMES_OF_DAY)

