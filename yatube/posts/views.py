from django.shortcuts import render, get_object_or_404, redirect
from .models import Follow, Post, Group, User, Comment
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from .utils import paginate_page
from django.views.decorators.cache import cache_page
from django.urls import reverse


@cache_page(1 * 20)
def index(request):
    """Главная страница со всеми постами."""
    post_list = Post.objects.select_related('author', 'group').all()
    page_obj = paginate_page(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_post(request, slug):
    """Страница со всеми постами определённой группы."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.group_posts.select_related('author', 'group').all()
    page_obj = paginate_page(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }

    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Страница пользователя с его постами."""
    author = get_object_or_404(User, username=username)
    posts = author.author_posts.select_related('author', 'group').all()
    page_obj = paginate_page(request, posts)
    if request.user.is_authenticated:
        following = (Follow.objects.
                     filter(user=request.user, author=author).exists())
    else:
        following = False
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Конкретная страница определённого поста."""
    page_obj = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=page_obj)
    form = CommentForm(request.POST or None)
    context = {
        'page_obj': page_obj,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Страница создания поста."""
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', request.user)
        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Страница редактирования поста."""
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post,
        )
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post.id)
        return render(
            request, 'posts/create_post.html',
            {'form': form, 'is_edit': True}
        )
    form = PostForm(initial={'text': post.text, 'group': post.group})
    return render(
        request, 'posts/create_post.html',
        {'form': form, 'is_edit': True}
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginate_page(request, posts)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if (request.user != author
            and not Follow.objects.
            filter(user=request.user, author=author).exists()):
        Follow.objects.create(user=request.user, author=author)
    return redirect(reverse('posts:profile', kwargs={'username': username}))


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = (Follow.objects.
              filter(user=request.user, author=author))
    if (follow.exists()):
        follow.delete()
    return redirect(reverse('posts:profile', kwargs={'username': username}))
