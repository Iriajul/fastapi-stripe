from fastapi import Request, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import stripe
from . import auth, models, config

router = APIRouter(prefix="/api/payment", tags=["payment"])

stripe.api_key = config.STRIPE_API_KEY
PRICE_ID = config.STRIPE_PRICE_ID
DOMAIN = config.DOMAIN

# ----------------------------------------
# Create Stripe Checkout Session
# ----------------------------------------
@router.get("/create_checkout/")
async def create_checkout(
    current_user: models.UserProfile = Depends(auth.get_current_user),
    db: Session = Depends(auth.get_db),
):
    if not current_user.stripe_customer_id:
        try:
            customer = stripe.Customer.create(email=current_user.username)
            current_user.stripe_customer_id = customer.id
            db.commit()
            db.refresh(current_user)
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=500, detail=f"Stripe error (creating customer): {str(e)}")

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": PRICE_ID, "quantity": 1}],
            mode="subscription",
            customer=current_user.stripe_customer_id,  # ✅ Only customer, not customer_email
            success_url=f"{DOMAIN}/api/payment/success/?username={current_user.username}&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{DOMAIN}/api/payment/cancel/",
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=f"Stripe error (creating checkout): {str(e)}")

    return {"checkout_url": checkout_session.url}

# ----------------------------------------
# Payment Success (redirect target)
# ----------------------------------------
@router.get("/success/")
async def payment_success(
    username: str,
    session_id: str,
    db: Session = Depends(auth.get_db),
):
    user = db.query(models.UserProfile).filter(models.UserProfile.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        customer_id = session.get("customer")
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=f"Stripe error (retrieving session): {str(e)}")

    user.is_subscribed = True
    if not user.stripe_customer_id:
        user.stripe_customer_id = customer_id
    db.commit()

    return {"message": "Subscription successful!"}

# ----------------------------------------
# Payment Cancel
# ----------------------------------------
@router.get("/cancel/")
async def payment_cancel():
    return {"message": "Payment cancelled."}

# ----------------------------------------
# Billing Portal Access
# ----------------------------------------
@router.get("/billing-portal/")
async def billing_portal(
    current_user: models.UserProfile = Depends(auth.get_current_user),
    db: Session = Depends(auth.get_db),
):
    if not current_user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="User has no active Stripe customer.")

    try:
        session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=f"{DOMAIN}/profile",
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=f"Stripe error (billing portal): {str(e)}")

    return {"portal_url": session.url}

# ----------------------------------------
# Stripe Webhook
# ----------------------------------------
@router.post("/webhook/")
async def stripe_webhook(request: Request, db: Session = Depends(auth.get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = config.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Listen for subscription changes (cancel, update, delete)
    if event["type"] in ["customer.subscription.updated", "customer.subscription.deleted"]:
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]
        status = subscription["status"]  # e.g., 'active', 'canceled', 'incomplete'

        user = db.query(models.UserProfile).filter(
            models.UserProfile.stripe_customer_id == customer_id
        ).first()

        if user:
            user.is_subscribed = status == "active"
            db.commit()

    return {"status": "success"}