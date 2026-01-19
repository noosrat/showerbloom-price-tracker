import requests
import os
import json

# Shopify JSON endpoint for the product
URL = "https://showerbloom.co.za/products/handheld-filtered-showerhead.json"
PRICE_FILE = "last_price.json"

# Load last price
if os.path.exists(PRICE_FILE):
    with open(PRICE_FILE) as f:
        last_price = json.load(f).get("price")
else:
    last_price = None

# Fetch product JSON
res = requests.get(URL)
data = res.json()

# Get current price (in cents)
price_cents = data["product"]["variants"][0]["price"]  # price in ZAR
current_price = float(price_cents)

print(f"Current price: R{current_price}")

# Compare and send email if first run or price dropped
if last_price is None or current_price < last_price:
    # Send email via Resend
    import requests
    email_data = {
        "from": "Price Tracker <noreply@resend.dev>",
        "to": [os.environ["EMAIL_TO"]],
        "subject": f"Price Alert: R{current_price} on Showerbloom",
        "html": f"<p>The Showerbloom showerhead price is now <strong>R{current_price}</strong>.</p>"
                f"<p>Link: <a href='https://showerbloom.co.za/products/handheld-filtered-showerhead'>Product Page</a></p>"
    }

    r = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {os.environ['RESEND_API_KEY']}",
            "Content-Type": "application/json"
        },
        json=email_data
    )

    if r.status_code == 200:
        print("Email sent successfully.")
    else:
        print("Error sending email:", r.text)

# Save current price for next run
with open(PRICE_FILE, "w") as f:
    json.dump({"price": current_price}, f)
