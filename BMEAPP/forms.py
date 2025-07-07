from django import forms
from .models import Asset, InstallationDocument,TrainigDocument,PurchaseDocument,Workbook,Gatepass,PRR,Departments
from django.contrib.auth.models import User, Group

class Create_AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['assetname','asset_make','asset_model','slno','dept','supplier','asset_type',
                  'pmdone','pmdur','caldone','caldur','wrstart','wrend','stat']
        
class Create_WorkForm(forms.ModelForm):
    class Meta:
        model = Workbook
        fields = [
                'wo_id',
                'asset_id',
                'asset_name',
                'description',
                'make',
                'model',
                'dept',
                'slno',
                'wo_date',
                'status',
                'reporter',
                'loginid',
                'usersign',         
        ]
        
class UserRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    group = forms.ModelChoiceField(queryset=Group.objects.all(), to_field_name="id", required=True, label='Group')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password','group']
        widgets = {
            'password': forms.PasswordInput(),
        }


class GatepassForm(forms.ModelForm):
    class Meta:
        model = Gatepass
        fields = [
            'pass_id',
            'collector_name',
            'send_to',
            'sender_name',
            'out_date',
            'bme_sign',
            'collector_sign',
            'contact_num',
            #'asset_name',
            ]
        
    def __init__(self, *arg, **kwargs):
        super(GatepassForm,self).__init__(*arg, **kwargs)

class GatepassApproval(forms.ModelForm):
    class Meta:
        model = Gatepass
        fields = [
            'status',
            'admin_sign',
            'pass_id',
            ]
        
    def __init__(self, *arg, **kwargs):
        super(GatepassApproval,self).__init__(*arg, **kwargs)

class gtSend(forms.ModelForm):
    class Meta:
        model = Gatepass
        fields = [
            'pass_id',
            'out_date',
            ]
        
    def __init__(self, *arg, **kwargs):
        super(gtSend,self).__init__(*arg, **kwargs)

class prCreateform(forms.ModelForm):
    class Meta:
        model = PRR
        fields = [
            'User_Name',
            'Dept',
            'Eq_Name',
            'Need',
            'Eq_Features',
            'User_Sign',
            'status'
            ]
        
    def __init__(self, *arg, **kwargs):
        super(prCreateform,self).__init__(*arg, **kwargs)




class ReportFilterForm(forms.Form):
    ASSET_TYPE_CHOICES = [
        ('CRITICAL', 'CRITICAL'),
        ('NON-CRITICAL', 'NON-CRITICAL')
    ]
    asset_type = forms.ChoiceField(choices=ASSET_TYPE_CHOICES, required=True)
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
#=======================================================================================================
#=======================================================================================================
from django import forms
from .models import Workbook, WorkDocument
from django.forms import modelformset_factory

class WorkbookForm(forms.ModelForm):
    class Meta:
        model = Workbook
        exclude = ['SR_report', 'invoice']  # include them if needed

class WorkDocumentForm(forms.ModelForm):
    class Meta:
        model = WorkDocument
        fields = ['asset_id', 'document']

WorkDocumentFormSet = modelformset_factory(
    WorkDocument,
    form=WorkDocumentForm,
    extra=1,
    can_delete=True
)


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Departments
        fields = ['LOCATION']