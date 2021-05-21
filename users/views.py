from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import UserRegisterForm, UserUpdateForm, ResendEmailConfirmationForm
from django.utils import timezone

import hashlib
import random
from django.contrib.auth import get_user_model
User = get_user_model()
import datetime
from blog.views import check_email_confirmation
from blog.models import Trade, Game, Transaction
from django.db.models import Q


# MESSAGE CONSTANTS
DANGER = 30
SUCCESS = 25


print('~~~top of users/views.py~~~')

@login_required
def account(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)

        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'Your account has been updated')
            return redirect('account')

        else: #todo: see SO comment. Can we just remove this to fix?
            stored_user = User.objects.filter(id=request.user.id).first()
            u_form = UserUpdateForm(request.POST, instance=request.user)
            u_form.username = stored_user.username # Get the values on this user that are stored in the DB
            u_form.email = stored_user.email

            u_form.fields['username'].initial = stored_user.username
            return render(request, 'users/account.html', {'u_form': u_form, 'title': 'Account'} )

    else:
        u_form = UserUpdateForm(instance=request.user)

    return render(request, 'users/account.html', {'u_form': u_form, 'title': 'Account' })


# ~~~DELETE USER(ACCOUNT)~~~
@login_required
def delete_account(request):
    if 'user_id' not in request.POST:
        messages.add_message(request, DANGER, 'There was a problem deleting this Account. Please try again. If the issue reoccurs, contact Support.')
        return redirect('/account')
    user_id = request.POST['user_id']
    user = User.objects.filter(id=user_id)
    if user is None:
        messages.add_message(request, DANGER, 'There was a problem deleting this Account. Please try again. If the issue reoccurs, contact Support.')
        return redirect('/account')

    transactions = Transaction.objects.filter(Q(trade_one__user_who_posted=user_id) | Q(trade_two__user_who_posted=user_id))
    trade_ids = set()
    for transaction in transactions:
        trade_ids.add(transaction.trade_one_id)
        trade_ids.add(transaction.trade_two_id)
    trades = Trade.objects.filter(pk__in=trade_ids)
    trades.update(is_trade_proposed=False)

    user.delete()
    messages.add_message(request, SUCCESS, 'Your account has been deleted.')
    return redirect('/login')


def account_locked(request): # account-locked url, show account locked page
    return render(request, 'users/account_locked.html', {'title': 'Account Locked'})


# Function called when user clicks 'Sign Up' button on register.html
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            reg_data = {}
            reg_data['username'] = form.cleaned_data['username']
            reg_data['email'] = form.cleaned_data['email']
            reg_data['password1'] = form.cleaned_data['password1']

            # generate a random key for email confirmation
            salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
            usernamesalt = reg_data['username']
            reg_data['activation_key'] = hashlib.sha1(salt.encode('utf-8') + usernamesalt.encode('utf-8')).hexdigest()
            reg_data['activation_url'] = request.build_absolute_uri('/activate/') # Note: we only force https in Production

            # generate a random key for easy email opt-out
            salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5] # todo: confrim make a new salt different from above
            reg_data['conf_trade_opt_out_key'] = hashlib.sha1(salt.encode('utf-8') + usernamesalt.encode('utf-8')).hexdigest()
            reg_data['conf_trade_opt_out_url'] = request.build_absolute_uri('/confirmed-trade-opt-out/')

            form_instance = form.save(commit=False) # this gives us access to set the value of a form field without saving it
            form_instance.activation_key = reg_data['activation_key']
            form_instance.conf_trade_opt_out_key = reg_data['conf_trade_opt_out_key']

            reg_data['email_path'] = "/ActivationEmail.txt"
            reg_data['email_subject'] = "Game Exchange: Confirm your email address"

            form.sendEmail(reg_data)
            form_instance.save()
            messages.success(request, f'Your account has been created! You are now able to log in')

            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form, 'title': 'Sign Up'})


