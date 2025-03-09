from django.urls import path
from library import views



# urlpatterns = [
#     path("", views.home),
#     path("dashbord", views.Dashbord),
#     path("logout", views.logout_view),
 
# ]

from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_user, name="logout"),
    path("callback", views.callback, name="callback"),
    # path("dashbord", views.Dashbord, name="dashbord"),
    path('book_list/', views.book_list, name='book_list'),
    path('books/new/', views.book_new, name='book_new'),
    path("books/<int:book_id>/edit/", views.book_edit, name="book_edit"),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),
    path("books/<int:book_id>/borrow/", views.borrow_book, name="borrow_book"),
    path("books/<int:book_id>/return/", views.return_book, name="return_book"),

]



