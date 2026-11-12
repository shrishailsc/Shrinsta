
from datetime import timedelta
from pathlib import Path

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q, Count

from .models import (
    Post,
    PostImage,
    Profile,
    Comment,
    Notification,
    Story,
    SavedPost,
    Reel,
    ReelComment,
    Message
)


# ==============================
# HOME / POSTS
# ==============================

def post_list(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")

        content = request.POST.get("content", "").strip()
        uploaded_images = request.FILES.getlist("images")
        single_image = request.FILES.get("image")

        if content or uploaded_images or single_image:
            post = Post.objects.create(
                content=content,
                author=request.user,
                image=None
            )

            if single_image:
                post.image = single_image
                post.save()

            for uploaded_image in uploaded_images:
                PostImage.objects.create(
                    post=post,
                    image=uploaded_image
                )

            messages.success(request, "Your post was published!")
        else:
            messages.error(request, "Add text or images!")

        return redirect("home")

    posts = Post.objects.all().order_by("-created_at")

    twenty_four_hours_ago = timezone.now() - timedelta(hours=24)

    stories = Story.objects.filter(
        created_at__gte=twenty_four_hours_ago
    ).select_related("author").order_by("-created_at")

    return render(
        request,
        "social/post_list.html",
        {
            "posts": posts,
            "stories": stories
        }
    )


# ==============================
# REGISTER
# ==============================

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)
        return redirect("home")

    return render(request, "social/register.html")


# ==============================
# PROFILE
# ==============================

@login_required
def profile(request):
    user_profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        user_profile.bio = request.POST.get("bio", "")

        if request.FILES.get("image"):
            user_profile.image = request.FILES.get("image")

        user_profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    return render(
        request,
        "social/profile.html",
        {
            "profile": user_profile,
            "followers_count": user_profile.followers.count(),
            "following_count": user_profile.following.count(),
        }
    )


# ==============================
# STORIES
# ==============================

@login_required
def add_story(request):
    if request.method == "POST":
        uploaded_image = request.FILES.get("image")

        if uploaded_image:
            Story.objects.create(
                author=request.user,
                image=uploaded_image
            )

            messages.success(request, "Your story was uploaded!")
            return redirect("home")

        messages.error(request, "Please select an image!")

    return render(request, "social/add_story.html")


@login_required
def view_story(request, story_id):
    twenty_four_hours_ago = timezone.now() - timedelta(hours=24)

    active_stories = list(
        Story.objects.filter(
            created_at__gte=twenty_four_hours_ago
        ).select_related("author").order_by("-created_at")
    )

    story = next(
        (item for item in active_stories if item.id == story_id),
        None
    )

    if story is None:
        messages.error(request, "This story has expired or does not exist.")
        return redirect("home")

    story_index = active_stories.index(story)

    previous_story = (
        active_stories[story_index - 1]
        if story_index > 0 else None
    )

    next_story = (
        active_stories[story_index + 1]
        if story_index < len(active_stories) - 1 else None
    )

    return render(
        request,
        "social/view_story.html",
        {
            "story": story,
            "previous_story": previous_story,
            "next_story": next_story,
        }
    )


# ==============================
# POST LIKES AND COMMENTS
# ==============================

@login_required
def like_post(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)

        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

            if post.author and post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    sender=request.user,
                    notification_type="LIKE",
                    post=post,
                    message=f"{request.user.username} liked your post."
                )

    return redirect("home")


@login_required
def add_comment(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get("content", "").strip()

        if content:
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )

            if post.author and post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    sender=request.user,
                    notification_type="COMMENT",
                    post=post,
                    message=f"{request.user.username} commented on your post."
                )

    return redirect("home")


# ==============================
# EDIT AND DELETE POSTS
# ==============================

