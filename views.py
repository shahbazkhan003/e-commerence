from django.shortcuts import render,redirect
from .models import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate ,login as auth_login ,logout as auth_logout
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .serializers import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.middleware.csrf import get_token
from rest_framework_simplejwt.tokens import RefreshToken

#Generate token manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@api_view(['GET'])
def product_view(request):
    topwears = Product.objects.filter(category='TW')
    jeans = Product.objects.filter(category='BW')
    mobiles = Product.objects.filter(category='M')
    laptops = Product.objects.filter(category='L')

    data = {
        'topwears': ProductSerializer(topwears, many=True).data,
        'jeans': ProductSerializer(jeans, many=True).data,
        'mobiles': ProductSerializer(mobiles, many=True).data,
        'laptops': ProductSerializer(laptops, many=True).data,
    }
    return Response(data)

@api_view(['GET'])
def product_detail_api(request, pk):
    product = get_object_or_404(Product, pk=pk)
    item_already_in_cart = False
    if request.user.is_authenticated:
        item_already_in_cart = Cart.objects.filter(product=product.id, user=request.user).exists()
    data = {
        'product': ProductSerializer(product).data,
        'item_already_in_cart': item_already_in_cart,
    }
    return Response(data)  


@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def add_to_cart_api(request):
    user = request.user
    product_id = request.data.get('prod_id')  
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)
    Cart.objects.create(user=user, product=product)
    return Response({"success": "Product added to cart"}, status=201)

# sarmadkhalique001@gmail.com
# sarmadkhalique001@gmail.com
@api_view(['GET'])
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        sniping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        if cart_product:
            for p in cart_product:
                temamount = (p.quantity * p.product.discount_price)
                amount += temamount
            total_amount = sniping_amount + amount
            cart_serializer = CartSerializer(cart, many=True)
            return Response({
                'cart': cart_serializer.data,
                'total_amount': total_amount,
                'amount': amount
            })
        else:
            return Response({'message': 'Cart is empty'}, status=404)
    else:
        return Response({'message': 'User not authenticated'}, status=401)

@login_required
def buy_now(request):
 return render(request, 'app/buynow.html')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def plus_cart_api(request, pk):
    if request.method == "GET":
        try:
            c = Cart.objects.get(Q(user=request.user) & Q(product=pk))
            c.quantity += 1
            c.save()
            amount = 0.0
            shipping_amount = 70.0
            cart_product = Cart.objects.filter(user=request.user)
            for p in cart_product:
                amount += (p.quantity * p.product.discount_price)
            total_amount = shipping_amount + amount  
            data = {
                'quantity': c.quantity,
                'amount': amount,
                'total_amount': total_amount,
            }
            return Response(data)
        except Cart.DoesNotExist:
            return Response({"error": "Cart item not found for this user and product."}, status=404)


@api_view(['GET']) 
@permission_classes([IsAuthenticated])
def minus_cart_api(request,pk):
    if request.method == "GET":
        try:
            c = Cart.objects.get(Q(user=request.user) & Q(product=pk))
            c.quantity -= 1
            c.save()
            amount = 0.0
            sniping_amount = 70.0
            cart_product = [p for p in Cart.objects.all() if p.user == request.user]
            if cart_product:
                for p in cart_product:
                    temamount = (p.quantity * p.product.discount_price)
                    amount += temamount
                data = {
                    'quantity': c.quantity,
                    'amount': amount,
                    'total_amount': sniping_amount + amount,
                }
                return Response(data, status=200) 
        except Cart.DoesNotExist:
            return Response({"error": "Cart item not found for this user and product."}, status=404)
