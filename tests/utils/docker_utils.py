import os
import time

import docker


def is_container_ready(container):
    container.reload()
    return container.status == "running"


def wait_for_stable_status(container, stable_duration=10, interval=1):
    start_time = time.time()
    stable_count = 0
    while time.time() - start_time < stable_duration:
        if is_container_ready(container):
            stable_count += 1
        else:
            stable_count = 0

        if stable_count >= stable_duration / interval:
            return True

        time.sleep(interval)
    return False

def ensure_network(client, network_name):
    try:
        network = client.networks.get(network_name)
        print(f"Network '{network_name}' already exists.")
    except docker.errors.NotFound:
        print(f"Network '{network_name}' does not exist. Creating...")
        client.networks.create(network_name, driver="bridge")




def start_database_container():
    client = docker.from_env()
    scripts_dir = os.path.abspath("./scripts")
    container_name = "test-db"
    # Use the function in your start_database_container function
    ensure_network(client, "dev-network")
    try:
        existing_container = client.containers.get(container_name)
        print(f"Container '{container_name} exists. Stopping and removing...")
        existing_container.stop()
        existing_container.remove()
        print((f"Container '{container_name} stopped and removed"))
    except docker.errors.NotFound:
        print(f"Container '{container_name}' does not exist.")

    # Define container configuration
    container_config = {
        "name": container_name,
        "image": "postgres:16.1-alpine3.19",
        "detach": True,
        "ports": {"5432": "5434"},
        "environment": {
            "POSTGRES_USER": "postgres",
            "POSTGRES_PASSWORD": "postgres",
        },
        "volumes": [f"{scripts_dir}:/docker-entrypoint-initdb.d"],
        "network_mode": "dev-network",
    }

    # Start Container
    container = client.containers.run(**container_config)

    while not is_container_ready(container):
        time.sleep(1)

    if not wait_for_stable_status(container):
        raise RuntimeError("Container did not stabilize within the specified time")

    return container
