# 🤖 Telegram Payment Bot

Professional Telegram bot with Telegram Stars payment integration. Supports both Aiogram 2.x and 3.x frameworks for premium subscription management.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Aiogram](https://img.shields.io/badge/Aiogram-2.x%20%7C%203.x-green.svg)](https://aiogram.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-blue.svg)](https://core.telegram.org/bots/api)

## 🌟 Features

- **💳 Telegram Stars Integration** - Native in-app payments
- **🔐 Premium Subscription Management** - Automated subscription handling
- **✅ Payment Validation** - Comprehensive pre-checkout validation
- **📊 Status Tracking** - Real-time subscription status monitoring
- **🛡️ Error Handling** - Professional error management and logging
- **📱 Inline Keyboards** - Enhanced user experience
- **🔄 Dual Framework Support** - Compatible with Aiogram 2.x and 3.x

## 📁 Project Structure

```
telegram-payment-bot/
├── main_3x.py    # Aiogram 3.x implementation
├── main_2x.py    # Aiogram 2.x implementation
└── README.md     # Project documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Basic knowledge of Telegram Bot API

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/xisache/pay-via-stars.git
   cd pay-via-stars
   ```

2. **Run the bot**

   **Aiogram 3.x:**
   ```bash
   python main_3x.py
   ```

   **Aiogram 2.x:**
   ```bash
   python main_2x.py
   ```

## 📋 Requirements

### Aiogram 3.x Version
```txt
aiogram==3.0.0+
aiohttp>=3.8.0
aiofiles>=0.8.0
```

### Aiogram 2.x Version
```txt
aiogram>=2.25.0,<3.0.0
aiohttp>=3.7.0
```

### Bot Configuration

Update the configuration constants in the bot files:

```python
# Configuration
TOKEN = 'YOUR_BOT_TOKEN_HERE'
PREMIUM_DURATION_DAYS = 1
STAR_PRICE = 10
MIN_PAYMENT = 1
MAX_PAYMENT = 2500
```

## 🎯 Usage

### Available Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and show premium subscription options |
| `/status` | Check current premium subscription status |
| `/help` | Display help information and available commands |

### Payment Flow

1. **User starts the bot** with `/start` command
2. **Bot sends an invoice** for premium subscription
3. **User completes payment** using Telegram Stars
4. **Bot validates payment** and activates premium subscription
5. **User receives confirmation** with subscription details

### Premium Features

- ✅ **Unlimited requests** - No rate limiting for premium users
- ✅ **Priority support** - Faster response times
- ✅ **Advanced features** - Access to premium-only functionality
- ✅ **Ad-free experience** - Clean interface without advertisements

## 🔧 API Integration

### Telegram Stars Payment

The bot uses Telegram's native Stars payment system:

```python
# Send invoice
await message.bot.send_invoice(
    chat_id=message.chat.id,
    title="🌟 1 kunlik Premium tarif",
    description="Premium subscription activation",
    payload=f"premium_{user_id}_{duration}",
    currency="XTR",  # Telegram Stars
    prices=[LabeledPrice(label='Telegram Stars', amount=10)]
)
```

### Payment Validation

```python
# Pre-checkout validation
@dp.pre_checkout_query()
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    # Validate payment parameters
    is_valid = (
        pre_checkout_query.currency == "XTR" and 
        MIN_PAYMENT <= pre_checkout_query.total_amount <= MAX_PAYMENT
    )
    await pre_checkout_query.answer(ok=is_valid)
```

## 🛠️ Development

### Code Structure

#### Aiogram 3.x Implementation
- **Modern async/await syntax**
- **Type hints throughout**
- **Structured error handling**
- **Professional logging setup**

#### Aiogram 2.x Implementation
- **Legacy compatibility**
- **Executor-based polling**
- **Callback query handling**
- **Comprehensive validation**

### Key Classes

```python
class PaymentHandler:
    """Handle payment-related operations"""
    
    def add_subscription(self, user_id: int, days: int) -> datetime
    def is_premium_active(self, user_id: int) -> bool
    def get_expiry_date(self, user_id: int) -> Optional[datetime]
```

### Error Handling

The bot includes comprehensive error handling:

- **API Error Handling** - Telegram API exceptions
- **Validation Errors** - Payment parameter validation
- **Logging System** - File and console logging
- **User Feedback** - Informative error messages

## 📊 Logging

The bot generates detailed logs for monitoring:

```
2024-08-01 12:00:00 - INFO - Start command received from user 123456
2024-08-01 12:00:01 - INFO - Invoice sent to user 123456
2024-08-01 12:00:05 - INFO - Pre-checkout approved for query abc123
2024-08-01 12:00:10 - INFO - Premium activated for user 123456 until 2025-08-02 12:00:10
```

## 🔒 Security

### Payment Security
- **Payload validation** - Secure payment payload generation
- **Amount validation** - Min/max payment limits
- **Currency validation** - Only Telegram Stars accepted
- **User validation** - User ID verification in payload

### Data Protection
- **No sensitive data storage** - Tokens and payments handled securely
- **Temporary data only** - Subscription data stored in memory
- **Logging safety** - No sensitive information in logs

## 🚀 Deployment

### Local Development
```bash
python main_3x.py  # For Aiogram 3.x
python main_2x.py  # For Aiogram 2.x
```

#### Using systemd
```ini
[Unit]
Description=Telegram Payment Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/opt/telegram-bot
ExecStart=/usr/bin/python3 main_3x.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Environment Setup

For production environments:

1. **Set up proper logging**
2. **Configure database** (replace in-memory storage)
3. **Set up monitoring** (health checks, metrics)
4. **Configure webhooks** (for better performance)

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Include comprehensive docstrings
- Write tests for new features
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Xisache Dev

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 📞 Support

- **Documentation**: Check this README and code comments
- **Issues**: [GitHub Issues](https://github.com/xisache/pay-via-stars/issues)
- **Telegram**: [@xisache_dev](https://t.me/xisache_dev)
- **Email**: ruxindoff@gmail.com

## 🎯 Roadmap

### Version 2.0
- [ ] **Database Integration** - PostgreSQL/SQLite support
- [ ] **Web Dashboard** - Admin panel for subscription management
- [ ] **Multiple Payment Methods** - Credit cards, PayPal integration
- [ ] **Analytics** - User behavior and payment analytics

### Version 2.1
- [ ] **Multi-language Support** - Internationalization
- [ ] **Subscription Tiers** - Multiple premium levels
- [ ] **Referral System** - User referral rewards
- [ ] **API Webhooks** - External service integration

## 📈 Statistics

- **Language**: Python 3.8+
- **Framework**: Aiogram 2.x/3.x
- **Payment System**: Telegram Stars
- **Architecture**: Async/Await
- **Database**: In-memory (upgradeable)

## 🏆 Acknowledgments

- **Aiogram Team** - For the excellent Telegram Bot framework
- **Telegram** - For the Bot API and Stars payment system
- **Python Community** - For the amazing ecosystem
- **Contributors** - Everyone who helps improve this project

---

<div align="center">

**Made with ❤️ for the Telegram Bot community**

[⭐ Star this repository](https://github.com/xisache/pay-via-stars) if you find it helpful!

</div>
