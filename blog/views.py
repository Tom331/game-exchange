# Best way to load in a template is to use django.shortcuts import render
# This allows us to return a rendered template. render() takes the request object as 1st param
# The 2nd param is the template name we want to render, eg) "blog/home.html"
# The 3rd optional param is context, a way to pass info into our template
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django_project import settings
from asgiref.sync import sync_to_async

print('~~~top of blog/views.py~~~')


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
from django.http import HttpResponseRedirect, Http404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from math import sin, cos, sqrt, atan2, radians
from functools import wraps
from django.db import connection
from django.template import Context, Template
from django.core.mail import send_mail
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import PrependedText
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Hidden, Field


# Transaction statuses
CANCELLED_BY_USER = 'Cancelled: Manually cancelled by ' # eg) "Cancelled: Manually cancelled by user3 on Mar 21, 7:14pm"
TRANSACTION_OPEN = 'Open'
COMPLETED_BY_ONE_USER_PREFIX = 'Completed by ' # eg) "Completed by User1. Waiting on confirmation from User2."
COMPLETED_BY_BOTH_USERS = 'Completed by both users' # Both users have completed the trade
FLAGGED_AS_INCOMPLETE = 'Flagged as incomplete by ' # by username


# Message Prompts
DANGER = 30 # Red message
SUCCESS = 25 # Green message

# Buffer added to travel radius if no matches found
NO_MATCHES_KM_BUFFER = 15 # I'm assuming users would be willing to travel an additional 15km (in any direction) to meet
                          # The reason this is 15 and not 30, is because we display the RADIUS to the user, not diameter
                          # So when you increase travel_radius by 15km, you're increasing the RADIUS, not the DIAMETER

PREMIUM_TRADES_ALLOWED = 3 # TODO: set to 6 # Confirmed Offers allowed for each membership type
MAX_TRADES_PER_USER = 30 # Max number of trades allowed to be entered by each user

# ~~~CREATE a TRADE~~~
@login_required
def trade_new(request):
    email_check = check_email_confirmation(request)
    if email_check != None:
        return email_check
    form = TradeCreateForm()
    return render(request, 'blog/trade_form.html', {'form': form, 'title': 'Propose New Trade'})


# ~~~CREATE a BUY TRADE~~~
@login_required
def buy_new(request):
    email_check = check_email_confirmation(request)
    if email_check is not None:
        return email_check
    form = BuyCreateForm()
    return render(request, 'blog/buy_form.html', {'form': form, 'title': 'Offer to Buy a Game'})


# ~~~CREATE a SELL TRADE~~~
@login_required
def sell_new(request):
    email_check = check_email_confirmation(request)
    if email_check != None:
        return email_check
    form = SellCreateForm()
    return render(request, 'blog/sell_form.html', {'form': form, 'title': 'Offer to Sell a Game'})


@login_required
def insert_new_trade(request):
    current_user = request.user # current user
    if 'the_game_you_own' not in request.POST or 'the_game_you_want_in_exchange' not in request.POST or 'condition' not in request.POST:
        messages.add_message(request, 30, 'There was a problem with one of the games you entered. Please try a different pair.')
        return trade_new(request)

    owned_game_id = request.POST['the_game_you_own']
    desired_game_id = request.POST['the_game_you_want_in_exchange']

    if owned_game_id == desired_game_id:
        messages.add_message(request, 30, 'The games cannot be the same')
        return trade_new(request)

    trades_with_desired_game = Trade.objects.filter(owned_game_id=desired_game_id, user_who_posted=current_user, is_completed=False)
    if trades_with_desired_game.count() > 0:
        trade = trades_with_desired_game.first()
        messages.add_message(request, 30, 'Trade was not saved. You specified in another offer that you already own ' + trade.owned_game.name
             + '. Delete the offer from the "Your Offers" page if you no longer own it.')
        return trade_new(request)

    duplicates = Trade.objects.filter(owned_game_id=owned_game_id, desired_game_id=desired_game_id, user_who_posted=current_user, is_completed=False)
    if duplicates.count() > 0:
        messages.add_message(request, 30, 'Trade was not saved. You have already submitted a proposed trade with that owned game and desired game.')
        return trade_new(request)

    total_trades = Trade.objects.filter(Q(user_who_posted=current_user) & Q(is_completed=False)) # Get non-completed trades for this user
    if total_trades.count() >= MAX_TRADES_PER_USER:
        messages.add_message(request, 30, 'Trade was not saved. Each user can only submit up to 30 trade proposals. Reach out to support if you wish to increase your limit.')
        return trade_new(request)

    trade = Trade(owned_game_id=owned_game_id, desired_game_id=desired_game_id, user_who_posted=current_user, condition=request.POST['condition'])
    trade.save()

    # Query for matches. Includes matches outside travel_radius, but within NO_MATCHES_KM_BUFFER
    current_user = request.user

    matches = Trade.objects.raw('SELECT DISTINCT t1.id AS id, ' 
                               't2.id AS t2_id, '
                               't2.name AS t2_name, '
                               't2.user_who_posted_id as t2_user_who_posted_id, '
                               'u1.lat as t2_lat, '
                               'u1.long as t2_long, '
                               'u1.travel_radius as t2_travel_radius '
                               'FROM blog_Trade t1, blog_Trade t2, users_myuser u1 '
                               'WHERE %s = t2.desired_game '
                               'AND %s = t2.owned_game '
                               'AND t1.user_who_posted_id = %s '
                               'AND t1.is_trade_proposed = false '
                               'AND t2.is_trade_proposed = false '
                               'AND t1.is_completed = false '
                               'AND t2.is_completed = false '
                               'AND u1.id = t2.user_who_posted_id '
                               'AND NOT(u1.email_confirmed = false AND %s > u1.email_confirmation_due_date) '

                               # 6373.0 = radius of earth in km. 
                               """ 
                               AND (6373.0 * (2 * atan2(sqrt((POWER(sin((%s - RADIANS(u1.lat)) / 2), 2) + cos(%s)
                               * cos(RADIANS(u1.lat)) * POWER(sin((%s - RADIANS(u1.long)) / 2), 2))),sqrt(1 - (POWER(sin((%s - RADIANS(u1.lat)) / 2), 2) + cos(%s)
                               * cos(RADIANS(u1.lat)) * POWER(sin((%s - RADIANS(u1.long)) / 2), 2)))))) < ( %s + u1.travel_radius + %s)
                                """,
                               [owned_game_id, desired_game_id, current_user.id, datetime.now(), radians(current_user.lat), radians(current_user.lat),
                                radians(current_user.long), radians(current_user.lat), radians(current_user.lat), radians(current_user.long),
                                current_user.travel_radius, 0]) # NO_MATCHES_KM_BUFFER: do not add buffer, what if there are other matches blocking the buffer?

    if len(matches) > 0:
        messages.add_message(request, 25, 'Congratulations! That trade has a match with someone nearby. Visit the "Your Matches" page to arrange a meetup.')
    else:
        messages.add_message(request, 25, 'Proposed trade was saved but no match was found. Check back later on the "Your Matches" page, or propose a new trade.')

    if current_user.first_trade_proposal is True:
        current_user.first_trade_proposal = False
        current_user.save()
        return render(request, 'blog/trade_form.html', {'form': TradeCreateForm(), 'title': 'Propose New Trade', 'first_trade_proposal': 'true'})
    else:
        return trade_new(request)


