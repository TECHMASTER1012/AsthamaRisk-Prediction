import os
from twilio.rest import Client
import logging

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "your_account_sid_here")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "your_auth_token_here")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER", "+1234567890")

def send_sms_alert(to_number: str, message_body: str):
    """
    Sends an SMS alert using Twilio.
    """
    if "your_account_sid_here" in TWILIO_ACCOUNT_SID or not TWILIO_ACCOUNT_SID:
        logging.warning("Twilio credentials not configured. Skipping SMS alert.")
        return False
        
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_FROM_NUMBER,
            to=to_number
        )
        logging.info(f"Sent SMS alert '{message_body}' to {to_number}. SID: {message.sid}")
        return True
    except Exception as e:
        logging.error(f"Failed to send Twilio SMS: {str(e)}")
        return False
