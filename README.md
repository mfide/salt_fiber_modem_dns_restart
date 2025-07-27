# 🌀 Fiber Box X6 Modem Restart
This Python script monitors DNS resolution using your **modem’s DNS server** (e.g., `192.168.1.1`).  
If the majority of well-known domains fail to resolve, the script triggers an **authenticated reboot** of the modem via its web interface.

---

## 🔧 Features

- Periodic DNS health checks (default: every 15 minutes)
- Uses the modem as the DNS resolver
- Reboots modem automatically via API (tested on Salt Fiber Box X6)
- Runs as a standalone script or in Docker
- Docker Compose support for easy deployment

---

## ⚙️ Environment Variables

| Variable               | Description                              | Example              | Required |
|------------------------|------------------------------------------|----------------------|----------|
| `MODEM_USERNAME`       | Modem admin username                     | `admin`              | ✅       |
| `MODEM_PASSWORD`       | Modem admin password                     | `yourpassword`       | ✅       |
| `MODEM_IP`             | Modem IP address (used for DNS & HTTP)   | `192.168.1.1`        | ✅       |
| `CHECK_INTERVAL_MINUTES` | Interval between checks (in minutes)   | `15`                 | ❌  |

---

## 🚀 Run with Docker

### 1. Build and Run (standalone)

```bash
docker build -t modem-restart .
docker run --rm \
  -e MODEM_USERNAME=admin \
  -e MODEM_PASSWORD=yourpassword \
  -e MODEM_IP=192.168.1.1 \
  -e CHECK_INTERVAL_MINUTES=15 \
  modem-restart
```

---

## 🐳 Run with Docker Compose

### docker-compose.yml

```yaml
services:
  modem-restart:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      MODEM_USERNAME: admin
      MODEM_PASSWORD: yourpassword
      MODEM_IP: 192.168.1.1
      CHECK_INTERVAL_MINUTES: 15
    restart: unless-stopped
```

### Start it

```bash
docker-compose up -d --build
```

---

## 📝 Domain List Checked

The following domains are resolved via your modem’s DNS server:

```
www.cloudflare.com
www.facebook.com
www.google.com
www.instagram.com
www.microsoft.com
www.reddit.com
www.salt.ch
www.sunrise.ch
www.swisscom.ch
www.whatsapp.com
www.x.com
```

> If **more than half fail**, the modem will reboot automatically.

---

## 🔍 Example Log Output

