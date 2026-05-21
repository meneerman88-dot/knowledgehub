import random
import requests

API_URL = "http://localhost:8000/api/v1/metrics"
API_KEY = "default-dev-key"

hosts = [
    "dc01.knowledgehub.local",
    "fileserver01.knowledgehub.local",
    "webserver01.knowledgehub.local",
    "monitoring01.knowledgehub.local",
    "dockerhost01.knowledgehub.local"
]

for host in hosts:
    cpu = random.randint(12, 88)
    memory = random.randint(20, 91)
    disk = random.randint(30, 84)

    status = "healthy"
    if cpu > 80 or memory > 80 or disk > 80:
        status = "warning"

    payload = {
        "hostname": host,
        "cpu_usage": cpu,
        "memory_usage": memory,
        "disk_usage": disk,
        "status": status
    }

    response = requests.post(
        API_URL,
        json=payload,
        headers={"x-api-key": API_KEY},
        timeout=5
    )

    print(host, response.status_code, response.text)
