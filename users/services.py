import requests
from django.conf import settings


def create_stripe_product(name):
    """Создаёт продукт в Stripe."""
    response = requests.post(
        'https://api.stripe.com/v1/products',
        headers={
            'Authorization': f'Bearer {settings.STRIPE_SECRET_KEY}'
        },
        data={'name': name}
    )

    response.raise_for_status()
    return response.json()


def create_stripe_price(product_id, amount):
    """Создаёт цену продукта в Stripe."""
    response = requests.post(
        'https://api.stripe.com/v1/prices',
        headers={
            'Authorization': f'Bearer {settings.STRIPE_SECRET_KEY}'
        },
        data={
            'product': product_id,
            'unit_amount': int(amount * 100),
            'currency': 'usd'
        }
    )

    response.raise_for_status()
    return response.json()


def create_stripe_session(price_id, success_url, cancel_url):
    """Создаёт платёжную сессию в Stripe."""
    response = requests.post(
        'https://api.stripe.com/v1/checkout/sessions',
        headers={
            'Authorization': f'Bearer {settings.STRIPE_SECRET_KEY}'
        },
        data={
            'mode': 'payment',
            'line_items[0][price]': price_id,
            'line_items[0][quantity]': 1,
            'success_url': success_url,
            'cancel_url': cancel_url
        }
    )

    response.raise_for_status()
    return response.json()