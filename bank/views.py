from django.shortcuts import render,redirect
from .models import User,Account
from .forms import *
from django.contrib.auth.views import LoginView,LogoutView
from django.views.generic import CreateView,DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
import random
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
class Register(CreateView):
    form_class = UsersForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')
    
class Login(LoginView):
    authentication_form = LoginForm
    template_name = 'login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('account_create')
    
class Logout(LogoutView):
    next_page = reverse_lazy('login')
    
    
class AccountCreate(LoginRequiredMixin,CreateView):
    model = Account
    form_class = AccountForm
    template_name = 'account_create.html'
    success_url = reverse_lazy('account')
    
    
    def dispatch(self, request, *args, **kwargs):
        
        account = Account.objects.filter(user=request.user).exists()
        if account:
            return redirect('account')
            
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    
    
class AccountDetail(LoginRequiredMixin,DetailView):
    model = Account
    template_name = 'account.html'
    context_object_name = 'account'
    
    def get_object(self, queryset = None):
        return Account.objects.filter(user=self.request.user).first()
    
class CardCreate(LoginRequiredMixin,CreateView):
    model = Card
    form_class = CardForm
    template_name = 'card_create.html'
    success_url = reverse_lazy('account')
    
    
    def form_valid(self, form):
        
        form.instance.user = self.request.user
        
        kod_16_rakama = []
        for i in range(16):
            kod = random.randint(0,9)
            kod1 = str(kod)
            kod_16_rakama.append(kod1)
        
        form.instance.card_number = ''.join(kod_16_rakama)
        
        form.instance.cvv = ''.join(str(random.randint(100,999)))
        
        
        pin = []
        for i in range(4):
            kod = str(random.randint(0,9))
            pin.append(kod)
            
        form.instance.pin = ''.join(pin)
               
        form.instance.date = timezone.now().date() + timedelta(days=365 * 3)
        
        
        return super().form_valid(form)
    

class CardDetail(DetailView):
    model = Card
    template_name = 'card_detail.html'
    context_object_name = 'card'
    
    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)
    
@login_required
def transfer_view(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            receiver_phone = form.cleaned_data.get('receiver_phone')
            receiver_card = form.cleaned_data.get('receiver_card')
            from_account = form.cleaned_data.get('from_account')
            from_card = form.cleaned_data.get('from_card')
            
            
            if amount <= 0:
                form.add_error('amount', 'Summa doljen bit bolshe nuli')
                return render(request, 'transfer.html', {'form': form})
            
            vbor = None
            if from_account:
                vbor = from_account
            elif from_card:
                vbor = from_card
                
            else:
                form.add_error(None, 'Vberite schot')
                return render(request, 'transfer.html', {'form': form})
            
            if vbor.balance < amount:
                form.add_error('amount','Nedostatochno sredstva')
                return render(request, 'transfer.html', {'form': form})
            
            
            receiver_user = None
            receiver_account = None
            receiver_card_obj = None
            
            
        
            if receiver_phone:
                receiver_user = User.objects.filter(phone_number = receiver_phone).first()
                if not receiver_user:
                    form.add_error('receiver_phone', 'Polzovatel s takimi nomerom ne naydeno')
                    return render(request, 'transfer.html', {'form': form})
                
                receiver_account = Account.objects.filter(user = receiver_user).first()
                if not receiver_account:
                    form.add_error('receiver_phone','U polzovatelya netu kart')
                    return render(request,'transfer.html',{'form':form})
                
                
            elif receiver_card :
                receiver_card_obj = Card.objects.filter(card_number=receiver_card).first()
                if not receiver_card_obj:
                    form.add_error('receiver_card','karta s takim nomer ne nayden')
                    return render(request,'transfer.html',{'form':form})
                receiver_user = receiver_card_obj.user
            else:
                form.add_error(None, 'Ukajiye poluchatelya Telefon ili Kartu')
                return render(request,'transfer.html',{'form':form})

   
            if from_account and receiver_account and from_account == receiver_account:
                form.add_error(None, 'Nelzya perevodit na tot je samiy schot')
                return render(request, 'transfer.html', {'form': form})
                            
            if from_card and receiver_card_obj and from_card == receiver_card_obj:
                form.add_error(None, 'Nelzya perevodit na tot je samuyu kartu')
                return render(request, 'transfer.html', {'form': form})
                        

            vbor.balance -= amount
            vbor.save()
        
            if receiver_phone:
                receiver_account.balance += amount
                receiver_account.save()
            
            elif receiver_card:
                receiver_card_obj.balance += amount
                receiver_card_obj.save()
            
            
            to_acc = None
            to_crd = None
        
        
            if receiver_phone:
                to_acc = receiver_account
            elif receiver_card:
                to_crd = receiver_card_obj
            
            
            Transaction.objects.create(
                sender=request.user,
                receiver=receiver_user,
                amount=amount,
                from_account=from_account,
                from_card=from_card,
                to_account = to_acc,
                to_card = to_crd
            )
          
            
            return redirect('account')
        
    else:
        form = TransactionForm(user = request.user)
        
    return render(request, 'transfer.html',{'form':form})
            
            
    
                
                
            
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import Transaction, Card

@login_required
def transaction_history_view(request, card_id=None):
    filter_type = request.GET.get('filter', 'all')
    target_card = None

    if card_id:

        target_card = get_object_or_404(Card, id=card_id, user=request.user)
        
        if filter_type == 'sent':
            transactions = Transaction.objects.filter(from_card=target_card).order_by('-id')
        elif filter_type == 'received':
            transactions = Transaction.objects.filter(to_card=target_card).order_by('-id')
        else:

            sent_list = list(Transaction.objects.filter(from_card=target_card))
            received_list = list(Transaction.objects.filter(to_card=target_card))

            combined = list(set(sent_list + received_list))
            transactions = sorted(combined, key=lambda x: x.id, reverse=True)
            
    else:
        if filter_type == 'sent':
            transactions = Transaction.objects.filter(sender=request.user).order_by('-id')
        elif filter_type == 'received':
            transactions = Transaction.objects.filter(receiver=request.user).order_by('-id')
        else:
            sent_list = list(Transaction.objects.filter(sender=request.user))
            received_list = list(Transaction.objects.filter(receiver=request.user))
            combined = list(set(sent_list + received_list))
            transactions = sorted(combined, key=lambda x: x.id, reverse=True)
        
    context = {
        'transactions': transactions,
        'current_filter': filter_type,
        'card': target_card,
    }
    return render(request, 'history.html', context)