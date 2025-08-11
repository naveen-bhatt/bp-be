# BP Backend - Production-Ready FastAPI Application

A comprehensive FastAPI backend application with clean architecture, featuring authentication, e-commerce capabilities, and modern development practices.

## 🚀 Features

- **Clean Architecture**: Strict separation of concerns with layers for controllers, services, repositories, and models
- **Authentication**: JWT-based auth with social login support (Google, GitHub, Apple)
- **E-commerce**: Complete shopping cart and checkout functionality
- **Payment Processing**: Stripe and Razorpay integration with webhook support
- **Database**: SQLAlchemy 2.0 with Alembic migrations
- **Testing**: Comprehensive test suite with pytest
- **Type Safety**: Full mypy type checking
- **Code Quality**: Ruff linting and formatting
- **Containerization**: Docker and Docker Compose ready
- **Production Ready**: Structured logging, error handling, and monitoring

## 🏗️ Architecture

```
app/
├── main.py                 # FastAPI application entry point
├── core/                   # Core application logic
│   ├── config.py          # Configuration management
│   ├── logging.py         # Structured logging
│   ├── db.py              # Database configuration
│   ├── security.py        # JWT and security utilities
│   ├── errors.py          # Global error handlers
│   └── dependencies.py    # Shared dependencies
├── middleware/             # HTTP middleware
├── models/                 # SQLAlchemy ORM models
├── repositories/           # Data access layer
├── services/              # Business logic layer
├── schemas/               # Pydantic request/response models
├── controllers/           # API route handlers
├── providers/             # External service integrations
│   ├── oauth/            # OAuth providers (Google, GitHub, Apple)
│   └── payments/         # Payment providers (Stripe, Razorpay)
└── utils/                 # Utility functions
```

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: MySQL/MariaDB with SQLAlchemy 2.0
- **Migrations**: Alembic
- **Authentication**: PyJWT with OAuth2 support
- **Validation**: Pydantic v2
- **Password Hashing**: Passlib with bcrypt
- **HTTP Client**: HTTPX
- **Testing**: pytest with async support
- **Type Checking**: mypy
- **Linting**: Ruff
- **Container**: Docker & Docker Compose

## 🚀 Quick Start

### Using Docker Compose (Recommended)

1. **Clone and setup**:
```bash
git clone <repository-url>
cd bp-be
cp env.example .env
```

2. **Configure environment variables** in `.env`:
```env
SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=mysql+pymysql://user:password@db:3306/bp_backend
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
```

3. **Start the application**:
```bash
docker-compose up -d
```

4. **Run migrations**:
```bash
docker-compose exec api alembic upgrade head
```

5. **Create admin user**:
```bash
docker-compose exec api python -m scripts.seed_admin
```

The API will be available at `http://localhost:8000`

### Manual Setup

1. **Requirements**:
   - Python 3.11+
   - MySQL/MariaDB database

2. **Installation**:
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
pip install -e ".[dev]"  # For development dependencies
```

3. **Configuration**:
```bash
cp env.example .env
# Edit .env with your settings
```

4. **Database setup**:
```bash
# Create database
mysql -u root -p -e "CREATE DATABASE bp_backend;"

# Run migrations
alembic upgrade head

# Seed admin user
python -m scripts.seed_admin
```

5. **Run the application**:
```bash
uvicorn app.main:app --reload
```

## 📋 API Documentation

Once running, visit:
- **Interactive Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

### Key Endpoints

#### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/social` - Social login
- `GET /api/v1/auth/me` - Get current user

#### Products
- `GET /api/v1/products` - List products
- `GET /api/v1/products/{id}` - Get product details
- `POST /api/v1/products` - Create product (admin)

#### Cart
- `GET /api/v1/cart` - Get current cart
- `POST /api/v1/cart/items` - Add item to cart
- `PATCH /api/v1/cart/items/{id}` - Update cart item
- `DELETE /api/v1/cart/items/{id}` - Remove cart item

#### Checkout & Payments
- `POST /api/v1/checkout/orders` - Create order from cart
- `POST /api/v1/checkout/payment-intent` - Create payment intent
- `POST /api/v1/checkout/webhook/stripe` - Stripe webhook
- `POST /api/v1/checkout/webhook/razorpay` - Razorpay webhook

## 🔧 Development

### Commands

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy app/

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Create migration
alembic revision --autogenerate -m "Description"

# Run migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run integration tests
pytest -m integration
```

## 🔐 OAuth Setup

### Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs
6. Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`

### GitHub OAuth

1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Create a new OAuth App
3. Set Authorization callback URL
4. Set `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` in `.env`

### Apple Sign In (TODO)

See `app/providers/oauth/apple.py` for implementation details.

## 💳 Payment Setup

### Stripe

1. Create [Stripe account](https://stripe.com/)
2. Get API keys from Dashboard
3. Set `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET`
4. Configure webhook endpoint: `https://yourapp.com/api/v1/checkout/webhook/stripe`
5. Subscribe to events: `payment_intent.succeeded`, `payment_intent.payment_failed`

### Razorpay

1. Create [Razorpay account](https://razorpay.com/)
2. Get API keys from Dashboard
3. Set `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET`
4. Configure webhook endpoint: `https://yourapp.com/api/v1/checkout/webhook/razorpay`

## 🚀 Deployment

### Environment Variables

Required environment variables for production:

```env
# Application
APP_NAME="BP Backend"
ENV=prod
SECRET_KEY=your-production-secret-key
DEBUG=false

# Database
DATABASE_URL=mysql+pymysql://user:password@host:3306/database

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# OAuth (configure as needed)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

# Payments (configure as needed)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Admin User
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=secure-admin-password
```

### Docker Production

```bash
# Build production image
docker build -t bp-backend:latest .

# Run with production config
docker run -d \
  --name bp-backend \
  -p 8000:8000 \
  --env-file .env.prod \
  bp-backend:latest
```

### Health Checks

The application includes health check endpoints:
- `GET /health` - Application health status
- Database connectivity check
- Version information

## 🧪 Example Usage

### User Registration and Login

```bash
# Register new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Shopping Flow

```bash
# List products
curl "http://localhost:8000/api/v1/products"

# Add to cart
curl -X POST "http://localhost:8000/api/v1/cart/items" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id": "product-uuid", "quantity": 2}'

# Create order
curl -X POST "http://localhost:8000/api/v1/checkout/orders" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'

# Create payment intent
curl -X POST "http://localhost:8000/api/v1/checkout/payment-intent" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"order_id": "order-uuid", "provider": "stripe"}'
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the test files for usage examples

---

Built with ❤️ using FastAPI and modern Python practices.