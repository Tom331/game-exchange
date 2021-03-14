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
from .models import Post

# Dummy Data(Dictionary)
posts = [
    {
        'author': 'CoreyMS',
        'title': 'Blog Post 1',
        'content': '1st post content',
        'date_posted': 'August 27, 2018'
    },
{
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': '2nd  post content',
        'date_posted': 'March 13, 2021(today)'
    }
]

def home(request):
    # This is a "Dictionary"
    context = {
        #'posts': Post.objects.all() #takes actual data from DB
        'posts': posts #takes dummy data
    }
    return render(request, 'blog/homeTest.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/homeTest.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5


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


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


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