#View called from activation email. Activate user if link didn't expire (1 week). Offer to resend link if the first expired
def activation(request, key): # key is the pk accepted in the url from clicking the link in the email. User may/may not be logged in... Actually maybe i will require login
    user = User.objects.filter(activation_key=key).first()

    if user is None: # No user found with that activation_key. Assume they clicked an old link and bring them to ResendEmailConfirmationForm
        if not request.user.is_authenticated:
            messages.add_message(request, 30, 'Your email confirmation link has expired. Login then enter your email to send a new one.')
        return redirect('new-activation-link')

    if user.email_confirmed:
        messages.success(request, f'Your email has been confirmed.')
        return redirect('blog-home')


    else: # Email not confirmed. User clicked link in email
        if timezone.now() > user.key_expires: # activation_key Expired
            return new_activation_link(request) # take user to form which sends a new email activation

        else: # Activation successful
            user.email_confirmed = True
            user.save()
            messages.success(request, f'Your email has been confirmed.')
            if request.user.is_authenticated:
                return redirect('blog-home')  # bring to home page if logged in
            else:
                return redirect('login')


@login_required
def new_activation_link(request): # email_confirmation_reset.html page. Activation link expired. Login is required.
    user = request.user

    if user is not None:
        if request.method == 'POST': # User entered email and clicked "Resend Email" button
            form = ResendEmailConfirmationForm(request.POST, instance=user)

            if form.is_valid():
                reg_data = {}
                reg_data['username']=user.username
                reg_data['email']=user.email # use what's on user instead of what's submitted in form
                reg_data['email_path']="/ResendActivationEmail.txt"
                reg_data['email_subject']="Game Exchange: Confirm your email address"
                reg_data['activation_url'] = request.build_absolute_uri('/activate/')

                salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
                usernamesalt = reg_data['username']
                reg_data['activation_key'] = hashlib.sha1(salt.encode('utf-8') + usernamesalt.encode('utf-8')).hexdigest()

                user.activation_key = reg_data['activation_key']
                user.key_expires = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=7), "%Y-%m-%d %H:%M:%S")
                user.save() # Update user with new activation key and key_expires

                if user.email.lower() == form.cleaned_data['email'].lower(): # todo: move this if beneath formvalid, only updatae user if email matches
                    form.resendEmail(reg_data)

                messages.success(request, f'If that email matches our records, we will resend your activation email. You may have to check your junk/spam folder.')
                return render(request, 'users/email_confirmation_reset.html', {'form': form, 'title': 'Resend Email Confirmation'})

            elif 'user with this Email address already exists'.lower() in str(form.errors.as_data()).lower(): # user entered another user's email for resend
                messages.success(request,
                    f'If that email matches our records, we will resend your activation email. You may have to check your junk/spam folder.')
                return redirect('blog-home')
            else:
                print('~~~~~~~PROD ERROR in new_activation_link(): Invalid ResendEmailConfirmationForm. Details below:~~~~~~~')
                print(form.errors.as_data())
                messages.add_message(request, 30,
                     'There was a problem resending your email confirmation. Please login and try again. Contact support if the issue reoccurs.')
                return redirect('blog-home')

        else: # GET method: user.overdue_for_email_confirmation is true, they clicked link in login.html. Bring to email_confirmation_reset page
            messages.add_message(request, 30,
                 'Your email confirmation link has expired. Enter your email below to send a new one.')
            return render(request, 'users/email_confirmation_reset.html', {'form': ResendEmailConfirmationForm, 'title': 'Resend Email Confirmation'})
            # return redirect('new-activation-link')

    else: # If user with that activation key was not found
        messages.add_message(request, 30,
             'There was a problem resending your email confirmation. Please login and try again. Contact support if the issue reoccurs.')
        return redirect('blog-home')


def confirmed_trade_opt_out(request, pk, opt_out_key):
    user = User.objects.filter(id=pk).first()
    if user.conf_trade_opt_out_key == opt_out_key:
        user.confirmed_trade_email_opt_in = False
        user.save()
        messages.add_message(request, 25, 'You have successfully unsubscribed from Trade Confirmation emails. Email preferences can be updated from the Account page.')
    else:
        messages.add_message(request, 30, 'Sorry, there was a problem with updating your email preferences. Please login and update them on your Account page.')
    opt_out_data = {}
    return render(request, 'users/display_messages.html', {'title': 'Game Exchange: Message'})


print('~~~bottom of users/views.py~~~')

