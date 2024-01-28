from django.urls import path
from . import views

urlpatterns = [
    path('', views.ArticlesListView.as_view(), name='article_list'),
    path('cat/<category>', views.ArticlesListView.as_view(), name='article_by_category_list'),
    path('<pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('add-article-comment', views.add_article_comment, name='add_article_comment'),
]