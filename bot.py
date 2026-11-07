import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# بيانات البوت والمشرف
BOT_TOKEN = "8953729199:AAGHjlB8FQiwb3KCiKWts9tqdT0CgAFQY5Y"
ADMIN_ID = 8932516552
SHAMCASH_ACCOUNT = "0947345832"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

SELECTING_PACKAGE, ENTERING_UID, SENDING_RECEIPT = range(3)

# قائمة المنتجات والباقات المتاحة
PRODUCTS = {
    "codm": {
        "name": "كول أوف ديوتي موبايل",
        "packages": {
            "cp_80": {"name": "80 CP", "price": "16,000 ل.س", "api_code": "COD_80"},
            "cp_420": {"name": "420 CP", "price": "70,000 ل.س", "api_code": "COD_420"},
            "cp_880": {"name": "880 CP", "price": "138,000 ل.س", "api_code": "COD_880"}
        }
    },
    "freefire": {
        "name": "فري فاير",
        "packages": {
            "ff_110": {"name": "110 جوهرة", "price": "15,000 ل.س", "api_code": "FF_110"},
            "ff_572": {"name": "572 جوهرة", "price": "70,000 ل.س", "api_code": "FF_572"},
            "ff_pass": {"name": "عضوية أسبوعية", "price": "32,000 ل.س", "api_code": "FF_WEEK"}
        }
    },
    "pubg": {
        "name": "ببجي موبايل",
        "packages": {
            "pubg_60": {"name": "60 UC", "price": "14,000 ل.س", "api_code": "PUBG_60"},
            "pubg_325": {"name": "325 UC", "price": "67,000 ل.س", "api_code": "PUBG_325"}
        }
    }
}

pending_orders = {}

def fulfill_order_via_api(game_code, player_uid, api_code):
    """دالة الربط مع مزود الـ API الخارجي"""
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔫 كول أوف ديوتي", callback_data="prod_codm")],
        [InlineKeyboardButton("🔥 فري فاير", callback_data="prod_freefire")],
        [InlineKeyboardButton("🪖 ببجي موبايل", callback_data="prod_pubg")],
        [InlineKeyboardButton("💬 الدعم الفني", url="https://wa.me/963947345832")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "👋 *أهلاً بك في متجر T_B STORE الرسمي*\n\n"
        "⚡ خدمة شحن تلقائي وفوري بالـ ID عبر شام كاش.\n"
        "اختر اللعبة أو الخدمة التي تريد شحنها للبدء:"
    )
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.callback_query.message.edit_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    return SELECTING_PACKAGE

