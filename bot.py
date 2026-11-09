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

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8953729199:AAGMwhzt5XQS-y6tko8EUoO71l8nZR84PHE"

# روابط الدعم المباشر
SUPPORT_WHATSAPP = "https://wa.me/963947345832"
SUPPORT_TELEGRAM = "https://t.me/T_B_STORRE"

# بيانات الألعاب والباقات
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

# لوحة المفاتيح الرئيسية (نفس تصميم MHD Store)
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🛍️ تصفح المتجر", callback_data="nav_browse")],
        [
            InlineKeyboardButton("➕ شحن الرصيد", callback_data="nav_deposit"),
            InlineKeyboardButton("👤 حسابي", callback_data="nav_profile")
        ],
        [
            InlineKeyboardButton("📦 طلباتي", callback_data="nav_orders"),
            InlineKeyboardButton("🔍 بحث", callback_data="nav_search")
        ],
        [InlineKeyboardButton("💬 الدعم الفني", callback_data="nav_support")]
    ]
    return InlineKeyboardMarkup(keyboard)

# قائمة أقسام المتجر
def store_categories_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("الأرقام", callback_data="cat_numbers"),
            InlineKeyboardButton("مزودات الانترنت", callback_data="cat_isp")
        ],
        [
            InlineKeyboardButton("الألعاب", callback_data="cat_games"),
            InlineKeyboardButton("تطبيقات الدردشة", callback_data="cat_chat")
        ],
        [
            InlineKeyboardButton("البطاقات", callback_data="cat_cards"),
            InlineKeyboardButton("الرصيد والعملات", callback_data="cat_currencies")
        ],
        [
            InlineKeyboardButton("برامج الكمبيوتر", callback_data="cat_pc"),
            InlineKeyboardButton("اشتراكات وسوشال ميديا", callback_data="cat_subs")
        ],
        [
            InlineKeyboardButton("📦 طلباتي", callback_data="nav_orders"),
            InlineKeyboardButton("🔍 بحث", callback_data="nav_search")
        ],
        [InlineKeyboardButton("🏠 الرئيسية", callback_data="nav_home")]
    ]
    return InlineKeyboardMarkup(keyboard)

