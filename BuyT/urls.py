from django.urls import path
from . import views
from . import admin2
from .views import test_ai


urlpatterns = [

    # =========================
    # USER
    # =========================
    path(
    "forgot-password/",
    views.forgot_password,
    name="forgot_password"
),

    path(
    "verify-otp/",
    views.verify_otp,
    name="verify_otp"
),

    path(
    "reset-password/",
    views.reset_password,
    name="reset_password"
),
    path("login/", views.login, name="login"),
    path("sign/", views.sign, name="sign"),
    # USER SIGNUP OTP
path("send-signup-otp/", views.send_signup_otp, name="send_signup_otp"),
path("verify-signup-otp/", views.verify_signup_otp, name="verify_signup_otp"),

# ADMIN SIGNUP OTP
path("send-admin-signup-otp/", views.send_admin_signup_otp, name="send_admin_signup_otp"),
path("verify-admin-signup-otp/", views.verify_admin_signup_otp, name="verify_admin_signup_otp"),
    path("logout/", views.logout, name="logout"),

    path("home/", views.home, name="home"),
    path("profile/", views.profile, name="profile"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),

    # =========================
    # PRODUCTS - USER
    # =========================

    path("products/", views.products, name="products"),
    path("category/<int:id>/", views.category_products, name="category_products"),
    path("search/", views.search, name="search"),

    # =========================
    # CART
    # =========================

    path("cart/", views.cart, name="cart"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("increase-quantity/<int:id>/", views.increase_quantity, name="increase_quantity"),
    path("decrease-quantity/<int:id>/", views.decrease_quantity, name="decrease_quantity"),
    path("remove-item/<int:id>/", views.remove_item, name="remove_item"),

    # =========================
    # CHECKOUT / ORDERS
    # =========================

    path("checkout/", views.checkout, name="checkout"),
    path("place-order/", views.place_order, name="place_order"),
    path(
        "order-success/<int:order_id>/",
        views.order_success,
        name="order_success"
    ),
    path("orders/", views.orders, name="orders"),

    # =========================
    # WISHLIST
    # =========================

    path("wishlist/", views.wishlist, name="wishlist"),
    path(
        "wishlist/add/<int:product_id>/",
        views.add_to_wishlist,
        name="add_to_wishlist"
    ),
    path(
        "wishlist/remove/<int:product_id>/",
        views.remove_from_wishlist,
        name="remove_from_wishlist"
    ),

    # =========================
    # OTHER PAGES
    # =========================

    path("categories/", views.categories, name="categories"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("privacy/", views.privacy, name="privacy"),
    path("social/", views.social, name="social"),
    path("terms/", views.terms, name="terms"),

    # =========================
    # AI
    # =========================

    path("api/chat/", views.chat_api, name="chat_api"),
    path("test-ai/", test_ai, name="test_ai"),
    path("chat/", views.chat_ai, name="chat_ai"),
    path("chatbot/", views.chatbot, name="chatbot"),

    # =========================
    # ADMIN AUTHENTICATION
    # =========================

    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),

    path(
        "admin-login/",
        views.admin_login,
        name="admin_login"
    ),

    path(
        "admin-signup/",
        views.admin_signup,
        name="admin_signup"
    ),

    path(
    "admin-forgot-password/",
    views.admin_forgot_password,
    name="admin_forgot_password"
),

    path(
    "admin-verify-otp/",
    views.admin_verify_otp,
    name="admin_verify_otp"
),

    path(
    "admin-reset-password/",
    views.admin_reset_password,
    name="admin_reset_password"
),

    # =========================
    # ADMIN - PRODUCTS
    # =========================

    path(
        "addproduct/",
        admin2.addproduct,
        name="addproduct"
    ),

    path(
        "admin-products/",
        admin2.read_products,
        name="admin_products"
    ),

    path(
        "admin-products/edit/<int:id>/",
        admin2.update_product,
        name="update_product"
    ),

    path(
        "admin-products/delete/<int:id>/",
        admin2.delete_product,
        name="delete_product"
    ),

    # =========================
    # ADMIN - BRANDS
    # =========================

    path(
        "addbrand/",
        admin2.addbrand,
        name="addbrand"
    ),

    path(
        "admin-brands/",
        admin2.read_brands,
        name="admin_brands"
    ),

    path(
        "admin-brands/edit/<int:id>/",
        admin2.update_brand,
        name="update_brand"
    ),

    path(
        "admin-brands/delete/<int:id>/",
        admin2.delete_brand,
        name="delete_brand"
    ),

    # =========================
    # ADMIN - CATEGORIES
    # =========================

    path(
        "addcategory/",
        admin2.addcategory,
        name="addcategory"
    ),

    path(
        "admin-logout/",
        views.admin_logout,
        name="admin_logout"
    ),

    path(
        "admin-categories/",
        admin2.read_categories,
        name="admin_categories"
    ),

    path(
        "admin-categories/edit/<int:id>/",
        admin2.update_category,
        name="update_category"
    ),

    path(
        "admin-categories/delete/<int:id>/",
        admin2.delete_category,
        name="delete_category"
    ),

    # =========================
    # ADMIN - USERS
    # =========================

    path(
        "admin-users/",
        admin2.read_users,
        name="admin_users"
    ),

    path(
        "admin-users/add/",
        admin2.add_user,
        name="add_user"
    ),

    path(
        "admin-users/edit/<int:id>/",
        admin2.update_user,
        name="update_user"
    ),

    path(
        "admin-users/delete/<int:id>/",
        admin2.delete_user,
        name="delete_user"
    ),

    # =========================
    # DEFAULT
    # =========================

    path(
        "",
        views.choose_role,
        name="choose_role"
    ),

    path(
    "product/<int:product_id>/",
    views.product_detail,
    name="product_detail"
),

path(
    "product/<int:product_id>/",
    views.product_detail,
    name="product_detail"
),

path(
    "admin-orders/",
    views.admin_orders,
    name="admin_orders"
),

path(
    "admin-payments/",
    views.admin_payments,
    name="admin_payments"
),

path(
    "admin-profile/",
    views.admin_profile,
    name="admin_profile"
),

    

    
]