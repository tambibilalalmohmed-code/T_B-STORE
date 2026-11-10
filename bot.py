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

# بيانات الأدمن الرسمية
ADMIN_ID = 8932516552
ADMIN_USERNAME = "Nob_404"
ALL_USERS = set()

SUPPORT_WHATSAPP = "https://wa.me/963947345832"
SUPPORT_TELEGRAM = f"https://t.me/{ADMIN_USERNAME}"

GAMES_DATA = {
    "pubg_global": {
        "title": "ببجي عالمي",
        "packages": [
            ("60 UC", "$1.1"),
            ("325 UC", "$5.1"),
            ("660 UC", "$9.49"),
            ("1800 UC", "$23.99"),
            ("3850 UC", "$48.50"),
            ("8100 UC", "$96.99")
        ]
    },
    "freefire": {
        "title": "فري فاير",
        "packages": [
            ("100 + 10 جوهرة", "$0.99"),
            ("210 + 21 جوهرة", "$1.99"),
            ("530 + 53 جوهرة", "$4.85"),
            ("1080 + 108 جوهرة", "$9.50"),
            ("2200 + 220 جوهرة", "$18.99")
        ]
    },
    "ff_memberships": {
        "title": "عضويات فري فاير",
        "packages": [
            ("عضوية أسبوعية (Weekly)", "$2.10"),
            ("عضوية شهرية (Monthly)", "$10.5")
        ]
    },
    "pubg_memberships": {
        "title": "عضويات ببجي",
        "packages": [
            ("برايم عادي (Prime)", "$0.99"),
            ("برايم بلس (Prime Plus)", "$9.99")
        ]
    }
}

CHAT_PAGES = [
    [
        ("yabi chat", "app_yabi"), ("ooyuni chat", "app_ooyuni"),
        ("ZAFAA LIVE", "app_zafaa"), ("habba chat", "app_habba"),
        ("POPPO LIVE", "app_poppo"), ("BIGO LIVE", "app_bigo"),
        ("YOHOO STAR", "app_yohoo"), ("IMO", "app_imo"),
        ("Mango star", "app_mango"), ("YALLA LIVE", "app_yalla")
    ],
    [
        ("YOPARTY", "app_yoparty"), ("BOLI", "app_boli"),
        ("Zarr chat", "app_zarr"), ("INFUN", "app_infun"),
        ("HOPI STAR", "app_hopi"), ("MEYO LIVE", "app_meyo"),
        ("YOPPO CHAT", "app_yoppo"), ("OUR TALK", "app_ourtalk"),
        ("HAPI عربي", "app_hapi"), ("WADI CHAT", "app_wadi")
    ],
    [
        ("SUPERMEET", "app_supermeet"), ("UME", "app_ume"),
        ("DIKA LIVE", "app_dika"), ("YAYYA CHAT", "app_yayya"),
        ("KARAK CHAT", "app_karak"), ("MIXU", "app_mixu"),
        ("VONE", "app_vone"), ("OHLA", "app_ohla"),
        ("NIU chat", "app_niu"), ("SHABAB", "app_shabab")
    ],
    [
        ("BAAT LIVE", "app_baat"), ("LAKA CHAT", "app_laka"),
        ("CRUSH LIVE", "app_crush"), ("BEST LIVE", "app_best"),
        ("TAKA LIVE", "app_taka"), ("WINKO", "app_winko"),
        ("YOHO WAKA", "app_yoho_waka"), ("SOUL CHILL", "app_soulchill"),
        ("YOOY CHAT", "app_yooy"), ("YOYO CHAT", "app_yoyo")
    ],
    [
        ("TADA CHAT", "app_tada"), ("HONEY JAR", "app_honey"),
        ("PARTY STAR", "app_partystar"), ("4FUN CHAT", "app_4fun"),
        ("POTA LIVE", "app_pota"), ("SOMATCH", "app_somatch"),
        ("YAAHLAN CHAT", "app_yaahlan"), ("TAMI CHAT", "app_tami"),
        ("KIYO LIVE", "app_kiyo"), ("WAHO CHAT", "app_waho")
    ],
    [
        ("OLAMET", "app_olamet"), ("TANGO LIVE", "app_tango"),
        ("SUGO CHAT", "app_sugo"), ("PIKA CHAT", "app_pika"),
        ("LIKEE", "app_likee"), ("SOUL STAR", "app_soulstar"),
        ("LAYLA", "app_layla"), ("WYAK CHAT", "app_wyak"),
        ("TALK TALK", "app_talktalk"), ("SUPER LIVE", "app_superlive")
    ],
    [
        ("HAKI CHAT", "app_haki"), ("DITTO LIVE", "app_ditto"),
        ("BOBO CHAT", "app_bobo"), ("FANCY", "app_fancy"),
        ("BINMO CHAT", "app_binmo"), ("LIGHT CHAT", "app_light"),
        ("MICO CHAT", "app_mico"), ("AHLAN CHAT", "app_ahlan"),
        ("COCCO LIVE", "app_cocco"), ("AZAL LIVE", "app_azal")
    ],
    [
        ("AYOME CHAT", "app_ayome"), ("JUNKO", "app_junko"),
        ("MIGO LIVE", "app_migo"), ("OOHLA CHAT", "app_oohla"),
        ("MAR7BA CHAT", "app_mar7ba"), ("STAR MAKER", "app_starmaker"),
        ("LITCHAT", "app_litchat"), ("SKY", "app_sky"),
        ("HAYA CHAT", "app_haya"), ("HABBY CHAT", "app_habby")
    ],
    [
        ("GOLD CHAT", "app_gold"), ("ARIA CHAT", "app_aria"),
        ("HAWA CHAT", "app_hawa"), ("BELLA CHAT", "app_bella"),
        ("NABD LIVE", "app_nabd"), ("DIMO CHAT", "app_dimo"),
        ("YOBI CHAT", "app_yobi"), ("GIMME LIVE", "app_gimme"),
        ("WEGO", "app_wego"), ("YIGO CHAT", "app_yigo")
    ]
]

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
        [InlineKeyboardButton("💬 الدعم", callback_data="nav_support")]
    ]
    return InlineKeyboardMarkup(keyboard)

