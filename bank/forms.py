from django import forms
from .models import *
from django.contrib.auth.forms import AuthenticationForm

class UsersForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['phone_number','password']
        widgets = {
            'password': forms.PasswordInput(),
        }
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['phone_number']
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        
        if phone_number:
            
            if not phone_number.startswith('+992'):
                raise forms.ValidationError('Nomer doljen nachinatsya s +992...')  
            
        return phone_number
    
    
class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Номер телефона')
    
    
class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name','last_name','address','passport_id']
        
class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['type']
        
        
class TransactionForm(forms.Form):
    receiver_phone = forms.CharField(max_length=13,required=False,label='Telefon poluchatelya')
    receiver_card = forms.CharField(max_length=16, required=False,label='Nomer Cart poluchatelya')
    
    
    amount = forms.IntegerField(label='summa Perevoda')
    
    
    from_account = forms.ModelChoiceField(queryset=Account.objects.none(), required=False, label="Iz scheta")
    from_card = forms.ModelChoiceField(queryset=Card.objects.none(), required=False, label="Iz Cart")
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['from_account'].queryset = Account.objects.filter(user=user)
            self.fields['from_card'].queryset = Card.objects.filter(user=user)
    