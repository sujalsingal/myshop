from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # PRODUCT PAGES
    path("detail/", views.ProductListView.as_view(), name="detail"),
    path(
        "product/<int:product_id>/",
        views.ProductDetailView.as_view(),
        name="product_detail",
    ),
    path(
        "product/quick-view/<int:product_id>/",
        views.quick_view_product,
        name="quick_view_product",
    ),
    # LOGIIN LOGOUT PAGES
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    #  CART PAGES
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path(
        "cart/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"
    ),
    path("cart", views.view_cart, name="view_cart"),
    path(
        "cart/increase/<int:product_id>/",
        views.increase_quantity,
        name="increase_quantity",
    ),
    path(
        "cart/decrease/<int:product_id>/",
        views.decrease_quantity,
        name="decrease_quantity",
    ),
    path("cart/count/", views.cart_count, name="cart_count"),
    #  PAYMENT PAGES
    path(
        "create-checkout-session/",
        views.create_checkout_session,
        name="create_checkout_session",
    ),
    path("success/", views.payment_success, name="payment_success"),
    path("cancel/", views.payment_cancel, name="payment_cancel"),
    # saved pages
    path("saved-items/", views.saved_items_view, name="saved_items"),
    path("save/<int:product_id>/", views.save_product, name="save_product"),
    path("remove-saved/<int:product_id>/", views.remove_saved, name="remove_saved"),
    path("orders/", views.order_history, name="order_history"),
]
