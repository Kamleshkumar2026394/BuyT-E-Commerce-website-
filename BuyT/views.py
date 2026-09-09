from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse , JsonResponse
from.models import signup,category,brand,product,Cart,CartItem,Order, OrderItem,Admin, Wishlist
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.core.paginator import Paginator
import json
import os
import random
import time
from django.db.models import Sum
from django.core.mail import EmailMessage
from .ai_service import ask_ai
from django.views.decorators.http import require_POST
from functools import wraps
from django.conf import settings
import requests
# Create your views here.



def send_email_via_brevo(subject, body, to_email, reply_to=None):
    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "api-key": settings.BREVO_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "sender": {
            "email": settings.DEFAULT_FROM_EMAIL,
            "name": "BuyT"
        },
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": body,
    }

    if reply_to:
        payload["replyTo"] = {"email": reply_to}

    response = requests.post(url, json=payload, headers=headers, timeout=10)

    if response.status_code != 201:
        raise Exception(
            f"Brevo send failed: {response.status_code} {response.text}"
        )

    return True


def login_required_custom(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        user_id = request.session.get("user_id")

        if not user_id:
            return redirect("login")

        try:
            signup.objects.get(id=user_id)
        except signup.DoesNotExist:
            request.session.flush()
            return redirect("login")

        return view_func(request, *args, **kwargs)

    return wrapper

@login_required_custom
def home(request):
    categories = category.objects.all()[:4]
    products = product.objects.all()[:4]
    brands = brand.objects.all()[:4] 
    return render(request,"index.html",{
       "categories": categories,
       "products": products,
       "brands":brands
    })

def sign(request):

    if request.method == "POST":

        Full_Name = request.POST.get("fullname", "").strip()
        Email = request.POST.get("email", "").strip()
        Phone = request.POST.get("phone", "").strip()
        Password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Required fields
        if not Full_Name or not Email or not Phone or not Password:
            messages.error(request, "All fields are required.")
            return redirect("sign")

        # Password match
        if Password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("sign")

        # Email already exists
        if signup.objects.filter(Email=Email).exists():
            messages.error(request, "Email already registered.")
            return redirect("sign")

        # Phone already exists
        if signup.objects.filter(Phone=Phone).exists():
            messages.error(request, "Phone number already registered.")
            return redirect("sign")

        # Check whether this email was verified
        verified_email = request.session.get(
            "signup_verified_email"
        )

        if verified_email != Email:
            messages.error(
                request,
                "Please verify your email with OTP first."
            )
            return redirect("sign")

        # Create account only after OTP verification
        signup.objects.create(
            Full_Name=Full_Name,
            Email=Email,
            Phone=Phone,
            Password=make_password(Password)
        )

        # Clear verification session
        request.session.pop(
            "signup_verified_email",
            None
        )

        messages.success(
            request,
            "Email verified and account created successfully. Please login."
        )

        return redirect("login")

    return render(request, "sign.html")

@require_POST
def send_signup_otp(request):

    email = request.POST.get("email", "").strip()

    if not email:
        return JsonResponse({
            "success": False,
            "message": "Please enter your email."
        })

    # Check existing email
    if signup.objects.filter(Email=email).exists():
        return JsonResponse({
            "success": False,
            "message": "Email already registered."
        })

    # Generate OTP
    otp = str(random.randint(100000, 999999))

    # Send email
    try:

        send_email_via_brevo(
    subject="BuyT Email Verification OTP",
    body=f"""
Hello,

Your BuyT email verification OTP is:

{otp}

This OTP is valid for 5 minutes.

Please enter this OTP on the BuyT signup page.

Regards,
BuyT Team
""",
    to_email=email,
)

    except Exception as e:

        print("SIGNUP OTP EMAIL ERROR:", repr(e))

        return JsonResponse({
            "success": False,
            "message": "Unable to send OTP. Please try again later."
        }, status=500)

    # Store OTP ONLY after email was successfully sent
    request.session["signup_email"] = email
    request.session["signup_otp"] = otp
    request.session["signup_otp_time"] = time.time()

    return JsonResponse({
        "success": True,
        "message": "OTP sent successfully."
    })

@require_POST
def verify_signup_otp(request):

    email = request.POST.get("email", "").strip()
    entered_otp = request.POST.get("otp", "").strip()

    session_email = request.session.get(
        "signup_email"
    )

    stored_otp = request.session.get(
        "signup_otp"
    )

    otp_time = request.session.get(
        "signup_otp_time"
    )

    # Check email
    if not session_email or email != session_email:
        return JsonResponse({
            "success": False,
            "message": "Email verification session expired. Please send OTP again."
        })

    # Check OTP exists
    if not stored_otp:
        return JsonResponse({
            "success": False,
            "message": "OTP not found. Please request a new OTP."
        })

    # Check expiry
    if otp_time and time.time() - otp_time > 300:

        request.session.pop("signup_otp", None)
        request.session.pop("signup_otp_time", None)

        return JsonResponse({
            "success": False,
            "message": "OTP has expired. Please request a new OTP."
        })

    # Check OTP
    if entered_otp != stored_otp:
        return JsonResponse({
            "success": False,
            "message": "Invalid OTP."
        })

    # Mark email as verified
    request.session["signup_verified_email"] = email

    # Remove OTP
    request.session.pop("signup_otp", None)
    request.session.pop("signup_otp_time", None)

    return JsonResponse({
        "success": True,
        "message": "Email verified successfully."
    })


def login(request):
    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = signup.objects.filter(Email=email).first()

        if user:
            if check_password(password, user.Password):

                request.session["user_id"] = user.id
                request.session["user_name"] = user.Full_Name

                return redirect("home")

            else:
                return render(request, "login.html",
                              {"message": "Incorrect Password"})

        else:
            return render(request, "login.html",
                          {"message": "Email does not exist"})

    return render(request, "login.html")
     

@login_required_custom
def categories(request):
     cat = category.objects.all()
     return render(request,"categories.html", {
        "categories": cat
    })

@login_required_custom
def category_products(request, id):

    cat = get_object_or_404(category, id=id)

    product_list = product.objects.filter(
        category=cat
    ).order_by("-created_at")

    paginator = Paginator(product_list, 16)

    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    return render(request, "category_products.html", {
        "category": cat,
        "products": products
    })

@login_required_custom
def about(request):
    return render(request,"About.html")


@login_required_custom
def contact(request):

    user_id = request.session.get("user_id")

    if not user_id:
        messages.error(request, "Please login first.")
        return redirect("login")

    user = signup.objects.get(id=user_id)

    if request.method == "POST":

        message = request.POST.get("message")

        email_body = f"""
New Message from BuyT

User Name: {user.Full_Name}
User Email: {user.Email}

Message:
{message}
"""

        send_email_via_brevo(
    subject="New Message from BuyT User",
    body=email_body,
    to_email=settings.DEFAULT_FROM_EMAIL,
    reply_to=user.Email,
)

        messages.success(
            request,
            "Your message has been sent successfully!"
        )

        return redirect("contact")

    return render(request, "Contact.html")

@login_required_custom
def products(request):

    # Get all products
    product_list = product.objects.all()

    # =========================
    # PAGINATION
    # =========================

    paginator = Paginator(product_list, 16)  # 16 products per page

    page_number = request.GET.get("page")

    products = paginator.get_page(page_number)


    # =========================
    # WISHLIST
    # =========================

    user_id = request.session.get("user_id")

    if user_id:

        wishlist_ids = set(
            Wishlist.objects.filter(
                user_id=user_id
            ).values_list(
                "product_id",
                flat=True
            )
        )

    else:

        wishlist_ids = set()


    # =========================
    # RENDER
    # =========================

    return render(
        request,
        "Products.html",
        {
            "products": products,
            "wishlist_ids": wishlist_ids,
        }
    )
def product_detail(request, product_id):

    product_obj = get_object_or_404(
        product,
        id=product_id
    )

    user_id = request.session.get("user_id")

    is_wishlisted = False

    if user_id:
        is_wishlisted = Wishlist.objects.filter(
            user_id=user_id,
            product_id=product_id
        ).exists()

    return render(
        request,
        "product_detail.html",
        {
            "product": product_obj,
            "is_wishlisted": is_wishlisted,
        }
    )


@login_required_custom
def add_to_cart(request, product_id):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")


    user = get_object_or_404(
        signup,
        id=user_id
    )


    pro = get_object_or_404(
        product,
        id=product_id
    )


    if pro.stock <= 0:

        messages.error(
            request,
            "This product is out of stock."
        )

        return redirect("products")


    cart, created = Cart.objects.get_or_create(
        user=user
    )


    item = CartItem.objects.filter(
        cart=cart,
        product=pro
    ).first()


    if item:

        if item.quantity >= pro.stock:

            messages.error(
                request,
                "You cannot add more than available stock."
            )

            return redirect("cart")


        item.quantity += 1
        item.save()

    else:

        CartItem.objects.create(
            cart=cart,
            product=pro,
            quantity=1
        )


    return redirect("cart")

@login_required_custom
def cart(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = signup.objects.get(id=user_id)

    cart = Cart.objects.filter(user=user).first()

    items = []

    total = 0

    if cart:

        items = CartItem.objects.filter(cart=cart)

        for item in items:

            total += item.product.price * item.quantity

    return render(request,
                  "cart.html",
                  {
                      "items": items,
                      "total": total
                  })

@login_required_custom
def privacy(request):
    return render(request,"privacy.html")

@login_required_custom
def terms(request):
    return render(request,"terms.html")

@login_required_custom
def social(request):
    return render(request,"social.html")

@login_required_custom
def increase_quantity(request, id):

    user_id = request.session.get("user_id")

    item = get_object_or_404(
        CartItem,
        id=id,
        cart__user_id=user_id
    )

    if item.quantity < item.product.stock:
        item.quantity += 1
        item.save()
    else:
        messages.error(
            request,
            "You cannot add more than available stock."
        )

    return redirect("cart")


@login_required_custom
def decrease_quantity(request, id):

    user_id = request.session.get("user_id")

    item = get_object_or_404(
        CartItem,
        id=id,
        cart__user_id=user_id
    )

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect("cart")


@login_required_custom
def remove_item(request, id):

    user_id = request.session.get("user_id")

    item = get_object_or_404(
        CartItem,
        id=id,
        cart__user_id=user_id
    )

    item.delete()

    return redirect("cart")

@login_required_custom
def profile(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = get_object_or_404(
        signup,
        id=user_id
    )

    return render(
        request,
        "profile.html",
        {
            "user": user
        }
    )

@login_required_custom
def edit_profile(request):
    return render(request, "edit_profile.html")


# Searching products

@login_required_custom
def search(request):
    query = request.GET.get("q", "").strip()

    product_list = product.objects.none()

    if query:
        product_list = product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__brand_name__icontains=query) |
            Q(category__category_name__icontains=query)
        ).distinct()

    paginator = Paginator(product_list, 12)

    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    return render(request, "search.html", {
        "products": products,
        "query": query
    })


def logout(request):
    request.session.flush()
    return redirect("login")

@login_required_custom
def checkout(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = get_object_or_404(
        signup,
        id=user_id
    )

    cart = Cart.objects.filter(
        user=user
    ).first()

    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    items = CartItem.objects.filter(
        cart=cart
    ).select_related("product")

    if not items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    total = 0

    for item in items:
        total += item.product.price * item.quantity

    return render(
        request,
        "checkout.html",
        {
            "items": items,
            "total": total
        }
    )

@login_required_custom
def place_order(request):

    if request.method != "POST":
        return redirect("checkout")


    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")


    user = get_object_or_404(
        signup,
        id=user_id
    )


    cart = Cart.objects.filter(
        user=user
    ).first()


    if not cart:
        messages.error(
            request,
            "Your cart is empty."
        )

        return redirect("cart")


    items = CartItem.objects.filter(
        cart=cart
    ).select_related("product")


    if not items.exists():

        messages.error(
            request,
            "Your cart is empty."
        )

        return redirect("cart")


    payment_method = request.POST.get(
        "payment_method"
    )


    if payment_method not in ["COD", "ONLINE"]:

        messages.error(
            request,
            "Invalid payment method."
        )

        return redirect("checkout")


    # Calculate total

    total = 0

    for item in items:

        # Check stock
        if item.quantity > item.product.stock:

            messages.error(
                request,
                f"Only {item.product.stock} "
                f"items available for "
                f"{item.product.name}."
            )

            return redirect("cart")


        total += (
            item.product.price *
            item.quantity
        )


    # Create Order

    order = Order.objects.create(

        user=user,

        total_amount=total,

        payment_method=payment_method,

        payment_status="PENDING",

        order_status="PLACED"

    )


    # Create Order Items

    for item in items:

        OrderItem.objects.create(

            order=order,

            product=item.product,

            quantity=item.quantity,

            price=item.product.price

        )


        # Reduce stock

        item.product.stock -= item.quantity

        item.product.save(
            update_fields=["stock"]
        )


    # Clear cart

    items.delete()


    return redirect(
        "order_success",
        order_id=order.id
    )

@login_required_custom
def order_success(request, order_id):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")


    order = get_object_or_404(
        Order,
        id=order_id,
        user_id=user_id
    )


    return render(
        request,
        "order_success.html",
        {
            "order": order
        }
    )

@login_required_custom
def orders(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")


    user = get_object_or_404(
        signup,
        id=user_id
    )


    orders = Order.objects.filter(
        user=user
    ).prefetch_related(
        "items__product"
    ).order_by("-created_at")


    return render(
        request,
        "orders.html",
        {
            "orders": orders
        }
    )
@require_POST
def chat_api(request):

    try:

        data = json.loads(request.body)

        message = data.get("message", "").strip()

        if not message:

            return JsonResponse({
                "reply": "Please enter a message."
            })


        # Temporary response
        reply = (
            "Hi! I'm BuyT AI. "
            "The AI assistant is being connected. "
            f"You said: {message}"
        )


        return JsonResponse({
            "reply": reply
        })


    except Exception as e:

        return JsonResponse(
            {
                "reply": "Something went wrong."
            },
            status=400
        )





def test_ai(request):
    answer = ask_ai("Hello, introduce yourself as a shopping assistant for BuyT.")
    return JsonResponse({"answer": answer})


@require_POST
def chat_ai(request):
    try:
        data = json.loads(request.body)
        message = data.get("message", "").strip()

        if not message:
            return JsonResponse(
                {"error": "Message is required"},
                status=400
            )

        # Search products based on user's question
        products = product.objects.select_related(
            "brand",
            "category"
        ).all()

        # Build website context
        product_context = ""

        for p in products:
            product_context += f"""
Product:
Name: {p.name}
Price: ₹{p.price}
Brand: {p.brand.brand_name}
Category: {p.category.category_name}
Description: {p.description}
Stock: {p.stock}
Rating: {p.rating}
Reviews: {p.reviews}
-------------------------
"""

        # Send website information to AI
        prompt = f"""
You are the official AI shopping assistant for BuyT.

You are answering questions about the BuyT e-commerce website.

IMPORTANT RULES:
1. Answer based ONLY on the BuyT website information provided below.
2. Do not invent products.
3. Do not invent prices.
4. Do not invent stock.
5. If a product is not available in the provided data, clearly say that it is not available.
6. Be helpful and conversational.
7. If the user asks for product recommendations, recommend products from the provided data.
8. Mention price, brand, category, rating and stock when useful.

BUY T WEBSITE PRODUCT DATA:

{product_context}

USER QUESTION:
{message}

Give a helpful answer based on the BuyT website.
"""

        answer = ask_ai(prompt)

        return JsonResponse({
            "answer": answer
        })

    except Exception as e:
        print("CHAT AI ERROR:", e)

        return JsonResponse(
            {"error": "Something went wrong with the AI assistant."},
            status=500
        )

def chatbot(request):
    return render(request, "chatbot.html")



def admin_dashboard(request):

    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")

    total_orders = Order.objects.count()

    cancelled_orders = Order.objects.filter(
        order_status="CANCELLED"
    ).count()

    pending_payments = Order.objects.filter(
        payment_status="PENDING"
    ).count()

    total_payments = Order.objects.filter(
        payment_status="PAID"
    ).aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    context = {
        "total_users": signup.objects.count(),
        "total_products": product.objects.count(),
        "total_categories": category.objects.count(),
        "total_brands": brand.objects.count(),

        # Orders
        "total_orders": total_orders,
        "cancelled_orders": cancelled_orders,

        # Payments
        "pending_payments": pending_payments,
        "total_payments": total_payments,
    }

    return render(
        request,
        "admin/dashboard.html",
        context
    )


def admin_login(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        try:

            admin = Admin.objects.get(
                email=email
            )

            if admin.check_password(password):

                request.session["admin_logged_in"] = True
                request.session["admin_id"] = admin.id
                request.session["admin_name"] = admin.name

                return redirect(
                    "admin_dashboard"
                )

            else:

                messages.error(
                    request,
                    "Invalid password."
                )

        except Admin.DoesNotExist:

            messages.error(
                request,
                "Admin not found."

            )

    return render(
        request,
        "admin/admin_login.html"
    )

def admin_signup(request):

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        password = request.POST.get(
            "password"
        )

        confirm_password = request.POST.get(
            "confirm_password"
        )


        # Required fields
        if not name or not email or not password:

            return render(
                request,
                "admin/admin_signup.html",
                {
                    "message":
                        "All fields are required."
                }
            )


        # Password match
        if password != confirm_password:

            return render(
                request,
                "admin/admin_signup.html",
                {
                    "message":
                        "Passwords do not match."
                }
            )


        # Existing admin
        if Admin.objects.filter(
            email=email
        ).exists():

            return render(
                request,
                "admin/admin_signup.html",
                {
                    "message":
                        "Admin with this email already exists."
                }
            )


        # Check email verification
        verified_email = request.session.get(
            "admin_signup_verified_email"
        )

        if verified_email != email:

            return render(
                request,
                "admin/admin_signup.html",
                {
                    "message":
                        "Please verify your email with OTP first."
                }
            )


        # Create admin
        admin = Admin(
            name=name,
            email=email
        )

        admin.set_password(password)

        admin.save()


        # Clear verification
        request.session.pop(
            "admin_signup_verified_email",
            None
        )

        request.session.pop(
            "admin_signup_email",
            None
        )


        messages.success(
            request,
            "Admin account created successfully. Please login."
        )

        return redirect(
            "admin_login"
        )


    return render(
        request,
        "admin/admin_signup.html"
    )

@login_required_custom
def add_to_wishlist(request, product_id):

    if not request.session.get("user_id"):
        return redirect("login")

    user_id = request.session.get("user_id")

    user = get_object_or_404(
        signup,
        id=user_id
    )

    product_obj = get_object_or_404(
        product,
        id=product_id
    )

    wishlist_item, created = Wishlist.objects.get_or_create(
        user=user,
        product=product_obj
    )

    return redirect(request.META.get("HTTP_REFERER", "products"))

@login_required_custom
def remove_from_wishlist(request, product_id):

    if not request.session.get("user_id"):
        return redirect("login")

    user_id = request.session.get("user_id")

    Wishlist.objects.filter(
        user_id=user_id,
        product_id=product_id
    ).delete()

    return redirect("wishlist")

@login_required_custom
def wishlist(request):

    if not request.session.get("user_id"):
        return redirect("login")

    user_id = request.session.get("user_id")

    wishlist_items = Wishlist.objects.filter(
        user_id=user_id
    ).select_related("product")

    return render(
        request,
        "wishlist.html",
        {
            "wishlist_items": wishlist_items
        }
    )

def admin_logout(request):
    request.session.pop("admin_logged_in", None)
    request.session.pop("admin_id", None)
    request.session.pop("admin_name", None)

    return redirect("admin_login")

def choose_role(request):
    return render(request, "role.html")




# password

def forgot_password(request):

    if request.method == "POST":

        email = request.POST.get("email", "").strip()

        if not email:
            return render(
                request,
                "forgot_password.html",
                {
                    "message": "Please enter your email."
                }
            )

        user = signup.objects.filter(
            Email=email
        ).first()

        if not user:

            return render(
                request,
                "forgot_password.html",
                {
                    "message": "No account found with this email."
                }
            )

        # Generate 6 digit OTP
        otp = str(random.randint(100000, 999999))

        # Send OTP
        try:

            send_email_via_brevo(
                subject="BuyT Password Reset OTP",
                body=f"""
Hello {user.Full_Name},

Your BuyT password reset OTP is:

{otp}

This OTP is valid for 5 minutes.

If you did not request a password reset, please ignore this email.

Regards,
BuyT Team
""",
                to_email=email,
            )

        except Exception as e:

            print("FORGOT PASSWORD OTP EMAIL ERROR:", repr(e))

            return render(
                request,
                "forgot_password.html",
                {
                    "message": "Unable to send OTP. Please try again later."
                }
            )

        # Store OTP in session ONLY after email was successfully sent
        request.session["reset_email"] = email
        request.session["reset_otp"] = otp
        request.session["reset_otp_time"] = time.time()

        return redirect("verify_otp")

    return render(
        request,
        "forgot_password.html"
    )

def verify_otp(request):

    reset_email = request.session.get("reset_email")
    stored_otp = request.session.get("reset_otp")
    otp_time = request.session.get("reset_otp_time")

    if not reset_email or not stored_otp:

        return redirect("forgot_password")

    if request.method == "POST":

        entered_otp = request.POST.get("otp", "").strip()

        # Check OTP expiry
        if otp_time:

            if time.time() - otp_time > 300:

                request.session.pop("reset_otp", None)
                request.session.pop("reset_otp_time", None)

                return render(
                    request,
                    "verify_otp.html",
                    {
                        "message": "OTP has expired. Please request a new OTP."
                    }
                )

        if entered_otp != stored_otp:

            return render(
                request,
                "verify_otp.html",
                {
                    "message": "Invalid OTP."
                }
            )

        # OTP is correct
        request.session["otp_verified"] = True

        request.session.pop("reset_otp", None)
        request.session.pop("reset_otp_time", None)

        return redirect("reset_password")

    return render(
        request,
        "verify_otp.html"
    )

def reset_password(request):

    if not request.session.get("otp_verified"):

        return redirect("forgot_password")

    email = request.session.get("reset_email")

    if not email:

        return redirect("forgot_password")

    if request.method == "POST":

        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if not password or not confirm_password:

            return render(
                request,
                "reset_password.html",
                {
                    "message": "All fields are required."
                }
            )

        if password != confirm_password:

            return render(
                request,
                "reset_password.html",
                {
                    "message": "Passwords do not match."
                }
            )

        user = signup.objects.filter(
            Email=email
        ).first()

        if not user:

            request.session.flush()

            return redirect("login")

        # Hash new password
        user.Password = make_password(password)

        user.save(
            update_fields=["Password"]
        )

        # Clear reset session data
        request.session.pop("reset_email", None)
        request.session.pop("otp_verified", None)

        messages.success(
            request,
            "Password reset successfully. Please login."
        )

        return redirect("login")

    return render(
        request,
        "reset_password.html"
    )

def admin_forgot_password(request):

    if request.method == "POST":

        email = request.POST.get("email", "").strip()

        if not email:

            return render(
                request,
                "admin/admin_forgot_password.html",
                {
                    "message": "Please enter your email."
                }
            )

        admin = Admin.objects.filter(
            email=email
        ).first()

        if not admin:

            return render(
                request,
                "admin/admin_forgot_password.html",
                {
                    "message": "No admin account found with this email."
                }
            )

        # Generate 6 digit OTP
        otp = str(
            random.randint(100000, 999999)
        )

        # Send OTP email
        try:

            send_email_via_brevo(
                subject="BuyT Admin Password Reset OTP",
                body=f"""
Hello {admin.name},

Your BuyT Admin password reset OTP is:

{otp}

This OTP is valid for 5 minutes.

If you did not request a password reset, please ignore this email.

Regards,
BuyT Team
""",
                to_email=email,
            )

        except Exception as e:

            print("ADMIN FORGOT PASSWORD OTP EMAIL ERROR:", repr(e))

            return render(
                request,
                "admin/admin_forgot_password.html",
                {
                    "message": "Unable to send OTP. Please try again later."
                }
            )

        # Store admin password reset information in session
        request.session["admin_reset_email"] = email
        request.session["admin_reset_otp"] = otp
        request.session["admin_reset_otp_time"] = time.time()

        return redirect("admin_verify_otp")

    return render(
        request,
        "admin/admin_forgot_password.html"
    )

def admin_verify_otp(request):

    reset_email = request.session.get(
        "admin_reset_email"
    )

    stored_otp = request.session.get(
        "admin_reset_otp"
    )

    otp_time = request.session.get(
        "admin_reset_otp_time"
    )

    # If reset process was not started
    if not reset_email or not stored_otp:

        return redirect(
            "admin_forgot_password"
        )

    if request.method == "POST":

        entered_otp = request.POST.get(
            "otp",
            ""
        ).strip()

        # Check OTP expiry
        if otp_time:

            if time.time() - otp_time > 300:

                request.session.pop(
                    "admin_reset_otp",
                    None
                )

                request.session.pop(
                    "admin_reset_otp_time",
                    None
                )

                return render(
                    request,
                    "admin/admin_verify_otp.html",
                    {
                        "message":
                        "OTP has expired. Please request a new OTP."
                    }
                )

        # Check OTP
        if entered_otp != stored_otp:

            return render(
                request,
                "admin/admin_verify_otp.html",
                {
                    "message": "Invalid OTP."
                }
            )

        # OTP verified
        request.session["admin_otp_verified"] = True

        # Remove OTP after successful verification
        request.session.pop(
            "admin_reset_otp",
            None
        )

        request.session.pop(
            "admin_reset_otp_time",
            None
        )

        return redirect(
            "admin_reset_password"
        )

    return render(
        request,
        "admin/admin_verify_otp.html"
    )

def admin_reset_password(request):

    # User must verify OTP first
    if not request.session.get(
        "admin_otp_verified"
    ):

        return redirect(
            "admin_forgot_password"
        )

    email = request.session.get(
        "admin_reset_email"
    )

    if not email:

        return redirect(
            "admin_forgot_password"
        )

    if request.method == "POST":

        password = request.POST.get(
            "password"
        )

        confirm_password = request.POST.get(
            "confirm_password"
        )

        if not password or not confirm_password:

            return render(
                request,
                "admin/admin_reset_password.html",
                {
                    "message":
                    "All fields are required."
                }
            )

        if password != confirm_password:

            return render(
                request,
                "admin/admin_reset_password.html",
                {
                    "message":
                    "Passwords do not match."
                }
            )

        admin = Admin.objects.filter(
            email=email
        ).first()

        if not admin:

            request.session.pop(
                "admin_reset_email",
                None
            )

            request.session.pop(
                "admin_otp_verified",
                None
            )

            return redirect(
                "admin_login"
            )

        # Hash and save new password
        admin.set_password(password)

        admin.save(
            update_fields=["password"]
        )

        # Clear reset session
        request.session.pop(
            "admin_reset_email",
            None
        )

        request.session.pop(
            "admin_otp_verified",
            None
        )

        messages.success(
            request,
            "Admin password reset successfully. Please login."
        )

        return redirect(
            "admin_login"
        )

    return render(
        request,
        "admin/admin_reset_password.html"
    )

@require_POST
def send_admin_signup_otp(request):

    email = request.POST.get("email", "").strip()

    if not email:
        return JsonResponse({
            "success": False,
            "message": "Please enter your email."
        })

    # Check existing admin
    if Admin.objects.filter(email=email).exists():

        return JsonResponse({
            "success": False,
            "message": "Admin with this email already exists."
        })

    # Generate OTP
    otp = str(
        random.randint(100000, 999999)
    )

    # Send email
    try:

        send_email_via_brevo(
            subject="BuyT Admin Email Verification OTP",
            body=f"""
Hello,

Your BuyT Admin signup verification OTP is:

{otp}

This OTP is valid for 5 minutes.

Please enter this OTP on the BuyT Admin Signup page.

Regards,
BuyT Team
""",
            to_email=email,
        )

    except Exception as e:

        print("ADMIN SIGNUP OTP EMAIL ERROR:", repr(e))

        return JsonResponse({
            "success": False,
            "message": "Unable to send OTP. Please try again later."
        }, status=500)

    # Store in session ONLY after email was successfully sent
    request.session["admin_signup_email"] = email
    request.session["admin_signup_otp"] = otp
    request.session["admin_signup_otp_time"] = time.time()

    return JsonResponse({
        "success": True,
        "message": "OTP sent successfully."
    })

@require_POST
def verify_admin_signup_otp(request):

    email = request.POST.get(
        "email",
        ""
    ).strip()

    entered_otp = request.POST.get(
        "otp",
        ""
    ).strip()


    session_email = request.session.get(
        "admin_signup_email"
    )

    stored_otp = request.session.get(
        "admin_signup_otp"
    )

    otp_time = request.session.get(
        "admin_signup_otp_time"
    )


    # Check email
    if not session_email or email != session_email:

        return JsonResponse({
            "success": False,
            "message":
                "Verification session expired. Please send OTP again."
        })


    # OTP missing
    if not stored_otp:

        return JsonResponse({
            "success": False,
            "message":
                "OTP not found. Please request a new OTP."
        })


    # Expiry
    if otp_time and time.time() - otp_time > 300:

        request.session.pop(
            "admin_signup_otp",
            None
        )

        request.session.pop(
            "admin_signup_otp_time",
            None
        )

        return JsonResponse({
            "success": False,
            "message":
                "OTP has expired. Please request a new OTP."
        })


    # Verify OTP
    if entered_otp != stored_otp:

        return JsonResponse({
            "success": False,
            "message": "Invalid OTP."
        })


    # Mark email verified
    request.session[
        "admin_signup_verified_email"
    ] = email


    # Remove OTP
    request.session.pop(
        "admin_signup_otp",
        None
    )

    request.session.pop(
        "admin_signup_otp_time",
        None
    )


    return JsonResponse({
        "success": True,
        "message": "Admin email verified successfully."
    })

def admin_orders(request):

    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")

    orders = Order.objects.select_related(
        "user"
    ).order_by("-created_at")

    return render(
        request,
        "admin/admin_orders.html",
        {
            "orders": orders
        }
    )

def admin_payments(request):

    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")

    orders = Order.objects.select_related(
        "user"
    ).order_by("-created_at")

    return render(
        request,
        "admin/admin_payments.html",
        {
            "orders": orders
        }
    )

def admin_profile(request):

    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")

    admin_id = request.session.get("admin_id")

    if not admin_id:
        return redirect("admin_login")

    admin = get_object_or_404(Admin, id=admin_id)

    return render(
        request,
        "admin/admin_profile.html",
        {
            "admin": admin
        }
    )