@login_required
def delete_post(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)

        if post.author == request.user:
            post.delete()
            messages.success(request, "Post deleted successfully!")
        else:
            messages.error(request, "You can only delete your own posts!")

    return redirect("home")


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        messages.error(request, "You can only edit your own posts!")
        return redirect("home")

    if request.method == "POST":
        content = request.POST.get("content", "").strip()

        if content:
            post.content = content
            post.save()
            messages.success(request, "Post updated successfully!")
            return redirect("home")

        messages.error(request, "Post cannot be empty!")

    return render(request, "social/edit_post.html", {"post": post})


# ==============================
# SEARCH USERS
# ==============================

@login_required
def search_users(request):
    query = request.GET.get("q", "").strip()

    users = User.objects.filter(
        username__icontains=query
    ).exclude(
        id=request.user.id
    ) if query else User.objects.none()

    return render(
        request,
        "social/search_users.html",
        {
            "users": users,
            "query": query
        }
    )


# ==============================
# FOLLOW / UNFOLLOW
# ==============================

@login_required
def follow_user(request, user_id):
    if request.method == "POST":
        target_user = get_object_or_404(User, id=user_id)

        if target_user != request.user:
            my_profile, created = Profile.objects.get_or_create(
                user=request.user
            )

            target_profile, created = Profile.objects.get_or_create(
                user=target_user
            )

            if not my_profile.following.filter(id=target_profile.id).exists():
                my_profile.following.add(target_profile)

                Notification.objects.create(
                    recipient=target_user,
                    sender=request.user,
                    notification_type="FOLLOW",
                    message=f"{request.user.username} started following you."
                )

            messages.success(
                request,
                f"You are now following {target_user.username}!"
            )

    return redirect("search_users")


@login_required
def unfollow_user(request, user_id):
    if request.method == "POST":
        target_user = get_object_or_404(User, id=user_id)

        my_profile = request.user.profile
        target_profile = get_object_or_404(Profile, user=target_user)

        my_profile.following.remove(target_profile)

        messages.success(
            request,
            f"You unfollowed {target_user.username}."
        )

    return redirect("search_users")


# ==============================
# CONNECTIONS
# ==============================

@login_required
def connections(request):
    user_profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    return render(
        request,
        "social/connections.html",
        {
            "followers": user_profile.followers.select_related("user"),
            "following": user_profile.following.select_related("user"),
            "followers_count": user_profile.followers.count(),
            "following_count": user_profile.following.count(),
        }
    )


@login_required
def user_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)

    user_profile, created = Profile.objects.get_or_create(
        user=profile_user
    )

    posts = Post.objects.filter(
        author=profile_user
    ).order_by("-created_at")

    return render(
        request,
        "social/user_profile.html",
        {
            "profile_user": profile_user,
            "profile": user_profile,
            "posts": posts,
            "followers_count": user_profile.followers.count(),
            "following_count": user_profile.following.count(),
        }
    )


# ==============================
# NOTIFICATIONS
# ==============================

@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related(
        "sender", "post"
    ).order_by("-created_at")

    user_notifications.filter(is_read=False).update(is_read=True)

    return render(
        request,
        "social/notifications.html",
        {
            "notifications": user_notifications,
            "unread_count": 0
        }
    )


# ==============================
# EXPLORE
# ==============================

@login_required
def explore(request):
    posts = Post.objects.all().order_by("-created_at")

    saved_post_ids = SavedPost.objects.filter(
        user=request.user
    ).values_list("post_id", flat=True)

    return render(
        request,
        "social/explore.html",
        {
            "posts": posts,
            "saved_post_ids": saved_post_ids
        }
    )


# ==============================
# SAVED POSTS
# ==============================

@login_required
def save_post(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)

        saved_post, created = SavedPost.objects.get_or_create(
            user=request.user,
            post=post
        )

        if not created:
            saved_post.delete()
            messages.success(request, "Post removed from saved posts!")
        else:
            messages.success(request, "Post saved successfully!")

    return redirect(request.META.get("HTTP_REFERER", "home"))


@login_required
def saved_posts(request):
    saved_items = SavedPost.objects.filter(
        user=request.user
    ).select_related(
        "post", "post__author"
    ).prefetch_related(
        "post__images", "post__likes", "post__comments"
    )

    return render(
        request,
        "social/saved_posts.html",
        {"saved_items": saved_items}
    )


