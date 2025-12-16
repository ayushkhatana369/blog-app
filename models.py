from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# ================= USERS =================
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# ================= CATEGORIES =================
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    posts = db.relationship("Post", backref="category", lazy=True)


# ================= TAGS =================
# Association table (NO model class)
post_tags = db.Table(
    "post_tags",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"))
)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    posts = db.relationship(
        "Post",
        secondary=post_tags,
        back_populates="tags"
    )


# ================= POSTS =================
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    views = db.Column(db.Integer, default=0)

    image = db.Column(db.String(255), nullable=True)

    is_published = db.Column(db.Boolean, default=True)


    meta_title = db.Column(db.String(255), nullable=True)
    meta_description = db.Column(db.String(300), nullable=True)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("category.id"),
        nullable=True
    )

    tags = db.relationship(
        "Tag",
        secondary=post_tags,
        back_populates="posts"
    )

    def reading_time(self):
        words = len(self.content.split())
        minutes = max(1, words // 200)
        return f"{minutes} min read"

    def excerpt(self, length=200):
        if len(self.content) <= length:
            return self.content
        return self.content[:length] + "..."

# ================= COMMENTS =================
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Link to Post
    post_id = db.Column(
        db.Integer,
        db.ForeignKey("post.id"),
        nullable=False
    )

    # Optional: author name (no login required)
    author = db.Column(db.String(100), nullable=True)

    post = db.relationship("Post", backref="comments")
