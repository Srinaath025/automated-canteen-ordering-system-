# CanteenFlow - Automated Canteen Ordering System

A fast-track web ordering platform designed for college and workplace canteens. It reduces counter congestion with instant kitchen tokens, categorized menu ordering, customizations, and multiple payment options.

---

## Features

- **User Authentication**: Secure registration and login using salted password hashing (`werkzeug.security`).
- **Persistent Database**: SQLite-powered data layer (`canteen.db`) for users, menu items, order history, and feedback.
- **Dynamic Menu**: Categorized dishes (Breakfast & Tiffin, Lunch & Meals, Beverages) with pure-veg badges, pricing, and photos.
- **Order Customizations**: Specify preparation notes (e.g. "Less spicy", "Extra sambar", "Strong filter").
- **Live Food Tray (Cart)**: Add/modify quantities, review order summary, or clear tray with live item count in the navbar.
- **Multiple Payment Options**:
  - UPI QR Code (GPay, PhonePe, Paytm)
  - Credit / Debit Card
  - Pay at Canteen Cash Counter
- **Kitchen Token Generation**: Unique token generation (e.g. `#CAN-8492`) with 3-stage visual progress tracker (Received &rarr; Preparing &rarr; Ready).
- **Order History**: Track active tokens and past meal orders.
- **Customer Feedback**: 5-star rating system with comments and community review feed.
- **Modern Responsive Design**: Glassmorphism UI, Outfit/Jakarta typography, micro-animations, and alert dismissal.

---

## Project Structure

```
canteen/
├── run.py                                    # Root launcher
└── automated-canteen-ordering-system--main/
    ├── app.py                                # Main Flask controller & endpoints
    ├── database.py                           # SQLite schema, queries, and seeding
    ├── requirements.txt                      # Project dependencies
    ├── canteen.db                            # SQLite database (auto-generated on first run)
    ├── static/
    │   ├── css/
    │   │   └── style.css                     # Custom glassmorphic styling & design system
    │   ├── js/
    │   │   └── main.js                       # Interactive steppers, QR toggle & validation
    │   └── a.jpeg                            # Canteen UPI QR Code asset
    └── templates/
        ├── base.html                         # Base shell with navbar, alerts & footer
        ├── login.html                        # Authentication login screen
        ├── register.html                     # Account creation with validation
        ├── menu.html                         # Dynamic food menu with categories
        ├── cart.html                         # Live tray & itemized billing
        ├── payment.html                      # Payment gateway simulation (QR/Card/Cash)
        ├── payment_confirmation.html         # Official kitchen token receipt
        ├── orders.html                       # Token tracking and order history
        └── feedback.html                     # 5-star rating & review submission
```

---

## How to Run

### 1. Install Dependencies
Ensure Python 3.10+ is installed:
```powershell
pip install -r requirements.txt
```

### 2. Start the Application
From the project folder:
```powershell
python app.py
```
*Or from the workspace root:*
```powershell
python run.py
```

### 3. Open in Browser
Visit **[http://127.0.0.1:5000](http://127.0.0.1:5000)**
1. Click **Register** to create your account (e.g., username: `canteen_user`, password: `password123`).
2. Log in and browse the menu.
3. Add items to your tray, customize instructions, and proceed to checkout.
4. Scan the QR code or select Cash Counter, place your order, and receive your kitchen token!

---

## Deploy to Render (Cloud Hosting)

This repository is configured for free cloud hosting on [Render](https://render.com).

### Option 1: Automatic Blueprint (Recommended)
1. Log in to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** > **Blueprint**.
3. Connect your GitHub repository: `https://github.com/Srinaath025/automated-canteen-ordering-system-`.
4. Render will read `render.yaml` and configure everything automatically. Click **Apply**.

### Option 2: Manual Web Service
1. Log in to [Render Dashboard](https://dashboard.render.com/) and click **New +** > **Web Service**.
2. Select your repository `automated-canteen-ordering-system-`.
3. Fill in the following settings:
   - **Name**: `canteenflow`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`
4. Click **Create Web Service**. Your live URL will be ready in 1-2 minutes!
