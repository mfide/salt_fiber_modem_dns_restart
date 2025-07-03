import os
import hashlib
import json
import random
import requests
import dns.resolver
import time
import builtins

# === Configuration from environment variables ===
username = os.environ.get("MODEM_USERNAME", "admin")
password = os.environ.get("MODEM_PASSWORD", "admin")
modem_ip = os.environ.get("MODEM_IP", "192.168.1.1")
check_interval_minutes = int(os.environ.get("CHECK_INTERVAL_MINUTES", "15"))

modem_http = f"http://{modem_ip}"
json_endpoint = f"{modem_http}/cgi/json-req"
check_interval_seconds = check_interval_minutes * 60

# Override print to always flush (for Docker logging)
print = lambda *args, **kwargs: builtins.print(*args, flush=True, **kwargs)

# Domains to check
check_domains = [
    "www.cloudflare.com",
    "www.facebook.com",
    "www.google.com",
    "www.instagram.com",
    "www.microsoft.com",
    "www.reddit.com",
    "www.salt.ch",
    "www.sunrise.ch",
    "www.swisscom.ch",
    "www.whatsapp.com",
    "www.x.com"
]

headers = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": modem_http,
    "Referer": f"{modem_http}/2.0/gui/",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9"
}

# === SHA512 hash function ===
def hash_encoder(data):
    return hashlib.sha512(data.encode("utf-8")).hexdigest()

# === Generate a client-side nonce ===
def gen_nonce():
    return str(random.randint(1000000000, 4294967295))

# === Step 1: Hash the password using SHA512 ===
hashed_pw = hash_encoder(password)

# === Step 2: Get nonce and session ID with a dummy login ===
def get_nonce_and_session():
    cnonce = gen_nonce()
    request_id = "1"
    ha1_dummy = hash_encoder(f"{username}::{hashed_pw}")
    auth_key_dummy = hash_encoder(f"{ha1_dummy}:{request_id}:{cnonce}:JSON:/cgi/json-req")

    payload = {
        "request": {
            "id": int(request_id),
            "session-id": 0,
            "priority": True,
            "actions": [{
                "id": 0,
                "method": "logIn",
                "parameters": {
                    "user": username,
                    "persistent": "true",
                    "session-options": {
                        "nss": [{"name": "gtw", "uri": "http://sagemcom.com/gateway-data"}],
                        "context-flags": {"get-content-name": True, "local-time": True},
                        "capability-depth": 2,
                        "capability-flags": {
                            "name": True,
                            "default-value": False,
                            "restriction": True,
                            "description": False
                        },
                        "time-format": "ISO_8601",
                        "jwt-auth": "true",
                        "write-only-string": "_XMO_WRITE_ONLY_",
                        "undefined-write-only-string": "_XMO_UNDEFINED_WRITE_ONLY_"
                    }
                }
            }],
            "cnonce": int(cnonce),
            "auth-key": auth_key_dummy
        }
    }

    response = requests.post(json_endpoint, headers=headers, data={"req": json.dumps(payload)})
    reply = response.json().get("reply", {})

    try:
        parameters = reply["actions"][0]["callbacks"][0]["parameters"]
        nonce = parameters["nonce"]
        session_id = parameters["id"]
        print(f"✅ Nonce received: {nonce}, Session ID: {session_id}")
        return nonce, session_id
    except Exception:
        print("❌ Failed to parse the response:")
        print(json.dumps(reply, indent=2))
        raise

# === Step 3: Perform real login and build the session cookie ===
def login_with_cookie(nonce, session_id):
    cnonce = gen_nonce()
    request_id = "2"
    ha1 = hash_encoder(f"{username}:{nonce}:{hashed_pw}")
    auth_key = hash_encoder(f"{ha1}:{request_id}:{cnonce}:JSON:/cgi/json-req")

    cookie_value = json.dumps({
        "req_id": int(request_id),
        "sess_id": str(session_id),
        "basic": False,
        "user": username,
        "dataModel": {
            "name": "Internal",
            "nss": [{"name": "gtw", "uri": "http://sagemcom.com/gateway-data"}]
        },
        "ha1": ha1,
        "nonce": nonce
    })

    cookies = {
        "session": cookie_value
    }

    payload = {
        "request": {
            "id": int(request_id),
            "session-id": int(session_id),
            "priority": True,
            "actions": [{
                "id": 0,
                "method": "logIn",
                "parameters": {
                    "user": username,
                    "persistent": "true"
                }
            }],
            "cnonce": int(cnonce),
            "auth-key": auth_key
        }
    }

    response = requests.post(json_endpoint, headers=headers, cookies=cookies, data={"req": json.dumps(payload)})
    reply = response.json().get("reply", {})
    print("✅ Login successful.")
    return ha1, cookies

# === Step 4: Send reboot request to modem ===
def reboot_modem(session_id, ha1, cookies):
    cnonce = gen_nonce()
    request_id = "3"
    auth_key = hash_encoder(f"{ha1}:{request_id}:{cnonce}:JSON:/cgi/json-req")

    payload = {
        "request": {
            "id": int(request_id),
            "session-id": int(session_id),
            "priority": False,
            "actions": [{
                "id": 0,
                "method": "reboot",
                "xpath": "Device",
                "parameters": {"source": "GUI"}
            }],
            "cnonce": int(cnonce),
            "auth-key": auth_key
        }
    }

    response = requests.post(json_endpoint, headers=headers, cookies=cookies, data={"req": json.dumps(payload)})
    print("🔁 Reboot request response code:", response.status_code)
    print(response.text)

def check_dns_resolution_via_modem(domains, dns_server_ip):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [dns_server_ip]
    resolver.timeout = 3
    resolver.lifetime = 5

    failed = []
    for domain in domains:
        try:
            answers = resolver.resolve(domain, 'A')
            print(f"✅ {domain} resolved to {[a.to_text() for a in answers]}")
        except Exception as e:
            print(f"❌ {domain} failed: {e}")
            failed.append(domain)

    total = len(domains)
    failed_count = len(failed)
    print(f"\n📊 {failed_count} of {total} domains failed.")

    return failed_count > (total / 2)


# === Main loop ===
while True:
    print(f"\n🔍 Checking DNS resolution via {modem_ip} at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    if check_dns_resolution_via_modem(check_domains, modem_ip):
        print("⚠️ Majority DNS failures detected. Rebooting modem...")
        try:
            nonce, session_id = get_nonce_and_session()
            ha1, cookies = login_with_cookie(nonce, session_id)
            reboot_modem(session_id, ha1, cookies)
        except Exception as e:
            print("❌ Failed to reboot modem:", e)
    else:
        print("🟢 DNS is working fine.")

    print(f"\n⏳ Waiting {check_interval_seconds // 60} minutes...\n")
    time.sleep(check_interval_seconds)