@login_required
def insert_new_buy_trade(request):
    current_user = request.user # current user
    if 'desired_game' not in request.POST or 'buy_price' not in request.POST:
        messages.add_message(request, 30, 'There was a problem with with the desired game or buy price. Please try again. Contact support if the issue reoccurs.')
        return buy_new(request)

    buy_price = request.POST['buy_price']
    desired_game_id = request.POST['desired_game']

    validation_redirect = is_buy_valid(request, current_user, desired_game_id, None) # Ensure no duplicates or other validation errors
    if validation_redirect is not True:
        return buy_new(request) # Validation error found: Redirect to previous page and show error

    trade = Trade(desired_game_id=desired_game_id, buy_price=buy_price, user_who_posted=current_user)
    trade.save()

    is_match_found = find_buy_match(buy_price, desired_game_id, current_user)
    if is_match_found:
        messages.add_message(request, 25, 'Congratulations! That offer has a match with someone nearby. Visit the "Your Matches" page to arrange a meetup.')
    else:
        messages.add_message(request, 25, 'Your offer to buy was saved but no match was found. Check back later on the "Your Matches" page, or make another offer.')

    if current_user.first_trade_proposal is True:
        current_user.first_trade_proposal = False
        current_user.save()
        return render(request, 'blog/buy_form.html', {'form': BuyCreateForm(), 'title': 'Offer to Buy a Game', 'first_trade_proposal': 'true'})
    else:
        return buy_new(request)


def find_buy_match(buy_price, desired_game_id, current_user): # Any matches found when inserting or updating a buy trade?
    matches = Trade.objects.raw('SELECT DISTINCT t1.id AS id, '
                                't2.id AS t2_id, '
                                't2.name AS t2_name, '
                                't2.user_who_posted_id as t2_user_who_posted_id, '
                                'u1.lat as t2_lat, '
                                'u1.long as t2_long, '
                                'u1.travel_radius as t2_travel_radius '
                                'FROM blog_Trade t1, blog_Trade t2, users_myuser u1 '
                                'WHERE %s >= t2.sell_price '
                                'AND %s = t2.owned_game '
                                'AND t1.user_who_posted_id = %s '
                                'AND t1.is_trade_proposed = false '
                                'AND t2.is_trade_proposed = false '
                                'AND t1.is_completed = false '
                                'AND t2.is_completed = false '
                                'AND u1.id = t2.user_who_posted_id '
                                'AND NOT(u1.email_confirmed = false AND %s > u1.email_confirmation_due_date) '

                                # 6373.0 = radius of earth in km. 
                                """ 
                                AND (6373.0 * (2 * atan2(sqrt((POWER(sin((%s - RADIANS(u1.lat)) / 2), 2) + cos(%s)
                                * cos(RADIANS(u1.lat)) * POWER(sin((%s - RADIANS(u1.long)) / 2), 2))),sqrt(1 - (POWER(sin((%s - RADIANS(u1.lat)) / 2), 2) + cos(%s)
                                * cos(RADIANS(u1.lat)) * POWER(sin((%s - RADIANS(u1.long)) / 2), 2)))))) < ( %s + u1.travel_radius + %s)
                                 """,
                                [buy_price, desired_game_id, current_user.id, datetime.now(), radians(current_user.lat),
                                 radians(current_user.lat),
                                 radians(current_user.long), radians(current_user.lat), radians(current_user.lat),
                                 radians(current_user.long),
                                 current_user.travel_radius,
                                 0])  # NO_MATCHES_KM_BUFFER: do not add buffer, what if there are other matches blocking the buffer?

    if len(matches) > 0:
        return True
    else:
        return False


def is_buy_valid(request, current_user, desired_game_id, current_trade_id):
    trades_with_desired_game = Trade.objects.filter(~Q(id=current_trade_id), owned_game_id=desired_game_id, user_who_posted=current_user, is_completed=False)
    if trades_with_desired_game.count() > 0: # Someone may want 2 copies, but then why are they trading away their current copy?
        trade = trades_with_desired_game.first()
        messages.add_message(request, 30, 'Offer was not saved. You specified in another offer that you already own ' + trade.owned_game.name
             + '. Delete the offer from the "Your Offers" page if you no longer own it.')
        return False

    duplicates = Trade.objects.filter(~Q(id=current_trade_id), desired_game_id=desired_game_id, buy_price__isnull=False, user_who_posted=current_user, is_completed=False)
    if duplicates.count() > 0:
        messages.add_message(request, 30, 'Offer was not saved. You have already submitted an offer to buy ' + str(duplicates.first().desired_game) +
             '. You can update the existing offer on the "Your Offers" page.')
        return False

    total_trades = Trade.objects.filter(Q(user_who_posted=current_user) & Q(is_completed=False)) # Get non-completed trades for this user
    if total_trades.count() >= MAX_TRADES_PER_USER:
        messages.add_message(request, 30, 'Each user can only submit up to 30 trade proposals. Reach out to support if you wish to increase your limit.')
        return False

    return True # No validation errors


