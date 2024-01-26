from django.db import models
from django.contrib.auth.models import User 
from django.db.models import Q, F

class Trooper(models.Model):
    RANK_CHOICES = (
        ('REC', 'Recruit (REC)'),
        ('PTE', 'Private (PTE)'),
        ('LCP', 'Lance Corporal (LCP)'),
        ('CPL', 'Corporal (CPL)'),
        ('CFC', 'Corporal First Class (CFC)'),
        ('3SG', '3rd Sergeant (3SG)')
    ) 
    rank = models.CharField(choices=RANK_CHOICES, default='REC')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, blank=True)
    commander = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.rank + ' ' + self.first_name + ' ' + self.last_name)

class Leave_Type(models.Model):
    leave_type = models.CharField()
    commander = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['leave_type','commander'], name='unique_leave_type_per_commander')
        ]

    #return the name of the leave type when a leave_type object is called
    def __str__(self):
        return str(self.leave_type)

class Current_Leave(models.Model):
    number_of_leaves = models.DecimalField(max_digits=5, decimal_places=1)
    remarks = models.CharField(blank=True)
    leave_type = models.ForeignKey(Leave_Type, on_delete=models.CASCADE, null=True)
    trooper = models.ForeignKey(Trooper, on_delete=models.CASCADE, null=True)
    commander = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['leave_type', 'trooper','commander'],
                                    name='unique_leave_type_per_trooper')
        ]

class Apply_Leave(models.Model):
    TRUE_FALSE_CHOICES = (
        ('YES', 'YES'),
        ('NO', 'NO')
    )
    start_date = models.DateField()
    end_date = models.DateField()
    half_day_bool = models.CharField(choices=TRUE_FALSE_CHOICES, default='NO')
    half_day = models.DateField(null=True, blank=True)
    current_leave = models.ForeignKey(Current_Leave, on_delete=models.CASCADE, null=True)
    trooper = models.ForeignKey(Trooper, on_delete=models.CASCADE, null=True)
    commander = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(end_date__gte = models.F('start_date')),name='end_date_gte_start_date', violation_error_message='Start date cannot be later than end date.'),
            models.UniqueConstraint(fields=['start_date','end_date', 'trooper','commander'], name='unique_applied_leave')
        ]

class Main_Duty(models.Model):
    name = models.CharField(max_length=30)
    commander = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)

class Additional_Duty(models.Model):
    name = models.CharField(max_length=30)
    commander = models.ForeignKey(User, on_delete=models.CASCADE)

class Duty_Date(models.Model):
    date = models.DateField()
    commander = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.date)
 
class Main_Duty_Time(models.Model):
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True) 
    main_duty = models.ForeignKey(Main_Duty, on_delete=models.CASCADE, null=True)
    trooper = models.ForeignKey(Trooper, on_delete=models.CASCADE, null=True)
    duty_date = models.ForeignKey(Duty_Date, on_delete=models.CASCADE, null=True)
    commander = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['start_time', 'end_time', 'main_duty', 'duty_date', 'commander'],
                                    name='unique_main_duty_time_per_date')
        ]

class Additional_Duty_Time(models.Model):
    TIMES_OF_DAY = (
        ('Morning', 'Morning'),
        ('Afternoon', 'Afternoon'),
        ('Night', 'Night'),
        ('Whole', 'Whole')
    ) 
    time_of_day = models.CharField(choices=TIMES_OF_DAY)
    add_duty = models.ForeignKey(Additional_Duty, on_delete=models.CASCADE, null=True)
    trooper = models.ForeignKey(Trooper, on_delete=models.CASCADE, null=True)
    duty_date = models.ForeignKey(Duty_Date, on_delete=models.CASCADE, null=True)
    commander = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['trooper', 'time_of_day', 'add_duty',  'commander'], name='unique_add_duty')
        ]
        
    