async def select_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    prod_id = query.data.replace("prod_", "")
    context.user_data["current_prod"] = prod_id
    prod = PRODUCTS[prod_id]

    keyboard = []
    for pkg_id, pkg_info in prod["packages"].items():
        keyboard.append([InlineKeyboardButton(f"{pkg_info['name']} - {pkg_info['price']}", callback_data=f"pkg_{pkg_id}")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_main")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(f"🎮 *{prod['name']}*\n\nاختر الباقة المطلوبة:", reply_markup=reply_markup, parse_mode="Markdown")
    return SELECTING_PACKAGE

async def select_package(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    pkg_id = query.data.replace("pkg_", "")
    context.user_data["current_pkg"] = pkg_id

    await query.message.edit_text(
        "🆔 *أرسل الآن معرف حسابك (Player ID / UID):*\n\n"
        "⚠️ يرجى التأكد من كتابة الرقم بشكل صحيح لتجنب أي خطأ في الشحن.",
        parse_mode="Markdown"
    )
    return ENTERING_UID

async def receive_uid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    context.user_data["player_uid"] = uid

    prod = PRODUCTS[context.user_data["current_prod"]]
    pkg = prod["packages"][context.user_data["current_pkg"]]

    payment_instructions = (
        f"✅ *تم حفظ البيانات:* \n"
        f"• الخدمة: {prod['name']}\n"
        f"• الباقة: {pkg['name']}\n"
        f"• الآيدي: `{uid}`\n"
        f"• المبلغ المطلوب: *{pkg['price']}*\n\n"
        f"💳 *طريقة الدفع:*\n"
        f"قم بتحويل المبلغ إلى حساب شام كاش:\n"
        f"`{SHAMCASH_ACCOUNT}` (اضغط على الرقم لنسخه)\n\n"
        f"📸 *أرسل الآن صورة إشعار التحويل لتأكيد الشحن فوراً.*"
    )

    await update.message.reply_text(payment_instructions, parse_mode="Markdown")
    return SENDING_RECEIPT

async def receive_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("⚠️ يرجى إرسال صورة إشعار التحويل من تطبيق شام كاش.")
        return SENDING_RECEIPT

    photo_file_id = update.message.photo[-1].file_id
    user = update.message.from_user
    order_id = f"TB{update.message.message_id}"

    prod = PRODUCTS[context.user_data["current_prod"]]
    pkg = prod["packages"][context.user_data["current_pkg"]]
    uid = context.user_data["player_uid"]

    pending_orders[order_id] = {
        "chat_id": update.message.chat_id,
        "prod_id": context.user_data["current_prod"],
        "pkg_id": context.user_data["current_pkg"],
        "api_code": pkg["api_code"],
        "uid": uid,
        "name": prod["name"],
        "pkg_name": pkg["name"]
    }

    await update.message.reply_text(
        "⏳ *تم استلام طلبك وإشعار الدفع بنجاح!*\n"
        "جاري التحقق وتنفيذ الشحن تلقائياً، ستصلك رسالة فور اكتمال العملية.",
        parse_mode="Markdown"
    )

    admin_keyboard = [
        [
            InlineKeyboardButton("🚀 تنفيذ فوري (API)", callback_data=f"approve_{order_id}"),
            InlineKeyboardButton("❌ رفض", callback_data=f"reject_{order_id}")
        ]
    ]
    admin_markup = InlineKeyboardMarkup(admin_keyboard)

    caption = (
        f"🔔 *طلب شحن جديد وارد:* `{order_id}`\n\n"
        f"👤 المستخدم: @{user.username or 'بدون معرف'} ({user.first_name})\n"
        f"🎮 الخدمة: {prod['name']}\n"
        f"📦 الباقة: {pkg['name']} ({pkg['price']})\n"
        f"🆔 الآيدي (UID): `{uid}`"
    )

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo_file_id,
        caption=caption,
        reply_markup=admin_markup,
        parse_mode="Markdown"
    )

    return ConversationHandler.END

async def admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    action, order_id = data.split("_", 1)
    order = pending_orders.get(order_id)

    if not order:
        await query.edit_message_caption(caption="⚠️ هذا الطلب تم اتخاذ إجراء عليه مسبقاً أو انتهت جلسته.")
        return

    if action == "approve":
        success = fulfill_order_via_api(order["prod_id"], order["uid"], order["api_code"])
        
        if success:
            await query.edit_message_caption(caption=query.message.caption + "\n\n✅ *تم التنفيذ والشحن عبر الـ API بنجاح!*", parse_mode="Markdown")
            await context.bot.send_message(
                chat_id=order["chat_id"],
                text=(
                    f"🎉 *مبروك! تم شحن حسابك بنجاح!*\n\n"
                    f"🎮 الخدمة: {order['name']}\n"
                    f"📦 الباقة: {order['pkg_name']}\n"
                    f"🆔 الآيدي: `{order['uid']}`\n\n"
                    f"شكراً لتعاملك مع *T_B STORE* ❤️"
                ),
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_caption(caption=query.message.caption + "\n\n⚠️ *فشل الاتصال بمزود الـ API.*", parse_mode="Markdown")

    elif action == "reject":
        await query.edit_message_caption(caption=query.message.caption + "\n\n❌ *تم رفض الطلب.*", parse_mode="Markdown")
        await context.bot.send_message(
            chat_id=order["chat_id"],
            text="❌ *عذراً، تم إلغاء طلبك.*\nالسبب: لم يتم العثور على الإشعار في شام كاش أو بيانات الدفع غير صحيحة.",
            parse_mode="Markdown"
        )

    pending_orders.pop(order_id, None)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم إلغاء العملية.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_PACKAGE: [
                CallbackQueryHandler(select_product, pattern="^prod_"),
                CallbackQueryHandler(select_package, pattern="^pkg_"),
                CallbackQueryHandler(start, pattern="^back_main$"),
            ],
            ENTERING_UID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_uid)
            ],
            SENDING_RECEIPT: [
                MessageHandler(filters.PHOTO, receive_receipt)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(admin_decision, pattern="^(approve|reject)_"))

    print("🤖 بوت T_B STORE يعمل الآن بنجاح...")
    app.run_polling()

if __name__ == "__main__":
    main()