@login_required
def insert_new_sell_trade(request):
    current_user = request.user # current user
    if 'owned_game' not in request.POST or 'sell_price' not in request.POST or 'condition' not in request.POST:
        messages.add_message(request, 30, 'There was a problem with with the desired game or sell price. Please try again. Contact support if the issue reoccurs.')
        return sell_new(request)

    sell_price = request.POST['sell_price']
    owned_game_id = request.POST['owned_game']

    trades_with_owned_game = Trade.objects.filter(desired_game_id=owned_game_id, user_who_posted=current_user, is_completed=False)
    if trades_with_owned_game.count() > 0:
        trade = trades_with_owned_game.first()
        messages.add_message(request, 30, 'Offer was not saved. You specified in another offer that your desired game is ' + str(trade.desired_game.name)
             + '. Delete the offer from the "Your Offers" page if you want to sell it.')
        return sell_new(request)

    # Users can have another trade record where their owned_game is 'owned_game_id', with a desired game being something else. hence null check
    duplicates = Trade.objects.filter(owned_game_id=owned_game_id, sell_price__isnull=False, user_who_posted=current_user, is_completed=False)
    if duplicates.count() > 0:
        messages.add_message(request, 30, 'Offer was not saved. You have already submitted an offer to sell ' + str(
            duplicates.first().owned_game) +'. You can update the existing offer on the "Your Offers" page.')
        return sell_new(request)

    total_trades = Trade.objects.filter(Q(user_who_posted=current_user) & Q(is_completed=False)) # Get non-completed trades for this user
    if total_trades.count() >= MAX_TRADES_PER_USER:
        messages.add_message(request, 30, 'Each user can only submit up to 30 offers. Reach out to support if you wish to increase your limit.')
        return sell_new(request)

    trade = Trade(owned_game_id=owned_game_id, sell_price=sell_price, user_who_posted=current_user, condition=request.POST['condition'])
    trade.save()

    is_match_found = find_sell_match(sell_price, owned_game_id, current_user)

    if is_match_found:
        messages.add_message(request, 25, 'Congratulations! That offer has a match with someone nearby. Visit the "Your Matches" page to arrange a meetup.')
    else:
        messages.add_message(request, 25, 'Your offer to sell was saved but no match was found. Check back later on the "Your Matches" page, or make another offer.')

    if current_user.first_trade_proposal is True:
        current_user.first_trade_proposal = False
        current_user.save()
        return render(request, 'blog/sell_form.html', {'form': SellCreateForm(), 'title': 'Offer to Sell a Game', 'first_trade_proposal': 'true'})
    else:
        return sell_new(request)


def find_sell_match(sell_price, owned_game_id, current_user): # Any matches found when inserting or updating a buy trade?
    matches = Trade.objects.raw('SELECT DISTINCT t1.id AS id, '
                                't2.id AS t2_id, '
                                't2.name AS t2_name, '
                                't2.user_who_posted_id as t2_user_who_posted_id, '
                                'u1.lat as t2_lat, '
                                'u1.long as t2_long, '
                                'u1.travel_radius as t2_travel_radius '
                                'FROM blog_Trade t1, blog_Trade t2, users_myuser u1 '
                                'WHERE %s <= t2.buy_price '
                                'AND %s = t2.desired_game '
                                'AND t1.user_who_posted_id = %s '
                                'AND t1.is_trade_proposed = false '
                                'AND t2.is_trade_proposed = false '
                                'AND t1.is_completed = false '
                                'AND t2.is_completed = false '
                                'AND u1.id = t2.user_who_posted_id '
                                'AND NOT(u1.email_confirmed = false AND %s > u1.email_confirmation_due_date) '

                                # 6373.0 = radius of earth in km. 
                                """ 
                                AND (6373.0 * (2 * atan2(sqrt((POWER(sin((%s - RADIANS(u1.lat)) / 2), 2) + cos(%s)
                                * cos(RADIANS(u1.lat)) * POWER(sin((%s - RADIANS(u1.long)) / 2), 2))),sqrt(1 - (POWER(sin((%s - RADIANS(u1.lat)) / 2), 2) + cos(%s)
                                * cos(RADIANS(u1.lat)) * POWER(sin((%s - RADIANS(u1.long)) / 2), 2)))))) < ( %s + u1.travel_radius + %s)
                                 """,
                                [sell_price, owned_game_id, current_user.id, datetime.now(), radians(current_user.lat),
                                 radians(current_user.lat),
                                 radians(current_user.long), radians(current_user.lat), radians(current_user.lat),
                                 radians(current_user.long),
                                 current_user.travel_radius,
                                 0])  # NO_MATCHES_KM_BUFFER: do not add buffer, what if there are other matches blocking the buffer?

    if len(matches) > 0:
        return True
    else:
        return False


@login_required
def set_confirm_trade_email_preference(request):
    request.user.first_trade_proposal = False # User has now inserted their first trade proposal and has just seen email notif. modal
    if 'user_id' not in request.POST or 'notifications' not in request.POST:
        messages.add_message(request, 30, 'There was a problem updating your email notification settings. Try updating them on the Account page.')
        return trade_new(request)

    if request.POST['notifications'] == 'yes':
        request.user.confirmed_trade_email_opt_in = True
        messages.add_message(request, 25,'Email notifications are turned on. They can be updated any time on the Account page.')
    elif request.POST['notifications'] == 'no':
        messages.add_message(request, 25, 'Email notifications are turned off. They can be updated any time on the Account page.')
    else:
        messages.add_message(request, 30, 'There was a problem updating your email notification settings. Try updating them on the Account page.')
    request.user.save()
    source_page = request.POST['source_page'] if 'source_page' in request.POST else None
    if source_page == 'trade':
        return trade_new(request)
    elif source_page == 'buy':
        return buy_new(request)
    elif source_page == 'sell':
        return sell_new(request)
    else:
        return render(request, 'blog/your-trades.html', {'title': 'Your Offers'})


