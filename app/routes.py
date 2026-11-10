
from urllib.parse import urlparse, urljoin

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import User, Post, Like, Comment, Follow, Bookmark


main = Blueprint("main", __name__)


# =========================================================
# SECURITY HELPERS
# =========================================================

def is_safe_url(target):
    """
    Check that a redirect URL points to this same website.
    This prevents external redirect attacks.
    """

    if not target:
        return False

    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    return (
        test_url.scheme in ("http", "https")
        and test_url.netloc == ref_url.netloc
    )


def safe_redirect(fallback):
    """
    Only redirect to the referrer if it belongs to this website.
    Otherwise, use the supplied fallback.
    """

    target = request.referrer

    if target and is_safe_url(target):
        return redirect(target)

    return redirect(fallback)


def valid_image_url(value):
    """
    Allow empty image URLs or valid HTTP/HTTPS URLs.
    """

    if not value:
        return True

    parsed = urlparse(value)

    return (
        parsed.scheme in ("http", "https")
        and bool(parsed.netloc)
    )


# =========================================================
# HOMEPAGE AND FEEDS
# =========================================================

@main.route("/")
def index():

    feed_type = request.args.get("feed", "for_you")

    if feed_type not in ("for_you", "following"):
        feed_type = "for_you"

    if current_user.is_authenticated and feed_type == "following":

        followed_ids = [
            follow.followed_id
            for follow in current_user.following
        ]

        posts = (
            Post.query
            .filter(Post.user_id.in_(followed_ids))
            .order_by(Post.created_at.desc())
            .all()
        )

    else:

        feed_type = "for_you"

        posts = (
            Post.query
            .order_by(Post.created_at.desc())
            .all()
        )

    return render_template(
        "index.html",
        posts=posts,
        feed_type=feed_type
    )


# =========================================================
# USER REGISTRATION
# =========================================================

@main.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not email or not password:

            flash(
                "Please complete all required fields.",
                "error"
            )

        elif len(username) < 3 or len(username) > 30:

            flash(
                "Username must be between 3 and 30 characters.",
                "error"
            )

        elif len(email) > 120:

            flash(
                "Email address is too long.",
                "error"
            )

        elif len(password) < 8:

            flash(
                "Password must contain at least 8 characters.",
                "error"
            )

        elif password != confirm_password:

            flash(
                "Your passwords do not match.",
                "error"
            )

        elif User.query.filter(
            or_(
                User.username == username,
                User.email == email
            )
        ).first():

            flash(
                "That username or email is already registered.",
                "error"
            )

        else:

            user = User(
                username=username,
                email=email
            )

            user.set_password(password)

            try:

                db.session.add(user)
                db.session.commit()

                login_user(user)

                flash(
                    "Your Devora account has been created!",
                    "success"
                )

                return redirect(url_for("main.index"))

            except IntegrityError:

                db.session.rollback()

                flash(
                    "That username or email is already in use.",
                    "error"
                )

    return render_template("register.html")


# =========================================================
# USER LOGIN
# =========================================================

@main.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(
            email=email
        ).first()

        if user and user.check_password(password):

            login_user(user)

            next_page = request.args.get("next")

            if next_page and is_safe_url(next_page):
                return redirect(next_page)

            return redirect(url_for("main.index"))

        flash(
            "Invalid email or password.",
            "error"
        )

    return render_template("login.html")


# =========================================================
# USER LOGOUT
# =========================================================

@main.route("/logout", methods=["POST"])
@login_required
def logout():

    logout_user()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(url_for("main.index"))


# =========================================================
# CREATE POST
# =========================================================

@main.route("/create-post", methods=["POST"])
@login_required
def create_post():

    content = request.form.get("content", "").strip()
    image_url = request.form.get("image_url", "").strip()

    if not content and not image_url:

        flash(
            "Your post cannot be empty.",
            "error"
        )

    elif len(content) > 5000:

        flash(
            "Your post is too long.",
            "error"
        )

    elif not valid_image_url(image_url):

        flash(
            "Please enter a valid image URL.",
            "error"
        )

    else:

        post = Post(
            user_id=current_user.id,
            content=content,
            image_url=image_url or None
        )

        db.session.add(post)
        db.session.commit()

        flash(
            "Your post has been published.",
            "success"
        )

    return redirect(url_for("main.index"))


# =========================================================
# DELETE POST
# =========================================================

@main.route("/delete-post/<int:post_id>", methods=["POST"])
@login_required
def delete_post(post_id):

    post = db.get_or_404(Post, post_id)

    if post.user_id != current_user.id:
        abort(403)

    db.session.delete(post)
    db.session.commit()

    flash(
        "Post deleted.",
        "success"
    )

    return safe_redirect(url_for("main.index"))


# =========================================================
# LIKE AND UNLIKE POSTS
# =========================================================

@main.route("/like/<int:post_id>", methods=["POST"])
@login_required
def like_post(post_id):

    post = db.get_or_404(Post, post_id)

    existing_like = Like.query.filter_by(
        user_id=current_user.id,
        post_id=post.id
    ).first()

    if existing_like:

        db.session.delete(existing_like)

    else:

        new_like = Like(
            user_id=current_user.id,
            post_id=post.id
        )

        db.session.add(new_like)

    db.session.commit()

    return safe_redirect(url_for("main.index"))


# =========================================================
# CREATE COMMENT
# =========================================================

@main.route("/comment/<int:post_id>", methods=["POST"])
@login_required
def comment_post(post_id):

    post = db.get_or_404(Post, post_id)

    content = request.form.get("content", "").strip()

    if not content:

        flash(
            "A comment cannot be empty.",
            "error"
        )

    elif len(content) > 1000:

        flash(
            "Your comment is too long.",
            "error"
        )

    else:

        comment = Comment(
            user_id=current_user.id,
            post_id=post.id,
            content=content
        )

        db.session.add(comment)
        db.session.commit()

    return safe_redirect(url_for("main.index"))


