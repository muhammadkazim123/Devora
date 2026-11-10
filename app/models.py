
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    bio = db.Column(db.String(250))
    profile_image = db.Column(db.String(255))

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    posts = db.relationship(
        "Post",
        back_populates="author",
        cascade="all, delete-orphan"
    )

    likes = db.relationship(
        "Like",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    comments = db.relationship(
        "Comment",
        back_populates="author",
        cascade="all, delete-orphan"
    )

    following = db.relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan"
    )

    followers = db.relationship(
        "Follow",
        foreign_keys="Follow.followed_id",
        back_populates="followed",
        cascade="all, delete-orphan"
    )

    saved_posts = db.relationship(
        "Bookmark",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    author = db.relationship(
        "User",
        back_populates="posts"
    )

    likes = db.relationship(
        "Like",
        back_populates="post",
        cascade="all, delete-orphan"
    )

    comments = db.relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan",
        order_by="Comment.created_at.asc()"
    )

    bookmarks = db.relationship(
        "Bookmark",
        back_populates="post",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Post {self.id}>"


class Like(db.Model):
    __tablename__ = "likes"

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "post_id",
            name="unique_user_post_like"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey("posts.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user = db.relationship(
        "User",
        back_populates="likes"
    )

    post = db.relationship(
        "Post",
        back_populates="likes"
    )

    def __repr__(self):
        return f"<Like {self.id}>"


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey("posts.id"),
        nullable=False
    )

    content = db.Column(db.String(1000), nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    author = db.relationship(
        "User",
        back_populates="comments"
    )

    post = db.relationship(
        "Post",
        back_populates="comments"
    )

    def __repr__(self):
        return f"<Comment {self.id}>"


class Follow(db.Model):
    __tablename__ = "follows"

    __table_args__ = (
        db.UniqueConstraint(
            "follower_id",
            "followed_id",
            name="unique_follow"
        ),
        db.CheckConstraint(
            "follower_id != followed_id",
            name="no_self_follow"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    follower_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    followed_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    follower = db.relationship(
        "User",
        foreign_keys=[follower_id],
        back_populates="following"
    )

    followed = db.relationship(
        "User",
        foreign_keys=[followed_id],
        back_populates="followers"
    )

    def __repr__(self):
        return f"<Follow {self.follower_id} -> {self.followed_id}>"

class Bookmark(db.Model):
    __tablename__ = "bookmarks"

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "post_id",
            name="unique_user_post_bookmark"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey("posts.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user = db.relationship(
        "User",
        back_populates="saved_posts"
    )

    post = db.relationship(
        "Post",
        back_populates="bookmarks"
    )

    def __repr__(self):
        return f"<Bookmark {self.user_id} -> {self.post_id}>"
