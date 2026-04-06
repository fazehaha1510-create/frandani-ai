import stripe
import os
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

PLANES = {
    "starter": {"nombre": "Starter", "precio": 0},
    "creator": {"nombre": "Creator", "precio": 1999},
    "pro": {"nombre": "Pro", "precio": 4999}
}


def crear_checkout_session(plan_id, user_email):
    if plan_id not in PLANES:
        raise ValueError("Plan no existe")
    plan = PLANES[plan_id]
    if plan["precio"] == 0:
        return "gratis"
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        customer_email=user_email,
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": "Frandani AI " + plan["nombre"]},
                "unit_amount": plan["precio"],
                "recurring": {"interval": "month"},
            },
            "quantity": 1,
        }],
        mode="subscription",
        success_url="https://frandani-ai.vercel.app/?pago=exitoso",
        cancel_url="https://frandani-ai.vercel.app/?pago=cancelado",
    )
    return session.url


def verificar_pago(session_id):
    session = stripe.checkout.Session.retrieve(session_id)
    return {"pagado": session.payment_status == "paid", "email": session.customer_email}


def cancelar_suscripcion(subscription_id):
    stripe.Subscription.cancel(subscription_id)
    return True