# قائمة الألعاب
def games_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔫 ببجي موبايل (PUBG)", callback_data="game_pubg")],
        [InlineKeyboardButton("🔥 فري فاير (Free Fire)", callback_data="game_freefire")],
        [InlineKeyboardButton("🔙 رجوع لأقسام المتجر", callback_data="nav_browse")],
        [InlineKeyboardButton("🏠 الرئيسية", callback_data="nav_home")]
    ]
    return InlineKeyboardMarkup(keyboard)

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name if update.effective_user else "صديقنا"
    welcome_text = (
        f"أهلاً {user_name} 👋\n\n"
        "كل خدماتك بمكان واحد في **T_B STORE**.\n"
        "الأسعار تتحدّث مباشرة وقت اختيار المنتج.\n\n"
        "👇 اختر من القائمة"
    )
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.edit_text(welcome_text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

# معالجة الضغط على الأزرار
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # الرئيسية
    if data == "nav_home":
        await start(update, context)

    # تصفح المتجر
    elif data == "nav_browse":
        text = "المتجر 🛍️\nاختر القسم، أو استخدم البحث للوصول للمنتج أسرع."
        await query.message.edit_text(text, reply_markup=store_categories_keyboard())

    # قسم الألعاب
    elif data == "cat_games":
        await query.message.edit_text(
            "🎮 قسم الألعاب:\nاختر اللعبة المطلوبة لعرض الفئات والأسعار بالدولار:",
            reply_markup=games_menu_keyboard()
        )

    # اختيار لعبة محددة
    elif data.startswith("game_"):
        game_key = data.replace("game_", "")
        context.user_data["selected_game"] = game_key
        game_info = GAMES_DATA[game_key]

        await query.message.edit_text(
            f"اخترت: {game_info['title']}\n\n"
            "يرجى إرسال **الآيدي (Player ID)** الخاص بحسابك في رسالة لإكمال الطلب:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع للألعاب", callback_data="cat_games")]])
        )

    # تفاصيل باقة محددة
    elif data.startswith("pkg_"):
        pkg_index = int(data.replace("pkg_", ""))
        game_key = context.user_data.get("selected_game")
        player_id = context.user_data.get("player_id", "غير محدد")
        game_info = GAMES_DATA[game_key]
        pkg_name, pkg_price = game_info["packages"][pkg_index]

        order_summary = (
            "🧾 تفاصيل الطلب:\n"
            f"🔹 القسم: {game_info['title']}\n"
            f"🔹 الفئة: {pkg_name}\n"
            f"💵 السعر: {pkg_price}\n"
            f"🆔 الآيدي: {player_id}\n\n"
            "لتأكيد الطلب والدفع، يرجى التواصل مع الدعم الفني فوراً:"
        )

        support_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 واتساب الدعم", url=SUPPORT_WHATSAPP)],
            [InlineKeyboardButton("✈️ تيليجرام الدعم", url=SUPPORT_TELEGRAM)],
            [InlineKeyboardButton("🔙 اختيار باقة أخرى", callback_data=f"game_{game_key}")],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="nav_home")]
        ])
        await query.message.edit_text(order_summary, reply_markup=support_markup)

    # شحن الرصيد
    elif data == "nav_deposit":
        deposit_text = (
            "➕ **شحن الرصيد:**\n\n"
            "طرق التعبئة المتوفرة حالياً:\n"
            "• شام كاش (Sham Cash)\n"
            "• سيريتل كاش / MTN كاش\n"
            "• USDT (Crypto)\n\n"
            "لإيداع الرصيد وتفعيله بحسابك، تواصل مع المحاسب المالي مباشرة:"
        )
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 تواصل لشحن رصيدك (WhatsApp)", url=SUPPORT_WHATSAPP)],
            [InlineKeyboardButton("✈️ تيليجرام الدعم", url=SUPPORT_TELEGRAM)],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="nav_home")]
        ])
        await query.message.edit_text(deposit_text, reply_markup=markup, parse_mode="Markdown")

    # حسابي
    elif data == "nav_profile":
        user = update.effective_user
        profile_text = (
            "👤 **معلومات حسابك:**\n\n"
            f"• الاسم: {user.first_name}\n"
            f"• الآيدي: `{user.id}`\n"
            "• رصيد الحساب: **0.00 $**\n"
            "• إجمالي الطلبات: 0 طلب\n"
        )
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ شحن الرصيد الآن", callback_data="nav_deposit")],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="nav_home")]
        ])
        await query.message.edit_text(profile_text, reply_markup=markup, parse_mode="Markdown")

    # طلباتي
    elif data == "nav_orders":
        orders_text = "📦 **سجل الطلبات:**\n\nلا توجد طلبات سابقة مسجلة حالياً."
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛍️ تصفح المتجر", callback_data="nav_browse")],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="nav_home")]
        ])
        await query.message.edit_text(orders_text, reply_markup=markup, parse_mode="Markdown")

    # البحث
    elif data == "nav_search":
        search_text = "🔍 خدمة البحث السريع قيد التحديث، يرجى التصفح عبر الأقسام."
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🛍️ تصفح المتجر", callback_data="nav_browse")]])
        await query.message.edit_text(search_text, reply_markup=markup)

    # الدعم الفني
    elif data == "nav_support":
        support_text = "💬 فريق دعم **T_B STORE** بخدمتكم لأي استفسار أو مساعدة:"
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 واتساب", url=SUPPORT_WHATSAPP)],
            [InlineKeyboardButton("✈️ تيليجرام", url=SUPPORT_TELEGRAM)],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="nav_home")]
        ])
        await query.message.edit_text(support_text, reply_markup=markup, parse_mode="Markdown")

    # الأقسام الأخرى التي لا تزال قيد الإضافة
    elif data.startswith("cat_"):
        temp_text = "⏳ هذا القسم قيد التجهيز وسيتوفر قريباً بالأسعار المحدثة."
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع لأقسام المتجر", callback_data="nav_browse")]])
        await query.message.edit_text(temp_text, reply_markup=markup)

# استقبال الآيدي المكتوب
async def handle_user_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game_key = context.user_data.get("selected_game")

    if game_key and game_key in GAMES_DATA:
        player_id = update.message.text.strip()
        context.user_data["player_id"] = player_id
        game_info = GAMES_DATA[game_key]

        buttons = []
        for idx, (pkg_name, price) in enumerate(game_info["packages"]):
            buttons.append([InlineKeyboardButton(f"{pkg_name} — {price}", callback_data=f"pkg_{idx}")])

        buttons.append([InlineKeyboardButton("🔙 رجوع للألعاب", callback_data="cat_games")])
        buttons.append([InlineKeyboardButton("🏠 الرئيسية", callback_data="nav_home")])

        await update.message.reply_text(
            f"✅ تم حفظ الآيدي: `{player_id}`\n\nاختر الفئة المطلوبة لـ {game_info['title']}:",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="Markdown"
        )
    else:
        await start(update, context)

# سيرفر ويب مصغر لإبقاء منصة Render شغالاً 24/7
async def handle_ping(request):
    return web.Response(text="T_B STORE Bot is Live 24/7!")

async def start_web_server():
    server = web.Application()
    server.router.add_get('/', handle_ping)
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Server listening on port {port}")

async def main():
    tg_app = ApplicationBuilder().token(TOKEN).build()

    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(CallbackQueryHandler(handle_buttons))
    tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_text))

    await start_web_server()

    async with tg_app:
        await tg_app.start()
        await tg_app.updater.start_polling()
        print("🤖 بوت T_B STORE المطور يعمل الآن بنجاح...")
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