# Form for creating a new Trade
class TradeCreateForm(LoginRequiredMixin, forms.Form):
    the_game_you_own = forms.ModelChoiceField(
        queryset=Game.objects.all(),
        to_field_name='owned',
        widget=autocomplete.ModelSelect2(
            url='game-autocomplete',
            attrs={
                'data-minimum-input-length': 2,
            },
        )
    )

    condition = forms.ChoiceField(choices=Trade.CONDITION_CHOICES, initial='Fair - 1 or 2 small scratches', label='Disc condition of your game', required=True)

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


# Form for creating a new "buy" Trade
class BuyCreateForm(LoginRequiredMixin, forms.Form):
    desired_game = forms.ModelChoiceField(
        queryset=Game.objects.all(),
        to_field_name='desired_game',
        widget=autocomplete.ModelSelect2(
            url='game-autocomplete',
            attrs={
                'data-minimum-input-length': 2,
            },
        )
    )

    buy_price = forms.IntegerField()

    def __init__(self, *args, **kwargs): # Set label for buy_price
        super(BuyCreateForm, self).__init__( *args, **kwargs)
        self.fields['buy_price'].label = "Max. Buy Price: The highest amount you would pay for this game"

        self.helper = FormHelper()  # prepend $ to buy_price
        self.helper.layout = Layout(
            Field('desired_game'),
            PrependedText('buy_price', '$'),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='post-button btn btn-outline-info')
            )
        )
        self.fields['buy_price'].required = True
        self.fields['desired_game'].required = True

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


# Form for updating a "buy" trade
class BuyUpdateForm(LoginRequiredMixin, forms.ModelForm):
    class Meta:
        model = Trade
        fields = ['buy_price', 'desired_game']

    def __init__(self, *args, **kwargs):  # Set label for buy_price
        super(BuyUpdateForm, self).__init__( *args, **kwargs)

        self.helper = FormHelper()  # prepend $ to buy_price
        self.helper.layout = Layout(
            PrependedText('buy_price', '$'),
            Field('desired_game'),
            ButtonHolder(
                Submit('submit', 'Update', css_class='post-button btn btn-outline-info')
            )
        )

        self.fields['buy_price'].label = "Max. Buy Price: The highest amount you would pay for this game"
        self.fields['desired_game'].help_text = "Make a new offer to find matches for other games."
        self.fields['desired_game'].disabled = True
        self.fields['buy_price'].required = True
        self.fields['desired_game'].required = True

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)



# Form for creating a new "sell" Trade
class SellCreateForm(LoginRequiredMixin, forms.Form):
    owned_game = forms.ModelChoiceField(
        queryset=Game.objects.all(),
        to_field_name='owned',
        widget=autocomplete.ModelSelect2(
            url='game-autocomplete',
            attrs={
                'data-minimum-input-length': 2,
            },
        )
    )

    sell_price = forms.IntegerField()
    condition = forms.ChoiceField(choices=Trade.CONDITION_CHOICES, initial='Fair - 1 or 2 small scratches', label='Disc condition of your game', required=True)



    def __init__(self, *args, **kwargs): # Set label for buy_price
        super(SellCreateForm, self).__init__(*args, **kwargs)
        self.fields['sell_price'].label = "Min. Sell Price: The lowest amount you would take for this game"

        self.helper = FormHelper()  # prepend $ to buy_price
        self.helper.layout = Layout(
            Field('owned_game'),
            PrependedText('sell_price', '$'),
            Field('condition'),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='post-button btn btn-outline-info')
            )
        )

        self.fields['sell_price'].required = True
        self.fields['owned_game'].required = True
        self.fields['condition'].required = True

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


# Form for updating a new "sell" Trade
class SellUpdateForm(LoginRequiredMixin, forms.ModelForm):
    class Meta:
        model = Trade
        fields = ['sell_price', 'owned_game', 'condition']

    condition = forms.ChoiceField(choices=Trade.CONDITION_CHOICES, label='Disc condition of your game', required=True)

    def __init__(self, *args, **kwargs):  # Set label for buy_price
        super(SellUpdateForm, self).__init__( *args, **kwargs)
        self.fields['sell_price'].label = "Min. Sell Price: The lowest amount you would take for this game"
        self.fields['owned_game'].help_text  = "Make a new offer to find matches for other games."
        self.fields['owned_game'].disabled= True

        self.helper = FormHelper()  # prepend $ to buy_price
        self.helper.layout = Layout(
            PrependedText('sell_price', '$'),
            Field('owned_game'),
            Field('condition'),
            ButtonHolder(
                Submit('submit', 'Update', css_class='post-button btn btn-outline-info')
            )
        )

        self.fields['sell_price'].required = True
        self.fields['owned_game'].required = True
        self.fields['condition'].required = True

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


