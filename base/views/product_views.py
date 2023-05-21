from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from base.models import Product, Review
from base.serializers import ProductSerializer, ReviewSerializer
from utils.Response import make_error_response

@api_view(['GET'])
def getProducts(request):
    try:
        products = Product.objects.all().order_by('-createdAt')
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    except:
        return Response(make_error_response("Unable to fetch products"), status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def getTopProducts(request):
    try:
        products = Product.objects.filter(rating__gte=4).order_by('-rating')[:5]
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    except:
        return Response(make_error_response("Unable to fetch products"), status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def getProduct(request, pk):
    try:
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data)
    except:
        return Response(make_error_response(f"Unable to fetch product with id:{pk}"), status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def createProduct(request):
    try:
        user = request.user

        data = request.data

        global description, countInStock

        description=''
        countInStock=0

        name=data['name']
        brand=data['brand']
        category=data['category']
        price=data['price']

        if 'description' in data:
            description = data['description']
        
        if 'countInStock' in data:
            countInStock=data['countInStock']

        product = Product.objects.create(
            user=user,
            name=name,
            price=price,
            brand=brand,
            category=category,
            description=description,
            countInStock=countInStock
        )

        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data)
    except:
        return Response(make_error_response("Unable to create product"), status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def updateProduct(request, pk):
    try:
        data = request.data
        product = Product.objects.filter(id=pk)
        if not product:
            return Response(make_error_response(f"Product with id {pk} does not exist"), status=status.HTTP_404_NOT_FOUND)

        product = product[0]
        serializer = ProductSerializer(product, many=False)

        if 'name' in data:
            product.name = data['name']

        if 'price' in data:
            product.price = data['price']

        if 'brand' in data:
            product.brand = data['brand']

        if 'category' in data:
            product.category = data['category']

        if 'countInStock' in data:
            product.countInStock = data['countInStock']

        if 'description' in data:
            product.description = data['description']

        product.save()

        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data)
    except Exception as e:
        return Response(make_error_response(f"Unable to update product with id:{pk}"), status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteProduct(request, pk):
    try:
        product = Product.objects.filter(id=pk)
        if not product:
            return Response(make_error_response(f"Product with id {pk} does not exist"), status=status.HTTP_404_NOT_FOUND)
        product = product[0]
        product.delete()
        return Response('Product deleted')
    except Exception as e:
        return Response(make_error_response(f"Unable to delete product with id:{pk}"), status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createProductReview(request, pk):
    try:
        user = request.user
        product = Product.objects.filter(id=pk)
        if not product:
            return Response(make_error_response(f"Product with id {pk} does not exist"), status=status.HTTP_404_NOT_FOUND)
        product = product[0]
        data = request.data

        alreadyExists = product.review_set.filter(user=user).exists()
        if alreadyExists:
            return Response(make_error_response('Product already reviewed'), status=status.HTTP_400_BAD_REQUEST)
        
        elif data['rating'] <= 0:
            return Response(make_error_response('Rating must be greater than 0'), status=status.HTTP_400_BAD_REQUEST)
        
        else:
            review = Review.objects.create(
                user=user,
                product=product,
                rating=data['rating'],
                comment=data['comment'],
            )

            reviews = product.review_set.all()
            product.numOfReviews = len(reviews)

            total = 0
            for i in reviews:
                total += i.rating

            product.rating = total / len(reviews)
            product.save()
            review.save()

            serializer = ReviewSerializer(review, many=False)

            return Response(serializer.data)
    except Exception as e:
        return Response(make_error_response(f"Unable to create review for product with id:{pk}"), status=status.HTTP_400_BAD_REQUEST)