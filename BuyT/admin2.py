from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from functools import wraps

from .models import product, category, brand, signup


# =========================================================
# ADMIN LOGIN CHECK
# =========================================================

def admin_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.session.get("admin_logged_in"):
            return redirect("admin_login")

        return view_func(request, *args, **kwargs)

    return wrapper


# =========================================================
# PRODUCT CRUD
# =========================================================

@admin_required
def addproduct(request):

    if request.method == "POST":

        image = request.FILES.get("image")
        name = request.POST.get("name")
        price = request.POST.get("price")
        description = request.POST.get("description")
        stock = request.POST.get("stock")
        rating = request.POST.get("rating")
        reviews = request.POST.get("reviews")
        brand_id = request.POST.get("brand_id")
        category_id = request.POST.get("category_id")

        product.objects.create(
            image=image,
            name=name,
            price=price,
            description=description,
            stock=stock or 0,
            rating=rating or 0,
            reviews=reviews or 0,
            brand_id=brand_id,
            category_id=category_id
        )

        messages.success(
            request,
            "Product added successfully."
        )

        return redirect("admin_products")

    context = {
        "brands": brand.objects.all(),
        "categories": category.objects.all()
    }

    return render(
        request,
        "admin/productform.html",
        context
    )


@admin_required
def read_products(request):

    products = product.objects.select_related(
        "brand",
        "category"
    ).all().order_by("-id")

    return render(
        request,
        "admin/admin_products.html",
        {
            "products": products
        }
    )


@admin_required
def update_product(request, id):

    item = get_object_or_404(
        product,
        id=id
    )

    if request.method == "POST":

        item.name = request.POST.get("name")
        item.price = request.POST.get("price")
        item.description = request.POST.get("description")

        item.stock = request.POST.get("stock") or 0
        item.rating = request.POST.get("rating") or 0
        item.reviews = request.POST.get("reviews") or 0

        item.brand_id = request.POST.get("brand_id")
        item.category_id = request.POST.get("category_id")

        image = request.FILES.get("image")

        if image:
            item.image = image

        item.save()

        messages.success(
            request,
            "Product updated successfully."
        )

        return redirect("admin_products")

    context = {
        "product": item,
        "brands": brand.objects.all(),
        "categories": category.objects.all()
    }

    return render(
        request,
        "admin/admin_product_form.html",
        context
    )


@admin_required
def delete_product(request, id):

    item = get_object_or_404(
        product,
        id=id
    )

    item.delete()

    messages.success(
        request,
        "Product deleted successfully."
    )

    return redirect("admin_products")


# =========================================================
# BRAND CRUD
# =========================================================

@admin_required
def addbrand(request):

    if request.method == "POST":

        brand_name = request.POST.get("brand_name")
        brand_image = request.FILES.get("brand_image")

        if not brand_name:
            messages.error(
                request,
                "Brand name is required."
            )

            return redirect("addbrand")

        if brand.objects.filter(
            brand_name=brand_name
        ).exists():

            messages.error(
                request,
                "This brand already exists."
            )

            return redirect("addbrand")

        brand.objects.create(
            brand_name=brand_name,
            brand_image=brand_image
        )

        messages.success(
            request,
            "Brand added successfully."
        )

        return redirect("admin_brands")

    return render(
        request,
        "admin/brandform.html"
    )


@admin_required
def read_brands(request):

    brands = brand.objects.all().order_by("-id")

    return render(
        request,
        "admin/admin_brands.html",
        {
            "brands": brands
        }
    )


@admin_required
def update_brand(request, id):

    item = get_object_or_404(
        brand,
        id=id
    )

    if request.method == "POST":

        brand_name = request.POST.get(
            "brand_name"
        )

        if not brand_name:
            messages.error(
                request,
                "Brand name is required."
            )

            return redirect(
                "update_brand",
                id=id
            )

        # Check duplicate brand name
        if brand.objects.filter(
            brand_name=brand_name
        ).exclude(id=id).exists():

            messages.error(
                request,
                "This brand already exists."
            )

            return redirect(
                "update_brand",
                id=id
            )

        item.brand_name = brand_name

        image = request.FILES.get(
            "brand_image"
        )

        if image:
            item.brand_image = image

        item.save()

        messages.success(
            request,
            "Brand updated successfully."
        )

        return redirect("admin_brands")

    return render(
        request,
        "admin/admin_brand_form.html",
        {
            "brand": item
        }
    )


@admin_required
def delete_brand(request, id):

    item = get_object_or_404(
        brand,
        id=id
    )

    # Prevent CASCADE deletion of products
    if item.products.exists():

        messages.error(
            request,
            "Cannot delete this brand because products are using it."
        )

        return redirect("admin_brands")

    item.delete()

    messages.success(
        request,
        "Brand deleted successfully."
    )

    return redirect("admin_brands")


# =========================================================
# CATEGORY CRUD
# =========================================================

@admin_required
def addcategory(request):

    if request.method == "POST":

        category_name = request.POST.get(
            "category_name"
        )

        category_image = request.FILES.get(
            "category_image"
        )

        if not category_name:

            messages.error(
                request,
                "Category name is required."
            )

            return redirect("addcategory")

        if category.objects.filter(
            category_name=category_name
        ).exists():

            messages.error(
                request,
                "This category already exists."
            )

            return redirect("addcategory")

        category.objects.create(
            category_name=category_name,
            category_image=category_image
        )

        messages.success(
            request,
            "Category added successfully."
        )

        return redirect("admin_categories")

    return render(
        request,
        "admin/categoryform.html"
    )


