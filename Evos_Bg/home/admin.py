from django import forms
from django.db import models
from django.contrib import admin
from django.utils.safestring import mark_safe
from home.models import Category, Product, Feedback, Order, ShopCart, Driver

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'status', 'create_at', 'image_preview']
    exclude = ('title',)

    def image_preview(self, obj):
        if obj.image:
            img_url = obj.image.url if hasattr(obj.image, 'url') else obj.image
            return mark_safe(f'<img src="{img_url}" width="50" height="50" />')
        return "Rasm yo‘q"

    image_preview.short_description = 'Категория'

class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'title', 'price', 'description', 'status', 'image_preview']
    exclude = ('title','description')

    def image_preview(self, obj):
        if obj.image:
            img_url = obj.image.url if hasattr(obj.image, 'url') else obj.image
            return mark_safe(f'<img src="{img_url}" width="50" height="50" />')
        return "Rasm yo‘q"

    image_preview.short_description = 'Продукт'

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['username', 'user_id', 'create_at']

class DriverAdmin(admin.ModelAdmin):
    list_display = ['fullname', 'phone', 'car_number']

class ShopcartAdmin(admin.ModelAdmin):
    list_display = ['id','user_id', 'product', 'quantity', 'total_price', 'status']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['status', 'code', 'phone', 'driver']
    readonly_fields = ('product_table', 'location_map')
    fields = ('status', 'driver', 'full_address_uz', 'link', 'product_table', 'location_map')
    list_filter = ()
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'style': 'width: 98.5%;', 'cols': '', 'rows': '',})},
        models.CharField: {'widget': forms.TextInput(attrs={'style': 'width: 98.5%;',})}
    }

    def product_table(self, obj):
        data = obj.product_data
        products = data.get('oder_uz', [])
        html = '<table style="border-collapse: collapse; width: 100%;">'
        html += '<tr style="background: #630414;">'
        html += '<th style="border: 1px solid #ddd; text-align: center;">ID</th>'
        html += '<th style="border: 1px solid #ddd; text-align: center;">Продукт</th>'
        html += '<th style="border: 1px solid #ddd; text-align: center;">Количество</th>'
        html += '<th style="border: 1px solid #ddd; text-align: center;">Общая цена</th>'
        html += '</tr>'
        for item in products:
            html += '<tr>'
            html += f'<td style="border: 1px solid #ddd; text-align: center;">{item.get("product_id", "-")}</td>'
            html += f'<td style="border: 1px solid #ddd; text-align: center;">{item.get("product_name", "-")}</td>'
            html += f'<td style="border: 1px solid #ddd; text-align: center;">{item.get("quantity", "-")}</td>'
            html += f'<td style="border: 1px solid #ddd; text-align: center;">{item.get("total_price", "-")} сум</td>'
            html += '</tr>'
        html += '</table> <style>.flex-container{align-items: normal;}</style>'
        return mark_safe(html)

    def location_map(self, obj):
        lat, lon = [x.strip() for x in obj.location.split(" - ")]
        lat = float(lat)
        lon = float(lon)
        popup_content = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; width: 165px; padding: 2px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="color: black;">📦 Код заказа</span> 
                <span style="color: #008efd;">{obj.code or '—'}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="color: black;">📞 Телефон</span> 
                <span style="color: #008efd;">{obj.phone or '—'}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="color: black;">📌 Телеграм ID</span> 
                <span style="color: #008efd;">{obj.user_id or '—'}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="color: black;">⏰ Время заказа</span> 
                <span style="color: #008efd;">{obj.time.strftime('%H:%M') or '—'}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="color: black;">📅 Созданный</span> 
                <span style="color: #008efd;">{obj.create_at.strftime('%d-%m-%Y') if obj.create_at else '—'}</span>
            </div>
        </div>
        """
        html = f"""
        <div style="border: 1px solid #e0e0e0; overflow: hidden; margin: 5px 0; background: #ffffff;">
            <div id="location-map" style="height: 350px; width: 100%;"></div>
        </div>
        <script>
            (function() {{
                var map = L.map('location-map').setView([{lat}, {lon}], 15);
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '&copy; OpenStreetMap contributors',
                    maxZoom: 15
                }}).addTo(map);
                var marker = L.marker([{lat}, {lon}]).addTo(map);
                marker.bindPopup(`{popup_content}`, {{closeButton: false}}).openPopup();
            }})();
        </script>
        <style>.field-location_map label {{display: none;}} .field-product_table label {{display: none;}}</style>
        """
        return mark_safe(html)
    class Media:
        css = {'all': ('https://unpkg.com/leaflet@1.7.1/dist/leaflet.css',)}
        js = ('https://unpkg.com/leaflet@1.7.1/dist/leaflet.js',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(ShopCart, ShopcartAdmin)
admin.site.register(Order, OrderAdmin)

