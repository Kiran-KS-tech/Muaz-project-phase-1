from celery import shared_task
import time


@shared_task
def send_push_notification(user_id, title, message):
    """
    Simulates sending a FCM push notification to a driver's mobile app.
    """
    print(f"[PUSH NOTIFICATION] Sending to User ID {user_id}: {title} - {message}")
    time.sleep(0.5)  # Simulate network latency
    return "Push notification sent successfully."


@shared_task
def send_email_notification(email, subject, body):
    """
    Simulates sending an transactional email.
    """
    print(f"[EMAIL NOTIFICATION] Sending to {email} | Subject: {subject} | Body: {body}")
    time.sleep(0.5)
    return "Email sent successfully."


@shared_task
def send_whatsapp_notification(phone_number, template_name, parameters):
    """
    Simulates sending a WhatsApp notification via Twilio / Meta Cloud API.
    """
    print(f"[WHATSAPP NOTIFICATION] Sending template '{template_name}' to {phone_number} with parameters: {parameters}")
    time.sleep(0.5)
    return "WhatsApp notification sent successfully."
