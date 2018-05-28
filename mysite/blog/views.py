from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from .models import Post, Comment

# Using a class-based view .
# 1 - importing generic ListView class

class post_list(ListView):  # using ListView
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

#
# def post_list(request):
#     object_list = Post.published.all()
#     paginator = Paginator(object_list, 3)
#     page = request.GET.get('page')
#     try:
#         posts = paginator.page(page)
#     except PageNotAnInteger:
#         #if page is not an integer
#         posts = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range (e.g. 9999), deliver last page of results.
#         posts = paginator.page(paginator.num_pages)
#     return render(request,'blog/post/list.html',{'posts':posts})



def post_detail (request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign current post to the comment
            new_comment.post = post
            # save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'blog/post/detail.html', context)


def post_share(request, post_id):
    post = get_object_or_404(Post, id = post_id, status='published')
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'],post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, settings.EMAIL_HOST_USER , [cd['to']])
            sent = True

    else:
        form = EmailPostForm()

    context = {
        'post': post,
        'form': form,
        'sent': sent,
    }

    return render(request, 'blog/post/share.html', context)