def store_categories_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🎮 الألعاب", callback_data="cat_games"),
            InlineKeyboardButton("💬 تطبيقات الدردشة", callback_data="chat_page_0")
        ],
        [
            InlineKeyboardButton("📦 طلباتي", callback_data="nav_orders"),
            InlineKeyboardButton("🔍 بحث", callback_data="nav_search")
        ],
        [InlineKeyboardButton("🏠 الرئيسية", callback_data="nav_home")]
    ]
    return InlineKeyboardMarkup(keyboard)

def games_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("فري فاير", callback_data="game_freefire"), InlineKeyboardButton("ببجي عالمي", callback_data="game_pubg_global")],
        [InlineKeyboardButton("عضويات فري فاير", callback_data="game_ff_memberships"), InlineKeyboardButton("جواكر", callback_data="sub_jawaker")],
        [InlineKeyboardButton("فري فاير أكواد", callback_data="sub_ff_codes"), InlineKeyboardButton("Lords mobile", callback_data="sub_lords")],
        [InlineKeyboardButton("ببجي أكواد", callback_data="sub_pubg_codes"), InlineKeyboardButton("عضويات ببجي", callback_data="game_pubg_memberships")],
        [InlineKeyboardButton("Brawl star", callback_data="sub_brawl"), InlineKeyboardButton("8BALL POOL", callback_data="sub_8ball")],
        [InlineKeyboardButton("🔙 رجوع للأقسام", callback_data="nav_browse")]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_chat_keyboard(page_index: int):
    items = CHAT_PAGES[page_index]
    keyboard = []
    for i in range(0, len(items), 2):
        if i + 1 < len(items):
            keyboard.append([
                InlineKeyboardButton(items[i][0], callback_data=items[i][1]),
                InlineKeyboardButton(items[i+1][0], callback_data=items[i+1][1])
            ])
        else:
            keyboard.append([InlineKeyboardButton(items[i][0], callback_data=items[i][1])])

    nav_buttons = []
    if page_index > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ السابق", callback_data=f"chat_page_{page_index - 1}"))
    if page_index < len(CHAT_PAGES) - 1:
        nav_buttons.append(InlineKeyboardButton("التالي ▶️", callback_data=f"chat_page_{page_index + 1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append([InlineKeyboardButton("🔙 رجوع للأقسام", callback_data="nav_browse")])
    return InlineKeyboardMarkup(keyboard)

def register_user(user):
    if user:
        ALL_USERS.add(user.id)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user)

    welcome_text = (
        f"أهلاً {user.first_name if user else 'صديقنا'} 👋\n\n"
        "كل خدماتك بمكان واحد.\n"
        "الأسعار تتحدّث مباشرة وقت اختيار المنتج.\n\n"
        "اختر من القائمة 👇"
    )
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard())
    elif update.callback_query:
        await update.callback_query.message.edit_text(welcome_text, reply_markup=main_menu_keyboard())

