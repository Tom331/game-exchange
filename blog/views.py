# Best way to load in a template is to use django.shortcuts import render
# This allows us to return a rendered template. render() takes the request object as 1st param
# The 2nd param is the template name we want to render, eg) "blog/home.html"
# The 3rd optional param is context, a way to pass info into our template
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post #import the Post object ('.' because in same directory)
from .models import Trade, Game
from django.db import connection
from dal import autocomplete
from django import forms


def trade_new(request):
    form = TradeCreateForm()
    return render(request, 'blog/trade_form.html', {'form': form, 'title': 'Propose New Trade'})


class TradeCreateForm(forms.Form):
    the_game_you_own = forms.ModelChoiceField(
        queryset=Game.objects.all(),
        to_field_name='name_and_platform',
        widget=autocomplete.ModelSelect2(
            url='game-autocomplete',
            attrs={
                'data-minimum-input-length': 2,
            },
        )
    )

    the_game_you_want_in_exchange = forms.ModelChoiceField(
        queryset=Game.objects.all(),
        to_field_name='name_and_platform',
        widget=autocomplete.ModelSelect2(
            url='game-autocomplete',
            attrs={
                'data-minimum-input-length': 2,
            },
        )
    )


class TradeCreateView(LoginRequiredMixin, CreateView):
    model = Trade
    fields = ["owned_game"]


class GameAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Game.objects.none()

        self.q = (self.q + '%').lower()
        qs = Game.objects.raw('SELECT Id AS id, name_and_platform AS name FROM blog_game WHERE LOWER( name_and_platform ) LIKE %s', [self.q])
        return qs



def home(request):
    return render(request, 'blog/home.html')


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5


class TradeListView(ListView):
    model = Trade
    template_name = 'blog/matches.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'trades'
    paginate_by = 5

    def get_queryset(self):
        current_user_id = self.request.user.id
        # Get trades of other users who match your submitted trades
        # t1 is the current_user's trade, t2 is the matched trade
        trades = Trade.objects.raw('SELECT DISTINCT t1.id AS id, ' 
                                   't2.id AS user2_trade_id, '
                                   't2.name AS t2_name, ' 
                                   't1.owned_game as t1_owned_game, '
                                   't1.desired_game as t1_desired_game, '
                                   't2.user_who_posted_id as t2_user_who_posted_id, '
                                   'u1.username as t2username '
                                   'FROM blog_Trade t1, blog_Trade t2, auth_user u1 '
                                   'WHERE t1.owned_game = t2.desired_game '
                                   'AND t1.desired_game = t2.owned_game '
                                   'AND t1.user_who_posted_id = %s '
                                   'AND t1.is_trade_proposed = false '
                                   'AND t2.is_trade_proposed = false '
                                   'AND u1.id = t2.user_who_posted_id',
                                   [current_user_id])

        return trades


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
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


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})
