import asyncio
import logging
import aiohttp
from aiogram.enums import ParseMode
from aiogram.types import KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder, InlineKeyboardButton

API_TOKEN = ""
API_BASE = "http://127.0.0.1:8000"

API_CATEGORY = f"{API_BASE}/Categories/"
API_CATEGORY_ID = f"{API_BASE}/CategoryDetail/"
API_FEEDBACK = f"{API_BASE}/FeedbackApi/"
API_GET_ORDER = f"{API_BASE}/GetOrder/"
API_POST_ORDER = f"{API_BASE}/PostDataApi/"
ALL_PRODUCT = f"{API_BASE}/GetProduct/"
SHOP_CART = f"{API_BASE}/ShopCartApi/"
FILTER_CART = f"{API_BASE}/GetShopcart/"
ALL_DELETE = f"{API_BASE}/DeleteShopcart/"
ID_DELETE = f"{API_BASE}/Delete_id/"

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

class Language(StatesGroup):
    language_code = State()

class Comment(StatesGroup):
    user_id = State()
    feedback = State()

class CategoryState(StatesGroup):
    select_id = State()

class ProductState(StatesGroup):
    product_id = State()
    total_qty = State()
    save_price = State()
    product_title = State()

class Users(StatesGroup):
    user_id = State()
    username = State()

class Order(StatesGroup):
    phone = State()
    location = State()

@dp.startup()
async def on_startup(bot: Bot):
    await bot.set_my_commands([
        types.BotCommand(command="/start", description="Botni ishga tushirish"),
        types.BotCommand(command="/category", description="Mahsulot xarid qilish"),
        types.BotCommand(command="/shopcart", description="Savatdagi mahsulotlar"),
        types.BotCommand(command="/my_order", description="Mening Buyurtmalarim"),
        types.BotCommand(command="/comment", description="Izoh Yozish"),
        types.BotCommand(command="/language", description="Sozlamalar"),
    ])

async def get_lang(state: FSMContext) -> str:
    data = await state.get_data()
    return data.get("language_code", "uz")

async def reset_state_keep_lang(state: FSMContext):
    lang = await get_lang(state)
    await state.clear()
    await state.update_data(language_code=lang)

def get_main_keyboard(lang: str) -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    if lang == 'ru':
        builder.button(text='🍽 Меню')
        builder.button(text='🛍 Мои заказы')
        builder.button(text='✍️ Комментарий')
        builder.button(text='⚙️ Настройки')
    else:
        builder.button(text='🍽 Menyu')
        builder.button(text='🛍 Buyurtmalarim')
        builder.button(text='✍️ Fikr bildirish')
        builder.button(text='⚙️ Sozlamalar')
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