# أمر لوحة التحكم
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user)
    if user and user.id == ADMIN_ID:
        admin_text = (
            "👑 أهلاً بك في لوحة تحكم الإدارة (T_B STORE)\n\n"
            f"👥 عدد المستخدمين الإجمالي: {len(ALL_USERS)}\n"
            f"🆔 معرف الأدمن: {user.id}\n\n"
            "📢 للإذاعة لجميع المستخدمين، اكتب:\n"
            "/broadcast نص الرسالة هنا"
        )
        await update.message.reply_text(admin_text)
    else:
        await update.message.reply_text("عذراً، هذا الأمر مخصص لإدارة المتجر فقط.")

# أمر الإذاعة العامة
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user)
    if not (user and user.id == ADMIN_ID):
        return

    msg_to_send = " ".join(context.args)
    if not msg_to_send:
        await update.message.reply_text("❌ يرجى كتابة نص الرسالة بعد الأمر.\nمثال:\n/broadcast عروض جديدة متوفرة الآن!")
        return

    success = 0
    for uid in ALL_USERS:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 تنبيه من إدارة المتجر:\n\n{msg_to_send}")
            success += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass

    await update.message.reply_text(f"✅ تم إرسال الإذاعة بنجاح إلى {success} مستخدم.")

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    register_user(update.effective_user)

    if data == "nav_home":
        await start(update, context)

    elif data == "nav_browse":
        await query.message.edit_text(
            "المتجر 🛍️\nاختر القسم، أو استخدم البحث للوصول للمنتج أسرع.",
            reply_markup=store_categories_keyboard()
        )

    elif data == "cat_games":
        await query.message.edit_text("📁 الالعاب\n\nاختر الخدمة:", reply_markup=games_menu_keyboard())

    elif data.startswith("chat_page_"):
        page_idx = int(data.replace("chat_page_", ""))
        await query.message.edit_text("📁 تطبيقات الدردشة\n\nاختر الخدمة:", reply_markup=build_chat_keyboard(page_idx))

    elif data.startswith("game_"):
        game_key = data.replace("game_", "")
        context.user_data["selected_game"] = game_key
        game_info = GAMES_DATA.get(game_key)

        if game_info:
            await query.message.edit_text(
                f"اخترت: {game_info['title']}\n\nيرجى إرسال الآيدي (Player ID) الخاص بحسابك في رسالة:",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع للألعاب", callback_data="cat_games")]])
            )
        else:
            await query.message.edit_text(
                "يرجى التواصل مع الدعم لتحديد الباقة والطلب:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💬 واتساب", url=SUPPORT_WHATSAPP)],
                    [InlineKeyboardButton(f"✈️ تيليجرام (@{ADMIN_USERNAME})", url=SUPPORT_TELEGRAM)],
                    [InlineKeyboardButton("🔙 رجوع للألعاب", callback_data="cat_games")]
                ])
            )

    elif data.startswith("sub_") or data.startswith("app_"):
        await query.message.edit_text(
            "⚡ هذه الخدمة متاحة للشحن الفوري عبر الدعم الفني، تواصل معنا لإتمام طلبك:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 واتساب الدعم", url=SUPPORT_WHATSAPP)],
                [InlineKeyboardButton(f"✈️ تيليجرام الدعم (@{ADMIN_USERNAME})", url=SUPPORT_TELEGRAM)],
                [InlineKeyboardButton("🔙 رجوع للأقسام", callback_data="nav_browse")]
            ])
        )

    elif data.startswith("pkg_"):
        pkg_index = int(data.replace("pkg_", ""))
        game_key = context.user_data.get("selected_game")
        player_id = context.user_data.get("player_id", "غير محدد")
        game_info = GAMES_DATA.get(game_key)
        pkg_name, pkg_price = game_info["packages"][pkg_index]
        user = update.effective_user

        order_summary = (
            "🧾 تفاصيل الطلب:\n"
            f"🔹 الخدمة: {game_info['title']}\n"
            f"🔹 الباقة: {pkg_name}\n"
            f"💵 السعر: {pkg_price}\n"
            f"🆔 الآيدي: {player_id}\n\n"
            "لتأكيد الطلب والدفع، يرجى التواصل مع الدعم الفني:"
        )

        support_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 واتساب الدعم", url=SUPPORT_WHATSAPP)],
            [InlineKeyboardButton(f"✈️ تيليجرام الدعم (@{ADMIN_USERNAME})", url=SUPPORT_TELEGRAM)],
            [InlineKeyboardButton("🔙 اختيار باقة أخرى", callback_data=f"game_{game_key}")],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="nav_home")]
        ])
        await query.message.edit_text(order_summary, reply_markup=support_markup)

        # إرسال إشعار فوري بحساب الأدمن
        try:
            alert_text = (
                "🔔 طلب شحن جديد!\n\n"
                f"👤 الزبون: {user.first_name} (@{user.username if user.username else 'لا يوجد'})\n"
                f"🆔 آيدي الزبون: {user.id}\n"
                f"🎮 الخدمة: {game_info['title']}\n"
                f"📦 الباقة: {pkg_name} ({pkg_price})\n"
                f"🎯 آيدي اللاعب: {player_id}"
            )
            await context.bot.send_message(chat_id=ADMIN_ID, text=alert_text)
        except Exception:
            pass

    elif data == "nav_deposit":
        deposit_text = (
            "➕ شحن الرصيد:\n\n"
            "طرق التعبئة المتوفرة:\n"
            "• شام كاش (Sham Cash)\n"
            "• سيريتل كاش / MTN كاش\n"
            "• USDT (Crypto)\n\n"
            "لإيداع الرصيد وتفعيله بحسابك، تواصل مع الدعم المالي مباشرة:"
        )
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 واتساب", url=SUPPORT_WHATSAPP)],
            [InlineKeyboardButton(f"✈️ تيليجرام (@{ADMIN_USERNAME})", url=SUPPORT_TELEGRAM)],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="nav_home")]
        ])
        await query.message.edit_text(deposit_text, reply_markup=markup)

    elif data == "nav_profile":
        user = update.effective_user
        profile_text = (
            "👤 معلومات حسابك:\n\n"
            f"• الاسم: {user.first_name}\n"
            f"• الآيدي: {user.id}\n"
            "• رصيد الحساب: 0.00 $\n"
            "• إجمالي الطلبات: 0 طلب\n"
        )
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ شحن الرصيد الآن", callback_data="nav_deposit")],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="nav_home")]
        ])
        await query.message.edit_text(profile_text, reply_markup=markup)

    elif data == "nav_orders":
        orders_text = "📦 سجل الطلبات:\n\nلا توجد طلبات سابقة مسجلة حالياً."
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛍️ تصفح المتجر", callback_data="nav_browse")],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="nav_home")]
        ])
        await query.message.edit_text(orders_text, reply_markup=markup)

    elif data == "nav_search":
        search_text = "🔍 خدمة البحث السريع قيد التحديث، يرجى التصفح عبر الأقسام."
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🛍️ تصفح المتجر", callback_data="nav_browse")]])
        await query.message.edit_text(search_text, reply_markup=markup)

    elif data == "nav_support":
        support_text = "💬 فريق دعم T_B STORE بخدمتكم لأي استفسار أو مساعدة:"
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 واتساب", url=SUPPORT_WHATSAPP)],
            [InlineKeyboardButton(f"✈️ تيليجرام (@{ADMIN_USERNAME})", url=SUPPORT_TELEGRAM)],
            [InlineKeyboardButton("🏠 الرئيسية", callback_data="nav_home")]
        ])
        await query.message.edit_text(support_text, reply_markup=markup)

async def handle_user_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update.effective_user)
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
            f"✅ تم حفظ الآيدي: {player_id}\n\nاختر الفئة المطلوبة لـ {game_info['title']}:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await start(update, context)

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
    tg_app.add_handler(CommandHandler("admin", admin_panel))
    tg_app.add_handler(CommandHandler("broadcast", broadcast))
    tg_app.add_handler(CallbackQueryHandler(handle_buttons))
    tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_text))

    await start_web_server()

    async with tg_app:
        await tg_app.start()
        await tg_app.updater.start_polling()
        print("🤖 بوت T_B STORE يعمل الآن بنجاح...")
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
