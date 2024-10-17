from django.db.models import Count
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from .models import Post, Status  # Import Status
from django.core.mail import send_mail
from django.contrib.postgres.search import SearchVector
from django.contrib.postgres.search import ( SearchVector, SearchQuery, SearchRank)
from django.contrib.postgres.search import TrigramSimilarity
from .forms import EmailPostForm, CommentForm , SearchForm # Ensure you import your form
from taggit.models import Tag

def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            
            # Combining SearchVector and TrigramSimilarity
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            
            # Annotating with similarity and rank
            results = (
                Post.published.annotate(
                    similarity=TrigramSimilarity('title', query),
                    rank=SearchRank(search_vector, search_query)  # Add rank for ordering
                )
                .filter(similarity__gt=0.1)  # Filter by trigram similarity
                .order_by('-rank')  # Order by rank (which we just annotated)
            )

    return render(request, 'blogsite/post/search.html', {
        'form': form,
        'query': query,
        'results': results
    })

@require_POST
def post_comment(request, post_id):
    post=get_object_or_404(Post, id=post_id, status=Status.PUBLISHED)
    comment=None #A comment was posted
    form=CommentForm(data=request.POST)
    if form.is_valid(): #create a comment objet without saving it to the database
        comment=form.save(commit=False) #Assign the post to the comment
        comment.post=post #save the comment to the database
        comment.save()
        return render (request, 'blogsite/post/comment.html',{'post':post, 'form': form, 'comment': comment})

def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status=Status.PUBLISHED)
    sent = False

    if request.method == 'POST':  # Form was submitted
        form = EmailPostForm(request.POST)  # Create form instance with submitted data
        
        if form.is_valid():  # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())

            subject = (
                f"{cd['name']} ({cd['email']}) recommends you read {post.title}"
            )

            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd['comments']}"
            )

            send_mail(
                subject=subject,
                message=message,
                from_email=None,  # Replace None with a valid email address if needed
                recipient_list=[cd['to']]
            )
            sent = True  # Indicate that the email has been sent
    else:
        form = EmailPostForm()  # Create a new empty form

    return render(request, 'blogsite/post/share.html', {
        'post': post,
        'form': form,
        'sent': sent  # Pass the sent status to the template
    })

def post_list(request, tag_slug=None):
    post_list = Post.published.all()  # Get all published posts
    tag=None
    if tag_slug:
        tag=get_object_or_404(Tag, slug=tag_slug)
        post_list.filter(tags__in=[tag])
    paginator = Paginator(post_list, 3)  # Pagination with 3 posts per page

    page_number = request.GET.get('page', 1)  # Get the page number from the query parameters
    try:
        posts = paginator.page(page_number)  # Get the page object
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blogsite/post/list.html', {'posts': posts, 'tag':tag })  # Pass the page object to the template

def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day
    )
    comments=post.comments.filter(active=True) #form for users to comment
    form=CommentForm() #List of all similar posts
    post_tags_ids=post.tags.values_list('id', flat=True)
    similar_posts=Post.published.filter( tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts=similar_posts.annotate(same_tags=Count('tags') ).order_by('-same_tags', '-publish')[:4]
    return render(request, 'blogsite/post/detail.html', {'post': post, 'comments': comments, 'form': form, 'similar_posts': similar_posts})  # Render the detail template