async def shopcart(user_id: int, lang: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{FILTER_CART}{user_id}/", timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                data = await response.json()
                total_quantity = sum(item.get('quantity') for item in data)
                total_price = sum(int(item.get('total_price')) for item in data)
                if lang == 'ru':
                    products_list = "\n".join([f"{i + 1}) {item.get('product_title_ru')} = {item.get('quantity')} x {item.get('total_price')} сум" for i, item in enumerate(data)])
                    text = (
                        f"🛍 <b>Все блюда которые вы добавили в корзину !</b>\n{products_list}\n\n"
                        f"<b>Количество продуктов - {total_quantity}</b>\n"
                        f"<b>Общая стоимость - {total_price} sum</b>"
                    )
                    builder = InlineKeyboardBuilder()
                    builder.button(text="🗑 Очистить корзину", callback_data="delete_all")
                    builder.button(text="🚖 Разместить заказ", callback_data="order_post")
                    builder.adjust(2)
                    for item in data:
                        p_title = item.get('product_title_ru')
                        p_id = str(item.get('id'))
                        builder.button(text=f"❌ {p_title}", callback_data=f"del_id_{p_id}")
                    builder.adjust(2, 1)
                    return text, builder.as_markup()
                else:
                    products_list = "\n".join([f"{i + 1}) {item.get('product_title_uz')} = {item.get('quantity')} x {item.get('total_price')} sum" for i, item in enumerate(data)])
                    text = (
                        f"🛍 <b>Barcha savatga qo'shgan taomlaringiz !</b>\n{products_list}\n\n"
                        f"<b>Maxsulotlar soni - {total_quantity}</b>\n"
                        f"<b>Umumiy narx - {total_price} sum</b>"
                    )
                    builder = InlineKeyboardBuilder()
                    builder.button(text="🗑 Savatni tozalash", callback_data="delete_all")
                    builder.button(text="🚖 Buyurtma berish", callback_data="order_post")
                    builder.adjust(2)
                    for item in data:
                        p_title = item.get('product_title_uz')
                        p_id = str(item.get('id'))
                        builder.button(text=f"❌ {p_title}", callback_data=f"del_id_{p_id}")
                    builder.adjust(2, 1)
                    return text, builder.as_markup()
            elif response.status == 204:
                if lang == 'ru':
                    text = "😔 <b>К сожалению, ваша корзина пуста</b>"
                    return text
                else:
                    text = "😔 <b>Afsuski Savatingiz boʻsh</b>"
                    return text

@dp.message(F.text.in_(["🇷🇺 Русский", "🇺🇿 O'zbekcha"]))
async def language_selection(message: types.Message, state: FSMContext):
    lang = "ru" if message.text == "🇷🇺 Русский" else "uz"
    await state.clear()
    await state.update_data(language_code=lang)
    await start_menu(message, state)

@dp.message(F.text.in_(["⚙️ Sozlamalar", "⚙️ Настройки", "/language"]))
async def language(message: types.Message, state: FSMContext):
    lang = await get_lang(state)
    builder = ReplyKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbekcha")
    builder.button(text="🇷🇺 Русский")
    builder.adjust(2)
    if lang == 'ru':
        await message.answer("Выберите язык !", reply_markup=builder.as_markup(resize_keyboard=True))
    else:
        await message.answer("Tilni tanlang !", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(F.text.in_(["⬅️ Ortga", "⬅️ Назад", "/start"]))
async def start_menu(message: types.Message, state: FSMContext):
    await reset_state_keep_lang(state)
    lang = await get_lang(state)
    if lang == "ru":
        await message.answer("Выберите одно из меню !", reply_markup=get_main_keyboard(lang))
    else:
        await message.answer("Menyulardan birini tanlang !", reply_markup=get_main_keyboard(lang))

@dp.message(F.text.in_(["🛍 Buyurtmalarim", "🛍 Мои заказы", "/my_order"]))
async def my_order(message: types.Message, state: FSMContext):
    lang = await get_lang(state)
    user_id = message.from_user.id
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_GET_ORDER}{user_id}/", timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                data = await response.json()
                for item in data:
                    status_one = item.get("status")
                    product_data = item.get("product_data")
                    if lang == 'ru':
                        status_str = {"New": "Новый", "Accepted": "Принял", "Rejected": "Отклоненный", "Expired": "Истекший"}.get(status_one, status_one)
                        text = (
                            f"<b>Номер заказа:</b> #{item.get('code')}\n"
                            f"<b>Телефон:</b> {item.get('phone')}\n"
                            f"<b>Статус:</b> {status_str}\n"
                            f"<b>адрес:</b> {item.get('full_address_ru')}"
                        )
                        products = product_data.get("order_ru", [])
                        for p in products:
                            text += f"\n➕ <b>{p.get('quantity')}</b> x {p.get('product_name')} : {p.get('total_price')} сум"
                        text += f"\n<b>Время заказа:</b> {item.get('time')}"
                        text += f"\n<b>Дата заказа:</b> {item.get('create_at')}"
                        if status_one not in ["Expired", "Rejected"]:
                            text += "\n<b>Время доставки:</b> 30 минут"
                        text += "\n<b>Телефон поддержки</b> +998901234567"
                    else:
                        status_str = {"New": "Yangi", "Accepted": "Qabul qilingan", "Rejected": "Rad etilgan", "Expired": "Muddati tugagan"}.get(status_one, status_one)
                        text = (
                            f"<b>Buyurtma raqami:</b> #{item.get('code')}\n"
                            f"<b>Telefon:</b> {item.get('phone')}\n"
                            f"<b>Holat:</b> {status_str}\n"
                            f"<b>Manzil:</> {item.get('full_address_uz')}"
                        )
                        products = product_data.get("oder_uz", [])
                        for p in products:
                            text += f"\n➕ <b>{p.get('quantity')}</b> x {p.get('product_name')} : {p.get('total_price')} sum"
                        text += f"\n<b>Buyurtma vaqti</b> {item.get('time')}"
                        text += f"\n<b>Buyurtma sana</b> {item.get('create_at')}"
                        if status_one not in ["Expired", "Rejected"]:
                            text += "\n<b>Yetkazib berish vaqti: 30 daqiqa</b>"
                        text += "\n<b>Ishonch telefoni</b> +998901234567"
                    await message.answer(text)
            elif response.status == 204:
                if lang == 'ru':
                    await message.answer("😔 <b>Извините, ваш заказ недоступен</b>")
                else:
                    await message.answer("😔 <b>Kechirasiz buyurtmalaringiz mavjud emas</b>")

@dp.message(F.text.in_(["✍️ Fikr bildirish", "✍️ Комментарий", "/comment"]))
async def action_comment(message: types.Message, state: FSMContext):
    lang = await get_lang(state)
    if lang == 'ru':
        await message.answer('Отправить комментарий')
    else:
        await message.answer('Izoh yuboring')
    await state.set_state(Comment.feedback)

@dp.message(Comment.feedback)
async def process_comment(message: types.Message, state: FSMContext):
    lang = await get_lang(state)
    if message.content_type == types.ContentType.PHOTO:
        if lang == 'ru':
            await message.answer("<b>Не отправляйте фото !</b>")
        else:
            await message.answer("<b>Rasm yubormang !</b>")
    elif message.content_type == types.ContentType.LOCATION:
        if lang == 'ru':
            await message.answer("<b>Не отправляйте локацию !</b>")
        else:
            await message.answer("<b>Lokatsiya yubormang !</b>")
    elif message.content_type == types.ContentType.VIDEO:
        if lang == 'ru':
            await message.answer("<b>Не отправляйте видео !</b>")
        else:
            await message.answer("<b>Video yubormang !</b>")
    elif message.content_type == types.ContentType.AUDIO:
        if lang == 'ru':
            await message.answer("<b>Не отправляйте аудио !</b>")
        else:
            await message.answer("<b>Audio yubormang !</b>")
    elif message.content_type == types.ContentType.DOCUMENT:
        if lang == 'ru':
            await message.answer("<b>Не отправляйте документ !</b>")
        else:
            await message.answer("<b>Hujjat yubormang !</b>")
    elif message.content_type == types.ContentType.CONTACT:
        if lang == 'ru':
            await message.answer("<b>Не отправляйте контакт !</b>")
        else:
            await message.answer("<b>Raqam yubormang !</b>")
    elif message.content_type == types.ContentType.TEXT:
        comment = message.text
        username = message.from_user.username
        form_data = {'user_id': message.from_user.id, 'comment': comment, 'username': username}
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{API_FEEDBACK}", json=form_data, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 201:
                    if lang == 'ru':
                        await message.answer("Комментарий отправлен !")
                    else:
                        await message.answer("Izoh yuborildi !")
                elif response.status == 400:
                    if lang == 'ru':
                        await message.answer("Комментарий не отправлен !")
                    else:
                        await message.answer("Izoh yuborilmadi !")

@dp.message(F.text.in_(["📥 Savat", "📥 Корзина", "/shopcart"]))
async def call_shopcart(message: types.Message, state: FSMContext):
    lang = await get_lang(state)
    user_id = message.from_user.id
    result = await shopcart(user_id, lang)
    if isinstance(result, tuple):
        text, reply_markup = result
        await message.answer(text, reply_markup=reply_markup)
    else:
        await message.answer(result)

@dp.message(F.text.in_(["🍽 Menyu", "🍽 Меню", "◀️ Ortga", "◀️ Назад", "/category"]))
async def category_food(message: types.Message, state: FSMContext):
    lang = await get_lang(state)
    async with aiohttp.ClientSession() as session:
        async with session.get(API_CATEGORY, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                data = await response.json()
                builder = ReplyKeyboardBuilder()
                if lang == 'ru':
                    for item in data:
                        builder.button(text=item.get('title_ru'), callback_data=f"cat_{item.get('id')}")
                    builder.adjust(2)
                    builder.row(
                        KeyboardButton(text="📥 Корзина"),
                        KeyboardButton(text="⬅️ Назад"),
                    )
                    await message.answer("Выбирайте одно из меню !", reply_markup=builder.as_markup(resize_keyboard=True))
                else:
                    for item in data:
                        builder.button(text=item.get('title_uz'), callback_data=f"cat_{item.get('id')}")
                    builder.adjust(2)
                    builder.row(
                        KeyboardButton(text="📥 Savat"),
                        KeyboardButton(text="⬅️ Ortga"),
                    )
                    await message.answer("Menyulardan birini tanlang !", reply_markup=builder.as_markup(resize_keyboard=True))
            elif response.status == 204:
                if lang == 'ru':
                    await message.answer("Категория не найдена !")
                else:
                    await message.answer("Kategoriya topilmadi !")

@dp.message(F.text)
async def category_selection(message: types.Message, state: FSMContext):
    lang = await get_lang(state)
    selected_title = message.text
    async with aiohttp.ClientSession() as session:
        async with session.get(ALL_PRODUCT, timeout=aiohttp.ClientTimeout(total=10)) as product_title:
            if product_title.status == 200:
                fetch_data = await product_title.json()
                if any(selected_title == item['title_uz'] or selected_title == item['title_ru'] for item in fetch_data):
                    await product_selection(message, state)
                    return
                else:
                    async with session.get(API_CATEGORY, timeout=aiohttp.ClientTimeout(total=10)) as category:
                        if category.status == 200:
                            categories = await category.json()
                            for category in categories:
                                if selected_title == category["title_uz"] or selected_title == category["title_ru"]:
                                    async with session.get(f"{API_CATEGORY_ID}{category['id']}/", timeout=aiohttp.ClientTimeout(total=10)) as category_detail:
                                        if category_detail.status == 200:
                                            detail = await category_detail.json()
                                            builder = ReplyKeyboardBuilder()
                                            image = detail.get('image')
                                            products = detail.get('product', [])
                                            if lang == 'ru':
                                                for item in products:
                                                    builder.button(text=item.get('title_ru'))
                                                builder.adjust(2)
                                                builder.row(KeyboardButton(text="◀️ Назад"))
                                                await message.answer_photo(image, reply_markup=builder.as_markup(resize_keyboard=True))
                                                await product_selection(message, state)
                                            else:
                                                for item in products:
                                                    builder.button(text=item.get('title_uz'))
                                                builder.adjust(2)
                                                builder.row(KeyboardButton(text="◀️ Ortga"))
                                                await message.answer_photo(image, reply_markup=builder.as_markup(resize_keyboard=True))
                                                await product_selection(message, state)
                                        elif category_detail.status == 204:
                                            if lang == 'ru':
                                                await message.answer("<b>Для этой категории не найдено ни одного товара !</b>")
                                            else:
                                                await message.answer("<b>Ushbu bo'limda hech qanday mahsulot topilmadi !</b>")
                        elif category.status == 204:
                            if lang == 'ru':
                                await message.answer("<b>Этот раздел не существует !</b>")
                            else:
                                await message.answer("<b>Ushbu bo'lim mavjud emas !</b>")

@dp.message(F.text)
async def product_selection(message: types.Message, state: FSMContext):
    lang = await get_lang(state)
    selected_title = message.text
    async with aiohttp.ClientSession() as session:
        async with session.get(ALL_PRODUCT, timeout=aiohttp.ClientTimeout(total=10)) as product:
            if product.status == 200:
                products = await product.json()
                for item in products:
                    if selected_title == item['title_uz'] or selected_title == item['title_ru']:
                        if lang == 'ru':
                            image_url = item.get('image')
                            product_id = str(item.get('id'))
                            product_price = str(item.get('price'))
                            title = item.get('title_ru')
                            product_description = item.get('description_ru')
                            await state.update_data(product_id=product_id, save_price=product_price, product_title=title, quantity=1)
                            builder = InlineKeyboardBuilder()
                            builder.add(InlineKeyboardButton(text=f"Оформить заказ ( {product_price} сум )", callback_data=f"order_id_{product_id}"))
                            keyboard = builder.as_markup()
                            product_detail = await message.answer_photo(photo=image_url, caption=product_description, reply_markup=keyboard)
                            await state.update_data(product_message_id=product_detail.message_id)
                        else:
                            image_url = item.get('image')
                            product_id = str(item.get('id'))
                            product_price = str(item.get('price'))
                            title = item.get('title_uz')
                            product_description = item.get('description_uz')
                            await state.update_data(product_id=product_id, save_price=product_price, product_title=title, quantity=1)
                            builder = InlineKeyboardBuilder()
                            builder.add(InlineKeyboardButton(text=f"Xarid qilish ( {product_price} sum )", callback_data=f"order_id_{product_id}"))
                            keyboard = builder.as_markup()
                            product_detail = await message.answer_photo(photo=image_url, caption=product_description, reply_markup=keyboard)
                            await state.update_data(product_message_id=product_detail.message_id)
            elif product.status == 204:
                if lang == 'ru':
                    await message.answer("Данный товар отсутствует !")
                else:
                    await message.answer("ushbu mahsulot mavjud emas !")

@dp.callback_query(F.data.startswith("order_id_"))
async def detail(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        callback_product_id = int(callback_query.data.split("_")[2])
        lang = await get_lang(state)
        data = await state.get_data()
        state_product_id = data.get('product_id')
        if isinstance(state_product_id, str):
            state_product_id = int(state_product_id)
        if callback_product_id == state_product_id:
            builder = InlineKeyboardBuilder()
            builder.button(text="-", callback_data='minus')
            builder.button(text="1", callback_data='noop')
            builder.button(text="+", callback_data='plus')
            builder.button(text="📥 Savatga qo'shish" if lang != 'ru' else "📥 Добавить в корзину", callback_data='shop')
            builder.adjust(3)
            await callback_query.message.edit_reply_markup(reply_markup=builder.as_markup())
    except Exception as e:
        logging.error(f"Detail callback error: {e}")
    finally:
        await callback_query.answer()

@dp.callback_query(F.data.in_(['minus', 'plus', 'noop', 'shop']))
async def quantity_handler(callback_query: types.CallbackQuery, state: FSMContext):
    lang = await get_lang(state)
    data = await state.get_data()
    quantity = data.get('quantity', 1)
    if callback_query.data == 'plus':
        quantity += 1
        await state.update_data(quantity=quantity)
        builder = InlineKeyboardBuilder()
        builder.button(text="-", callback_data='minus')
        builder.button(text=str(quantity), callback_data='noop')
        builder.button(text="+", callback_data='plus')
        builder.button(text="📥 Savatga qo'shish" if lang != 'ru' else "📥 Добавить в корзину", callback_data='shop')
        builder.adjust(3)
        await callback_query.message.edit_reply_markup(reply_markup=builder.as_markup())
        await callback_query.answer()
        return
    elif callback_query.data == 'minus' and quantity > 1:
        quantity -= 1
        await state.update_data(quantity=quantity)
        builder = InlineKeyboardBuilder()
        builder.button(text="-", callback_data='minus')
        builder.button(text=str(quantity), callback_data='noop')
        builder.button(text="+", callback_data='plus')
        builder.button(text="📥 Savatga qo'shish" if lang != 'ru' else "📥 Добавить в корзину",callback_data='shop')
        builder.adjust(3)
        await callback_query.message.edit_reply_markup(reply_markup=builder.as_markup())
        await callback_query.answer()
        return
    elif callback_query.data == 'noop':
        await callback_query.answer()
        return
    elif callback_query.data == 'shop':
        user_id = callback_query.from_user.id
        username = callback_query.from_user.username or 'No username'
        product_id = data.get('product_id')
        try:
            price = int(data.get('save_price', 0))
        except (ValueError, TypeError):
            price = 0
        product_title = data.get('product_title', 'Unknown')
        total_sum = price * quantity
        form_data = {
            'user_id': user_id,
            'product': product_id,
            'quantity': quantity,
            'total_price': total_sum,
            'username': username
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(SHOP_CART, json=form_data, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 201:
                    if lang == 'ru':
                        msg_text = (
                            f"🎉 Ваш заказ успешно добавлен в корзину\n"
                            f"<b>🌯 {quantity} x {product_title} = {total_sum} сум</b>"
                        )
                    else:
                        msg_text = (
                            f"🎉 Buyurtmangiz savatga muvaffaqiyatli qo'shildi\n"
                            f"<b>🌯 {quantity} x {product_title} = {total_sum} sum</b>"
                        )
                    await callback_query.message.answer(msg_text)
                    await callback_query.message.delete_reply_markup()
                elif response.status == 400:
                    await callback_query.message.answer("Xatolik yuz berdi." if lang != 'ru' else "Ошибка.")
                else:
                    await callback_query.message.answer("Kutilmagan xatolik." if lang != 'ru' else "Неизвестная ошибка.")
        await callback_query.answer()
        return

@dp.callback_query(F.data.startswith("del_id_"))
async def delete_id(callback_query: types.CallbackQuery, state: FSMContext):
    lang = await get_lang(state)
    user_id = callback_query.from_user.id
    product_id = callback_query.data.split("_")[2]
    async with aiohttp.ClientSession() as session:
        async with session.delete(f'{ID_DELETE}{product_id}/', timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                result = await shopcart(user_id, lang)
                if isinstance(result, tuple):
                    text, keyboard = result
                    await callback_query.message.edit_text(text, reply_markup=keyboard)
                else:
                    await callback_query.message.edit_text(result)

@dp.callback_query(F.data == "delete_all")
async def all_delete_cart(callback_query: types.CallbackQuery, state: FSMContext):
    lang = await get_lang(state)
    user_id = callback_query.from_user.id
    async with aiohttp.ClientSession() as session:
        async with session.delete(f"{ALL_DELETE}{user_id}/", timeout=aiohttp.ClientTimeout(total=10)) as response:
             if response.status == 200:
                if lang == 'ru':
                    await callback_query.message.answer("✅ <b>Все товары, которые вы добавили в корзину, были удалены.</b>")
                else:
                    await callback_query.message.answer("✅ <b>Savatga qo'shgan barcha mahsulotlaringiz o'chirildi</b>")
                await callback_query.message.delete()

@dp.callback_query(F.data == "order_post")
async def order(callback_query: types.CallbackQuery, state: FSMContext):
    lang = await get_lang(state)
    if lang == 'ru':
        builder = ReplyKeyboardBuilder()
        builder.button(text='📞 Мой номер', request_contact=True)
        builder.button(text='📍 Мой адрес', request_location=True)
        builder.button(text='⬅️ Назад')
        builder.adjust(2, 1)
        await callback_query.message.answer("Пожалуйста, введите свой номер телефона !", reply_markup=builder.as_markup(resize_keyboard=True))
        await state.set_state(Order.phone)
    else:
        builder = ReplyKeyboardBuilder()
        builder.button(text='📞 Mening raqamim', request_contact=True)
        builder.button(text='📍 Manzilim', request_location=True)
        builder.button(text='⬅️ Ortga')
        builder.adjust(2, 1)
        await callback_query.message.answer("Iltimos telefon raqamingizni kiriting !", reply_markup=builder.as_markup(resize_keyboard=True))
        await state.set_state(Order.phone)

@dp.message(Order.phone)
async def process_phone(message: types.Message, state: FSMContext):
    lang = await get_lang(state)
    if message.content_type == types.ContentType.PHOTO:
        if lang == 'ru':
            await message.answer("<b>Не отправляйте фото !</b>")
        else:
            await message.answer("<b>Rasm yubormang !</b>")
    elif message.content_type == types.ContentType.TEXT:
        if lang == 'ru':
            await message.answer("<b>Не отправляйте текст !</b>")
        else:
            await message.answer("<b>Matn yubormang !</b>")
    elif message.content_type == types.ContentType.VIDEO:
        if lang == 'ru':
            await message.answer("<b>Не отправляйте видео !</b>")
        else:
            await message.answer("<b>Video yubormang !</b>")
    elif message.content_type == types.ContentType.AUDIO:
        if lang == 'ru':
            await message.answer("<b>Не отправляйте аудио !</b>")
        else:
            await message.answer("<b>Audio yubormang !</b>")
    elif message.content_type == types.ContentType.DOCUMENT:
        if lang == 'ru':
            await message.answer("<b>Не отправляйте документ !</b>")
        else:
            await message.answer("<b>Hujjat yubormang !</b>")
    elif message.content_type == types.ContentType.LOCATION:
        if lang == 'ru':
            await message.answer("<b>Не отправляйте локацию !</b>")
        else:
            await message.answer("<b>Lokatsiya yubormang !</b>")
    elif message.content_type == types.ContentType.CONTACT:
        phone_number = message.contact.phone_number
        await state.update_data(phone=phone_number)
        if lang == 'ru':
            await message.answer("Пожалуйста, введите свой адрес !")
        else:
            await message.answer("Iltimos manzilingizni tashlang !")
        await state.set_state(Order.location)

@dp.message(Order.location)
async def order_post(message: types.Message, state: FSMContext):
    lang = await get_lang(state)
    if message.content_type == types.ContentType.PHOTO:
        if lang == 'ru':
            await message.answer("<b>Не отправляйте фото !</b>")
        else:
            await message.answer("<b>Rasm yubormang !</b>")
    elif message.content_type == types.ContentType.TEXT:
        if lang == 'ru':
            await message.answer("<b>Не отправляйте текст !</b>")
        else:
            await message.answer("<b>Matn yubormang !</b>")
    elif message.content_type == types.ContentType.VIDEO:
        if lang == 'ru':
            await message.answer("<b>Не отправляйте видео !</b>")
        else:
            await message.answer("<b>Video yubormang !</b>")
    elif message.content_type == types.ContentType.AUDIO:
        if lang == 'ru':
            await message.answer("<b>Не отправляйте аудио !</b>")
        else:
            await message.answer("<b>Audio yubormang !</b>")
    elif message.content_type == types.ContentType.DOCUMENT:
        if lang == 'ru':
            await message.answer("<b>Не отправляйте документ !</b>")
        else:
            await message.answer("<b>Hujjat yubormang !</b>")
    elif message.content_type == types.ContentType.CONTACT:
        if lang == 'ru':
            await message.answer("<b>Не отправляйте контакт !</b>")
        else:
            await message.answer("<b>Raqam yubormang !</b>")
    elif message.content_type == types.ContentType.LOCATION:
        phone = (await state.get_data()).get('phone')
        user_id = message.from_user.id
        lat, lon = message.location.latitude, message.location.longitude
        location_coords = f"{lat} - {lon}"
        async with aiohttp.ClientSession() as session:
            headers_uz = {'User-Agent': 'FastFoodBot/1.0', 'Accept-Encoding': 'gzip, deflate', 'Cache-Control': 'no-cache', 'Accept-Language': 'uz-UZ',}
            headers_ru = {'User-Agent': 'FastFoodBot/1.0', 'Accept-Encoding': 'gzip, deflate', 'Cache-Control': 'no-cache', 'Accept-Language': 'ru-RU', }
            params = {'lat': lat, 'lon': lon, 'format': 'json', 'zoom': 18, 'addressdetails': 1}
            async with session.get(f"https://nominatim.openstreetmap.org/reverse", params=params, headers=headers_ru, timeout=aiohttp.ClientTimeout(total=5)) as address_ru:
                if address_ru.status == 200:
                    get_address = await address_ru.json()
                    addr = get_address.get("address", {})
                    country = addr.get("country", "")
                    city = addr.get("city", "") or addr.get("town", "") or addr.get("village", "")
                    district = addr.get("county", "")
                    street = addr.get("road", "") or addr.get("hamlet", "")
                    full_address_ru = " ".join(filter(None, [country, city, district, street]))
                else:
                    if lang == 'ru':
                        await message.answer("Адрес не установлен !")
                    else:
                        await message.answer("Manzil aniqlanmadi !")
                async with session.get(f"https://nominatim.openstreetmap.org/reverse", params=params, headers=headers_uz, timeout=aiohttp.ClientTimeout(total=5)) as geo_resp:
                    if geo_resp.status == 200:
                        geo_data = await geo_resp.json()
                        addr = geo_data.get("address", {})
                        country = addr.get("country", "")
                        city = addr.get("city", "") or addr.get("town", "") or addr.get("village", "")
                        district = addr.get("county", "")
                        street = addr.get("road", "") or addr.get("hamlet", "")
                        full_address_uz = " ".join(filter(None, [country, city, district, street]))
                        async with session.get(f"{FILTER_CART}{user_id}/", timeout=aiohttp.ClientTimeout(total=10)) as response:
                            if response.status == 200:
                                data = await response.json()
                                product_ids = []
                                oder_uz = []
                                order_ru = []
                                for item in data:
                                    product_id = item.get("product")
                                    if not product_id:
                                        continue
                                    quantity = item.get("quantity")
                                    total_price = str(item.get("total_price"))
                                    title_uz = item.get("product_title_uz")
                                    title_ru = item.get("product_title_ru")
                                    product_ids.append(product_id)
                                    oder_uz.append({
                                        "product_id": product_id,
                                        "product_name": title_uz,
                                        "quantity": quantity,
                                        "total_price": total_price
                                    })
                                    order_ru.append({
                                        "product_id": product_id,
                                        "product_name": title_ru,
                                        "quantity": quantity,
                                        "total_price": total_price
                                    })
                                order_data = {
                                    "product": product_ids,
                                    "location": location_coords,
                                    "language": lang if lang is not None else "uz",
                                    "user_id": str(user_id),
                                    "phone": phone,
                                    "full_address_uz": full_address_uz,
                                    "full_address_ru": full_address_ru,
                                    "product_data": {"oder_uz": oder_uz, "order_ru": order_ru}
                                }
                                async with session.post(API_POST_ORDER, json=order_data, timeout=aiohttp.ClientTimeout(total=10)) as post_data:
                                    if post_data.status == 201:
                                        async with session.delete(f'{ALL_DELETE}{user_id}/', timeout=aiohttp.ClientTimeout(total=10)) as shopcard_delete:
                                            if shopcard_delete.status == 200:
                                                if lang == 'ru':
                                                    await message.answer("🎉 <b>Заказы успешно получены</b>")
                                                else:
                                                    await message.answer("🎉 <b>Buyurtmalar muvaffaqiyatli qabul qilindi!</b>")
                                            elif shopcard_delete.status == 400:
                                                if lang == 'ru':
                                                    await message.answer("<b>Товары в корзине не были удалены !</b>")
                                                else:
                                                    await message.answer("<b>Savatdagi mahsulotlar o'chirilmadi</b>")
                                    elif post_data.status == 400:
                                        if lang == 'ru':
                                            await message.answer("<b>Заказ не оформлен. Попробуйте еще раз.</b>")
                                        else:
                                            await message.answer("<b>Buyurtma berilmadi. Iltimos qaytadan urinib ko'ring.</b>")
                                    await reset_state_keep_lang(state)
                                    await start_menu(message, state)
                            elif response.status == 204:
                                if lang == 'ru':
                                    await message.answer("Корзина пуста !")
                                else:
                                    await message.answer("Savat bo'sh !")
                    else:
                        if lang == 'ru':
                            await message.answer("Адрес не установлен !")
                        else:
                            await message.answer("Manzil aniqlanmadi !")

async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
