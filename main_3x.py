"""
Telegram Bot with Payment Integration using Aiogram 3.x
=====================================================

Professional Telegram bot for handling Star payments and premium subscriptions.
Supports Telegram Stars (XTR) currency for in-app purchases.

Features:
- Start command with invoice generation
- Pre-checkout query validation
- Successful payment processing
- Premium subscription activation
- Comprehensive error handling
- Professional logging setup

Author: Xisache Dev
GitHub: https://github.com/xisache/pay-via-stars
Version: 1.0.0
License: MIT
"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta
from typing import Optional

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramAPIError

# Configuration
TOKEN = 'YOUR_BOT_TOKEN_HERE'  # Replace with your actual bot token
PREMIUM_DURATION_DAYS = 1
STAR_PRICE = 10
MIN_PAYMENT = 1
MAX_PAYMENT = 2500

# Initialize dispatcher
dp = Dispatcher()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class PaymentHandler:
    """Handle payment-related operations"""
    
    def __init__(self):
        self.active_subscriptions = {}  # In production, use database
    
    def add_subscription(self, user_id: int, days: int) -> datetime:
        """Add premium subscription for user"""
        expiry_date = datetime.now() + timedelta(days=days)
        self.active_subscriptions[user_id] = expiry_date
        logger.info(f"Premium subscription added for user {user_id} until {expiry_date}")
        return expiry_date
    
    def is_premium_active(self, user_id: int) -> bool:
        """Check if user has active premium subscription"""
        if user_id not in self.active_subscriptions:
            return False
        return datetime.now() < self.active_subscriptions[user_id]


# Initialize payment handler
payment_handler = PaymentHandler()


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    Handle /start command - send invoice for premium subscription
    """
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        
        logger.info(f"Start command received from user {user_id} (@{username})")
        
        # Check if user already has premium
        if payment_handler.is_premium_active(user_id):
            await message.answer(
                "✅ Sizda allaqachon premium obuna mavjud!\n"
                "Premium funksiyalardan foydalanishingiz mumkin."
            )
            return
        
        # Create inline keyboard for additional options
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💎 Premium haqida ma'lumot", callback_data="info_premium")]
        ])
        
        # Send invoice
        await message.bot.send_invoice(
            chat_id=message.chat.id,
            title="🌟 1 kunlik Premium tarif",
            description="Premium tarifni aktivlashtirish uchun to'lov qiling va barcha imkoniyatlardan foydalaning!",
            payload=f"premium_{user_id}_{PREMIUM_DURATION_DAYS}day",
            currency="XTR",
            prices=[LabeledPrice(label='Telegram Stars', amount=STAR_PRICE)],
            reply_markup=keyboard
        )
        
        logger.info(f"Invoice sent to user {user_id}")
        
    except TelegramAPIError as e:
        logger.error(f"Telegram API error in start command: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
    except Exception as e:
        logger.error(f"Unexpected error in start command: {e}")
        await message.answer("❌ Kutilmagan xatolik yuz berdi.")


@dp.message(Command("status"))
async def cmd_status(message: Message) -> None:
    """Check premium subscription status"""
    try:
        user_id = message.from_user.id
        
        if payment_handler.is_premium_active(user_id):
            expiry_date = payment_handler.active_subscriptions[user_id]
            await message.answer(
                f"✅ Premium obuna faol!\n"
                f"⏰ Tugash vaqti: {expiry_date.strftime('%Y-%m-%d %H:%M')}"
            )
        else:
            await message.answer(
                "❌ Premium obuna mavjud emas.\n"
                "Premium olish uchun /start buyrug'ini yuboring."
            )
            
    except Exception as e:
        logger.error(f"Error in status command: {e}")
        await message.answer("❌ Status tekshirishda xatolik yuz berdi.")


@dp.pre_checkout_query()
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery) -> None:
    """
    Handle pre-checkout queries - validate payment before processing
    """
    try:
        query_id = pre_checkout_query.id
        amount = pre_checkout_query.total_amount
        currency = pre_checkout_query.currency
        payload = pre_checkout_query.invoice_payload
        
        logger.info(f"Pre-checkout query: {query_id}, Amount: {amount}, Currency: {currency}")
        
        # Validate payment parameters
        is_valid = (
            currency == "XTR" and 
            MIN_PAYMENT <= amount <= MAX_PAYMENT and
            payload.startswith("premium_")
        )
        
        if is_valid:
            await pre_checkout_query.answer(ok=True)
            logger.info(f"Pre-checkout approved for query {query_id}")
        else:
            error_msg = "Noto'g'ri to'lov miqdori yoki valyuta turi."
            await pre_checkout_query.answer(
                ok=False,
                error_message=error_msg
            )
            logger.warning(f"Pre-checkout rejected for query {query_id}: {error_msg}")
            
    except TelegramAPIError as e:
        logger.error(f"Telegram API error in pre-checkout: {e}")
        await pre_checkout_query.answer(ok=False, error_message="Texnik xatolik yuz berdi.")
    except Exception as e:
        logger.error(f"Unexpected error in pre-checkout: {e}")
        await pre_checkout_query.answer(ok=False, error_message="Kutilmagan xatolik.")


@dp.message(F.successful_payment)
async def successful_payment(message: Message) -> None:
    """
    Handle successful payments - activate premium subscription
    """
    try:
        payment = message.successful_payment
        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        
        logger.info(
            f"Successful payment from user {user_id} (@{username}): "
            f"{payment.total_amount} {payment.currency}"
        )
        
        # Validate payment details
        if payment.currency == "XTR" and MIN_PAYMENT <= payment.total_amount <= MAX_PAYMENT:
            # Activate premium subscription
            expiry_date = payment_handler.add_subscription(user_id, PREMIUM_DURATION_DAYS)
            
            # Send success message with subscription details
            success_message = (
                "🎉 Tabriklaymiz! Premium obuna muvaffaqiyatli aktivlashtirildi!\n\n"
                f"💎 Obuna turi: {PREMIUM_DURATION_DAYS} kunlik Premium\n"
                f"⏰ Tugash vaqti: {expiry_date.strftime('%Y-%m-%d %H:%M')}\n"
                f"💰 To'langan summa: {payment.total_amount} {payment.currency}\n\n"
                "✨ Endi barcha premium funksiyalardan foydalanishingiz mumkin!"
            )
            
            await message.answer(success_message)
            
            # Log successful activation
            logger.info(f"Premium activated for user {user_id} until {expiry_date}")
            
        else:
            # Invalid payment parameters
            error_message = (
                "❌ To'lov parametrlarida xatolik aniqlandi.\n"
                "Iltimos, qo'llab-quvvatlash xizmati bilan bog'laning."
            )
            await message.answer(error_message)
            logger.warning(f"Invalid payment parameters from user {user_id}")
            
    except Exception as e:
        logger.error(f"Error processing successful payment: {e}")
        await message.answer(
            "❌ To'lovni qayta ishlashda xatolik yuz berdi. "
            "Qo'llab-quvvatlash xizmati bilan bog'laning."
        )


async def main() -> None:
    """
    Main function to start the bot
    """
    try:
        # Initialize bot with default properties
        bot = Bot(
            token=TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        # Get bot info
        bot_info = await bot.get_me()
        logger.info(f"Bot started: @{bot_info.username}")
        
        # Start polling
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")
        sys.exit(1)