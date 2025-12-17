📝 My Flask Blog

A full-featured blog application built with Flask, SQLite, and Jinja2, supporting user authentication, posts, categories, tags, comments, search, image uploads, dark/light mode, and an admin dashboard.

🚀 Features

🔐 User authentication (login / logout)

✍️ Create, edit, and delete blog posts

🗂 Categories & 🏷 Tags support

💬 Comment system on posts

🔍 Search posts by title or content

🖼 Post image uploads

🌗 Dark / Light mode toggle

📊 Admin dashboard (posts, views, comments)

📄 Pagination for posts

🧠 Reading time estimation

📝 Markdown support with syntax highlighting .


🛠 Tech Stack

Backend: Flask, Flask-Login, Flask-SQLAlchemy

Frontend: Jinja2, HTML, CSS

Database: SQLite

Markdown: Python-Markdown (fenced_code, codehilite)

Auth & Security: Werkzeug

Version Control: Git & GitHub


PORJECT STRUCUTURE : 
blogg/
├── app.py
├── models.py
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── post.html
│   ├── admin.html
│   ├── edit.html
│   ├── login.html
│   ├── dashboard.html
│   └── ...
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/
├── instance/
│   └── blog.db   (ignored in git)
├── venv/         (ignored in git)
└── .gitignore


Installation & Setup
1️⃣ Clone the repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

2️⃣ Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Run the application
python app.py


The app will be available at:

http://127.0.0.1:5000 

🔑 Default Admin Credentials

Created automatically on first run

Username: admin
Password: admin123


⚠️ Change this in production

🧪 Notes

instance/blog.db is ignored in Git (local database only)

venv/ is ignored

Image uploads are stored in static/uploads/posts

SQLite is used for simplicity; can be replaced with PostgreSQL/MySQL

📌 Future Improvements

User registration

Role-based permissions

Post drafts & scheduling

Rich text editor

API endpoints

Deployment (Docker / Render / Railway)

📄 License

This project is for learning and personal use.
Feel free to fork and improve 🚀

🙌 Author

Built with ❤️ by AYUSH KHATANA