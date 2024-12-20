import requests
import logging

from dotenv import dotenv_values

logging.basicConfig(filename="/home/cole/ddns/.log", level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("DNS_LOGGER")

env = dotenv_values()

API_TOKEN = env["CLOUDFLARE_TOKEN"]
ZONE_ID = env["ZONE_ID"]

ip = requests.get("https://v4.ident.me/").text.strip()


url = "https://api.cloudflare.com/client/v4/zones"
headers = {
    "Authorization" : f"Bearer {API_TOKEN}",
    "Content-Type" : "application/json"
}



url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records"



dns = requests.get(url=url, headers=headers)

home_record = list(filter(lambda e: e["name"]=="home.dwab.dev", dns.json()["result"]))[0]
wild_record = list(filter(lambda e: e["name"]=="*.dwab.dev", dns.json()["result"]))[0]

url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{home_record['id']}"
if home_record["content"] != ip:
    logger.info(f"""Records do not match.
        Record:{home_record['content']}
        IP:    {ip}
    """)
    body = {"content": ip,
            "name":"home.dwab.dev",
            "type":"A",
            "proxied": False,
            "ttl" : 1,
            }
    logger.info(f"Patch response for home.dwab.dev: \n{requests.patch(url=url, headers=headers,json=body).text}")
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{wild_record['id']}"
    body = {"content": ip,
            "name":"*.dwab.dev",
            "type":"A",
            "proxied": True,
            "ttl" : 1,
            }
    logger.info(f"Patch response for home.dwab.dev: \n{requests.patch(url=url, headers=headers,json=body).text}")

else:
    logger.info(f"Records match. IP: {ip}")
