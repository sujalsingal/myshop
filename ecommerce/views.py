from decimal import Decimal
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView
from ecommerce.utils.cart_utils import get_cart_items_and_total
from .models import Category, Order, OrderItem, Product, Review, Saved, Customer

stripe.api_key = settings.STRIPE_SECRET_KEY


def index(request):
    categories = Category.objects.prefetch_related(
        Prefetch(
            "product_set",
            queryset=Product.objects.order_by("-id")[:15],
            to_attr="top_products",
        )
    )
    return render(request, "ecommerce/index.html", {"categories": categories})


class ProductDetailView(DetailView):
    model = Product
    template_name = "ecommerce/product_detail.html"
    context_object_name = "product"
    pk_url_kwarg = "product_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        reviews = product.reviews.all()
        context["reviews"] = reviews
        context["review_count"] = reviews.count()
        context["avg_rating"] = round(
            reviews.aggregate(Avg("rating"))["rating__avg"] or 0, 1
        )
        context["categories"] = Category.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to leave a review.")
            return redirect("login")
        rating = request.POST.get("rating")
        comment = request.POST.get("comment", "")
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError()
        except (ValueError, TypeError):
            messages.error(request, "Rating must be between 1 and 5.")
            return redirect("product_detail", product_id=product.id)
        Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={"rating": rating, "comment": comment},
        )
        messages.success(request, "Your review has been submitted.")
        return redirect("product_detail", product_id=product.id)