# UPDATE "BUY" TRADE
@login_required
def update_buy(request, pk):
    email_check = check_email_confirmation(request) # Ensure email confirmation not overdue
    if email_check != None:
        return email_check

    offer = Trade.objects.filter(id=pk).first()
    if request.method == 'POST':
        current_user = request.user  # current user
        if 'hidden_desired_game' not in request.POST or 'buy_price' not in request.POST:
            messages.add_message(request, 30, 'There was a problem with with the desired game or buy price. Please try again. Contact support if the issue reoccurs.')
            return buy_new(request)

        buy_price = request.POST['buy_price']
        desired_game_id = request.POST['hidden_desired_game'] # hidden input element because disabled elements do not send over POST

        offer.buy_price = buy_price
        offer.desired_game_id = desired_game_id

        buy_form = BuyUpdateForm(request.POST, instance=offer)
        if buy_form.is_valid():
            buy_form.save()
            is_match_found = find_buy_match(offer.buy_price, offer.desired_game_id, current_user)
            if is_match_found:
                messages.add_message(request, 25, 'Congratulations! That offer has a match with someone nearby. Visit the "Your Matches" page to arrange a meetup.')
            else:
                messages.add_message(request, 25, 'Your offer to buy was saved but no match was found. Check back later on the "Your Matches" page, or make another offer.')
            context = {'form': buy_form, 'is_update': True, 'title': 'Update Offer Form', 'offer': offer}
            return render(request, 'blog/buy_form.html', context)

    else: #GET request
        if offer is None or offer.desired_game is None or offer.buy_price is None: # If a Trade with this id is not found, redirect to custom 404 page
            messages.add_message(request, 30, 'This offer was not found. It may have been deleted.')
            return render(request, 'users/display_messages.html', {'title': 'Game Exchange: Offer Not Found'})

        buy_form = BuyUpdateForm() # ModelForm
        buy_form.fields['buy_price'].initial = offer.buy_price
        buy_form.fields['desired_game'].initial = offer.desired_game.id
        context = {'form': buy_form, 'is_update': True, 'title': 'Update Offer Form', 'offer': offer} #is_update tells template to disable desired_game
        return render(request, 'blog/buy_form.html', context)


# UPDATE "SELL" TRADE
@login_required
def update_sell(request, pk):
    email_check = check_email_confirmation(request) # Ensure email confirmation not overdue
    if email_check != None:
        return email_check

    offer = Trade.objects.filter(id=pk).first()

    if request.method == 'POST':
        current_user = request.user  # current user
        if 'hidden_owned_game' not in request.POST or 'sell_price' not in request.POST:
            messages.add_message(request, 30, 'There was a problem with with the owned game or sell price. Please try again. Contact support if the issue reoccurs.')
            return buy_new(request)

        sell_price = request.POST['sell_price']
        owned_game_id = request.POST['hidden_owned_game'] # hidden input element because disabled elements do not send over POST

        offer.sell_price = sell_price
        offer.owned_game_id = owned_game_id

        sell_form = SellUpdateForm(request.POST, instance=offer)
        if sell_form.is_valid():
            sell_form.save()
            is_match_found = find_sell_match(offer.sell_price, offer.owned_game_id, current_user)
            if is_match_found:
                messages.add_message(request, 25, 'Congratulations! That offer has a match with someone nearby. Visit the "Your Matches" page to arrange a meetup.')
            else:
                messages.add_message(request, 25, 'Your offer to buy was saved but no match was found. Check back later on the "Your Matches" page, or make another offer.')
            context = {'form': sell_form, 'is_update': True, 'title': 'Update Trade Form', 'offer': offer}
            return render(request, 'blog/sell_form.html', context)

    else: #GET request
        if offer is None or offer.owned_game is None or offer.sell_price is None: # If a Trade with this id is not found, redirect to custom 404 page
            messages.add_message(request, 30, 'This offer was not found. It may have been deleted.')
            return render(request, 'users/display_messages.html', {'title': 'Game Exchange: Offer Not Found'})

        sell_form = SellUpdateForm() # ModelForm
        sell_form.fields['sell_price'].initial = offer.sell_price
        sell_form.fields['owned_game'].initial = offer.owned_game.id
        sell_form.fields['condition'].initial = offer.condition
        context = {'form': sell_form, 'is_update': True, 'title': 'Update Offer Form', 'offer': offer}
        return render(request, 'blog/sell_form.html', context)


# ~~~DELETE TRADE~~~
@login_required
def delete_trade(request):
    if 'trade_id' not in request.POST:
        messages.add_message(request, DANGER, 'There was a problem deleting this trade. Please try again.')
        return redirect('/your-trades')
    trade_id = request.POST['trade_id']
    trade = Trade.objects.filter(id=trade_id)
    trade.delete()
    messages.add_message(request, SUCCESS, 'Offer deleted')
    return redirect('/your-trades')


# Go to home
def home(request):
    return render(request, 'blog/home.html', {'title': 'Home'})


# Confirmed Trades page
class ConfirmedTradesListView(LoginRequiredMixin, ListView):
    model = Trade
    template_name = 'blog/confirmed-trades.html'
    context_object_name = 'transactions'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Confirmed Trades: In Progress'
        return context

    def get_queryset(self):
        current_user = self.request.user
        transactions = Transaction.objects.filter( # Transactions for this user which are not cancelled or completed
            (Q(trade_one__user_who_posted=current_user) | Q(trade_two__user_who_posted=current_user))
             & (~Q(status=COMPLETED_BY_BOTH_USERS) & ~Q(user_who_completed=current_user)) &
                ~Q(status__startswith='Cancelled') & ~Q(status__startswith='Flagged as incomplete')).order_by('-created_date') #hardcode WITH CASE (bad)
        return transactions

    def get(self, *args, **kwargs):  # Overwrite the view returned to ensure email confirmation is not overdue
        email_check = check_email_confirmation(self.request)
        if email_check != None: # If the user's email confirmation is overdue, redirect to login
            return email_check
        return super(ConfirmedTradesListView, self).get(*args, **kwargs)


# Cancelled Trades page
class CancelledTradesListView(LoginRequiredMixin, ListView):
    model = Trade
    template_name = 'blog/cancelled-trades.html'
    context_object_name = 'transactions'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Confirmed Trades: Cancelled'
        return context

    def get_queryset(self):
        current_user = self.request.user
        transactions = Transaction.objects.filter(
            (Q(trade_one__user_who_posted=current_user) | Q(trade_two__user_who_posted=current_user))
            & Q(status__startswith='Cancelled')).order_by('-created_date')  # hardcode WITH CASE (bad)
        return transactions

    def get(self, *args, **kwargs): # Overwrite the view returned to ensure email confirmation is not overdue
        email_check = check_email_confirmation(self.request)
        if email_check != None: # If the user's email confirmation is overdue, redirect to login
            return email_check
        return super(CancelledTradesListView, self).get(*args, **kwargs)


