from kubernetes import client, config

def get_pod_requests(namespace):
    config.load_kube_config()
    v1 = client.CoreV1Api()

    pods = v1.list_namespaced_pod(namespace)

    result = {}

    for pod in pods.items:
        name = pod.metadata.name
        cpu_req = 0
        mem_req = 0

        for container in pod.spec.containers:
            if container.resources and container.resources.requests:
                cpu = container.resources.requests.get("cpu", "0")
                mem = container.resources.requests.get("memory", "0")
            else:
                cpu = "0"
                mem = "0"

            cpu_req += convert_cpu_to_m(cpu)
            mem_req += convert_memory_to_mib(mem)

        result[name] = {
            "cpu_m": cpu_req,
            "memory_mib": mem_req
        }

    return result


def convert_cpu_to_m(cpu):
    if cpu.endswith("m"):
        return int(cpu[:-1])
    return int(float(cpu) * 1000)


def convert_memory_to_mib(mem):
    if mem.endswith("Gi"):
        return int(float(mem[:-2]) * 1024)
    if mem.endswith("Mi"):
        return int(float(mem[:-2]))
    if mem.endswith("Ki"):
        return int(float(mem[:-2]) / 1024)
    if mem.isdigit():
        return int(int(mem) / (1024 * 1024))
    return 0

def deployment_is_ignored(namespace, deployment_name):
    from kubernetes import client, config
    config.load_kube_config()
    apps = client.AppsV1Api()

    dep = apps.read_namespaced_deployment(deployment_name, namespace)

    labels = dep.metadata.labels or {}
    return labels.get("kube-thrift/ignore", "false").lower() == "true"
