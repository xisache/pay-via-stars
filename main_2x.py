"""
Telegram Bot with Payment Integration using Aiogram 2.x
=====================================================

Professional Telegram bot for handling Star payments and premium subscriptions.
Legacy version compatible with Aiogram 2.x framework.

Features:
- Start command with invoice generation
- Pre-checkout query validation
- Successful payment processing
- Premium subscription management
- Comprehensive error handling
- Professional logging setup

Author: Xisache Dev
GitHub: https://github.com/xisache/pay-via-stars
Version: 1.0.0
License: MIT
"""

import json
import logging
import sys
from datetime import datetime, timedelta
from typing import Dict, Optional

from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.utils.exceptions import TelegramAPIError

# Configuration
TOKEN = 'YOUR_BOT_TOKEN_HERE'  # Replace with your actual bot token
PREMIUM_DURATION_DAYS = 1
STAR_PRICE = 10
MIN_PAYMENT = 1
MAX_PAYMENT = 2500

# Initialize bot and dispatcher
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_v2.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class PaymentManager:
    """Manage payment operations and premium subscriptions"""
    
    def __init__(self):
        self.active_subscriptions: Dict[int, datetime] = {}  # In production, use database
        self.payment_history: Dict[str, dict] = {}
    
    def activate_premium(self, user_id: int, days: int) -> datetime:
        """Activate premium subscription for specified days"""
        expiry_date = datetime.now() + timedelta(days=days)
        self.active_subscriptions[user_id] = expiry_date
        logger.info(f"Premium subscription activated for user {user_id} until {expiry_date}")
        return expiry_date
    
    def check_premium_status(self, user_id: int) -> bool:
        """Check if user has active premium subscription"""
        if user_id not in self.active_subscriptions:
            return False
        return datetime.now() < self.active_subscriptions[user_id]
    
    def get_expiry_date(self, user_id: int) -> Optional[datetime]:
        """Get premium subscription expiry date"""
        return self.active_subscriptions.get(user_id)
    
    def record_payment(self, payment_id: str, user_id: int, amount: int, currency: str):
        """Record payment information"""
        self.payment_history[payment_id] = {
            'user_id': user_id,
            'amount': amount,
            'currency': currency,
            'timestamp': datetime.now(),
            'status': 'completed'
        }


