# Subscription Manager

A professional, full-featured subscription tracking application built with Python Flask and SQLite. Track all your subscriptions, manage renewals, monitor spending, and never miss a payment again.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [User Guide](#user-guide)
  - [Getting Started](#getting-started)
  - [Dashboard](#dashboard)
  - [Managing Subscriptions](#managing-subscriptions)
  - [Payment Methods](#payment-methods)
  - [Subscription Groups](#subscription-groups)
  - [Reports & Analytics](#reports--analytics)
  - [Budget Planning](#budget-planning)
  - [Notifications](#notifications)
  - [Admin Panel](#admin-panel)
  - [Profile Settings](#profile-settings)
- [API Reference](#api-reference)
- [Database Schema](#database-schema)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Features

### Core Features

| Feature | Description |
|---------|-------------|
| **Multi-User Authentication** | Secure user registration and login with password hashing |
| **Subscription Management** | Full CRUD operations for subscriptions with detailed tracking |
| **Payment Methods** | Track credit cards and bank accounts linked to subscriptions |
| **Smart Notifications** | In-app and email alerts for upcoming renewals |
| **Comprehensive Reports** | Analyze spending by category, provider, payment method |
| **Budget Planning** | Calendar view and forecasting for upcoming expenses |
| **Dark Mode** | Toggle between light and dark themes |
| **Multi-Currency** | Support for USD, EUR, GBP, INR, CAD, AUD, JPY |

### Advanced Features

| Feature | Description |
|---------|-------------|
| **Trial Period Tracking** | Mark subscriptions as trials with end date tracking |
| **Price History** | Automatic tracking when subscription prices change |
| **Secure Credentials** | Encrypted storage for account emails and usernames |
| **Document Attachments** | Upload receipts, invoices, and contracts |
| **Subscription Groups** | Bundle related subscriptions (e.g., "Microsoft 365 Family") |
| **Admin Panel** | Manage categories, providers, subscription types, and users |
| **CSV Export** | Export all subscription data for external analysis |
| **Responsive Design** | Works seamlessly on desktop, tablet, and mobile |

---

## Screenshots

### Dashboard
The dashboard provides a quick overview of your subscription portfolio:
- Active subscription count
- Monthly and yearly spending
- Upcoming renewals (next 15 days)
- Spending breakdown by category (pie chart)
- Monthly spending trends (bar chart)

### Subscription List
View all subscriptions with:
- Filter by status (active/inactive/cancelled)
- Filter by category
- Sort by name, amount, renewal date, or date added
- Card-based layout with key information

### Budget Calendar
Visual calendar showing:
- Renewal dates for each day
- Monthly totals
- Navigation between months

---

## Technology Stack

### Backend
- **Python 3.11+** - Programming language
- **Flask 3.0** - Web framework
- **SQLAlchemy** - ORM for database operations
- **Flask-Login** - User session management
- **Flask-Mail** - Email notifications
- **APScheduler** - Background task scheduling
- **Werkzeug** - Password hashing
- **Cryptography** - Credential encryption

### Frontend
- **HTML5/CSS3** - Markup and styling
- **Bootstrap 5.3** - UI framework
- **Bootstrap Icons** - Icon library
- **Chart.js** - Data visualizations
- **JavaScript (ES6+)** - Client-side interactivity

### Database
- **SQLite** - Lightweight, file-based database

---

## Installation

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- Git

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/lalitnayyar/myPersonalSubscriptionModel.git
   cd myPersonalSubscriptionModel
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional)
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env with your settings
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Open in browser**
   ```
   http://localhost:5000
   ```

---

## Configuration

### Environment Variables

Create a `.env` file in the root directory with the following settings:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this

# Database (default: SQLite)
DATABASE_URL=sqlite:///instance/subscriptions.db

# Email Configuration (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@subscriptionm.com

# Encryption Key (for credential storage)
ENCRYPTION_KEY=your-encryption-key-change-this
```

### Email Setup (Gmail)

To enable email notifications with Gmail:

1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password:
   - Go to Google Account → Security → App passwords
   - Select "Mail" and your device
   - Copy the generated password
3. Use the app password in `MAIL_PASSWORD`

---

## User Guide

### Getting Started

#### Registration
1. Navigate to the application URL
2. Click "Create one" on the login page
3. Fill in your details:
   - Full Name
   - Email Address
   - Password (minimum 6 characters)
   - Default Currency
4. Click "Create Account"

The first registered user automatically becomes an admin.

#### Login
1. Enter your email and password
2. Optionally check "Remember me" for persistent sessions
3. Click "Sign In"

---

### Dashboard

The dashboard is your home base, providing:

#### Summary Cards
- **Active Subscriptions**: Count of currently active subscriptions
- **Monthly Spend**: Total monthly cost in your default currency
- **Yearly Estimate**: Projected annual spending
- **Trial Subscriptions**: Count of active trials

#### Upcoming Renewals
Shows subscriptions due in the next 15 days with:
- Subscription name
- Renewal date
- Days remaining (color-coded badges)
- Amount due

#### Recent Notifications
Displays the latest unread notifications for quick action.

#### Charts
- **Spending by Category**: Doughnut chart showing distribution
- **Monthly Spending**: Bar chart of spending trends

#### Quick Actions
- Add Subscription
- Add Payment Method
- Export CSV
- View Reports

---

### Managing Subscriptions

#### Adding a Subscription

1. Click "Add Subscription" from the dashboard or subscriptions page
2. Fill in the form:

**Basic Information**
| Field | Description | Required |
|-------|-------------|----------|
| Name | Subscription name (e.g., "Netflix Premium") | Yes |
| Provider | Service provider (e.g., Netflix) | No |
| Category | Category for organization | No |
| Type/Tier | Subscription tier (e.g., Premium) | No |
| Notes | Additional notes | No |

**Pricing**
| Field | Description | Required |
|-------|-------------|----------|
| Amount | Subscription cost | Yes |
| Currency | Payment currency | Yes |
| Billing Cycle | Monthly, Yearly, or One-time | Yes |

**Dates & Renewal**
| Field | Description | Required |
|-------|-------------|----------|
| Start Date | When subscription started | Yes |
| Next Renewal Date | When payment is due | No |
| Reminder Days | Days before renewal to notify (default: 15) | No |
| Auto-renew | Whether subscription auto-renews | No |

**Trial Period**
| Field | Description | Required |
|-------|-------------|----------|
| Is Trial | Mark as trial subscription | No |
| Trial End Date | When trial expires | No |

**Payment & Group**
| Field | Description | Required |
|-------|-------------|----------|
| Payment Method | Card/bank for payment | No |
| Subscription Group | Group/bundle membership | No |

**Account Credentials** (Encrypted)
| Field | Description | Required |
|-------|-------------|----------|
| Account Email | Login email for the service | No |
| Account Username | Username if different from email | No |

3. Click "Add Subscription"

#### Viewing a Subscription

The detail view shows:
- All subscription information
- Monthly/yearly cost calculations
- Days until renewal with status badge
- Account credentials (with copy to clipboard)
- Price change history
- Attached documents

#### Editing a Subscription

1. Click "Edit" on the subscription card or detail page
2. Modify any fields
3. If changing the price, optionally add a reason
4. Click "Save Changes"

Price changes are automatically tracked in the history.

#### Subscription Status Management

**Status Types:**
- **Active**: Currently running subscription
- **Inactive**: Temporarily paused
- **Cancelled**: Permanently cancelled

**Actions:**
- **Deactivate**: Pause an active subscription
- **Reactivate**: Resume an inactive subscription with a new start date
- **Cancel**: Mark as cancelled (sets auto-renew to false)
- **Delete**: Permanently remove (with confirmation)

#### Filtering and Sorting

**Filters:**
- Status: All, Active, Inactive, Cancelled
- Category: Filter by any category

**Sort Options:**
- Name (A-Z)
- Amount (highest first)
- Renewal Date (soonest first)
- Date Added (newest first)

---

### Payment Methods

#### Adding a Payment Method

1. Navigate to "Payment Methods" in the menu
2. Click "Add Payment Method"
3. Fill in:
   - **Type**: Credit/Debit Card or Bank Account
   - **Name**: Descriptive name (e.g., "Chase Visa")
   - **Last 4 Digits**: For identification (optional)
   - **Expiry Date**: For cards (optional)
   - **Set as Default**: Make this the default payment method

#### Managing Payment Methods

- **View Subscriptions**: See all subscriptions using this payment method
- **Edit**: Update payment method details
- **Set as Default**: Change the default payment method
- **Delete**: Remove (only if no subscriptions are using it)

#### Expiry Alerts

The system automatically:
- Flags cards expiring within 30 days
- Marks expired cards
- Creates notifications for expiring cards

---

### Subscription Groups

Groups allow you to bundle related subscriptions together.

#### Use Cases
- Microsoft 365 Family (multiple apps under one subscription)
- Amazon Prime (Prime Video, Music, Shopping benefits)
- Apple One Bundle

#### Creating a Group

1. Navigate to "Groups" in the menu
2. Click "Create Group"
3. Enter:
   - **Group Name**: e.g., "Microsoft 365 Family"
   - **Description**: Optional details
4. Click "Create Group"

#### Managing Groups

- **Add Subscriptions**: Click "Add Subscription" and select from available subscriptions
- **Remove Subscriptions**: Click "Remove" next to any subscription in the group
- **View Total Cost**: See combined monthly cost of all subscriptions in the group
- **Edit/Delete**: Modify or remove the group

---

### Reports & Analytics

#### Report Types

**By Category**
- Pie chart visualization
- Monthly and yearly totals per category
- List of subscriptions in each category
- Sorted by spending (highest first)

**By Provider**
- Spending grouped by service provider
- Subscription counts per provider
- Quick links to provider websites

**By Payment Method**
- See which cards/accounts are charged the most
- Monthly totals per payment method
- List of associated subscriptions

**By Status**
- Compare active vs inactive vs cancelled
- Count and cost breakdown
- Quick links to filtered views

#### Exporting Data

**CSV Export:**
1. Go to Reports → Export CSV
2. Download includes:
   - Name, Provider, Category
   - Amount, Currency, Billing Cycle
   - Status, Renewal Date, Start Date
   - Auto-renew, Is Trial, Notes

---

### Budget Planning

#### Monthly Calendar

The budget calendar shows:
- Visual monthly grid
- Subscription renewals on their due dates
- Color-coded badges for each subscription
- Monthly total at the top
- Navigation between months

#### Yearly Overview

- Bar chart of monthly spending
- Month-by-month breakdown
- Renewal counts per month
- Yearly total and monthly average

#### 6-Month Forecast

- Projected spending for next 6 months
- List of subscriptions due each month
- Running total for the forecast period

---

### Notifications

#### Notification Types

| Type | Icon | Description |
|------|------|-------------|
| Renewal Reminder | Calendar | Subscription due within reminder period |
| Payment Due | Credit Card | Payment is due soon |
| Expired | Warning | Subscription has expired |
| Trial Ending | Clock | Trial period ending soon |
| Price Change | Dollar | Subscription price has changed |
| Card Expiring | Card | Payment method expiring soon |

#### In-App Notifications

- Bell icon in navbar shows unread count
- Dropdown shows latest 5 notifications
- Click notification to view related subscription
- "View All" link to full notification history

#### Managing Notifications

- **Mark as Read**: Click checkmark on individual notification
- **Mark All as Read**: Bulk action for all notifications
- **Delete**: Remove individual notifications
- **Filter**: By type or read/unread status

#### Email Notifications

When enabled (in Profile settings):
- Renewal reminders sent at configured days before
- Trial ending alerts
- Payment method expiry warnings

---

### Admin Panel

*Admin access required*

#### Managing Categories

Categories help organize subscriptions.

**Default Categories:**
- Entertainment
- Productivity
- Cloud Storage
- Music
- News & Media
- Health & Fitness
- Education
- Utilities
- Shopping
- Other

**Category Properties:**
- Name
- Icon (Bootstrap Icons class, e.g., "bi-film")
- Color (hex code for visual identification)
- Description

#### Managing Providers

Providers are the companies offering subscriptions.

**Default Providers:**
Netflix, Spotify, Amazon Prime, Disney+, Microsoft 365, Google One, Apple Music, iCloud+, YouTube Premium, HBO Max, Dropbox, Adobe Creative Cloud, Notion, Slack, GitHub, Other

**Provider Properties:**
- Name
- Website URL
- Logo (upload image)
- Default Category

#### Managing Subscription Types

Types represent subscription tiers.

**Default Types:**
- Free
- Basic
- Standard
- Premium
- Enterprise
- Family
- Student

#### Managing Users

- View all registered users
- See subscription counts per user
- Grant/revoke admin access
- View registration and login dates

---

### Profile Settings

#### Account Information

- **Full Name**: Update display name
- **Email**: View only (cannot be changed)
- **Default Currency**: Set preferred currency for displays
- **Email Notifications**: Toggle email alerts on/off
- **Dark Mode**: Toggle dark theme

#### Change Password

1. Enter current password
2. Enter new password (minimum 6 characters)
3. Confirm new password
4. Click "Change Password"

#### Account Statistics

View your account info:
- Member since date
- Last login time
- Active subscription count
- Account type (Admin/User)

---

## API Reference

The application includes a REST API for programmatic access.

### Endpoints

#### Subscriptions
```
GET  /api/subscriptions          - List all subscriptions
GET  /api/subscriptions/:id      - Get subscription details
GET  /api/upcoming-renewals      - Get upcoming renewals
```

#### Dashboard
```
GET  /api/dashboard/stats        - Get dashboard statistics
GET  /api/spending/by-category   - Get spending by category
```

#### Reference Data
```
GET  /api/categories             - List all categories
GET  /api/providers              - List all providers
```

#### Notifications
```
GET  /api/notifications          - List notifications
POST /api/notifications/:id/read - Mark as read
POST /api/notifications/read-all - Mark all as read
```

### Response Format

All API responses are JSON:

```json
{
  "id": 1,
  "name": "Netflix",
  "amount": 15.99,
  "currency": "USD",
  "billing_cycle": "monthly",
  "status": "active",
  "next_renewal_date": "2024-02-15",
  "days_until_renewal": 12
}
```

---

## Database Schema

### Entity Relationship Diagram

```
users
├── id (PK)
├── email (unique)
├── password_hash
├── full_name
├── default_currency
├── email_alerts_enabled
├── is_admin
├── dark_mode
├── created_at
└── last_login

subscriptions
├── id (PK)
├── user_id (FK → users)
├── name
├── provider_id (FK → providers)
├── category_id (FK → categories)
├── subscription_type_id (FK → subscription_types)
├── payment_method_id (FK → payment_methods)
├── group_id (FK → subscription_groups)
├── amount
├── currency
├── billing_cycle
├── start_date
├── next_renewal_date
├── reminder_days
├── status
├── auto_renew
├── is_trial
├── trial_end_date
├── account_email_encrypted
├── account_username_encrypted
├── notes
├── created_at
└── updated_at

payment_methods
├── id (PK)
├── user_id (FK → users)
├── type
├── name
├── last_four_digits
├── expiry_date
├── is_default
└── created_at

categories
├── id (PK)
├── name (unique)
├── icon
├── color
└── description

providers
├── id (PK)
├── name (unique)
├── website
├── logo_url
├── category_id (FK → categories)
└── created_at

subscription_types
├── id (PK)
├── name (unique)
└── description

subscription_groups
├── id (PK)
├── user_id (FK → users)
├── name
├── description
└── created_at

subscription_price_history
├── id (PK)
├── subscription_id (FK → subscriptions)
├── old_amount
├── new_amount
├── currency
├── changed_at
└── reason

subscription_attachments
├── id (PK)
├── subscription_id (FK → subscriptions)
├── filename
├── original_filename
├── file_type
├── file_size
├── uploaded_at
└── notes

notifications
├── id (PK)
├── user_id (FK → users)
├── subscription_id (FK → subscriptions)
├── type
├── message
├── is_read
├── email_sent
├── created_at
└── read_at

currency_rates
├── id (PK)
├── from_currency
├── to_currency
├── rate
└── updated_at
```

---

## Project Structure

```
subscriptionM/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration settings
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # User model
│   │   ├── subscription.py      # Subscription models
│   │   ├── payment_method.py    # Payment method model
│   │   ├── provider.py          # Provider, Category, Type models
│   │   ├── notification.py      # Notification model
│   │   └── currency.py          # Currency rate model
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication routes
│   │   ├── dashboard.py         # Dashboard routes
│   │   ├── subscriptions.py     # Subscription CRUD
│   │   ├── payments.py          # Payment methods
│   │   ├── reports.py           # Reports & analytics
│   │   ├── budget.py            # Budget planning
│   │   ├── admin.py             # Admin panel
│   │   ├── api.py               # REST API endpoints
│   │   ├── notifications.py     # Notification management
│   │   ├── groups.py            # Subscription groups
│   │   └── attachments.py       # File attachments
│   ├── services/
│   │   ├── __init__.py
│   │   ├── notification_service.py  # Notification logic
│   │   ├── email_service.py         # Email sending
│   │   ├── currency_service.py      # Currency conversion
│   │   ├── encryption_service.py    # Credential encryption
│   │   └── scheduler_service.py     # Background tasks
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── subscriptions/
│   │   ├── payments/
│   │   ├── reports/
│   │   ├── budget/
│   │   ├── admin/
│   │   ├── notifications/
│   │   ├── groups/
│   │   └── attachments/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css        # Custom styles
│   │   └── js/
│   │       └── app.js           # Custom JavaScript
│   └── uploads/                 # File upload storage
├── instance/                    # SQLite database
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
└── README.md                    # This file
```

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/myPersonalSubscriptionModel.git
cd myPersonalSubscriptionModel

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run in development mode
FLASK_ENV=development python run.py
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - The web framework used
- [Bootstrap](https://getbootstrap.com/) - UI framework
- [Chart.js](https://www.chartjs.org/) - Data visualization
- [Bootstrap Icons](https://icons.getbootstrap.com/) - Icon library

---

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/lalitnayyar/myPersonalSubscriptionModel/issues) page
2. Create a new issue with detailed description
3. Include steps to reproduce any bugs

---

**Made with by Lalit Nayyar**
