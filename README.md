# 💸 MiniPay — Wallet & Payment REST API

A clean, secure, and lightweight **digital wallet API** built with Django and Django REST Framework. Supports user registration, JWT authentication, wallet management, deposits, peer-to-peer transfers, and transaction history.

---

## ✨ Features

- 🔐 **JWT Authentication** — Secure login with access & refresh tokens
- 👤 **User Registration** — Auto-creates a wallet on signup
- 💼 **Wallet** — View your current balance
- 💰 **Deposit** — Add funds to your wallet (up to $100,000 per transaction)
- 💸 **Transfer** — Send money to other users instantly
- 📜 **Transaction History** — Full log of all your deposits and transfers
- 🛡️ **Validation** — Blocks self-transfers, negative amounts, and insufficient balance

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | Django 4.2 |
| REST API | Django REST Framework 3.14+ |
| Authentication | SimpleJWT 5.3+ |
| Database | SQLite (dev) |
| Language | Python 3.10+ |

---

## 📁 Project Structure

```
minipay/
├── config/
│   ├── settings.py       # Django settings & JWT config
│   ├── urls.py           # Root URL routing
│   └── wsgi.py
├── payments/
│   ├── models.py         # Wallet & Transaction database models
│   ├── serializers.py    # Input validation & output formatting
│   ├── views.py          # Business logic for each endpoint
│   └── urls.py           # API route definitions
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/minipay.git
cd minipay
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and set your own `SECRET_KEY`:

```env
SECRET_KEY=your-super-secret-key-here
DEBUG=True
ALLOWED_HOSTS=*
```

### 5. Run Database Migrations

```bash
python manage.py migrate
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

API is now live at **http://127.0.0.1:8000**

---

## 📡 API Endpoints

Base URL: `http://127.0.0.1:8000/api`

| Method | Endpoint | Auth Required | Description |
|--------|----------|:---:|-------------|
| `POST` | `/register` | ❌ | Create a new account |
| `POST` | `/login` | ❌ | Get JWT access & refresh tokens |
| `POST` | `/token/refresh` | ❌ | Refresh your access token |
| `GET` | `/wallet` | ✅ | View your wallet balance |
| `POST` | `/deposit` | ✅ | Add money to your wallet |
| `POST` | `/transfer` | ✅ | Send money to another user |
| `GET` | `/transactions` | ✅ | View your full transaction history |

---

## 🧪 Testing the API

> **Tip for Windows users:** PowerShell's `curl` is not the real curl. Use `curl.exe` or use [Thunder Client](https://www.thunderclient.com/) (VS Code extension) or [Postman](https://www.postman.com/).

### Step 1 — Register a User

```bash
curl.exe -X POST http://127.0.0.1:8000/api/register `
  -H "Content-Type: application/json" `
  -d "{\"username\": \"alice\", \"email\": \"alice@example.com\", \"password\": \"SecurePass123!\", \"password2\": \"SecurePass123!\"}"
```

**Response:**
```json
{
  "message": "Account created successfully.",
  "user": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com"
  }
}
```

---

### Step 2 — Login (Get Your Token)

```bash
curl.exe -X POST http://127.0.0.1:8000/api/login `
  -H "Content-Type: application/json" `
  -d "{\"username\": \"alice\", \"password\": \"SecurePass123!\"}"
```

**Response:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR..."
}
```

> Copy the `access` token — you'll need it for all protected endpoints below.

---

### Step 3 — View Wallet

```bash
curl.exe http://127.0.0.1:8000/api/wallet `
  -H "Authorization: Bearer <your_access_token>"
```

**Response:**
```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "balance": "0.00",
  "created_at": "2026-04-24T09:00:00Z",
  "updated_at": "2026-04-24T09:00:00Z"
}
```

---

### Step 4 — Deposit Money

```bash
curl.exe -X POST http://127.0.0.1:8000/api/deposit `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer <your_access_token>" `
  -d "{\"amount\": \"500.00\"}"
```

**Response:**
```json
{
  "message": "$500.00 deposited successfully.",
  "new_balance": "500.00",
  "transaction_id": 1
}
```

---

### Step 5 — Transfer Money to Another User

```bash
curl.exe -X POST http://127.0.0.1:8000/api/transfer `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer <your_access_token>" `
  -d "{\"receiver_username\": \"bob\", \"amount\": \"100.00\", \"note\": \"Lunch money\"}"
```

**Response:**
```json
{
  "message": "$100.00 transferred to bob successfully.",
  "new_balance": "400.00",
  "transaction_id": 2
}
```

---

### Step 6 — View Transaction History

```bash
curl.exe http://127.0.0.1:8000/api/transactions `
  -H "Authorization: Bearer <your_access_token>"
```

**Response:**
```json
{
  "count": 2,
  "transactions": [
    {
      "id": 2,
      "sender_username": "alice",
      "receiver_username": "bob",
      "amount": "100.00",
      "transaction_type": "TRANSFER",
      "status": "SUCCESS",
      "note": "Lunch money",
      "timestamp": "2026-04-24T09:15:00Z"
    },
    {
      "id": 1,
      "sender_username": null,
      "receiver_username": "alice",
      "amount": "500.00",
      "transaction_type": "DEPOSIT",
      "status": "SUCCESS",
      "note": "Wallet deposit",
      "timestamp": "2026-04-24T09:10:00Z"
    }
  ]
}
```

---

## ⚙️ JWT Token Info

| Token | Lifetime | Purpose |
|---|---|---|
| `access` | 1 hour | Used in `Authorization: Bearer <token>` header |
| `refresh` | 7 days | Used to get a new access token at `/api/token/refresh` |

To refresh your access token:

```bash
curl.exe -X POST http://127.0.0.1:8000/api/token/refresh `
  -H "Content-Type: application/json" `
  -d "{\"refresh\": \"<your_refresh_token>\"}"
```

---

## 🔒 Security Notes

> ⚠️ This project is configured for **development only**.

Before deploying to production:

- Change `SECRET_KEY` to a long random string and load it from environment variables
- Set `DEBUG = False`
- Set `ALLOWED_HOSTS` to your actual domain
- Switch from SQLite to PostgreSQL or MySQL
- Enable HTTPS

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙋 Author

Built by sujan subedi — feel free to fork, star ⭐, and contribute!
