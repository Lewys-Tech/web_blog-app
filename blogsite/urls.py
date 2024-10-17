from django.urls import path
from . import views
from .feeds import LatestPostFeed

app_name = 'blogsite'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    # path('', views.PostListView.as_view(), name='post_list'),

    path('post/<int:id>/', views.post_detail, name='post_detail'),  # New pattern for ID access
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail_by_date'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path( '<int:post_id>/comment/', views.post_comment,name='post_comment' ),
    path( 'tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag' ),
    path('feed/', LatestPostFeed(), name='post_feed'),
    path('search/', views.post_search,name='post_search'),
]