# Cancelled Trades page
class CompletedTradesListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'blog/completed-trades.html'
    context_object_name = 'transactions'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Confirmed Trades: Completed'
        return context

    def get_queryset(self):
        current_user = self.request.user
        transactions = Transaction.objects.filter(
            (Q(trade_one__user_who_posted=current_user) | Q(trade_two__user_who_posted=current_user))
            & (Q(status='Completed by both users') | Q(user_who_completed=current_user) | Q(status__startswith='Flagged as incomplete'))).order_by('-created_date')  # hardcode WITH CASE (bad)
        return transactions

    def get(self, *args, **kwargs):  # Overwrite the view returned to ensure email confirmation is not overdue
        email_check = check_email_confirmation(self.request)
        if email_check != None: # If the user's email confirmation is overdue, redirect to login
            return email_check
        return super(CompletedTradesListView, self).get(*args, **kwargs)


@login_required
def insert_transaction(request):
    if 'trade_1_id' not in request.POST or 'trade_2_id' not in request.POST:
        messages.add_message(request, DANGER, 'There was a problem confirming this trade. Please try again.')
        return redirect('/matches')

    trade_one_id = request.POST['trade_1_id'] # current user's trade
    trade_two_id = request.POST['trade_2_id'] # matched user's trade
    Trade.objects.filter(Q(id=trade_one_id) | Q(id=trade_two_id)).update(is_trade_proposed=True) # bulk update of 2 trade records

    # Edge Case: Current user and a matched user loaded Matches page at same time. Other user confirmed. Now current user is trying to confirm...
    dupe_transaction = Transaction.objects.filter(Q(trade_two_id=trade_one_id) & Q(trade_one_id=trade_two_id) &
              Q(trade_two__user_who_posted=request.user) & Q(status__startswith='Waiting for 2nd')).first()
    if dupe_transaction is not None:
        messages.add_message(request, SUCCESS, str(dupe_transaction.trade_one.user_who_posted.username[:25]) + ' confirmed this match within the last few minutes. Please confirm below.')
        return redirect('confirmed-trade', pk=dupe_transaction.pk)

    transaction = insert_transaction_and_send_email(request, trade_one_id, trade_two_id)
    return redirect('confirmed-trade', pk=transaction.pk)

def insert_transaction_and_send_email(request, trade_one_id, trade_two_id):
    transaction_price = None
    if 'transaction_price' in request.POST:
        transaction_price = request.POST['transaction_price']  # Average of the buy_price and sell_price if this is a buy/sell transaction

    transaction = Transaction(trade_one_id=trade_one_id, trade_two_id=trade_two_id, price=transaction_price)
    transaction.save()

    matched_user = Trade.objects.filter(id=trade_two_id).first().user_who_posted
    if matched_user.confirmed_trade_email_opt_in is True:  # Send email to user matched with
        email_context_data = {}
        email_context_data['username'] = matched_user.username # some items in dict may be null, depending on Trade type
        email_context_data['transaction_url'] = request.build_absolute_uri('/confirmed-trade/' + str(transaction.id))
        email_context_data['owned_game'] = transaction.trade_two.owned_game
        email_context_data['desired_game'] = transaction.trade_two.desired_game
        email_context_data['opt_out_url'] = request.build_absolute_uri(
            '/confirmed-trade-opt-out/' + str(matched_user.id) + '/' + str(matched_user.conf_trade_opt_out_key))
        email_context_data['email_address'] = matched_user.email

        # Get platforms if matched trade has desired/owned game
        if transaction.trade_two.desired_game is not None: # Matched user is buying or trading
            email_context_data['desired_game_platform'] = transaction.trade_two.desired_game.platform
        if transaction.trade_two.owned_game is not None: # Matched user is selling or trading
            email_context_data['owned_game_platform'] = transaction.trade_two.owned_game.platform

        # Get transaction price if this is a buy/sell trade:
        if transaction.price is not None:
            email_context_data['transaction_price'] = transaction.price

        # Get email subject and email template based off Trade type
        if transaction.trade_one.desired_game is not None and transaction.trade_one.owned_game is not None: # Matched user is trading with current user
            email_context_data['email_subject'] = "A user confirmed this trade with you: Get " + str(transaction.trade_two.desired_game) + \
                ' for your copy of ' + str(transaction.trade_two.owned_game)
            email_context_data['email_path'] = "/ConfirmedTrade.txt"

        elif transaction.trade_one.buy_price is not None and transaction.trade_two.sell_price is not None: # Matched user is selling to current user
            email_context_data['email_subject'] = "A user confirmed to buy " + str(transaction.trade_two.owned_game) + \
                  ' from you for $' + str(transaction.price)
            email_context_data['email_path'] = "/SellTrade.txt"

        elif transaction.trade_one.sell_price is not None and transaction.trade_two.buy_price is not None: # Matched user is buying from current user
            email_context_data['email_subject'] = "A user confirmed to sell " + str(transaction.trade_two.desired_game) + \
                  ' to you for $' + str(transaction.price)
            email_context_data['email_path'] = "/BuyTrade.txt"

        messages.add_message(request, SUCCESS,matched_user.username[:25] + ' has been notified of your interest in this offer.')
        send_email(email_context_data)
    return transaction

