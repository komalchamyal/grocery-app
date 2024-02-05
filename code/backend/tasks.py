from main import celery
from model import Product, User, Order
import csv
from celery.schedules import crontab
from datetime import datetime, timedelta
import requests


################# Export as CSV - for Managers ###################

@celery.task()
def export_csv_task():
    products = Product.query.all()  
    filename = "./static/ManagerFile.csv"

    try:
        with open(filename, "w", newline="") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Product ID", "Product Name", "Category", "Stock", "Price", "Expiry Date"])

            for product in products:
                csv_writer.writerow([product.productID, product.product_name, product.product_category, product.stock, product.price, product.expiry_date])
        
        return {"message": "file exported", "file_path": filename}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}




################# Daily Reminder on Google Chat - For Users ###################

@celery.task()
def remind_users():
    user_list = User.query.all()
    for user in user_list:
        if user.role=="user":
            print(user)
            orders = Order.query.filter_by(username=user.username).all()
            if not orders:
                send_google_chat_message(user)

def send_google_chat_message(user):
    webhook_url = 'https://chat.googleapis.com/v1/spaces/AAAA-HvzV_o/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=Uj_1LLi9B5BtE1Qo1RMktDNzpfyWzB_PRiTI1CiP1Ow'
    message = f"Hi {user.username}, it seems you haven't visited/bought anything lately. Consider checking out our latest products!"
    payload = {
        'text': message,
    }
    requests.post(webhook_url, json=payload)

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # dom, hour, minute = 1, 17, 30
    sender.add_periodic_task(60, remind_users.s(), name="Daily reminder")
    sender.add_periodic_task(5, generate_monthly_report.s(), name="Monthly Report")  


################# Monthly Report - For Users ###################

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_mail(to_address, message, subject):
    try:
        msg = MIMEMultipart()
        msg["From"] = "noreply@urbanshopper.com"
        msg["To"] = to_address
        msg["Subject"] = subject
        
        msg.attach(MIMEText(message, "html"))
        print("inside")
        s = smtplib.SMTP(host="localhost", port=1025)
        s.login(msg["From"], "")
        s.send_message(msg)
        s.quit()
    except Exception as e:
        print(f"Failed to connect to SMTP server: {e}")
    return True

@celery.task()
def generate_monthly_report():
    current_month = datetime.now().strftime('%B')
    current_year = datetime.now().year

    users = User.query.all()
    for user in users:
        if user.role=="user":
            orders = Order.query.filter_by(username=user.username).all()
            amount = 0
            total_orders = 0
            
            # Get the first and last day of the previous month
            today = datetime.utcnow()
            first_day_of_current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
            first_day_of_previous_month = last_day_of_previous_month.replace(day=1)
            last_day_of_current_month = (first_day_of_current_month.replace(month=first_day_of_current_month.month % 12 + 1) - timedelta(days=1))

            for order in orders:
                print(first_day_of_current_month)
                print(order.timestamp)
                print(last_day_of_previous_month)
                # if first_day_of_current_month <= order.timestamp <= last_day_of_current_month:
                if first_day_of_previous_month <= order.timestamp <= last_day_of_previous_month:
                    amount += order.amount
                    total_orders += 1
            html_content = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Urban Shopper - Your Monthly Activity</title>
                    </head>
                    <body>
                        <h1> Your Monthly Activity - {current_month} {current_year}</h1>
                        <p>Hello {user.username.capitalize()},</p>
                        <p>Here's your Monthly Shopping activity for the month of {current_month} {current_year}:</p>
                        <ul>
                            <li>Total Expenditure: ₹{amount}</li>
                            <li>Total Orders: {total_orders}</li>
                        </ul>
                        <p>We appreciate your choice in our services. Happy shopping and have a great time! </p>
                        <p>Best regards,</p>
                        <p>Urban Shopper</p>
                    </body>
                    </html>
            """
            print("sending mail")
            send_mail(user.email, html_content, f"{user.username}'s monthly report")
