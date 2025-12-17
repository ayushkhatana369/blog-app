from flask import Flask, render_template, request, redirect, url_for, flash
import os
os.makedirs("instance", exist_ok=True)
from werkzeug.utils import secure_filename
from models import db, Post, User, Category, Tag, Comment
import markdown
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user
)

app = Flask(__name__)

# ================= CONFIG =================
UPLOAD_FOLDER = "static/uploads/posts"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = "change-this-later"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# ✅ Flask 3.x compatible DB initialization
with app.app_context():
    db.create_all()

    # Create default admin user if not exists
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()




# ================= LOGIN =================
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ================= HELPERS =================
@app.template_filter("markdown")
def markdown_filter(text):
    return markdown.markdown(
        text,
        extensions=["fenced_code", "codehilite"]
    )

def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

# ================= PUBLIC ROUTES =================
@app.route("/")
def index():
    page = request.args.get("page", 1, type=int)

    pagination = (
        Post.query
        .filter(Post.is_published == True)
        .order_by(Post.created_at.desc())
        .paginate(page=page, per_page=5, error_out=False)
    )

    return render_template(
        "index.html",
        posts=pagination.items,
        pagination=pagination
    )

@app.route("/post/<int:post_id>")
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)

    if not post.is_published and not current_user.is_authenticated:
        return redirect(url_for("index"))

    post.views += 1
    db.session.commit()

    meta_title = post.meta_title or post.title
    meta_description = post.meta_description or post.excerpt(160)

    return render_template(
        "post.html",
        post=post,
        meta_title=meta_title,
        meta_description=meta_description
    )

@app.route("/category/<string:name>")
def category_view(name):
    category = Category.query.filter_by(name=name).first_or_404()

    posts = (
        Post.query
        .filter_by(category=category, is_published=True)
        .order_by(Post.created_at.desc())
        .all()
    )

    return render_template(
        "category.html",
        category=category,
        posts=posts
    )

@app.route("/tag/<string:name>")
def tag_view(name):
    tag = Tag.query.filter_by(name=name).first_or_404()
    posts = [p for p in tag.posts if p.is_published]
    return render_template("tag.html", tag=tag, posts=posts)

@app.route("/search")
def search():
    query = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)

    pagination = (
        Post.query
        .filter(
            Post.is_published == True,
            (Post.title.ilike(f"%{query}%")) |
            (Post.content.ilike(f"%{query}%"))
        )
        .order_by(Post.created_at.desc())
        .paginate(page=page, per_page=5, error_out=False)
    )

    return render_template(
        "index.html",
        posts=pagination.items,
        pagination=pagination
    )

# ================= AUTH =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and user.check_password(request.form["password"]):
            login_user(user)
            return redirect(url_for("admin"))
        flash("Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

# ================= ADMIN =================
@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    categories = Category.query.order_by(Category.name).all()
    tags = Tag.query.order_by(Tag.name).all()

    if request.method == "POST":
        image_file = request.files.get("image")
        filename = None

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image_file.save(image_path)

        post = Post(
            title=request.form["title"],
            content=request.form["content"],
            category_id=request.form.get("category_id") or None,
            image=filename,
            is_published=bool(request.form.get("is_published"))
        )

        tag_ids = request.form.getlist("tags")
        for tag_id in tag_ids:
            tag = Tag.query.get(tag_id)
            if tag:
                post.tags.append(tag)

        db.session.add(post)
        db.session.commit()
        return redirect(url_for("index"))

    return render_template(
        "admin.html",
        categories=categories,
        tags=tags
    )

@app.route("/admin/edit/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    categories = Category.query.order_by(Category.name).all()
    tags = Tag.query.order_by(Tag.name).all()

    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]
        post.category_id = request.form.get("category_id") or None
        post.is_published = bool(request.form.get("is_published"))

        post.tags.clear()
        for tag_id in request.form.getlist("tags"):
            tag = Tag.query.get(tag_id)
            if tag:
                post.tags.append(tag)

        db.session.commit()
        return redirect(url_for("post_detail", post_id=post.id))

    return render_template(
        "edit.html",
        post=post,
        categories=categories,
        tags=tags
    )

# ================= COMMENTS =================
@app.route("/post/<int:post_id>/comment", methods=["POST"])
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)

    if not post.is_published:
        return redirect(url_for("index"))

    content = request.form.get("content")
    author = request.form.get("author")

    if content:
        comment = Comment(content=content, author=author, post=post)
        db.session.add(comment)
        db.session.commit()

    return redirect(url_for("post_detail", post_id=post.id))

@app.route("/admin/comment/delete/<int:comment_id>", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for("post_detail", post_id=post_id))
@app.route("/write", methods=["GET", "POST"])
@login_required
def write_post():
    categories = Category.query.order_by(Category.name).all()
    tags = Tag.query.order_by(Tag.name).all()

    if request.method == "POST":
        post = Post(
            title=request.form["title"],
            content=request.form["content"],
            category_id=request.form.get("category_id") or None,
            is_published=current_user.is_admin  # 🔑 KEY LINE
        )

        tag_ids = request.form.getlist("tags")
        for tag_id in tag_ids:
            tag = Tag.query.get(tag_id)
            if tag:
                post.tags.append(tag)

        db.session.add(post)
        db.session.commit()

        if current_user.is_admin:
            return redirect(url_for("index"))
        else:
            flash("Post submitted for review ✨")
            return redirect(url_for("index"))

    return render_template(
        "write.html",
        categories=categories,
        tags=tags
    )

@app.route("/admin/delete/<int:post_id>", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    total_posts = Post.query.count()
    total_comments = Comment.query.count()

    most_viewed_post = (
        Post.query
        .order_by(Post.views.desc())
        .first()
    )

    recent_posts = (
        Post.query
        .order_by(Post.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard.html",
        total_posts=total_posts,
        total_comments=total_comments,
        most_viewed_post=most_viewed_post,
        recent_posts=recent_posts
    )


# ================= START =================
if __name__ == "__main__":
    app.run(debug=True)

