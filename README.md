# Telegram Marketplace Bot

A refactored, modular Telegram bot for managing a marketplace with cart functionality, checkout flow, and Stripe payment integration.

## Features

- 🛍️ Product browsing by category
- 🛒 Shopping cart management
- 📝 Multi-step checkout with delivery address collection
- 💳 Stripe payment integration
- 📧 Email notifications via Mailgun
- ⏱️ Session timeout management
- 🔄 Clean, modular code structure

## Project Structure

\`\`\`
telegram-bot/
├── main.py                   # Entry point
├── config.json               # Product catalog
├── requirements.txt          # Dependencies
├── .env.example             # Environment variables template
│
├── bot/                     # Bot logic
│   ├── config.py           # Configuration loader
│   ├── handlers/           # Message & callback handlers
│   │   ├── commands.py
│   │   ├── cart.py
│   │   └── checkout.py
│   ├── services/           # Business logic
│   │   ├── cart_service.py
│   │   ├── order_service.py
│   │   ├── payment_service.py
│   │   └── email_service.py
│   └── utils/              # Helper functions
│       ├── session.py
│       ├── validation.py
│       └── formatting.py
│
└── webhooks/               # Flask webhook server
    ├── app.py
    └── stripe_handler.py
\`\`\`

## Setup

### 1. Install Dependencies

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

\`\`\`bash
cp .env.example .env
\`\`\`

Edit `.env` with your actual values:
- `TELEGRAM_BOT_TOKEN` - Get from [@BotFather](https://t.me/botfather)
- `STRIPE_SECRET_KEY` - From your Stripe dashboard
- `STRIPE_WEBHOOK_SECRET` - From Stripe webhook settings
- `MAILGUN_API_KEY` - From Mailgun dashboard
- `MAILGUN_DOMAIN` - Your Mailgun domain
- Email addresses for notifications

### 3. Configure Products

Edit `config.json` to set up your product catalog:

\`\`\`json
{
  "shop_name": "Your Shop Name",
  "currency": "GBP",
  "products": {
    "Category Name": {
      "Product Name": "9.99"
    }
  }
}
\`\`\`

### 4. Set Up Ngrok (for local testing)

For local development with Stripe webhooks:

\`\`\`bash
ngrok http 5000
\`\`\`

Copy the HTTPS URL to your `.env` file as `NGROK_URL`.

### 5. Configure Stripe Webhook

In your Stripe dashboard:
1. Go to Developers → Webhooks
2. Add endpoint: `https://your-ngrok-url.ngrok-free.app/webhook`
3. Select event: `checkout.session.completed`
4. Copy the webhook secret to your `.env` file

### 6. Run the Bot

\`\`\`bash
python main.py
\`\`\`

## Usage

### Bot Commands

- `/start` - Start the bot and show welcome message
- `/order` - Browse products
- `/cart` - View shopping cart
- `/help` - Show help information
- `/restart` - Clear session and start over

### Order Flow

1. Browse products by category
2. Add items to cart with quantities
3. View/edit cart
4. Checkout (provide delivery details)
5. Complete payment via Stripe
6. Receive confirmation

## Development

### Running Locally

1. Ensure all environment variables are set in `.env`
2. Run ngrok for webhook testing
3. Start the bot with `python main.py`
4. Test in Telegram

### Testing Payments

Use Stripe test cards:
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`

## Deployment

For production deployment to Google Cloud:

1. Remove ngrok dependency
2. Use environment variables from VM/Cloud Run
3. Configure domain for webhooks
4. Update Stripe webhook URL

## Python Version

Requires Python 3.10.12 or higher

## License

Private project
