from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path(
        "create-listing/", views.ListingCreateView.as_view(), name="ListingCreateView"
    ),
    path(
        "update-listing/<int:pk>",
        views.ListingUpdateView.as_view(),
        name="ListingUpdateView",
    ),
    path("categories/", views.CategoryListView.as_view(), name="CategoryListView"),
    path("view-listing/<int:pk>", views.ListingView.as_view(), name="ListingView"),
    path("get_bid/<int:pk>", views.get_bid, name="get_bid"),
    path(
        "add-to-watch-list/<int:pk>", views.add_to_watch_list, name="add_to_watch_list"
    ),
    path(
        "remove-from-watch-list/<int:pk>",
        views.remove_from_watch_list,
        name="remove_from_watch_list",
    ),
    path(
        "add_to_watch_list_htmx/<int:pk>",
        views.add_to_watch_list_htmx,
        name="add_to_watch_list_htmx",
    ),
    path(
        "remove_from_watch_list_htmx/<int:pk>",
        views.remove_from_watch_list_htmx,
        name="remove_from_watch_list_htmx",
    ),
    path("watch_list", views.show_watch_list, name="show_watch_list"),
    path(
        "remove_from_watch_list_htmx_hard/<int:pk>",
        views.remove_from_watch_list_htmx_hard,
        name="remove_from_watch_list_htmx_hard",
    ),
    path("show-my-bids/", views.show_my_bids, name="show_my_bids"),
    path(
        "close-the-action/<int:pk>", views.close_the_auction, name="close_the_auction"
    ),
    path("add-comment/<int:pk>", views.add_comment, name="add_comment"),
]
