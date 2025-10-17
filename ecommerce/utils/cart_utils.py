from decimal import Decimal

from ecommerce.models import Product


def get_cart_items_and_total(cart):
    items = []
    total = Decimal("0.00")

    product_ids = cart.keys()

    products = Product.objects.filter(pk__in=product_ids)

    product_map = {str(p.pk): p for p in products}

    for product_id, quantity in cart.items():
        product = product_map.get(str(product_id))
        if not product:
            continue

        item_total = Decimal(product.product_price) * quantity
        items.append(
            {
                "product": product,
                "item_total": item_total,
                "quantity": quantity,
            }
        )
        total += item_total

    return items, total