Below is a real-world example of how the system detects a DNS failure and initiates a modem reboot:
```
modem-restart-1  | 🔍 Checking DNS resolution via 192.168.1.1 at 2025-07-21 05:54:56
modem-restart-1  | ✅ www.cloudflare.com resolved to ['104.16.124.96', '104.16.123.96']
modem-restart-1  | ✅ www.facebook.com resolved to ['157.240.17.35']
modem-restart-1  | ✅ www.google.com resolved to ['172.217.168.36']
modem-restart-1  | ✅ www.instagram.com resolved to ['157.240.17.174']
modem-restart-1  | ✅ www.microsoft.com resolved to ['23.212.193.218']
modem-restart-1  | ✅ www.reddit.com resolved to ['146.75.117.140']
modem-restart-1  | ✅ www.salt.ch resolved to ['213.55.192.11']
modem-restart-1  | ✅ www.sunrise.ch resolved to ['212.35.60.35']
modem-restart-1  | ✅ www.swisscom.ch resolved to ['195.186.208.154']
modem-restart-1  | ✅ www.whatsapp.com resolved to ['157.240.17.60']
modem-restart-1  | ✅ www.x.com resolved to ['172.66.0.227']
modem-restart-1  | 
modem-restart-1  | 📊 0 of 11 domains failed.
modem-restart-1  | 🟢 DNS is working fine.
modem-restart-1  | 
modem-restart-1  | ⏳ Waiting 15 minutes...
modem-restart-1  | 
modem-restart-1  | 
modem-restart-1  | 🔍 Checking DNS resolution via 192.168.1.1 at 2025-07-21 06:09:56
modem-restart-1  | ❌ www.cloudflare.com failed: All nameservers failed to answer the query www.cloudflare.com. IN A: Server Do53:192.168.1.1@53 answered REFUSED
modem-restart-1  | ❌ www.facebook.com failed: All nameservers failed to answer the query www.facebook.com. IN A: Server Do53:192.168.1.1@53 answered REFUSED
modem-restart-1  | ❌ www.google.com failed: All nameservers failed to answer the query www.google.com. IN A: Server Do53:192.168.1.1@53 answered REFUSED
modem-restart-1  | ❌ www.instagram.com failed: All nameservers failed to answer the query www.instagram.com. IN A: Server Do53:192.168.1.1@53 answered REFUSED
modem-restart-1  | ❌ www.microsoft.com failed: All nameservers failed to answer the query www.microsoft.com. IN A: Server Do53:192.168.1.1@53 answered REFUSED
modem-restart-1  | ❌ www.reddit.com failed: All nameservers failed to answer the query www.reddit.com. IN A: Server Do53:192.168.1.1@53 answered REFUSED
modem-restart-1  | ❌ www.salt.ch failed: All nameservers failed to answer the query www.salt.ch. IN A: Server Do53:192.168.1.1@53 answered REFUSED
modem-restart-1  | ❌ www.sunrise.ch failed: All nameservers failed to answer the query www.sunrise.ch. IN A: Server Do53:192.168.1.1@53 answered REFUSED
modem-restart-1  | ❌ www.swisscom.ch failed: All nameservers failed to answer the query www.swisscom.ch. IN A: Server Do53:192.168.1.1@53 answered REFUSED
modem-restart-1  | ❌ www.whatsapp.com failed: All nameservers failed to answer the query www.whatsapp.com. IN A: Server Do53:192.168.1.1@53 answered REFUSED
modem-restart-1  | ❌ www.x.com failed: All nameservers failed to answer the query www.x.com. IN A: Server Do53:192.168.1.1@53 answered REFUSED
modem-restart-1  | 
modem-restart-1  | 📊 11 of 11 domains failed.
modem-restart-1  | ⚠️ Majority DNS failures detected. Rebooting modem...
modem-restart-1  | ✅ Nonce received: 2374046353, Session ID: 1495818435
modem-restart-1  | ✅ Login successful.
modem-restart-1  | 🔁 Reboot request response code: 200
modem-restart-1  | {"reply":{"uid":0,"id":3,"error":{"code":16777216,"description":"XMO_REQUEST_NO_ERR"},"actions":[{"uid":1,"id":0,"error":{"code":16777238,"description":"XMO_NO_ERR"},"callbacks":[{"uid":1,"result":{"code":16777238,"description":"XMO_NO_ERR"},"xpath":"Device","parameters":{}}]}],"events":[]}}
modem-restart-1  | 
modem-restart-1  | ⏳ Waiting 15 minutes...
modem-restart-1  | 
modem-restart-1  | 
modem-restart-1  | 🔍 Checking DNS resolution via 192.168.1.1 at 2025-07-21 06:24:58
modem-restart-1  | ✅ www.cloudflare.com resolved to ['104.16.124.96', '104.16.123.96']
modem-restart-1  | ✅ www.facebook.com resolved to ['157.240.17.35']
modem-restart-1  | ✅ www.google.com resolved to ['142.250.203.100']
modem-restart-1  | ✅ www.instagram.com resolved to ['157.240.17.174']
modem-restart-1  | ✅ www.microsoft.com resolved to ['23.212.193.218']
modem-restart-1  | ✅ www.reddit.com resolved to ['146.75.117.140']
modem-restart-1  | ✅ www.salt.ch resolved to ['213.55.192.11']
modem-restart-1  | ✅ www.sunrise.ch resolved to ['212.35.60.35']
modem-restart-1  | ✅ www.swisscom.ch resolved to ['195.186.208.154']
modem-restart-1  | ✅ www.whatsapp.com resolved to ['157.240.17.60']
modem-restart-1  | ✅ www.x.com resolved to ['162.159.140.229']
modem-restart-1  | 
modem-restart-1  | 📊 0 of 11 domains failed.
modem-restart-1  | 🟢 DNS is working fine.
modem-restart-1  | 
modem-restart-1  | ⏳ Waiting 15 minutes...
```

# Device DNS Configuration

You can change the DNS address using the web interface by visiting the following hidden URL:

[http://192.168.1.1/2.0/gui/#/mybox/dns/server](http://192.168.1.1/2.0/gui/#/mybox/dns/server)

> **Note:** This page might not be accessible from standard navigation menus. Make sure your device is connected to the local network and visit the link directly in your browser.

## 📃 License

MIT License — feel free to use and adapt.

---

## 📬 Contact

Open an issue or PR if you have suggestions or modem compatibility questions.
