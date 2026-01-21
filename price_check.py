import requests
import os
import json
import sys

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

current_price = float(data["product"]["variants"][0]["price"])
print(f"Current price: R{current_price}")

price_dropped = last_price is not None and current_price < last_price
first_run = last_price is None

# Send email only if first run OR price dropped
if first_run or price_dropped:
    email_data = {
        "from": "Price Tracker <noreply@resend.dev>",
        "to": [os.environ["EMAIL_TO"]],
        "subject": f"Price Alert: R{current_price} on Showerbloom",
        "html": f"""
        <p>The Showerbloom showerhead price is now <strong>R{current_price}</strong>.</p>
        <p><a href="https://showerbloom.co.za/products/handheld-filtered-showerhead">View product</a></p>
        """
    }

    r = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {os.environ['RESEND_API_KEY']}",
            "Content-Type": "application/json"
        },
        json=email_data
    )

    print("Email sent" if r.status_code == 200 else r.text)

# Only update file if price changed or first run
if first_run or current_price != last_price:
    with open(PRICE_FILE, "w") as f:
        json.dump({"price": current_price}, f)
    print("Price file updated")
    sys.exit(10)  # signal to workflow that we should commit
else:
    print("No price change")
    sys.exit(0)