import requests
from home.models import Order
from django.dispatch import receiver
from django.db.models.signals import pre_save

BOT_TOKEN = ""

@receiver(pre_save, sender=Order)
def accepted_signals(sender, instance, *args, **kwargs):
    if instance.status == 'Accepted':
        bot_token = f"{BOT_TOKEN}"
        user_id = f"{instance.user_id}"
        order_lang = f"{instance.language}"
        driver = 'No Name'
        driver_phone = 'No Phone Number'
        driver_avto = 'No Driver Car Number'
        if instance.driver is not None:
            driver = instance.driver.fullname
            driver_phone = instance.driver.phone
            driver_avto = instance.driver.car_number
        if order_lang == "uz":
            message = f"✅ Buyurtmangiz Yo'lga chiqdi - Buyurtma № {instance.code}\n🚕 Yetkazib berish turi : Avtomobilda yetkazib berish - {driver_avto}\n👤 Yetkazib beruvchi shaxs - {driver}\n📞 Yetkazib beruvchining raqami {driver_phone}"
            url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
            payload = {
                'chat_id': user_id,
                'text': message
            }
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                print("Xabar muvaffaqiyatli yuborildi")
            else:
                print(f"Xabar yuborilmadi: {response.status_code} - {response.text}")
        elif order_lang == "ru":
            message = f"✅ Ваш заказ отправлен - № {instance.code}\n🚕 Способ доставки: машина - {driver_avto}\n👤 Поставщик - {driver}\n📞 Мобильный номер поставщика : {driver_phone}"
            url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
            payload = {
                'chat_id': user_id,
                'text': message
            }
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                print("Xabar muvaffaqiyatli yuborildi")
            else:
                print(f"Xabar yuborilmadi: {response.status_code} - {response.text}")

@receiver(pre_save, sender=Order)
def rejected_signals(sender, instance, *args, **kwargs):
    if instance.status == 'Rejected':
        bot_token = f"{BOT_TOKEN}"
        user_id = f"{instance.user_id}"
        order_lang = f"{instance.language}"
        if order_lang == "uz":
            message = f"❌ Buyurtmangiz bekor qilindi - № {instance.code}\n📆 24 soat ichida buyurtma uchun to'langan summa qaytariladi\n👤 Ishonch raqamlarimiz +998901234567"
            url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
            payload = {
                'chat_id': user_id,
                'text': message
            }
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                print("Xabar muvaffaqiyatli yuborildi!")
            else:
                print(f"Xabar yuborilmadi: {response.status_code} - {response.text}")
        elif order_lang == "ru":
            message = f"❌ Ваш заказ отменен - № {instance.code}\n📆 В течение 24 часов уплаченная за заказ сумма будет возвращена\n👤 Справочный колл-центр +998901234567"
            url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
            payload = {
                'chat_id': user_id,
                'text': message
            }
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                print("Xabar muvaffaqiyatli yuborildi")
            else:
                print(f"Xabar yuborilmadi: {response.status_code} - {response.text}")
