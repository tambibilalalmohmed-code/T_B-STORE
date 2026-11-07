import os
import asyncio
import logging
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# التوكن الجديد الخاص بالبوت
TOKEN = "8953729199:AAGMwhzt5XQS-y6tko8EUoO71l8nZR84PHE"

# بيانات الدعم الفني
SUPPORT_WHATSAPP = "https://wa.me/963947345832"
SUPPORT_TELEGRAM = "https://t.me/T_B_STORRE"

# قائمة الألعاب والفئات بالدولار
GAMES_DATA = {
    "pubg": {
        "title": "🔫 ببجي موبايل (PUBG Mobile)",
        "packages": [
            ("60 UC", "$0.99"),
            ("325 UC", "$4.99"),
            ("660 UC", "$9.49"),
            ("1800 UC", "$23.99"),
            ("3850 UC", "$48.50"),
            ("8100 UC", "$96.99")
        ]
    },
    "freefire": {
        "title": "🔥 فري فاير (Free Fire)",
        "packages": [
            ("100 + 10 جوهرة", "$0.99"),
            ("210 + 21 جوهرة", "$1.99"),
            ("530 + 53 جوهرة", "$4.85"),
            ("1080 + 108 جوهرة", "$9.50"),
            ("2200 + 220 جوهرة", "$18.99"),
            ("عضوية أسبوعية (Weekly)", "$1.99"),
            ("عضوية شهرية (Monthly)", "$9.99")
        ]
    }
}

# دالة القائمة الرئيسية
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔫 ببجي موبايل (PUBG)", callback_data="game_pubg")],
        [InlineKeyboardButton("🔥 فري فاير (Free Fire)", callback_data="game_freefire")],
        [InlineKeyboardButton("💬 الدعم الفني والخدمات الأخرى", callback_data="support_info")]
    ]
    return InlineKeyboardMarkup(keyboard)

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    welcome_text = (
        "👋 **أهلاً بك في متجر T_B STORE الرسمي 🎮⚡**\n\n"
        "متجرك الأول لشحن الألعاب والخدمات الرقمية بأفضل الأسعار وأسرع تنفيذ.\n\n"
        "🔹 اختر اللعبة التي تريد شحنها من القائمة بالأسفل:"
    )
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.edit_text(welcome_text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

# التعامل مع الأزرار
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "main_menu":
        await start(update, context)

    elif data.startswith("game_"):
        game_key = data.replace("game_", "")
        context.user_data["selected_game"] = game_key
        game_info = GAMES_DATA[game_key]

        await query.message.edit_text(
            f"اخترت: **{game_info['title']}**\n\n"
            "يرجى إرسال **الآيدي (Player ID)** الخاص بحسابك لإكمال الطلب:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="main_menu")]])
        )

    elif data.startswith("pkg_"):
        pkg_index = int(data.replace("pkg_", ""))
        game_key = context.user_data.get("selected_game")
        player_id = context.user_data.get("player_id", "غير محدد")
        game_info = GAMES_DATA[game_key]
        pkg_name, pkg_price = game_info["packages"][pkg_index]

        order_summary = (
            "🧾 **تفاصيل الطلب:**\n"
            f"🔹 الخدمة: {game_info['title']}\n"
            f"🔹 الباقة: {pkg_name}\n"
            f"💵 السعر: {pkg_price}\n"
            f"🆔 الآيدي: `{player_id}`\n\n"
            "لتأكيد الطلب والدفع، يرجى التواصل مع الدعم الفني فوراً عبر الأزرار أدناه:"
        )

        support_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 واتساب (WhatsApp)", url=SUPPORT_WHATSAPP)],
            [InlineKeyboardButton("✈️ تيليجرام الدعم", url=SUPPORT_TELEGRAM)],
            [InlineKeyboardButton("🔙 اختيار باقة أخرى", callback_data=f"game_{game_key}")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ])

        await query.message.edit_text(order_summary, reply_markup=support_markup, parse_mode="Markdown")

    elif data == "support_info":
        support_text = (
            "🛠️ **قسم الدعم الفني والخدمات الأخرى**\n\n"
            "لشحن التطبيقات، الاشتراكات الرقمية، أو الاستفسار وتأكيد الدفع، تواصل معنا مباشرة:"
        )
        support_buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 واتساب (WhatsApp)", url=SUPPORT_WHATSAPP)],
            [InlineKeyboardButton("✈️ تيليجرام الدعم", url=SUPPORT_TELEGRAM)],
            [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")]
        ])
        await query.message.edit_text(support_text, reply_markup=support_buttons, parse_mode="Markdown")

# استقبال الآيدي من المستخدم
async def handle_user_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game_key = context.user_data.get("selected_game")

    if game_key and game_key in GAMES_DATA:
        player_id = update.message.text.strip()
        context.user_data["player_id"] = player_id
        game_info = GAMES_DATA[game_key]

        buttons = []
        for idx, (pkg_name, price) in enumerate(game_info["packages"]):
            buttons.append([InlineKeyboardButton(f"{pkg_name} — {price}", callback_data=f"pkg_{idx}")])

        buttons.append([InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")])

        await update.message.reply_text(
            f"✅ تم حفظ الآيدي: `{player_id}`\n\n"
            f"اختر الفئة المطلوبة لـ **{game_info['title']}**:",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="Markdown"
        )
    else:
        await start(update, context)

# صفحة ويب وهمية لإبقاء سيرفر Render شغالاً 24 ساعة
async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 تم تشغيل خادم الويب على المنفذ {port}")

async def main():
    tg_app = ApplicationBuilder().token(TOKEN).build()

    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(CallbackQueryHandler(handle_buttons))
    tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_text))

    await start_web_server()

    print("🤖 بوت T_B STORE يعمل الآن بنجاح...")
    await tg_app.initialize()
    await tg_app.start()
    await tg_app.updater.start_polling()

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