def send_email(email_context_data):
    owned_game_platform = None
    desired_game_platform = None
    transaction_price = None

    if 'owned_game_platform' in email_context_data:
        owned_game_platform = email_context_data['owned_game_platform']
    if 'desired_game_platform' in email_context_data:
        desired_game_platform = email_context_data['desired_game_platform']
    if 'transaction_price' in email_context_data:
        transaction_price = email_context_data['transaction_price']

    c = Context({ 'transaction_url': email_context_data['transaction_url'],
          'owned_game': email_context_data['owned_game'],
          'desired_game': email_context_data['desired_game'],
          'username': email_context_data['username'],
          'owned_game_platform': owned_game_platform,
          'desired_game_platform': desired_game_platform,
          'transaction_price': transaction_price,
          'opt_out_url': email_context_data['opt_out_url']
     })
    f = open(settings.MEDIA_ROOT + email_context_data['email_path'], 'r')
    t = Template(f.read())
    f.close()

    message = t.render(c)
    send_mail(email_context_data['email_subject'], message, 'Game Exchange <no-reply@GameExchange.com>',
          [email_context_data['email_address']], fail_silently=False)


class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = 'blog/transaction_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Committed Trade Record'
        return context

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404: # redirect to 404 page specifically for transaction (eg. if user deleted account)
            messages.add_message(request, 30, 'This committed offer was not found. It may have been deleted.')
            return render(request, 'users/display_messages.html', {'title': 'Game Exchange: Committed Offer Not Found'})
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


# ~~~Set Transaction to Cancelled~~~
@login_required
def set_transaction_to_cancelled_by_user(request):
    if request.POST.get('transaction_id') is None:
        messages.add_message(request, DANGER, 'There was a problem cancelling this trade, please try again. Reach out to support if the error reoccurs.')
        return redirect('/confirmed-trades')
    transaction_id = str(request.POST.get('transaction_id'))
    transaction = Transaction.objects.get(id=transaction_id)
    if len(str(request.user)) > 25:
        transaction.status = CANCELLED_BY_USER + ' ' + str(request.user)[:25] + '...'
    else:
        transaction.status = CANCELLED_BY_USER + ' ' + str(request.user)
    transaction.user_cancelled_date = timezone.now()
    transaction.save()

    # bulk update of 2 trade records so they show up on Matches page again and have a null transaction_price(used in logic for templates/email :9)
    Trade.objects.filter(Q(id=transaction.trade_one_id) | Q(id=transaction.trade_two_id)).update(is_trade_proposed=False)
    Trade.objects.filter(Q(id=transaction.trade_one_id) | Q(id=transaction.trade_two_id)).update(transaction_price=None )
    messages.add_message(request, SUCCESS, 'Trade cancelled')
    return redirect('confirmed-trade', pk=transaction.pk)


# ~~~Set Transaction to Completed~~~
@login_required
def set_transaction_to_completed(request):
    if request.POST.get('transaction_id') is None:
        messages.add_message(request, DANGER, 'There was a problem completing this trade, please try again. Reach out to support if the error reoccurs.')
        return redirect('/confirmed-trades')
    transaction = Transaction.objects.get(id=request.POST.get('transaction_id'))

    if transaction.user_who_completed is None: # This is the first user who marked transaction as Completed
        transaction.user_who_completed = request.user

        # If current user(who is completing the transaction) is the user who confirmed the trade 1st, use the other user as user_who_hasnt_completed
        user_who_hasnt_completed = str(transaction.trade_two.user_who_posted if (request.user == transaction.trade_one.user_who_posted) else transaction.trade_one.user_who_posted)
        if len(user_who_hasnt_completed) > 25:
            user_who_hasnt_completed = user_who_hasnt_completed[:25] + '...' # overwrite with truncated username if longer than 25

        if len(str(request.user)) > 25:
            transaction.status = COMPLETED_BY_ONE_USER_PREFIX + ' ' + str(request.user)[:25] + '... Waiting for confirmation from ' + user_who_hasnt_completed
        else:
            transaction.status = COMPLETED_BY_ONE_USER_PREFIX + ' ' + str(request.user) + '. Waiting for confirmation from ' + user_who_hasnt_completed
    else: # This is the second user who marked transaction as Completed
        transaction.confirmed_to_completed_duration = (datetime.now(transaction.created_date.tzinfo) - transaction.created_date)
        transaction.status = COMPLETED_BY_BOTH_USERS
        # bulk update of 2 trade records so do not show up on the Your Trades page, or counted towards the limit of trade insertion
        Trade.objects.filter(Q(id=transaction.trade_one_id) | Q(id=transaction.trade_two_id)).update(is_completed=True)

    transaction.save()
    messages.add_message(request, SUCCESS, 'Trade completed. Thanks for using Game Exchange!')
    return redirect('confirmed-trade', pk=transaction.pk)


