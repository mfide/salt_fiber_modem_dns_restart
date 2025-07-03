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

## 📃 License

MIT License — feel free to use and adapt.

---

## 📬 Contact

Open an issue or PR if you have suggestions or modem compatibility questions.
