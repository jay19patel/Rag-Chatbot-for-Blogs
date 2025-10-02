# AI Blog Creator Chat

A production-ready AI-powered blog creation application built with FastAPI, featuring a modern web interface and Docker containerization.

## 🏗️ Project Structure

```
ai-chatbot/
├── app/                    # Application code
│   ├── static/            # Static files (CSS, JS, images)
│   ├── templates/         # HTML templates
│   ├── __init__.py
│   ├── blog_schema.py     # Blog data models
│   ├── blog_service.py    # Blog business logic
│   ├── chat_api.py        # Chat API endpoints
│   ├── config.py          # Configuration settings
│   ├── db_storage.py      # Database operations
│   ├── db.py             # Database connection
│   └── tools.py          # Utility functions
├── nginx/                 # Nginx configuration
├── logs/                  # Application logs
├── main.py               # FastAPI application entry point
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker image configuration
├── docker-compose.yaml   # Docker Compose configuration
├── docker-compose.prod.yml # Production overrides
├── docker-compose.override.yml # Development overrides
└── start.sh             # Production startup script
```

## 🚀 Quick Start

### Development Mode

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python main.py
   ```

3. **Access the application:**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Production with Docker

1. **Build and run with Docker Compose:**
   ```bash
   # Development
   docker-compose up --build
   
   # Production
   docker-compose -f docker-compose.yaml -f docker-compose.prod.yml up --build -d
   ```

2. **Access the application:**
   - Web Interface: http://localhost
   - API Documentation: http://localhost/docs

## 🐳 Docker Deployment

### Development
```bash
docker-compose up --build
```

### Production
```bash
docker-compose -f docker-compose.yaml -f docker-compose.prod.yml up --build -d
```

### Environment Variables

Create a `.env` file for production:
```env
APP_NAME=AI Blog Creator Chat
VERSION=1.0.0
DEBUG=False
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./app/data/blog.db
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
```

## 🔧 Configuration

### Nginx Configuration
The application includes production-ready Nginx configuration with:
- Rate limiting
- Gzip compression
- Security headers
- Static file caching
- Health checks

### Application Features
- **Multi-worker Gunicorn**: 4 workers for production
- **Health Checks**: Built-in health monitoring
- **Logging**: Structured logging with rotation
- **Security**: Non-root user, security headers
- **Performance**: Optimized for production

## 📊 Monitoring

### Health Checks
- Application: `http://localhost:8000/api`
- Nginx: `http://localhost/health`

### Logs
- Application logs: `./logs/`
- Nginx logs: `./logs/nginx/`

## 🛠️ Development

### Adding New Features
1. Add new API endpoints in `app/chat_api.py`
2. Update templates in `app/templates/`
3. Add static files to `app/static/`
4. Update database models in `app/blog_schema.py`

### Database Operations
- Database models: `app/blog_schema.py`
- Database operations: `app/db_storage.py`
- Database connection: `app/db.py`

## 🔒 Security Features

- **Non-root container**: Application runs as non-root user
- **Security headers**: XSS protection, content type sniffing prevention
- **Rate limiting**: API endpoint protection
- **Input validation**: Pydantic models for data validation
- **CORS configuration**: Proper cross-origin resource sharing

## 📈 Performance Optimizations

- **Gzip compression**: Reduced bandwidth usage
- **Static file caching**: Improved load times
- **Connection pooling**: Database connection optimization
- **Worker processes**: Multi-process handling
- **Keep-alive connections**: Reduced connection overhead

## 🚀 Production Deployment

### Prerequisites
- Docker and Docker Compose
- Domain name (optional)
- SSL certificate (for HTTPS)

### Deployment Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ai-chatbot
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Deploy with Docker Compose:**
   ```bash
   docker-compose -f docker-compose.yaml -f docker-compose.prod.yml up -d
   ```

4. **Verify deployment:**
   ```bash
   curl http://localhost/health
   ```

### SSL/HTTPS Setup
To enable HTTPS, update the Nginx configuration and add SSL certificates to the nginx volume mounts.

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 80 and 8000 are available
2. **Permission issues**: Check file permissions for logs directory
3. **Database errors**: Verify database connection settings
4. **Memory issues**: Adjust worker count in docker-compose.prod.yml

### Debug Mode
Enable debug mode by setting `DEBUG=True` in environment variables.

## 📝 API Documentation

The application provides automatic API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
