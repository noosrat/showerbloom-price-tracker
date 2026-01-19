import requests
from bs4 import BeautifulSoup
import os
import json

URL = "https://showerbloom.co.za/products/handheld-filtered-showerhead"
PRICE_FILE = "last_price.json"

# Load last price
if os.path.exists(PRICE_FILE):
    with open(PRICE_FILE) as f:
        last_price = json.load(f).get("price")
else:
    last_price = None

# Fetch page
headers = {"User-Agent": "Mozilla/5.0"}
res = requests.get(URL, headers=headers)
soup = BeautifulSoup(res.text, "html.parser")

# Extract price from JSON-LD
price = None
for script in soup.find_all("script", type="application/ld+json"):
    data = json.loads(script.string)
    try:
        price = float(data["offers"]["price"])
        break
    except:
        continue

if price is None:
    print("Price not found")
    exit()

print(f"Current price: R{price}")

# Compare and update
if last_price is None or price < last_price:
    # Send email via Resend
    import requests
    email_data = {
        "from": "Price Tracker <noreply@resend.dev>",
        "to": [os.environ["EMAIL_TO"]],
        "subject": f"Price Alert: R{price} on Showerbloom",
        "html": f"<p>The Showerbloom showerhead price is now <strong>R{price}</strong>.</p><p>Link: <a href='{URL}'>Product Page</a></p>"
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

# Save current price
with open(PRICE_FILE, "w") as f:
    json.dump({"price": price}, f)
