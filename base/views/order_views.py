from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from base.models import Product, Order, OrderItem
from base.serializers import ProductSerializer, OrderSerializer
from utils.Response import make_error_response

from django.utils import timezone
from decimal import Decimal

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOrderItems(request):
    try:
        user = request.user
        data = request.data

        if 'orderItems' not in data or len(data['orderItems'])==0:
            return Response(make_error_response("No order item"), status=status.HTTP_404_NOT_FOUND)
        
        orderItems = data['orderItems']

        products = []
        productsPrice=0

        for orderItem in orderItems:
            product = Product.objects.filter(id=orderItem['productId'])

            if not product:
                return Response(make_error_response(f"Product with id {orderItem['productId']} not found"), status=status.HTTP_404_NOT_FOUND)
            
            product = product[0]
            totalPrice+=product.price

            product.countInStock -= orderItem['qty']
            products.append(product)
        
        taxPrice=Decimal(0.18)*productsPrice
        shippingPrice=Decimal(0.1)*productsPrice
        totalPrice=Decimal(1.28)*productsPrice

        if 'paymentMethod' not in data:
            return Response(make_error_response("No payment method"), status=status.HTTP_404_NOT_FOUND)
        
        if 'shippingAddress' not in data:
            return Response(make_error_response("No shipping address"), status=status.HTTP_404_NOT_FOUND)
        
        order = Order.objects.create(
            user = user,
            paymentMethod=data['paymentMethod'],
            taxPrice=taxPrice,
            shippingPrice=shippingPrice,
            productsPrice=productsPrice,
            totalPrice=totalPrice,
            shippingAddress=data['shippingAddress']
        )

        order.save()
        for product in products:
            product.save()

        serializer = OrderSerializer(order, many=False)
        resp = {'orderItems': orderItems}
        resp.update(serializer.data)
        return Response(resp)
    except Exception as e:
        return Response(make_error_response("Unable to create order"), status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyOrders(request):
    try:
        user = request.user
        orders = user.order_set.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(make_error_response("Not able to retrieve orders"), status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def getOrders(request):
    try:
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(make_error_response("Not able to retrieve orders"), status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderById(request, pk):

    user = request.user

    try:
        order = Order.objects.filter(_id=pk)
        if not order:
            return Response(make_error_response("Order not found"), status=status.HTTP_400_BAD_REQUEST)
        
        order=order[0]

        if user.is_staff or order.user == user:
            serializer = OrderSerializer(order, many=False)
            return Response(serializer.data)
        else:
            Response({'detail': 'Not authorized to view this order'},
                     status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'detail': 'Order does not exist'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateOrderToPaid(request, pk):
    order = Order.objects.filter(_id=pk)

    if not order:
        return Response(make_error_response("Order not found"), status=status.HTTP_400_BAD_REQUEST)
        
    order=order[0]

    if order.isPaid:
        return Response(make_error_response("Order already paid"), status=status.HTTP_400_BAD_REQUEST)

    order.isPaid = True
    order.paidAt = timezone.now()
    order.save()

    return Response('Order was paid')

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateOrderToDelivered(request, pk):
    order = Order.objects.filter(_id=pk)

    if not order:
        return Response(make_error_response("Order not found"), status=status.HTTP_400_BAD_REQUEST)
        
    order=order[0]

    if order.isDelivered:
        return Response(make_error_response("Order already delivered"), status=status.HTTP_400_BAD_REQUEST)

    order.isDelivered = True
    order.deliveredAt = timezone.now()
    order.save()

    return Response('Order was delivered')