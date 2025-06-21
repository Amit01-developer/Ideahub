from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from forms import LoginForm, RegisterForm, IdeaForm
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '82eb2acb-6122-4396-b25a-7e3026b86052'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ideahub.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

class Idea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(100))
    category = db.Column(db.String(50))
    upvotes = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    idea_id = db.Column(db.Integer, db.ForeignKey('idea.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data  
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
def index():
    q = request.args.get('q', '')
    if q:
        ideas = Idea.query.filter(
            Idea.title.contains(q) | Idea.tags.contains(q) | Idea.category.contains(q)
        ).order_by(Idea.id.desc()).all()
    else:
        ideas = Idea.query.order_by(Idea.id.desc()).all()
    return render_template('index.html', ideas=ideas)

@app.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():
    form = IdeaForm()
    if form.validate_on_submit():
        idea = Idea(
            title=form.title.data,
            description=form.description.data,
            tags=form.tags.data,
            category=form.category.data,
            user_id=current_user.id
        )
        db.session.add(idea)
        db.session.commit()
        flash("Idea submitted!", "success")
        return redirect(url_for("index"))
    return render_template('submit.html', form=form)

@app.route('/idea/<int:id>')
def idea_detail(id):
    idea = Idea.query.get_or_404(id)
    comments = Comment.query.filter_by(idea_id=id).order_by(Comment.id.desc()).all()
    return render_template('idea_detail.html', idea=idea, comments=comments)

@app.route('/idea/<int:id>/upvote', methods=['POST'])
@login_required
def upvote(id):
    idea = Idea.query.get_or_404(id)
    idea.upvotes += 1
    db.session.commit()
    return redirect(url_for('idea_detail', id=id))

@app.route('/idea/<int:id>/comment', methods=['POST'])
@login_required
def comment(id):
    content = request.form.get('content')
    if content:
        new_comment = Comment(content=content, idea_id=id, user_id=current_user.id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment posted!', 'info')
    return redirect(url_for('idea_detail', id=id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)