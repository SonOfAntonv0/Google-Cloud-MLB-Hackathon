
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

def send_email(to_email):
    load_dotenv()
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("EMAIL_FROM")

    content_theatre_url = "https://cloud-hackathon-venky.web.app/content-theatre"

    subject = "Your MLB Content is Ready! ⚾"
    body = f"""
    <h3>Your personalized MLB content is ready! 🎉</h3>
    <p>Click the button below to view your content:</p>
    <p><a href="{content_theatre_url}" target="_blank" 
    style="background-color: #1E88E5; color: white; padding: 10px 20px; 
    text-decoration: none; font-size: 16px; border-radius: 5px;">
    View Your Content</a></p>
    <p>Enjoy your highlights! ⚡</p>
    """


    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure connection
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, to_email, msg.as_string())
        server.quit()
        print(f"✅ Email sent successfully to {to_email}")
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")

