from prometheus_api_client import PrometheusConnect

PROMETHEUS_URL = "http://localhost:9090"

def get_prom_client():
    return PrometheusConnect(url=PROMETHEUS_URL, disable_ssl=True)


def get_cpu_usage(namespace):
    prom = get_prom_client()

    query = f"""
    sum(rate(container_cpu_usage_seconds_total{{namespace="{namespace}", image!=""}}[5m]))
    by (pod)
    """

    result = prom.custom_query(query=query)
    return result


def get_memory_usage(namespace):
    prom = get_prom_client()

    query = f"""
    sum(container_memory_usage_bytes{{namespace="{namespace}", image!=""}})
    by (pod)
    """

    result = prom.custom_query(query=query)
    return result
