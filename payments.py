import stripe
import os
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

PLANES = {
    "starter":  {"nombre": "Starter",  "precio": 0,     "desc": "Free plan"},
    "creator":  {"nombre": "Creator",  "precio": 2999,  "desc": "For creators getting started"},
    "pro":      {"nombre": "Pro",      "precio": 6999,  "desc": "For serious active earners"},
    "elite":    {"nombre": "Elite",    "precio": 14999, "desc": "For full-time earners & studios"},
}

def crear_checkout_session(plan_id: str, user_email: str) -> str:
    if plan_id not in PLANES:
        raise ValueError(f"Plan '{plan_id}' no existe")
    plan = PLANES[plan_id]
    if plan["precio"] == 0:
        return "gratis"
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        customer_email=user_email,
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": f"Frandani AI — {plan['nombre']}",
                    "description": plan["desc"],
                },
                "unit_amount": plan["precio"],
                "recurring": {"interval": "month"},
            },
            "quantity": 1,
        }],
        mode="subscription",
        success_url="https://frandani-ai.vercel.app/?pago=exitoso",
        cancel_url="https://frandani-ai.vercel.app/?pago=cancelado",
        metadata={"plan_id": plan_id}
    )
    return session.url

def crear_checkout_creditos(cantidad: int, user_email: str) -> str:
    """Checkout para compra de créditos extra"""
    # Price per credit based on volume
    if cantidad < 100:
        price_per = 90   # $0.90/credit in cents
    elif cantidad < 300:
        price_per = 75
    elif cantidad < 600:
        price_per = 65
    else:
        price_per = 55

    total = cantidad * price_per  # total in cents

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        customer_email=user_email,
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": f"Frandani AI — {cantidad} Credits",
                    "description": f"Top-up credits. Never expire. ${price_per/100:.2f}/credit.",
                },
                "unit_amount": total,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url="https://frandani-ai.vercel.app/?pago=creditos",
        cancel_url="https://frandani-ai.vercel.app/?pago=cancelado",
        metadata={"creditos": str(cantidad), "email": user_email}
    )
    return session.url

def verificar_pago(session_id: str) -> dict:
    session = stripe.checkout.Session.retrieve(session_id)
    return {
        "pagado": session.payment_status == "paid",
        "email": session.customer_email,
        "plan": session.metadata.get("plan_id", ""),
    }

def cancelar_suscripcion(subscription_id: str) -> bool:
    stripe.Subscription.cancel(subscription_id)
    return True