# ==============================
# REELS - UPLOAD VIDEO
# ==============================

@login_required
def upload_reel(request):
    if request.method == "POST":
        video = request.FILES.get("video")
        caption = request.POST.get("caption", "").strip()

        if not video:
            messages.error(request, "Please select a video!")
            return redirect("upload_reel")

        allowed_extensions = [".mp4", ".webm", ".ogg"]
        extension = Path(video.name).suffix.lower()

        if extension not in allowed_extensions:
            messages.error(
                request,
                "Only MP4, WebM and OGG videos are allowed!"
            )
            return redirect("upload_reel")

        if video.size > 50 * 1024 * 1024:
            messages.error(
                request,
                "Video size must be below 50 MB!"
            )
            return redirect("upload_reel")

        Reel.objects.create(
            author=request.user,
            video=video,
            caption=caption
        )

        messages.success(request, "Your Reel was uploaded successfully!")
        return redirect("reels")

    return render(request, "social/upload_reel.html")


# ==============================
# REELS - DISPLAY VIDEOS
# ==============================

@login_required
def reels(request):
    all_reels = Reel.objects.select_related(
        "author"
    ).prefetch_related(
        "likes", "comments"
    ).order_by("-created_at")

    return render(
        request,
        "social/reels.html",
        {"reels": all_reels}
    )


# ==============================
# REELS - LIKE / UNLIKE
# ==============================

@login_required
def like_reel(request, reel_id):
    if request.method == "POST":
        reel = get_object_or_404(Reel, id=reel_id)

        if reel.likes.filter(id=request.user.id).exists():
            reel.likes.remove(request.user)
        else:
            reel.likes.add(request.user)

    return redirect("reels")


# ==============================
# REELS - ADD COMMENT
# ==============================

@login_required
def add_reel_comment(request, reel_id):
    if request.method == "POST":
        reel = get_object_or_404(Reel, id=reel_id)
        content = request.POST.get("content", "").strip()

        if content:
            ReelComment.objects.create(
                reel=reel,
                author=request.user,
                content=content
            )
            messages.success(request, "Comment added!")

    return redirect("reels")


# ==============================
# DIRECT MESSAGING - INBOX
# ==============================



@login_required
def inbox(request):
    search_query = request.GET.get("q", "").strip()

    chat_users = User.objects.filter(
        Q(sent_messages__receiver=request.user) |
        Q(received_messages__sender=request.user)
    ).exclude(
        id=request.user.id
    ).distinct().annotate(
        unread_count=Count(
            "sent_messages",
            filter=Q(
                sent_messages__receiver=request.user,
                sent_messages__is_read=False
            ),
            distinct=True
        )
    )

    search_users = User.objects.none()

    if search_query:
        search_users = User.objects.filter(
            username__icontains=search_query
        ).exclude(id=request.user.id)

    return render(request, "social/inbox.html", {
        "chat_users": chat_users,
        "search_users": search_users,
        "search_query": search_query,
    })


@login_required
def chat(request, user_id):

    other_user = get_object_or_404(User, id=user_id)

    if other_user == request.user:
        return redirect("inbox")

    if request.method == "POST":
        content = request.POST.get("content", "").strip()

        if content:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                content=content
            )

        return redirect("chat", user_id=other_user.id)

    chat_messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).select_related(
        "sender", "receiver"
    ).order_by("created_at")

    Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)

    return render(
        request,
        "social/chat.html",
        {
            "other_user": other_user,
            "chat_messages": chat_messages
        }
    )


# ==============================
# DIRECT MESSAGING - DELETE MESSAGE
# ==============================

@login_required
def delete_message(request, message_id):

    if request.method == "POST":

        message = get_object_or_404(
            Message,
            id=message_id,
            sender=request.user
        )

        other_user = message.receiver

        message.delete()

        messages.success(request, "Message deleted successfully!")

        return redirect("chat", user_id=other_user.id)

    return redirect("inbox")
