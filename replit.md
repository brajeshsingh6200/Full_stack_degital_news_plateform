# Digital News Portal - Flask Application

## Overview

This is a Digital News Portal built with Flask that serves as a news aggregation platform. The application combines live news from NewsAPI.org with custom articles created through an admin interface. It features a responsive web design with Bootstrap, categorized news browsing, search functionality, and a comprehensive admin dashboard for content management.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (July 14, 2025)

✓ Added user registration and login system
✓ Enhanced User model with admin privileges and verification status
✓ Created separate login/register pages for regular users
✓ Updated navigation to show user authentication status
✓ Added admin privilege checks for dashboard and article management
✓ Integrated PostgreSQL database with proper user authentication

## System Architecture

### Frontend Architecture
- **Technology**: HTML5, CSS3, JavaScript with Bootstrap 5 for responsive design
- **Theme**: Dark theme implementation using Bootstrap agent theme
- **UI Components**: Responsive navigation, card-based article layouts, modal dialogs, and form interfaces
- **Static Assets**: Custom CSS for styling enhancements and JavaScript for interactive features

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database ORM**: SQLAlchemy with Flask-SQLAlchemy extension
- **Authentication**: Flask-Login for session management
- **Template Engine**: Jinja2 (built into Flask)
- **Configuration**: Environment-based configuration for database and API keys

### Database Schema
- **Users Table**: Stores admin user credentials with Flask-Login integration
- **Articles Table**: Stores custom articles with metadata (title, content, author, category, timestamps)
- **Database Options**: SQLite for development, configurable for PostgreSQL in production

## Key Components

### Authentication System
- **Flask-Login Integration**: Manages user sessions and login state
- **Password Security**: Werkzeug password hashing for secure credential storage
- **Admin Protection**: Login required decorators for admin routes

### News Service Integration
- **NewsAPI.org Integration**: Fetches live news articles by category and search terms
- **Error Handling**: Robust error handling for API failures and timeouts
- **Data Formatting**: Standardizes article format between live news and custom articles

### Article Management
- **CRUD Operations**: Full create, read, update, delete functionality for articles
- **Category System**: Predefined categories (business, entertainment, health, science, sports, technology)
- **Content Types**: Support for both live API news and custom admin-created articles

### Search and Filtering
- **Category Filtering**: Filter articles by predefined news categories
- **Search Functionality**: Search across both live news and custom articles
- **Pagination**: Implemented for better performance with large datasets

## Data Flow

1. **User Request**: User visits homepage or searches for articles
2. **News Aggregation**: System fetches live news from NewsAPI and custom articles from database
3. **Data Processing**: Articles are formatted into consistent structure and sorted by publication date
4. **Template Rendering**: Jinja2 templates render the combined article data
5. **Response**: HTML page served to user with responsive design

### Admin Workflow
1. **Authentication**: Admin logs in through dedicated login page
2. **Dashboard Access**: Admin dashboard shows all custom articles with management options
3. **Article Management**: Admin can create, edit, or delete custom articles
4. **Database Updates**: Changes are persisted to SQLAlchemy database

## External Dependencies

### API Services
- **NewsAPI.org**: Primary source for live news articles
- **Configuration**: API key stored as environment variable

### Frontend Libraries
- **Bootstrap 5**: CSS framework for responsive design
- **Font Awesome**: Icon library for UI elements
- **jQuery**: JavaScript library for DOM manipulation

### Python Packages
- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM
- **Flask-Login**: User session management
- **Requests**: HTTP library for API calls
- **Werkzeug**: Password hashing and security utilities

## Deployment Strategy

### Development Setup
- **Local Development**: Uses SQLite database and debug mode
- **Environment Variables**: SESSION_SECRET, DATABASE_URL, NEWS_API_KEY
- **Port Configuration**: Runs on port 5000 with host binding to 0.0.0.0

### Production Considerations
- **Database**: Configurable to use PostgreSQL via DATABASE_URL environment variable
- **Proxy Support**: ProxyFix middleware for reverse proxy deployments
- **Security**: Environment-based secret key management
- **Logging**: Configured logging for debugging and monitoring

### File Structure
```
├── app.py              # Application factory and configuration
├── main.py             # Application entry point
├── models.py           # Database models (User, Article)
├── routes.py           # URL routes and view functions
├── news_service.py     # NewsAPI integration service
├── templates/          # Jinja2 HTML templates
├── static/            # CSS, JavaScript, and other static assets
└── requirements.txt   # Python dependencies
```

The application follows Flask best practices with clear separation of concerns, making it maintainable and scalable for future enhancements.