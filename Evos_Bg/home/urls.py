from home import views
from django.urls import path

urlpatterns = [
    path('Categories/', views.Categories.as_view(), name='Categories'),
    path('GetProduct/', views.GetProduct.as_view(), name='GetProduct'),
    path('ProductDetail/<int:id>/', views.ProductDetail.as_view(), name='ProductDetail'),
    path('CategoryDetail/<int:id>/', views.CategoryDetail.as_view(), name='CategoryDetail'),
    path('FeedbackApi/', views.FeedbackApi.as_view(), name='FeedbackApi'),
    path('ShopCartApi/', views.ShopCartApi.as_view(), name='ShopCartApi'),
    path('GetShopcart/<str:user_id>/', views.GetShopcart.as_view(), name='GetShopcart'),
    path('DeleteShopcart/<str:user_id>/', views.DeleteShopcart.as_view(), name='DeleteShopcart'),
    path('Delete_id/<int:id>/', views.Delete_id.as_view(), name='Delete_id'),
    path('GetOrder/<str:user_id>/', views.GetOrder.as_view(), name='GetOrder'),
    path('PostDataApi/', views.PostDataApi.as_view(), name='PostDataApi'),
]