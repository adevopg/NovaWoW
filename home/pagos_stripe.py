import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(amount, currency="eur", success_url=None, cancel_url=None):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": currency,
                    "product_data": {"name": "Renombrar personaje"},
                    "unit_amount": int(amount * 100),  # Convertir euros a centavos
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return {"success": True, "session_id": session.id}
    except Exception as e:
        return {"success": False, "error": str(e)}
