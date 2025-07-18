
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


### 1. Welcome Screen
![image alt](https://github.com/Iriajul/fastapi-stripe/blob/83cdc5a81d0c0d8809dd36989b03c0aad7e055f0/assets/welcome.png)

### 2. Signup Page
![image alt](https://github.com/Iriajul/fastapi-stripe/blob/5f3982f3162e664e3d1f02df4cc5e7a84fb72311/assets/signup.png)

### 3. Login Page
![image alt](https://github.com/Iriajul/fastapi-stripe/blob/5f3982f3162e664e3d1f02df4cc5e7a84fb72311/assets/login.png)

### 3. Profile
![image alt](https://github.com/Iriajul/fastapi-stripe/blob/5f3982f3162e664e3d1f02df4cc5e7a84fb72311/assets/profile.png)

### 3. Subscription
![image alt](https://github.com/Iriajul/fastapi-stripe/blob/5f3982f3162e664e3d1f02df4cc5e7a84fb72311/assets/subscription.png)

### 3. Back to profile
![image alt](https://github.com/Iriajul/fastapi-stripe/blob/5f3982f3162e664e3d1f02df4cc5e7a84fb72311/assets/subprofile.png)

### 3. Manage billing
![image alt](https://github.com/Iriajul/fastapi-stripe/blob/5f3982f3162e664e3d1f02df4cc5e7a84fb72311/assets/managebilling.png)

### Installation
bash
# Clone the repository
git clone https://github.com/iriajul/fastapi-stripe.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Run the application
uvicorn main:app --reload

### Workflow
![image alt](https://github.com/Iriajul/fastapi-stripe/blob/3605cb0d5329936e6d4a7ca27df00c3a6a2c9a40/assets/deepseek_mermaid_20250717_9582c5.png)


