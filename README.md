
A complete authentication and subscription management system built with FastAPI, integrating JWT authentication and Stripe payments.

## ✨ Features

- ✅ Secure user registration and login
- ✅ JWT authentication with refresh tokens
- ✅ Password hashing with bcrypt
- 💳 Stripe subscription payments
- 🏦 Stripe billing portal integration
- 🔔 Webhook handling for real-time updates
- 🖥️ Ready-to-use frontend templates
- 🗄️ PostgreSQL/SQLite database support

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Stripe account
- PostgreSQL 

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/fastapi-stripe.git
cd auth-subscription-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Run the application
uvicorn main:app --reload

### 🖼️ Home Page
![Home Page](assets/welcome.png)