# =========================================================
# DELETE COMMENT
# =========================================================

@main.route("/delete-comment/<int:comment_id>", methods=["POST"])
@login_required
def delete_comment(comment_id):

    comment = db.get_or_404(Comment, comment_id)

    if comment.user_id != current_user.id:
        abort(403)

    db.session.delete(comment)
    db.session.commit()

    flash(
        "Comment deleted.",
        "success"
    )

    return safe_redirect(url_for("main.index"))


# =========================================================
# FOLLOW AND UNFOLLOW USERS
# =========================================================

@main.route("/follow/<int:user_id>", methods=["POST"])
@login_required
def follow_user(user_id):

    user = db.get_or_404(User, user_id)

    if user.id == current_user.id:
        abort(400)

    existing_follow = Follow.query.filter_by(
        follower_id=current_user.id,
        followed_id=user.id
    ).first()

    if existing_follow:

        db.session.delete(existing_follow)

    else:

        new_follow = Follow(
            follower_id=current_user.id,
            followed_id=user.id
        )

        db.session.add(new_follow)

    db.session.commit()

    return safe_redirect(
        url_for(
            "main.profile",
            username=user.username
        )
    )


# =========================================================
# BOOKMARK AND REMOVE BOOKMARK
# =========================================================

@main.route("/bookmark/<int:post_id>", methods=["POST"])
@login_required
def bookmark_post(post_id):

    post = db.get_or_404(Post, post_id)

    existing_bookmark = Bookmark.query.filter_by(
        user_id=current_user.id,
        post_id=post.id
    ).first()

    if existing_bookmark:

        db.session.delete(existing_bookmark)

    else:

        new_bookmark = Bookmark(
            user_id=current_user.id,
            post_id=post.id
        )

        db.session.add(new_bookmark)

    db.session.commit()

    return safe_redirect(url_for("main.index"))


# =========================================================
# SAVED POSTS
# =========================================================

@main.route("/saved")
@login_required
def saved():

    bookmarks = (
        Bookmark.query
        .filter_by(user_id=current_user.id)
        .order_by(Bookmark.id.desc())
        .all()
    )

    posts = [
        bookmark.post
        for bookmark in bookmarks
        if bookmark.post is not None
    ]

    return render_template(
        "saved.html",
        posts=posts
    )


# =========================================================
# USER PROFILE
# =========================================================

@main.route("/profile/<username>")
def profile(username):

    user = User.query.filter_by(
        username=username
    ).first_or_404()

    posts = (
        Post.query
        .filter_by(user_id=user.id)
        .order_by(Post.created_at.desc())
        .all()
    )

    is_following = False

    if current_user.is_authenticated:

        is_following = Follow.query.filter_by(
            follower_id=current_user.id,
            followed_id=user.id
        ).first() is not None

    return render_template(
        "profile.html",
        user=user,
        posts=posts,
        is_following=is_following
    )


# =========================================================
# FOLLOWERS
# =========================================================

@main.route("/followers/<int:user_id>")
def followers(user_id):

    user = db.get_or_404(User, user_id)

    # Pass Follow objects because followers.html
    # accesses follow.follower.username and follow.follower.bio.

    followers_list = (
        Follow.query
        .filter_by(followed_id=user.id)
        .order_by(Follow.created_at.desc())
        .all()
    )

    return render_template(
        "followers.html",
        user=user,
        followers=followers_list
    )


# =========================================================
# FOLLOWING
# =========================================================

@main.route("/following/<int:user_id>")
def following(user_id):

    user = db.get_or_404(User, user_id)

    # Pass Follow objects because following.html
    # accesses follow.followed.username and follow.followed.bio.

    following_list = (
        Follow.query
        .filter_by(follower_id=user.id)
        .order_by(Follow.created_at.desc())
        .all()
    )

    return render_template(
        "following.html",
        user=user,
        following=following_list
    )


# =========================================================
# EDIT PROFILE
# =========================================================

@main.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        bio = request.form.get("bio", "").strip()
        profile_image = request.form.get("profile_image", "").strip()

        existing_username = User.query.filter(
            User.username == username,
            User.id != current_user.id
        ).first()

        existing_email = User.query.filter(
            User.email == email,
            User.id != current_user.id
        ).first()

        if not username:

            flash(
                "Username cannot be empty.",
                "error"
            )

        elif len(username) < 3 or len(username) > 30:

            flash(
                "Username must be between 3 and 30 characters.",
                "error"
            )

        elif not email:

            flash(
                "Email address cannot be empty.",
                "error"
            )

        elif len(email) > 120:

            flash(
                "Email address is too long.",
                "error"
            )

        elif len(bio) > 250:

            flash(
                "Your bio must be 250 characters or fewer.",
                "error"
            )

        elif existing_username:

            flash(
                "That username is already taken.",
                "error"
            )

        elif existing_email:

            flash(
                "That email address is already registered.",
                "error"
            )

        elif not valid_image_url(profile_image):

            flash(
                "Please enter a valid profile image URL.",
                "error"
            )

        else:

            current_user.username = username
            current_user.email = email
            current_user.bio = bio or None
            current_user.profile_image = profile_image or None

            try:

                db.session.commit()

                flash(
                    "Your profile has been updated.",
                    "success"
                )

                return redirect(
                    url_for(
                        "main.profile",
                        username=current_user.username
                    )
                )

            except IntegrityError:

                db.session.rollback()

                flash(
                    "That username or email is already in use.",
                    "error"
                )

    return render_template("edit_profile.html")
