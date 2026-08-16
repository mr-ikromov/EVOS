from modeltranslation.translator import register, TranslationOptions
from home.models import *

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('title',)

@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('title','description')

@register(Order)
class OrderTranslationOptions(TranslationOptions):
    fields = ('full_address',)