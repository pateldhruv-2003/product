from django.shortcuts import render, redirect,get_object_or_404
from.models import product,Order
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
import uuid
from django.contrib import messages
from django.http import JsonResponse
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
import razorpay
from django.core.paginator import Paginator
from decimal import Decimal

# Create your views here.
def showproductlist(request):
    search = request.GET.get('search')
  
    if search:  
        print(search)
        pro = product.objects.filter(name__icontains=search)
    else:       
        pro= product.objects.all()
    return render(request,'showproductlist.html',{'product':pro,'que':search})

@login_required(login_url='login_view')    
def addproduct(request):
    if request.method == "POST":
        s = product()
        s.name  = request.POST.get('txtname') 
        s.description = request.POST.get('txtdescription')
        s.price = request.POST.get('txtprice')
        s.image = request.FILES.get('txtimage')
        s.save()
        return redirect(showproductlist)
        
    else:
        return render(request,"addproduct.html")

def delete_product(request,id):
    p = product.objects.get(id = id)
    p.delete()
    return redirect(showproductlist)

@login_required(login_url='login_view')    
def edit_product(request,id):
    s = product.objects.get(id=id)
    if request.method == "POST":
        s.name  = request.POST.get('txtname') 
        s.description= request.POST.get('txtdescription')
        s.price =  request.POST.get('txtprice')
        s.image = request.FILES.get('txtimage')
        s.save()
        return redirect(showproductlist)
        
    else:
        return render(request,"addedit.html",{"product" : s})
    
    
@login_required(login_url='login_view')    
def add_to_cart(request, product_id):
    pro = get_object_or_404(product, id=product_id)
    cart = request.session.get("cart", {})

    if str(product_id) in cart:
        cart[str(product_id)]["quantity"] += 1  # use lowercase consistently
    else:
        cart[str(product_id)] = {
            "name": pro.name,
            "price": float(pro.price),
            "quantity": 1,
            "image": pro.image.url if pro.image else None
        }

    print(cart)

    request.session["cart"] = cart
    request.session.modified = True
    return redirect('cart_view')

@login_required(login_url='login_view')    
def cart_view(request):
    cart = request.session.get("cart", {})
    total_amount = 0
    print(cart)

    for item in cart.values():
        quantity = item.get("quantity") or item.get("quantity") or 0
        total_amount += float(item["price"]) * quantity

    return render(request, "cart.html", {"cart": cart, "total_amount": total_amount})
       
 
def logout(request):
    request.session.flush()  # Clears all session data
    return redirect('login_view') 

def productdetail(request,id):
    a = product.objects.get(id=id)
    return render(request,"amazondetail.html",{"product" : a})

  
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({"success": True})

        return JsonResponse({"success": False, "errors": "Invalid username or password!"})

    return render(request, "login.html")

def update_cart(request,product_id,action):
    cart = request.session.get("cart",{})
    
    if str(product_id) in cart:
        if action == "increase" :
            cart[str(product_id)] ["quantity"]+=1
        elif action == "decrease" :
            if cart[str(product_id)]["quantity"]>1:
                cart[str(product_id)]["quantity"]-=1
            else:
                del cart[str(product_id)]
    request.session["cart"] = cart
    request.session.modified = True
    return redirect("cart_view")

def delete_from_cart(request,product_id):
    cart = request.session.get("cart",{})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session["cart"] = cart
        request.session.modified = True
    return redirect("cart_view")        
                    
def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        errors = []

        # Validation
        if not username or not email or not password or not confirm_password:
            errors.append("All fields are required!")
        if password != confirm_password:
            errors.append("Passwords do not match!")
        if User.objects.filter(username=username).exists():
            errors.append("Username already exists!")

        if errors:
            return JsonResponse({"success": False, "errors": errors})

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        
        return JsonResponse({"success": True})

    return render(request, "register.html")

def productdetail(request,id):
    a = product.objects.get(id=id)
    return render(request,"productdetail.html",{"product" : a})
 
                    
def payment(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    order_amount = 50000  # ₹500 in paise
    order_currency = 'INR'
    order_receipt = 'order_rcptid_11'

    order = client.order.create(dict(amount=order_amount, currency=order_currency, receipt=order_receipt))
    
    context = {
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order_id': order['id'],
        'amount': order_amount,
        'currency': order_currency
    }
    return render(request, 'payment.html', context)

@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except:
            data = request.POST
        
        params_dict = {
            'razorpay_order_id': data.get('razorpay_order_id'),
            'razorpay_payment_id': data.get('razorpay_payment_id'),
            'razorpay_signature': data.get('razorpay_signature')
        }

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            client.utility.verify_payment_signature(params_dict)
            return render(request, 'success.html')
        except:
            return render(request, 'failure.html')

    return HttpResponseBadRequest()



def chekout(request):
    return render(request, 'checkout.html')