# ~~~One user set to complete, but the other says it was not complete~~~
@login_required
def flag_transaction_as_incomplete(request):
    if request.POST.get('transaction_id') is None:
        messages.add_message(request, DANGER, 'There was a problem flagging this trade, please try again. Reach out to support if the error reoccurs.')
        return redirect('/confirmed-trades')

    transaction = Transaction.objects.get(id=request.POST.get('transaction_id'))

    if len(str(request.user)) > 25:
        transaction.status = FLAGGED_AS_INCOMPLETE + str(request.user)[:25] + '... Contact support if you need help resolving this trade.'
    else:
        transaction.status = FLAGGED_AS_INCOMPLETE + str(request.user) + '. Contact support if you need help resolving this trade.'

    transaction.save()
    # bulk update of 2 trade records so do not show up on the Your Trades page, or counted towards the limit of trade insertion
    Trade.objects.filter(Q(id=transaction.trade_one_id) | Q(id=transaction.trade_two_id)).update(is_completed=True)
    messages.add_message(request, SUCCESS, 'Trade flagged as incomplete. Please submit a new offer if you still own your game and want to trade or sell it.')
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
    context_object_name = 'trades'
    paginate_by = 5
    template_name = 'blog/matches.html' # <app>/<model>_<viewtype>.html
    matches_found_within_radius = False
    more_trades_allowed = True # Specifies if the user can confirm another trade
    num_trades_remaining = 0 # Specifies if the user can confirm another trade
    transaction_price = None # The price that will be displayed on the transaction: Floor of (sell_price+buy_price)/2

    def get_queryset(self):
        trades = get_matches(self.request.user, 0)
        if len(trades) > 0: # If matches were found within the current user's travel_radius, show matches
            self.matches_found_within_radius = True # Tell template matches were found within current user's travel_radius
            return trades
        else: # If no trades were found within the current user's travel_radius, increase the radius by a buffer
            return get_matches(self.request.user, NO_MATCHES_KM_BUFFER)

    def get_context_data(self, **kwargs): # Set var to let template know if match was found within user's travel_radius
        context = super().get_context_data(**kwargs)
        context['matches_found_within_radius'] = self.matches_found_within_radius
        context['more_trades_allowed'] = self.more_trades_allowed
        context['num_trades_remaining'] = self.num_trades_remaining
        context['title'] = 'Matches'
        return context

    def get(self, *args, **kwargs): # Overwrite the view returned
        email_check = check_email_confirmation(self.request)
        if email_check != None: # If the user's email confirmation is overdue, redirect to login
            return email_check

        # 'Waiting for' can be 'Waiting for 2nd confirmation...' or 'Completed by User1. Waiting for confirmation from User2'
        transactions = Transaction.objects.filter((Q(status='Open') | Q(status__contains='Waiting for')) & # hardcode
              (Q(trade_one__user_who_posted=self.request.user) | Q(trade_two__user_who_posted=self.request.user)) & ~Q(user_who_completed=self.request.user))
        if len(transactions) >= PREMIUM_TRADES_ALLOWED:
            self.more_trades_allowed = False
        self.num_trades_remaining = PREMIUM_TRADES_ALLOWED - len(transactions) - 1 # How many trade confirmations after this one
        return super(TradeListView, self).get(*args, **kwargs)


# Matches query
def get_matches(current_user, travel_radius_buffer):
    trades = Trade.objects.raw('SELECT DISTINCT t1.id AS id, '  # todo: order by membership type
                               't2.id AS t2_id, '
                               't2.name AS t2_name, '
                               't1.owned_game as t1_owned_game, '
                               't1.desired_game as t1_desired_game, '
                               't1.buy_price as t1_buy_price, '
                               't1.sell_price as t1_sell_price, '
                               't2.buy_price as t2_buy_price, '
                               't2.sell_price as t2_sell_price, '
                               't2.user_who_posted_id as t2_user_who_posted_id, '
                               't2.created_date as t2_created_date, '
                               't2.condition as t2_condition, '
                               'u1.username as t2_username, '
                               'u1.lat as t2_lat, '
                               'u1.long as t2_long, '
                               'u1.travel_radius as t2_travel_radius '
                               'FROM blog_Trade t1, blog_Trade t2, users_myuser u1 '
                               'WHERE ( ' # Match on games if trade, or sell/buy price if sell or buy
                                   '(t1.owned_game = t2.desired_game '
                                   'AND t1.desired_game = t2.owned_game) '
                                   'OR (t1.buy_price >= t2.sell_price '
                                   'AND t1.desired_game = t2.owned_game) '
                                   'OR (t1.sell_price <= t2.buy_price '
                                   'AND t1.owned_game = t2.desired_game) '
                               ') '
                               
                               'AND t1.user_who_posted_id = %s '
                               'AND t1.is_trade_proposed = false '
                               'AND t2.is_trade_proposed = false '
                               # 'AND t1.is_completed = false ' # shouldn't need this because is_trade_proposed will be false
                               # 'AND t2.is_completed = false '
                               'AND u1.id = t2.user_who_posted_id '
                               'AND NOT(u1.email_confirmed = false AND %s > u1.email_confirmation_due_date) ' 

                               # Location match... 6373.0 = radius of earth in km. 
                               """ 
                               AND (6373.0 * (2 * atan2(sqrt((POWER(sin((%s - RADIANS(u1.lat)) / 2), 2) + cos(%s)
                               * cos(RADIANS(u1.lat)) * POWER(sin((%s - RADIANS(u1.long)) / 2), 2))),sqrt(1 - (POWER(sin((%s - RADIANS(u1.lat)) / 2), 2) + cos(%s)
                               * cos(RADIANS(u1.lat)) * POWER(sin((%s - RADIANS(u1.long)) / 2), 2)))))) < ( %s + u1.travel_radius + %s )
                                """,
                               [current_user.id, datetime.now(), radians(current_user.lat),
                                radians(current_user.lat), radians(current_user.long), radians(current_user.lat), radians(current_user.lat), radians(current_user.long),
                                current_user.travel_radius, travel_radius_buffer])

    for trade in trades:
        if trade.t1_buy_price is not None and trade.t2_sell_price is not None: # trade1 is buying, trade2 is selling
            trade.transaction_price = round((trade.t1_buy_price+trade.t2_sell_price)/2)
        elif trade.t1_sell_price is not None and trade.t2_buy_price is not None: # trade2 is buying, trade1 is selling
            trade.transaction_price = round((trade.t1_sell_price+trade.t2_buy_price)/2)

    return trades

# Your Trades page
class YourTradesListView(LoginRequiredMixin, ListView):
    model = Trade
    template_name = 'blog/your-trades.html'
    context_object_name = 'trades'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Your Trades'
        return context

    def get_queryset(self):
        current_user = self.request.user
        trades = Trade.objects.filter(Q(user_who_posted=current_user) & Q(is_completed=False)).order_by('-created_date')
        return trades

    def get(self, *args, **kwargs): # Overwrite the view returned
        email_check = check_email_confirmation(self.request)
        if email_check != None:
            return email_check
        return super(YourTradesListView, self).get(*args, **kwargs)


# Go to About page
def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})


# Go to FAQ page
def faq(request):
    return render(request, 'blog/faq.html', {'title': 'FAQ'})


def check_email_confirmation(request):
    if not request.user.email_confirmed and timezone.now() > request.user.email_confirmation_due_date:
        return redirect('login')
    else:
        return None


print('~~~bottom of blog/views.py~~~')