@permission_classes([IsAuthenticated])
def remove_cart_api(request,pk):
    try:
        cart_item = get_object_or_404(Cart, Q(user=request.user) & Q(product=pk))
        cart_item.delete()
        amount = 0.0
        shipping_amount = 70.0
        cart_products = Cart.objects.filter(user=request.user)
        for item in cart_products:
            amount += item.quantity * item.product.discount_price
        total_amount = amount + shipping_amount
        return Response({
            'amount': amount,
            'total_amount': total_amount
        })
    except Cart.DoesNotExist:
        return Response({"error": "Cart item not found for this user and product."}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def profile_api(request):
    if request.method == 'POST':
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = Customer(user=request.user, **serializer.validated_data)
            customer.save()
            return Response({"message": "Profile updated successfully"}, status=200)
        else:
            return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def address_api(request):
    customer = Customer.objects.filter(user=request.user)
    if not customer.exists():
        return Response({"message": "No customer data found"}, status=404)
    serializer = CustomerSerializer(customer, many=True)
    return Response({"customer": serializer.data}, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def orders_api(request):
    orders = OrderPlaced.objects.filter(user=request.user)
    if not orders.exists():
        return Response({"message": "No orders found"}, status=404)
    serializer = OrderPlacedSerializer(orders, many=True)
    return Response({"orders": serializer.data}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def change_password_api(request):
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    if not new_password or not confirm_password:
        return Response(
            {"error": "Please fill all the fields"},
            status=400  
        )
    if new_password != confirm_password:
        return Response(
            {"error": "Passwords do not match"},
            status=400
        )
    user = request.user
    user.set_password(new_password)
    user.save()
    return Response(
        {"success": "Your password has been changed successfully"},
        status=200
    )

@api_view(['GET'])
@permission_classes([AllowAny])  
def mobile_api(request, data=None):
    if data == 'None':
        mobiles = Product.objects.filter(category='M')  
    elif data in ["redmi", "realme", "iphone", "vivo"]:
        mobiles = Product.objects.filter(category='M', brand=data) 
    elif data == 'bellow':
        mobiles = Product.objects.filter(category='M', selling_price__lt=10000)  
    elif data == 'above':
        mobiles = Product.objects.filter(category='M', selling_price__gt=10000)
    else:
        mobiles = Product.objects.filter(category='M') 
    mobile_data = list(mobiles.values('id', 'title', 'brand','description' ,'selling_price','discount_price', 'category','created_date','product_image'))
    return Response({"mobiles": mobile_data}, status=200)

@api_view(['GET'])
@permission_classes([AllowAny])
def laptop_api(request,data=None):
 laptops = Product.objects.filter(category='L')
 if data == None:
   laptops = Product.objects.filter(category='L')
 elif data ==  'hp' or data == 'iphone' or data == 'dell':
   laptops = Product.objects.filter(category='L', brand=data)
 laptop_data =list(laptops.values('id', 'title', 'brand','description' ,'selling_price','discount_price', 'category','created_date','product_image'))  
 return Response({'laptop_data' : laptop_data},status=200)

@api_view(['GET'])
@permission_classes([AllowAny])
def topwear_api(request):
  topwears = Product.objects.filter(category='TW')
  topwear_data =list(topwears.values('id', 'title', 'brand','description' ,'selling_price','discount_price', 'category','created_date','product_image')) 
  return Response({'topwear_data' : topwear_data},status=200)

@api_view(['GET'])
@permission_classes([AllowAny])
def buttomwear_api(request):
  buttomwear = Product.objects.filter(category='BW')
  buttomwear_data =list(buttomwear.values('id', 'title', 'brand','description' ,'selling_price','discount_price', 'category','created_date','product_image')) 
  return Response({'buttomwear_data' : buttomwear_data},status=200)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response({"error": "Please provide both username and password"}, status=400)
    user = authenticate(username=username, password=password)
    if user is not None:
        token = get_tokens_for_user(user)
        auth_login(request, user)
        return Response({'token':token,"success": "Successfully logged in"}, status=200)
    else:
        return Response({"error": "Invalid username or password"}, status=401)

@api_view(['POST'])
@permission_classes([AllowAny])
def customer_registration_api(request):
    username = request.data.get('username')
    firstname = request.data.get('firstname')
    lastname = request.data.get('lastname')
    email = request.data.get('email')
    password = request.data.get('password')
    confirm_password = request.data.get('confirm_password')  # Ensure correct key
    if not all([username, firstname, lastname, email, password, confirm_password]):
        return Response({"error": "Please fill all the fields"}, status=400)
    if password != confirm_password:
        return Response({"error": "Passwords do not match"}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already taken"}, status=400)
    try:
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = firstname
        user.last_name = lastname
        user.save()
        token = get_tokens_for_user(user)
        user = authenticate(username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return Response({'token': token, "success": "Account created successfully and you are logged in!"}, status=201)
        else:
            return Response({"error": "Account created, but login failed. Please try to log in manually."}, status=500)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def checkout_api(request):
    user = request.user
    address = Customer.objects.filter(user=user)
    cart_item = Cart.objects.filter(user=user)
    cart_product = Cart.objects.filter(user=user).select_related('product')
    total_amount = sum([p.quantity * p.product.discount_price for p in cart_product]) + 70.0
    response_data = {
        'total_amount': total_amount,
        'address': list(address.values()),  
        'cart_items': list(cart_item.values(
            'id', 
            'product__name',
            'quantity', 
            'product__discount_price'
        ))  
    }

    return Response(response_data)

@api_view(['POST'])
def payment_done_api(request):
    user = request.user
    custid = request.data.get('custid')
    if not custid:
        raise ValidationError("Customer ID is required")
    customer = get_object_or_404(Customer, id=custid)
    cart_item = Cart.objects.filter(user=user)
    if not cart_item:
        return Response({"message": "No items in the cart"}, status=400)
    for c in cart_item:
        OrderPlaced.objects.create(user=user, customer=customer, product=c.product, quantity=c.quantity)
        c.delete()
    return Response({"message": "Payment processed successfully, order placed!"}, status=200)

@api_view(['POST'])
def logout_api(request):
    auth_logout(request)
    return Response({'message': 'Successfully logged out!'}, status=200)

@api_view(['POST'])
def new_password_api(request, email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid email address'})
    new_password = request.data.get('new_password', '').strip()
    confirm_password = request.data.get('confirm_password', '').strip()
    if not new_password or not confirm_password:
        return Response({'error': 'Please fill all the fields'})
    if new_password == confirm_password:
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password successfully reset!'})
    else:
        return Response({'error': 'Passwords do not match'})

@api_view(['GET'])
def search_api(request, pk):
    product = Product.objects.filter(id=pk).first()  
    if product:
        keyword = request.GET.get('keyword', '') 
        if keyword: 
            products = Product.objects.filter(title__icontains=keyword, id=pk).order_by("-created_date")
            serialized_products = ProductSerializer(products, many=True)
            return Response({'products': serialized_products.data, 'keyword': keyword})
        else:
            products = Product.objects.filter(id=pk).order_by("-created_date")
            serialized_products = ProductSerializer(products, many=True)
            return Response({'products': serialized_products.data})
    return Response({'error': 'Product not found with the given pk'}, status=404)

