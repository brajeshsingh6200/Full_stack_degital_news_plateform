from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, db
from models import User, Article
from news_service import news_service
import logging
from datetime import datetime

# Categories for news filtering
CATEGORIES = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']

@app.route('/')
def index():
    """Homepage with news articles"""
    category = request.args.get('category', 'general')
    page = request.args.get('page', 1, type=int)
    
    # Get live news from NewsAPI
    live_news = news_service.get_top_headlines(category=category if category != 'general' else None, page=page)
    
    # Get custom articles from database
    custom_articles = Article.query.filter_by(is_custom=True)
    if category != 'general':
        custom_articles = custom_articles.filter_by(category=category)
    
    custom_articles = custom_articles.order_by(Article.created_at.desc()).limit(10).all()
    
    # Convert custom articles to consistent format
    formatted_custom_articles = []
    for article in custom_articles:
        formatted_article = {
            'title': article.title,
            'description': article.summary,
            'content': article.content,
            'author': article.author or 'Staff Writer',
            'source': 'News Portal',
            'url': url_for('article_detail', article_id=article.id),
            'image_url': article.image_url,
            'published_at': article.created_at,
            'is_custom': True,
            'id': article.id
        }
        formatted_custom_articles.append(formatted_article)
    
    # Combine and sort articles
    all_articles = live_news + formatted_custom_articles
    all_articles.sort(key=lambda x: x['published_at'], reverse=True)
    
    return render_template('index.html', 
                         articles=all_articles, 
                         categories=CATEGORIES, 
                         current_category=category,
                         page=page)

@app.route('/article/<int:article_id>')
def article_detail(article_id):
    """Display full article details"""
    article = Article.query.get_or_404(article_id)
    return render_template('article.html', article=article)

@app.route('/search')
def search():
    """Search functionality"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if not query:
        flash('Please enter a search term.', 'warning')
        return redirect(url_for('index'))
    
    # Search live news
    live_results = news_service.search_news(query, page=page)
    
    # Search custom articles
    custom_results = Article.query.filter(
        Article.title.contains(query) | 
        Article.content.contains(query) |
        Article.summary.contains(query)
    ).order_by(Article.created_at.desc()).all()
    
    # Format custom articles
    formatted_custom_results = []
    for article in custom_results:
        formatted_article = {
            'title': article.title,
            'description': article.summary,
            'content': article.content,
            'author': article.author or 'Staff Writer',
            'source': 'News Portal',
            'url': url_for('article_detail', article_id=article.id),
            'image_url': article.image_url,
            'published_at': article.created_at,
            'is_custom': True,
            'id': article.id
        }
        formatted_custom_results.append(formatted_article)
    
    # Combine results
    all_results = live_results + formatted_custom_results
    all_results.sort(key=lambda x: x['published_at'], reverse=True)
    
    return render_template('search_results.html', 
                         articles=all_results, 
                         query=query, 
                         page=page)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_admin=False,
            is_verified=True  # Auto-verify for simplicity
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.is_verified:
                flash('Account not verified. Please contact admin.', 'warning')
                return render_template('login.html')
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user)
            flash('Login successful!', 'success')
            
            # Redirect to admin dashboard if admin, otherwise to home
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page - redirect to main login"""
    flash('Please use the main login page.', 'info')
    return redirect(url_for('login'))



@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    articles = Article.query.filter_by(is_custom=True).order_by(Article.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('admin_dashboard.html', articles=articles)

@app.route('/admin/article/new', methods=['GET', 'POST'])
@login_required
def admin_new_article():
    """Create new article"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        summary = request.form.get('summary')
        author = request.form.get('author')
        category = request.form.get('category')
        image_url = request.form.get('image_url')
        
        if not title or not content:
            flash('Title and content are required.', 'danger')
            return render_template('admin_article_form.html', categories=CATEGORIES)
        
        article = Article(
            title=title,
            content=content,
            summary=summary,
            author=author,
            category=category,
            image_url=image_url,
            is_custom=True
        )
        
        db.session.add(article)
        db.session.commit()
        
        flash('Article created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_article_form.html', categories=CATEGORIES)

@app.route('/admin/article/<int:article_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_article(article_id):
    """Edit existing article"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    article = Article.query.get_or_404(article_id)
    
    if request.method == 'POST':
        article.title = request.form.get('title')
        article.content = request.form.get('content')
        article.summary = request.form.get('summary')
        article.author = request.form.get('author')
        article.category = request.form.get('category')
        article.image_url = request.form.get('image_url')
        
        if not article.title or not article.content:
            flash('Title and content are required.', 'danger')
            return render_template('admin_article_form.html', article=article, categories=CATEGORIES)
        
        db.session.commit()
        flash('Article updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_article_form.html', article=article, categories=CATEGORIES)

@app.route('/admin/article/<int:article_id>/delete', methods=['POST'])
@login_required
def admin_delete_article(article_id):
    """Delete article"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    flash('Article deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
