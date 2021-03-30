# Best way to load in a template is to use django.shortcuts import render
# This allows us to return a rendered template. render() takes the request object as 1st param
# The 2nd param is the template name we want to render, eg) "blog/home.html"
# The 3rd optional param is context, a way to pass info into our template
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


from django.contrib.auth import get_user_model


from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post #import the Post object ('.' because in same directory)
from .models import Trade, Game, Transaction
from django.db import connection
from dal import autocomplete
from django import forms
from django.contrib import messages
from django.contrib.messages import constants as message_constants
from django.db.models import Q
import datetime
from datetime import datetime
from django.shortcuts import redirect
import time
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required


# Transaction statuses
TRANSACTION_CANCELLED_BY_USER = 'Cancelled: Manually cancelled by ' # user3 on Mar 21, 7:14pm
TRANSACTION_OPEN = 'Open'

# MESSAGE CONSTANTS
DANGER = 30
SUCCESS = 25


# ~~~CREATE TRADE~~~
@login_required
def trade_new(request):
    form = TradeCreateForm()
    return render(request, 'blog/trade_form.html', {'form': form, 'title': 'Propose New Trade'})


@login_required
def insert_new_trade(request):
    user_who_posted = request.user # current user
    if ('the_game_you_own' not in request.POST or 'the_game_you_want_in_exchange' not in request.POST):
        messages.add_message(request, 30, 'There was a problem with one of the games you entered. Please try a different pair.')
        return trade_new(request)

    owned_game_id = request.POST['the_game_you_own']
    desired_game_id = request.POST['the_game_you_want_in_exchange']

    if owned_game_id == desired_game_id:
        messages.add_message(request, 30, 'The games cannot be the same')
        return trade_new(request)

    trades_with_desired_game = Trade.objects.filter(owned_game_id=desired_game_id, user_who_posted=user_who_posted)
    if trades_with_desired_game.count() > 0:
        trade = trades_with_desired_game.first()
        messages.add_message(request, 30, 'You specified in another trade that you already own ' + trade.owned_game.name + '. Delete the trade from the "Your Trades" page if you no longer own it.')
        return trade_new(request)

    games = Game.objects.filter(Q(id=owned_game_id) | Q(id=desired_game_id))

    #todo: replace with owned_game_id=owned_game_id
    trade = Trade(owned_game=games.filter(id=owned_game_id).first(), desired_game=games.filter(id=desired_game_id).first(), user_who_posted=user_who_posted)
    trade.save()
    messages.add_message(request, 25, 'Proposed trade was saved. Check your Matches to see if someone wants to do that trade.')
    return trade_new(request)


class TradeCreateForm(LoginRequiredMixin, forms.Form):
    the_game_you_own = forms.ModelChoiceField(
        queryset=Game.objects.all(),
        to_field_name='owned',
        widget=autocomplete.ModelSelect2(
            url='game-autocomplete',
            attrs={
                'data-minimum-input-length': 2, #res, sp
            },
        )
    )

    the_game_you_want_in_exchange = forms.ModelChoiceField(
        queryset=Game.objects.all(),
        to_field_name='desired',
        widget=autocomplete.ModelSelect2(
            url='game-autocomplete',
            attrs={
                'data-minimum-input-length': 2,
            },
        )
    )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class GameAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Game.objects.none()

        self.q = ('%' + self.q + '%').lower() # add '%' to complete LIKE clause
        qs = Game.objects.raw('SELECT Id AS id, name_and_platform AS name FROM blog_game WHERE LOWER( name_and_platform ) LIKE %s ORDER BY name_and_platform', [self.q])
        return qs


# ~~~DELETE TRADE~~~
@login_required
def delete_trade(request):
    if 'trade_id' not in request.POST:
        messages.add_message(request, DANGER, 'There was a problem deleting this trade. Please try again.')
        return redirect('/your-trades')
    trade_id = request.POST['trade_id']
    trade = Trade.objects.filter(id=trade_id)
    trade.delete()
    messages.add_message(request, SUCCESS, 'Trade deleted')
    return redirect('/your-trades')


# Go to home
def home(request):
    return render(request, 'blog/home.html')


# Confirmed Trades page
class ConfirmedTradesListView(LoginRequiredMixin, ListView):
    model = Trade
    template_name = 'blog/confirmed-trades.html'
    context_object_name = 'transactions'
    paginate_by = 3

    def get_queryset(self):
        current_user = self.request.user
        transactions = Transaction.objects.filter(
            (Q(trade_one__user_who_posted=current_user) | Q(trade_two__user_who_posted=current_user))
             & ~Q(status__startswith='Cancelled')).order_by('-created_date') #hardcode WITH CASE (bad)
        return transactions


