import os
import docker
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1/metrics")
API_KEY = os.getenv("API_KEY", "default-dev-key")


def get_container_metrics():
    client = docker.from_env()
    containers = client.containers.list(all=True)

    metrics = []

    for container in containers:
        status = container.status

        try:
            stats = container.stats(stream=False)

            cpu_delta = (
                stats["cpu_stats"]["cpu_usage"]["total_usage"]
                - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            )

            system_delta = (
                stats["cpu_stats"]["system_cpu_usage"]
                - stats["precpu_stats"]["system_cpu_usage"]
            )

            cpu_count = len(stats["cpu_stats"]["cpu_usage"].get("percpu_usage", [1]))

            cpu_usage = 0
            if system_delta > 0 and cpu_delta > 0:
                cpu_usage = (cpu_delta / system_delta) * cpu_count * 100

            memory_usage = stats["memory_stats"].get("usage", 0)
            memory_limit = stats["memory_stats"].get("limit", 1)
            memory_percent = (memory_usage / memory_limit) * 100

        except Exception:
            cpu_usage = 0
            memory_percent = 0

        metric = {
            "hostname": f"container-{container.name}",
            "cpu_usage": round(cpu_usage, 2),
            "memory_usage": round(memory_percent, 2),
            "disk_usage": 0,
            "status": "healthy" if status == "running" else "warning"
        }

        metrics.append(metric)

    return metrics


def send_metrics(metrics):
    for metric in metrics:
        response = requests.post(
            API_URL,
            json=metric,
            headers={"x-api-key": API_KEY},
            timeout=5
        )

        print(f"Sent {metric['hostname']} - Status code: {response.status_code}")


if __name__ == "__main__":
    container_metrics = get_container_metrics()
    send_metrics(container_metrics)