# Initialize payment manager
payment_manager = PaymentManager()


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    """
    Handle /start command - display welcome message and send invoice
    """
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        
        logger.info(f"Start command received from user {user_id} (@{username})")
        
        # Check existing premium status
        if payment_manager.check_premium_status(user_id):
            expiry_date = payment_manager.get_expiry_date(user_id)
            await message.answer(
                "✅ <b>Sizda allaqachon premium obuna mavjud!</b>\n\n"
                f"⏰ Tugash vaqti: <code>{expiry_date.strftime('%Y-%m-%d %H:%M')}</code>\n"
                "💎 Premium funksiyalardan foydalanishingiz mumkin."
            )
            return
        
        # Welcome message
        welcome_text = (
            "🌟 <b>Premium Telegram Bot</b>\n\n"
            "Assalomu alaykum! Premium obunani aktivlashtirish uchun "
            "quyidagi to'lov tugmasini bosing.\n\n"
            "💰 Narx: 10 Telegram Stars\n"
            "⏱ Muddat: 1 kun\n"
            "🎯 Premium imkoniyatlar: Cheksiz foydalanish"
        )
        
        # Create inline keyboard
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton("💎 Premium haqida", callback_data="premium_info"),
            InlineKeyboardButton("📊 Statistika", callback_data="user_stats")
        )
        
        await message.answer(welcome_text, reply_markup=keyboard)
        
        # Send invoice using direct API call
        invoice_data = {
            "chat_id": message.from_user.id,
            "title": "🌟 1 kunlik Premium tarif",
            "description": "Premium tarifni aktivlashtirish va barcha imkoniyatlardan foydalanish uchun to'lov",
            "payload": f"premium_subscription_{user_id}_{PREMIUM_DURATION_DAYS}",
            "currency": "XTR",
            "prices": json.dumps([{"label": "Telegram Stars", "amount": STAR_PRICE}])
        }
        
        await bot.request(method="sendInvoice", data=invoice_data)
        logger.info(f"Invoice sent to user {user_id}")
        
    except TelegramAPIError as e:
        logger.error(f"Telegram API error in start command: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
    except Exception as e:
        logger.error(f"Unexpected error in start command: {e}")
        await message.answer("❌ Kutilmagan xatolik yuz berdi.")


@dp.message_handler(commands=['status'])
async def cmd_status(message: types.Message):
    """Check premium subscription status"""
    try:
        user_id = message.from_user.id
        
        if payment_manager.check_premium_status(user_id):
            expiry_date = payment_manager.get_expiry_date(user_id)
            remaining_time = expiry_date - datetime.now()
            hours_remaining = int(remaining_time.total_seconds() // 3600)
            
            status_text = (
                "✅ <b>Premium obuna faol!</b>\n\n"
                f"⏰ Tugash vaqti: <code>{expiry_date.strftime('%Y-%m-%d %H:%M')}</code>\n"
                f"⏳ Qolgan vaqt: <b>{hours_remaining} soat</b>\n"
                "💎 Barcha premium funksiyalar mavjud!"
            )
        else:
            status_text = (
                "❌ <b>Premium obuna mavjud emas</b>\n\n"
                "Premium obuna olish uchun /start buyrug'ini yuboring.\n"
                "💰 Narx: 10 Telegram Stars\n"
                "⏱ Muddat: 1 kun"
            )
            
        await message.answer(status_text)
        
    except Exception as e:
        logger.error(f"Error in status command: {e}")
        await message.answer("❌ Status tekshirishda xatolik yuz berdi.")


@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    """Show help information"""
    help_text = (
        "🤖 <b>Bot buyruqlari:</b>\n\n"
        "/start - Premium obuna sotib olish\n"
        "/status - Obuna holatini tekshirish\n"
        "/help - Yordam ma'lumotlari\n\n"
        "💡 <b>Premium imkoniyatlar:</b>\n"
        "• Cheksiz so'rovlar\n"
        "• Tezkor javob olish\n"
        "• Maxsus funksiyalar\n\n"
        "💰 Narx: 10 Telegram Stars (1 kun)"
    )
    await message.answer(help_text)


@dp.callback_query_handler(lambda c: c.data in ['premium_info', 'user_stats'])
async def process_callback(callback_query: types.CallbackQuery):
    """Handle inline keyboard callbacks"""
    try:
        await bot.answer_callback_query(callback_query.id)
        
        if callback_query.data == 'premium_info':
            info_text = (
                "💎 <b>Premium obuna haqida:</b>\n\n"
                "✅ Cheksiz so'rovlar\n"
                "✅ Tezkor javob berish\n"
                "✅ Maxsus funksiyalar\n"
                "✅ Reklama yo'q\n"
                "✅ Prioritet qo'llab-quvvatlash\n\n"
                "💰 Narx: 10 Telegram Stars\n"
                "⏱ Muddat: 1 kun"
            )
            await bot.send_message(callback_query.from_user.id, info_text)
            
        elif callback_query.data == 'user_stats':
            user_id = callback_query.from_user.id
            is_premium = payment_manager.check_premium_status(user_id)
            
            stats_text = (
                "📊 <b>Sizning statistikangiz:</b>\n\n"
                f"👤 User ID: <code>{user_id}</code>\n"
                f"💎 Premium: {'✅ Faol' if is_premium else '❌ Faol emas'}\n"
                f"📅 Qo'shilgan sana: Bugun\n"
            )
            
            if is_premium:
                expiry_date = payment_manager.get_expiry_date(user_id)
                stats_text += f"⏰ Premium tugashi: <code>{expiry_date.strftime('%Y-%m-%d %H:%M')}</code>\n"
                
            await bot.send_message(callback_query.from_user.id, stats_text)
            
    except Exception as e:
        logger.error(f"Error in callback handler: {e}")


@dp.pre_checkout_query_handler(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    """
    Handle pre-checkout queries with comprehensive validation
    """
    try:
        query_id = pre_checkout_query.id
        amount = pre_checkout_query.total_amount
        currency = pre_checkout_query.currency
        payload = pre_checkout_query.invoice_payload
        user_id = pre_checkout_query.from_user.id
        
        logger.info(
            f"Pre-checkout query from user {user_id}: "
            f"Amount={amount}, Currency={currency}, Payload={payload}"
        )
        
        # Comprehensive validation
        validation_checks = [
            currency == "XTR",
            MIN_PAYMENT <= amount <= MAX_PAYMENT,
            payload.startswith("premium_subscription_"),
            str(user_id) in payload
        ]
        
        if all(validation_checks):
            await bot.answer_pre_checkout_query(
                pre_checkout_query_id=query_id,
                ok=True
            )
            logger.info(f"Pre-checkout approved for user {user_id}")
        else:
            error_message = "Noto'g'ri to'lov parametrlari. Iltimos, qayta urinib ko'ring."
            await bot.answer_pre_checkout_query(
                pre_checkout_query_id=query_id,
                ok=False,
                error_message=error_message
            )
            logger.warning(f"Pre-checkout rejected for user {user_id}: Validation failed")
            
    except TelegramAPIError as e:
        logger.error(f"Telegram API error in pre-checkout: {e}")
        await bot.answer_pre_checkout_query(
            pre_checkout_query_id=pre_checkout_query.id,
            ok=False,
            error_message="Texnik xatolik yuz berdi. Qayta urinib ko'ring."
        )
    except Exception as e:
        logger.error(f"Unexpected error in pre-checkout: {e}")
        await bot.answer_pre_checkout_query(
            pre_checkout_query_id=pre_checkout_query.id,
            ok=False,
            error_message="Kutilmagan xatolik yuz berdi."
        )


@dp.message_handler(content_types=types.ContentTypes.SUCCESSFUL_PAYMENT, state='*')
async def successful_payment_handler(message: types.Message):
    """
    Handle successful payments with detailed processing
    """
    try:
        payment = message.successful_payment
        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        
        logger.info(
            f"Successful payment from user {user_id} (@{username}): "
            f"{payment.total_amount} {payment.currency}, "
            f"Provider: {payment.provider_payment_charge_id}"
        )
        
        # Validate payment details
        if (payment.currency == "XTR" and 
            MIN_PAYMENT <= payment.total_amount <= MAX_PAYMENT):
            
            # Record payment
            payment_manager.record_payment(
                payment.provider_payment_charge_id,
                user_id,
                payment.total_amount,
                payment.currency
            )
            
            # Activate premium subscription
            expiry_date = payment_manager.activate_premium(user_id, PREMIUM_DURATION_DAYS)
            
            # Create success message with all details
            success_message = (
                "🎉 <b>Tabriklaymiz! To'lov muvaffaqiyatli amalga oshirildi!</b>\n\n"
                "💎 <b>Premium obuna faollashtirildi!</b>\n\n"
                f"📋 To'lov ID: <code>{payment.provider_payment_charge_id}</code>\n"
                f"💰 To'langan summa: <b>{payment.total_amount} {payment.currency}</b>\n"
                f"📅 Faollashtirish sanasi: <code>{datetime.now().strftime('%Y-%m-%d %H:%M')}</code>\n"
                f"⏰ Tugash vaqti: <code>{expiry_date.strftime('%Y-%m-%d %H:%M')}</code>\n\n"
                "✨ <b>Endi siz barcha premium funksiyalardan foydalanishingiz mumkin!</b>\n\n"
                "📱 Status tekshirish uchun: /status\n"
                "❓ Yordam uchun: /help"
            )
            
            # Create inline keyboard for quick actions
            keyboard = InlineKeyboardMarkup(row_width=2)
            keyboard.add(
                InlineKeyboardButton("📊 Statistika", callback_data="user_stats"),
                InlineKeyboardButton("💎 Premium info", callback_data="premium_info")
            )
            
            await message.answer(success_message, reply_markup=keyboard)
            
        else:
            # Handle invalid payment
            error_message = (
                "❌ <b>To'lov parametrlarida xatolik!</b>\n\n"
                "To'lov qabul qilinmadi. Iltimos, qo'llab-quvvatlash "
                "xizmati bilan bog'laning.\n\n"
                f"💰 Qabul qilingan: {payment.total_amount} {payment.currency}\n"
                f"📋 To'lov ID: <code>{payment.provider_payment_charge_id}</code>"
            )
            await message.answer(error_message)
            logger.warning(f"Invalid payment from user {user_id}: {payment.total_amount} {payment.currency}")
            
    except Exception as e:
        logger.error(f"Error processing successful payment: {e}")
        await message.answer(
            "❌ <b>To'lovni qayta ishlashda xatolik yuz berdi!</b>\n\n"
            "Iltimos, qo'llab-quvvatlash xizmati bilan bog'laning.\n"
            "Sizning to'lovingiz xavfsiz va qayta ishlanadi."
        )


def setup_bot():
    """Setup bot with error handling"""
    try:
        logger.info("Setting up Telegram bot...")
        
        # Add middleware for error handling
        @dp.errors_handler()
        async def errors_handler(update, exception):
            logger.error(f"Update {update} caused error {exception}")
            return True
            
        logger.info("Bot setup completed successfully")
        return True
    except Exception as e:
        logger.error(f"Bot setup failed: {e}")
        return False


if __name__ == '__main__':
    try:
        if setup_bot():
            logger.info("Starting Aiogram 2.x Payment Bot...")
            executor.start_polling(
                dp, 
                skip_updates=True,
                on_startup=lambda dp: logger.info("Bot started successfully!"),
                on_shutdown=lambda dp: logger.info("Bot stopped")
            )
        else:
            logger.error("Bot setup failed, exiting...")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")
        sys.exit(1)