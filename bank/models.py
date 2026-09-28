from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    phone_number = models.CharField(max_length=13, unique=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    def __str__(self):
        return self.phone_number
    
    
class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='account')
    first_name = models.CharField(max_length=75)
    last_name = models.CharField(max_length=75)
    address = models.CharField(max_length=75)
    passport_id = models.CharField(max_length=9,unique=True)
    balance = models.IntegerField(default=1000)
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    
class Card(models.Model):
    card_number = models.CharField(max_length=16,unique=True)
    cvv = models.CharField(max_length=3)
    date = models.DateField()
    type = models.CharField(max_length=50,default='Credit')
    pin = models.CharField( max_length=4)
    balance = models.IntegerField(default=500)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='cards')
    
    def __str__(self):
        return f'{self.card_number}'
    
    
class Transaction(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE,related_name='sender',null=True,blank=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE,related_name='receiver',null=True,blank=True)
    amount = models.IntegerField()
    cr_at = models.DateTimeField(auto_now_add=True)
    
    
    
    from_account = models.ForeignKey(Account, on_delete=models.CASCADE,related_name='from_account',null=True,blank=True)
    from_card = models.ForeignKey(Card, on_delete=models.CASCADE,related_name='from_card',null=True,blank=True)
    to_account = models.ForeignKey(Account, on_delete=models.CASCADE,related_name='to_account',null=True,blank=True)
    to_card = models.ForeignKey(Card, on_delete=models.CASCADE,related_name='to_card',null=True,blank=True)
    
    
    def __str__(self):
        return f'{self.id}  {self.amount}'