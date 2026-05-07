# apps/core/utils.py
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
import stripe

def send_email(to_email, subject, template, context=None):
    """Send email using SendGrid"""
    from django.template.loader import render_to_string
    
    html_message = render_to_string(f'emails/{template}.html', context or {})
    
    send_mail(
        subject=subject,
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        html_message=html_message,
        fail_silently=False,
    )

def send_sms(to_number, message):
    """Send SMS using Twilio"""
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    message = client.messages.create(
        body=message,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=to_number
    )
    return message.sid

def create_stripe_payment_intent(amount, currency='usd', metadata=None):
    """Create Stripe payment intent"""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    intent = stripe.PaymentIntent.create(
        amount=int(amount * 100),  # Convert to cents
        currency=currency,
        metadata=metadata or {},
    )
    return intent

def generate_booking_confirmation(booking):
    """Generate booking confirmation data"""
    return {
        'booking_id': str(booking.id),
        'customer_name': booking.customer.get_full_name(),
        'services': [service.name for service in booking.services.all()],
        'total_amount': float(booking.total_amount),
        'deposit_amount': float(booking.deposit_amount),
        'date': booking.booking_date,
        'time': booking.time_slot,
        'type': booking.type,
        'qr_code': booking.qr_code.url if booking.qr_code else None
    }