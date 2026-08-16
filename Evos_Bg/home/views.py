from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from home.serializers import *
from home.models import Category, Product, ShopCart, Order

class Categories(APIView):
    def get(self, request):
        categories = Category.objects.filter(status='True').order_by('-id')
        if not categories.exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class CategoryDetail(APIView):
    def get(self, request, id):
        categories = Category.objects.get(pk=id)
        serializer = CategoryDetailSerializer(categories)
        if not serializer.data.get('product'):
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetProduct(APIView):
    def get(self, request):
        products = Product.objects.filter(status='True')
        if not products.exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductDetail(APIView):
    def get(self, request, id):
        products = Product.objects.get(pk=id)
        if not products.exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = ProductSerializer(products)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FeedbackApi(APIView):
    def post(self, request):
        serializers = FeedbackSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

class ShopCartApi(APIView):
    def post(self, request):
        serializers = ShopCartSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

class GetShopcart(APIView):
    def get(self, request, user_id):
        carts = ShopCart.objects.filter(user_id=user_id)
        if not carts.exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DeleteShopcart(APIView):
    def delete(self, request, user_id):
        cart = ShopCart.objects.filter(user_id=user_id)
        cart.delete()
        return Response(status=status.HTTP_200_OK)

class Delete_id(APIView):
    def delete(self, request, id):
        cart = ShopCart.objects.get(pk=id)
        cart.delete()
        return Response(status=status.HTTP_200_OK)

class GetOrder(APIView):
    def get(self, request, user_id):
        orders = Order.objects.filter(user_id=user_id)
        if not orders.exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = OrderGetSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PostDataApi(APIView):
    def post(self, request):
        serializers = OrderPostSerializer(data=request.data)
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)