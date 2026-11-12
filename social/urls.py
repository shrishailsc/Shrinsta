
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.post_list, name="home"),

    path("register/", views.register, name="register"),

    # SAVED POSTS
    path("save/<int:post_id>/", views.save_post, name="save_post"),
    path("saved/", views.saved_posts, name="saved_posts"),

    # SEARCH AND EXPLORE
    path("search/", views.search_users, name="search_users"),
    path("explore/", views.explore, name="explore"),

    # FOLLOW SYSTEM
    path("follow/<int:user_id>/", views.follow_user, name="follow_user"),
    path("unfollow/<int:user_id>/", views.unfollow_user, name="unfollow_user"),

    # POSTS
    path("like/<int:post_id>/", views.like_post, name="like_post"),
    path("comment/<int:post_id>/", views.add_comment, name="add_comment"),
    path("delete/<int:post_id>/", views.delete_post, name="delete_post"),
    path("edit/<int:post_id>/", views.edit_post, name="edit_post"),

    # LOGIN AND LOGOUT
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="social/login.html"
        ),
        name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # PROFILE
    path("profile/", views.profile, name="profile"),
    path("connections/", views.connections, name="connections"),
    path("user/<int:user_id>/", views.user_profile, name="user_profile"),

    # NOTIFICATIONS
    path("notifications/", views.notifications, name="notifications"),

    # STORIES
    path("add-story/", views.add_story, name="add_story"),
    path("story/<int:story_id>/", views.view_story, name="view_story"),

    # REELS
    path("upload-reel/", views.upload_reel, name="upload_reel"),
    path("reels/", views.reels, name="reels"),
    path("like-reel/<int:reel_id>/", views.like_reel, name="like_reel"),
    path("reel-comment/<int:reel_id>/", views.add_reel_comment, name="add_reel_comment"),

    # DIRECT MESSAGING
    path("inbox/", views.inbox, name="inbox"),
path("chat/<int:user_id>/", views.chat, name="chat"),
   path("delete-message/<int:message_id>/", views.delete_message, name="delete_message"),
]
