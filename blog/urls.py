from django.urls import path, include
from django.conf.urls import url
print('~~~top of blog/urls.py~~~')


from .views import (
    TradeListView,
    YourTradesListView,
    ConfirmedTradesListView,
    CancelledTradesListView,
    CompletedTradesListView,
    GameAutoComplete
)
from . import views

urlpatterns = [
    # the 'name' param can be referenced in html. eg) href="{% url 'blog-home' %}". This allows us to avoid hard-coding
    # params: path(route, view, kwargs=None, name=None)¶
    # route is a str that contains a url pattern
    # view is a view function or the result of a as_view() class. It can also be an django.urls.include()
    # The kwargs argument allows you to pass additional arguments to the view function or method.

    # STATIC
    path('', views.home, name='blog-home'), # home.html
    path('about/', views.about, name='blog-about'), # about.html
    path('faq/', views.faq, name='blog-faq'), # faq.html
    path('matches/', TradeListView.as_view(), name='blog-matches'), # matches.html with list view of Trades that match

    # TRADES
    path('your-trades/', YourTradesListView.as_view(), name='blog-trades'), # your-trades.html with list view of your Trades
    path('trade/confirm/', views.insert_transaction, name='trade-confirm'), # url to accept POST call from Matches page to create a Transaction
    path('trade/delete/', views.delete_trade, name='trade-delete'), #  url to accept POST call from Your Trades page to delete a trade
    path('trade/new/', views.trade_new, name='trade-create'), # creates form and renders it to trade_form.html
    path('buy/new/', views.buy_new, name='trade-buy'), # creates form and renders it to buy_form.html
    path('sell/new/', views.sell_new, name='trade-sell'), # creates form and renders it to sell_form.html
    path('trade/insert/', views.insert_new_trade, name='trade-insert'), # accepts POST call to create a new Trade record
    path('buy/insert/', views.insert_new_buy_trade, name='buy-insert'), # accepts POST call to create a new Buy record
    path('sell/insert/', views.insert_new_sell_trade, name='sell-insert'), # accepts POST call to create a new Sell record
    path('trade/insert-update-email/', views.set_confirm_trade_email_preference, name='trade-insert-update-email'), # accepts POST call to set confirm trade email pref.

    # updating Trade records:
    path('update-buy/<int:pk>/', views.update_buy, name='update-buy'), # Loads update trade page/form and validates on POST call
    path('update-sell/<int:pk>/', views.update_sell, name='update-sell'), # Loads update trade page/form and validates on POST call

    # TRANSACTIONS
    path('confirmed-trades/', ConfirmedTradesListView.as_view(), name='blog-confirmed-trades'), # confirmed-trades.html with list view of Transactions
    path('cancelled-trades/', CancelledTradesListView.as_view(), name='blog-cancelled-trades'), # cancelled-trades.html with list view of cancelled Transactions
    path('completed-trades/', CompletedTradesListView.as_view(), name='blog-completed-trades'), # completed-trades.html with list view of completed Transactions
    path('confirmed-trade/<int:pk>/', views.TransactionDetailView.as_view(), name='confirmed-trade'), # Loads transaction page/form
    path('transaction/cancel/', views.set_transaction_to_cancelled_by_user, name='confirmed-trade-cancel'), # Accepts POST call to cancel transaction
    path('transaction/complete/', views.set_transaction_to_completed, name='confirmed-trade-complete'), # Accepts POST call to cancel transaction
    path('transaction/flag-incomplete/', views.flag_transaction_as_incomplete, name='confirmed-trade-flag-incomplete'), # Accepts POST call to cancel transaction
    path('transaction/open/', views.set_transaction_to_open, name='confirmed-trade-open'), # Accepts POST call to confirm transaction

    url( # url that somehow gets the json object of Game records to allow auto-complete
        r'^game-autocomplete/$',
        GameAutoComplete.as_view(),
        name='game-autocomplete'
    ),

    # old
    # path('', PostListView.as_view(), name='blog-home'), # old home page
    # path('trade/<int:pk>/', PostDetailView.as_view(), name='blog-matches'), # I think this
    # path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'), # url to update a specific post
    # path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'), # url to delete a specific post
    # path('user/<str:username>', UserPostListView.as_view(), name='user-posts'), # <str:username> captures a string value from the username param in the URL
    # (r'^messages/', include('django_messages.urls')),
]

print('~~~bottom of blog/urls.py~~~')
