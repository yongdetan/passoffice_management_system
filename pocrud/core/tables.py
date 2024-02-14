import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html

class LeaveTypeTable(tables.Table):
    leave_type = tables.Column(verbose_name='Leave Type')
    delete = tables.Column(verbose_name='Delete', orderable=False)

    def render_delete(self, record):
        delete_url = reverse('delete_leave_type', args=[record['id']])
        return format_html('<a class="btn btn-danger" href="{}">Delete</a>', delete_url)
    
    class Meta:
        attrs = {'class': 'table table-bordered'}

class CurrentLeaveTable(tables.Table):
    trooper = tables.Column(verbose_name='Trooper')
    leave_type = tables.Column(verbose_name='Leave Type')
    number_of_leaves = tables.Column(verbose_name='Number of Leaves')
    remarks = tables.Column(verbose_name='Remarks')
    update = tables.Column(verbose_name='Update', orderable=False)
    delete = tables.Column(verbose_name='Delete', orderable=False)

    def render_update(self, record):
        update_url = reverse('update_current_leave', args=[record['id']])
        return format_html('<a class="btn btn-warning" href="{}">Update</a>', update_url)
    

    def render_delete(self, record):
        delete_url = reverse('delete_current_leave', args=[record['id']])
        return format_html('<a class="btn btn-danger" href="{}">Delete</a>', delete_url)

    class Meta:
        attrs = {'class': 'table table-bordered'}

class ApplyLeaveTable(tables.Table):
    trooper = tables.Column(verbose_name='Trooper')
    start_date = tables.Column(verbose_name='Start Time')
    end_date = tables.Column(verbose_name='End Time')
    half_day = tables.Column(verbose_name='Half Day')
    days = tables.Column(verbose_name='Total Days')
    leave_type = tables.Column(verbose_name='Leave')
    update = tables.Column(verbose_name='Update', orderable=False)
    delete = tables.Column(verbose_name='Delete', orderable=False)

    def render_update(self, record):
        update_url = reverse('update_apply_leave', args=[record['id']])
        return format_html('<a class="btn btn-warning" href="{}">Update</a>', update_url)
    
    def render_delete(self, record):
        delete_url = reverse('delete_apply_leave', args=[record['id']])
        return format_html('<a class="btn btn-danger" href="{}">Delete</a>', delete_url)
    
    class Meta:
        order_by = 'start_date'
        attrs = {'class': 'table table-bordered'}

class TrooperTable(tables.Table):
    rank = tables.Column(verbose_name='Rank')
    first_name = tables.Column(verbose_name='First Name')
    last_name = tables.Column(verbose_name='Last Name')
    initial = tables.Column(verbose_name='Initial')
    update = tables.Column(verbose_name='Update', orderable=False)
    delete = tables.Column(verbose_name='Delete', orderable=False)

    def render_update(self, record):
        update_url = reverse('update_trooper', args=[record['id']])
        return format_html('<a class="btn btn-warning" href="{}">Update</a>', update_url)
    

    def render_delete(self, record):
        delete_url = reverse('delete_trooper', args=[record['id']])
        return format_html('<a class="btn btn-danger" href="{}">Delete</a>', delete_url)

    class Meta:
        attrs = {'class': 'table table-bordered'}
        sequence = ('...','delete')
    
class MainDutyTable(tables.Table):
    duty = tables.Column(verbose_name='Duty')
    delete = tables.Column(verbose_name='Delete', orderable=False)

    def render_delete(self, record):
        delete_url = reverse('delete_main_duty', args=[record['id']])
        return format_html('<a class="btn btn-danger" href="{}">Delete</a>', delete_url)
    
    class Meta:
        attrs = {'class': 'table table-bordered'}

class TrooperMainDutyTable(tables.Table):
    selection = tables.CheckBoxColumn(accessor='id',attrs = { "th__input": {"onclick": "toggle(this)"}}, orderable=False)
    start = tables.Column(verbose_name='Start')
    end = tables.Column(verbose_name='End')
    delete = tables.Column(verbose_name='Delete', orderable=False)

    def render_delete(self, record):

        delete_url = reverse('delete_trooper_main_duty', args=[record['id']])
        return format_html('<a href="{}">Delete</a>', delete_url)
        
    class Meta:
        attrs = {'class': 'table table-bordered', 'style':'font-weight:bold'}
        sequence = ('selection', '...','delete')


class AdditionalDutyTable(tables.Table):
    duty = tables.Column(verbose_name='Duty')
    delete = tables.Column(verbose_name='Delete', orderable=False)

    def render_delete(self, record):
        delete_url = reverse('delete_additional_duty', args=[record['id']])
        return format_html('<a class="btn btn-danger" href="{}">Delete</a>', delete_url)
    
    class Meta:
        attrs = {'class': 'table table-bordered'}


class TrooperAdditionalDutyTable(tables.Table):
    time_of_day = tables.Column(verbose_name='Time of Day')
    delete = tables.Column(verbose_name='Delete', orderable=False)

    def render_delete(self, record):
        delete_url = reverse('delete_trooper_additional_duty', args=[record['id']])
        return format_html('<a href="{}">Delete</a>', delete_url)

    class Meta:
        attrs = {'class': 'table table-bordered', 'style':'font-weight:bold'}
        sequence = ('...','delete')


class StrengthTable(tables.Table):
    name = tables.Column(verbose_name='Name')

    class Meta:
        attrs = {'class': 'table table-bordered'}

class PeakSecureTable(tables.Table):
    trooper = tables.Column(verbose_name='Trooper')
    peak = tables.Column(verbose_name='Peaks')
    secure = tables.Column(verbose_name='Secure')

    class Meta:
        attrs = {'class': 'table table-bordered'}