# Cancelled Trades page
class CancelledTradesListView(LoginRequiredMixin, ListView):
    model = Trade
    template_name = 'blog/cancelled-trades.html'
    context_object_name = 'transactions'
    paginate_by = 3

    def get_queryset(self):
        current_user = self.request.user
        transactions = Transaction.objects.filter(
            (Q(trade_one__user_who_posted=current_user) | Q(trade_two__user_who_posted=current_user))
            & Q(status__startswith='Cancelled')).order_by('-created_date')  # hardcode WITH CASE (bad)
        return transactions


@login_required
def insert_transaction(request):
    print('~~~insert_transaction~~~')
    if 'trade_1_id' not in request.POST or 'trade_2_id' not in request.POST:
        messages.add_message(request, DANGER, 'There was a problem confirming this trade. Please try again.')
        return redirect('/matches')

    trade_one_id = request.POST['trade_1_id']
    trade_two_id = request.POST['trade_2_id']
    Trade.objects.filter(Q(id=trade_one_id) | Q(id=trade_two_id)).update(is_trade_proposed=True) # bulk update of 2 trade records

    transaction = Transaction(trade_one_id=trade_one_id, trade_two_id=trade_two_id)
    transaction.save()

    return redirect('confirmed-trade', pk=transaction.pk)



class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = 'blog/transaction_detail.html'


# ~~~Set Transaction to Cancelled~~~
@login_required
def set_transaction_to_cancelled_by_user(request):
    if request.POST.get('transaction_id') is None:
        messages.add_message(request, DANGER, 'There was a problem cancelling this trade. Please try again.')
        return redirect('/confirmed-trades')
    transaction_id = str(request.POST.get('transaction_id'))
    transaction = Transaction.objects.get(id=transaction_id)
    transaction.status = TRANSACTION_CANCELLED_BY_USER + ' ' + str(request.user)
    transaction.user_cancelled_date = timezone.now()
    transaction.save()

    # bulk update of 2 trade records so they show up on Matches page again
    Trade.objects.filter(Q(id=transaction.trade_one_id) | Q(id=transaction.trade_two_id)).update(is_trade_proposed=False)
    messages.add_message(request, SUCCESS, 'Trade cancelled')
    return redirect('confirmed-trade', pk=transaction.pk)


# ~~~Set Transaction to Open~~~
@login_required
def set_transaction_to_open(request):
    if request.POST.get('transaction_id') is None:
        messages.add_message(request, DANGER, 'There was a problem confirming this trade. Please try again.')
        return redirect('/confirmed-trades')

    transaction_id = str(request.POST.get('transaction_id'))
    transaction = Transaction.objects.get(id=transaction_id)
    transaction.status = TRANSACTION_OPEN
    transaction.save()

    messages.add_message(request, SUCCESS, 'Trade is now Open')
    return redirect('confirmed-trade', pk=transaction.pk)


# Matches page
class TradeListView(LoginRequiredMixin, ListView):
    model = Trade
    template_name = 'blog/matches.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'trades'
    paginate_by = 5

    def get_queryset(self):
        current_user_id = self.request.user.id
        # Get trades of other users who match your submitted trades
        # t1 is the current_user's trade, t2 is the matched trade
        trades = Trade.objects.raw('SELECT DISTINCT t1.id AS id, '  #todo: order by membership type
                                   't2.id AS t2_id, '
                                   't2.name AS t2_name, ' 
                                   't1.owned_game as t1_owned_game, '
                                   't1.desired_game as t1_desired_game, '
                                   't2.user_who_posted_id as t2_user_who_posted_id, '
                                   't2.created_date as t2_created_date, '
                                   'u1.username as t2_username ' 
                                   'FROM blog_Trade t1, blog_Trade t2, auth_user u1 '
                                   'WHERE t1.owned_game = t2.desired_game '
                                   'AND t1.desired_game = t2.owned_game '
                                   'AND t1.user_who_posted_id = %s '
                                   'AND t1.is_trade_proposed = false '
                                   'AND t2.is_trade_proposed = false '
                                   'AND u1.id = t2.user_who_posted_id',
                                   [current_user_id])

        return trades


# Your Trades page
class YourTradesListView(LoginRequiredMixin, ListView):
    model = Trade
    template_name = 'blog/your-trades.html'
    context_object_name = 'trades'
    paginate_by = 5

    def get_queryset(self):
        current_user = self.request.user
        trades = Trade.objects.filter(user_who_posted=current_user).order_by('-created_date')
        return trades


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(get_user_model(), username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


# Go to About page
def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})


# Go to FAQ page
def faq(request):
    return render(request, 'blog/faq.html', {'title': 'FAQ'})