@admin_required
def read_categories(request):

    categories = category.objects.all().order_by("-id")

    return render(
        request,
        "admin/admin_categories.html",
        {
            "categories": categories
        }
    )


@admin_required
def update_category(request, id):

    item = get_object_or_404(
        category,
        id=id
    )

    if request.method == "POST":

        category_name = request.POST.get(
            "category_name"
        )

        if not category_name:

            messages.error(
                request,
                "Category name is required."
            )

            return redirect(
                "update_category",
                id=id
            )

        # Check duplicate category name
        if category.objects.filter(
            category_name=category_name
        ).exclude(id=id).exists():

            messages.error(
                request,
                "This category already exists."
            )

            return redirect(
                "update_category",
                id=id
            )

        item.category_name = category_name

        image = request.FILES.get(
            "category_image"
        )

        if image:
            item.category_image = image

        item.save()

        messages.success(
            request,
            "Category updated successfully."
        )

        return redirect("admin_categories")

    return render(
        request,
        "admin/admin_category_form.html",
        {
            "category": item
        }
    )


@admin_required
def delete_category(request, id):

    item = get_object_or_404(
        category,
        id=id
    )

    # Prevent CASCADE deletion of products
    if item.products.exists():

        messages.error(
            request,
            "Cannot delete this category because products are using it."
        )

        return redirect("admin_categories")

    item.delete()

    messages.success(
        request,
        "Category deleted successfully."
    )

    return redirect("admin_categories")


# =========================================================
# USER CRUD
# =========================================================

@admin_required
def read_users(request):

    users = signup.objects.all().order_by("-id")

    return render(
        request,
        "admin/admin_users.html",
        {
            "users": users
        }
    )


@admin_required
def add_user(request):

    if request.method == "POST":

        full_name = request.POST.get("Full_Name")
        email = request.POST.get("Email")
        phone = request.POST.get("Phone")
        password = request.POST.get("Password")

        # -------------------------
        # Validation
        # -------------------------

        if not full_name:
            messages.error(
                request,
                "Full name is required."
            )

            return redirect("add_user")

        if not email:
            messages.error(
                request,
                "Email is required."
            )

            return redirect("add_user")

        if not phone:
            messages.error(
                request,
                "Phone number is required."
            )

            return redirect("add_user")

        if not password:
            messages.error(
                request,
                "Password is required."
            )

            return redirect("add_user")

        # -------------------------
        # Duplicate Email
        # -------------------------

        if signup.objects.filter(
            Email=email
        ).exists():

            messages.error(
                request,
                "Email already exists."
            )

            return redirect("add_user")

        # -------------------------
        # Duplicate Phone
        # -------------------------

        if signup.objects.filter(
            Phone=phone
        ).exists():

            messages.error(
                request,
                "Phone number already exists."
            )

            return redirect("add_user")

        # -------------------------
        # Create User
        # -------------------------

        signup.objects.create(
            Full_Name=full_name,
            Email=email,
            Phone=phone,
            Password=make_password(password)
        )

        messages.success(
            request,
            "User added successfully."
        )

        return redirect("admin_users")

    return render(
        request,
        "admin/admin_user_form.html"
    )


@admin_required
def update_user(request, id):

    user = get_object_or_404(
        signup,
        id=id
    )

    if request.method == "POST":

        full_name = request.POST.get(
            "Full_Name"
        )

        email = request.POST.get(
            "Email"
        )

        phone = request.POST.get(
            "Phone"
        )

        password = request.POST.get(
            "Password"
        )

        # -------------------------
        # Validation
        # -------------------------

        if not full_name:
            messages.error(
                request,
                "Full name is required."
            )

            return redirect(
                "update_user",
                id=id
            )

        if not email:
            messages.error(
                request,
                "Email is required."
            )

            return redirect(
                "update_user",
                id=id
            )

        if not phone:
            messages.error(
                request,
                "Phone number is required."
            )

            return redirect(
                "update_user",
                id=id
            )

        # -------------------------
        # Duplicate Email
        # -------------------------

        if signup.objects.filter(
            Email=email
        ).exclude(id=id).exists():

            messages.error(
                request,
                "Email already exists."
            )

            return redirect(
                "update_user",
                id=id
            )

        # -------------------------
        # Duplicate Phone
        # -------------------------

        if signup.objects.filter(
            Phone=phone
        ).exclude(id=id).exists():

            messages.error(
                request,
                "Phone number already exists."
            )

            return redirect(
                "update_user",
                id=id
            )

        # -------------------------
        # Update User
        # -------------------------

        user.Full_Name = full_name
        user.Email = email
        user.Phone = phone

        # Only update password if entered
        if password:
            user.Password = make_password(
                password
            )

        user.save()

        messages.success(
            request,
            "User updated successfully."
        )

        return redirect("admin_users")

    return render(
        request,
        "admin/admin_user_form.html",
        {
            "user": user
        }
    )


@admin_required
def delete_user(request, id):

    user = get_object_or_404(
        signup,
        id=id
    )

    user.delete()

    messages.success(
        request,
        "User deleted successfully."
    )

    return redirect("admin_users")