class ProductListView(ListView):
    model = Product
    template_name = "ecommerce/detail.html"
    context_object_name = "products"

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search")
        selected_category = self.request.GET.get("category")
        sort_by = self.request.GET.get("sort_by")
        if selected_category:
            queryset = queryset.filter(category__choice__iexact=selected_category)
        if search_query:
            queryset = queryset.filter(
                Q(product_name__icontains=search_query)
                | Q(category__choice__icontains=search_query)
            ).distinct()
        sort_map = {
            "price_asc": "product_price",
            "price_desc": "-product_price",
            "name_asc": "product_name",
            "newest": "-id",
        }
        if sort_by in sort_map:
            queryset = queryset.order_by(sort_map[sort_by])
        else:
            queryset = queryset.order_by("id")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["selected_category"] = self.request.GET.get("category")
        context["search_query"] = self.request.GET.get("search")
        context["selected_sort_by"] = self.request.GET.get("sort_by")
        if self.request.user.is_authenticated:
            saved_product_ids = Saved.objects.filter(
                user=self.request.user
            ).values_list("product_id", flat=True)
            context["saved_product_ids"] = set(saved_product_ids)
        else:
            context["saved_product_ids"] = set()
        return context


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect("index")
        else:
            messages.error(request, "invalid username or password")
        if not username or not password:
            messages.error(request, "All fields are required.")
        elif len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
    return render(request, "ecommerce/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("index")


def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        confirm = request.POST["confirm"]
        if not username or not password:
            messages.error(request, "All fields are required.")
        elif len(password) < 6:
            messages.error(request, "Password must be at least 8 characters.")
        if password != confirm:
            messages.error(request, "Passwords do not match")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
        else:
            user = User.objects.create_user(username=username, password=password)
            Customer.objects.create(user=user)
            messages.success(request, "Registration successful. Please log in.")
            return redirect("login")
    return render(request, "ecommerce/register.html")


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = request.session.get("cart", {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session["cart"] = cart
    return JsonResponse(
        {
            "status": "success",
            "cart_total_items": sum(cart.values()),
            "message": f"{product.product_name} added to cart!",
            "redirect_url": reverse("view_cart"),
        }
    )


@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session["cart"] = cart
    return redirect("view_cart")


def view_cart(request):
    cart = request.session.get("cart", {})
    cart_items, total = get_cart_items_and_total(cart)
    return render(
        request,
        "ecommerce/cart.html",
        {
            "cart_items": cart_items,
            "total": total,
            "stripe_public_key": settings.STRIPE_PUBLISHABLE_KEY,
        },
    )


@require_POST
def increase_quantity(request, product_id):
    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session["cart"] = cart
    product = get_object_or_404(Product, pk=product_id)
    quantity = cart[str(product_id)]
    item_total = product.product_price * int(quantity)
    return JsonResponse(
        {
            "status": "success",
            "quantity": int(quantity),
            "item_total": float(item_total),
            "cart_total_items": sum(cart.values()),
        }
    )


@require_POST
def decrease_quantity(request, product_id):
    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}
    if str(product_id) in cart:
        if cart[str(product_id)] > 1:
            cart[str(product_id)] -= 1
        else:
            del cart[str(product_id)]
        request.session["cart"] = cart
        quantity = cart.get(str(product_id), 0)
        if quantity > 0:
            product = get_object_or_404(Product, pk=product_id)
            item_total = product.product_price * int(quantity)
        else:
            item_total = Decimal("0.00")
        return JsonResponse(
            {
                "status": "success",
                "quantity": int(quantity),
                "item_total": float(item_total),
                "cart_total_items": sum(cart.values()),
            }
        )
    return JsonResponse({"status": "error", "message": "Product not in cart"})


@require_POST
def create_checkout_session(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to login first to proceed to checkout.")
        return redirect("login")
    cart = request.session.get("cart", {})
    _, total = get_cart_items_and_total(cart)
    if total < 50:
        messages.error(request, "Minimum order value must be at least ₹50.")
        return redirect("view_cart")
    line_items = []
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        line_items.append(
            {
                "price_data": {
                    "currency": "inr",
                    "product_data": {
                        "name": product.product_name,
                    },
                    "unit_amount": int(Decimal(product.product_price) * 100),
                },
                "quantity": quantity,
            }
        )
    if not line_items:
        return redirect("view_cart")
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=request.build_absolute_uri(reverse("payment_success"))
            + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(reverse("payment_cancel")),
        )
        return redirect(session.url, code=303)
    except Exception as e:
        messages.error(request, f"Payment error: {str(e)}")
        return redirect("view_cart")


def payment_cancel(request):
    return render(request, "ecommerce/cancel.html")


def payment_success(request):
    cart = request.session.get("cart", {})
    if not cart:
        return redirect("index")

    total = Decimal("0.00")
    try:
        order = Order.objects.create(
            user=request.user,
            total_amount=0,
            payment_id=request.GET.get("session_id"),
            status="processing",
        )
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=product_id)
            price = product.product_price
            total += price * quantity
            OrderItem.objects.create(
                order=order, product=product, quantity=quantity, price=price
            )
    except Exception:
        messages.error(request, "There was a problem finalizing your order.")
        return redirect("view_cart")
    order.total_amount = total
    order.save()
    request.session["cart"] = {}
    messages.success(request, "Your order has been placed successfully!")
    return render(request, "ecommerce/success.html", {"order": order})


@login_required(login_url="login")
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by("created_at")
    return render(request, "ecommerce/order_history.html", {"orders": orders})


def quick_view_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    context = {
        "product": product,
    }
    html_content = render_to_string(
        "ecommerce/product_quick_view.html", context, request=request
    )
    return JsonResponse({"html": html_content})


def cart_count(request):
    cart = request.session.get("cart", {})
    return JsonResponse({"cart_count": len(cart)})


@login_required(login_url="login")
def saved_items_view(request):
    saved_products = Product.objects.filter(saved_by__user=request.user)
    return render(
        request, "ecommerce/saved_items.html", {"saved_products": saved_products}
    )


@require_POST
def save_product(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        saved_item, created = Saved.objects.get_or_create(
            user=request.user, product=product
        )
        if not created:
            saved_item.delete()
            return JsonResponse(
                {
                    "status": "removed",
                    "message": f"{product.product_name} removed from saved items.",
                }
            )
        return JsonResponse(
            {
                "status": "added",
                "message": f"{product.product_name} added to saved items.",
            }
        )
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@require_POST
def remove_saved(request, product_id):
    saved_item = Saved.objects.filter(user=request.user, product_id=product_id).first()
    if saved_item:
        saved_item.delete()
    return JsonResponse({"status": "removed", "message": "removed from saved items."})
