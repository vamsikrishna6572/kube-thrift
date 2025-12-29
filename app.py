from prometheus_client import get_cpu_usage, get_memory_usage
from recommender import get_pod_requests
from cost_calculator import calculate_savings
from github_pr import create_pr

# ===== Safety Guardrails =====
PROTECTED_NAMESPACES = {"kube-system", "monitoring", "argocd", "default"}

MIN_CPU_M = 50
MIN_MEM_MB = 64

MIN_MONTHLY_SAVINGS = 5      # $ threshold
MIN_PERCENT_REDUCTION = 0.25  # 25%



def maybe_open_pr(namespace, deployment, rec_cpu, rec_mem, total_savings):
    """
    Decide if PR should be created and call create_pr.
    """
    # Simple policy:
    if total_savings > 0:
        create_pr(namespace, deployment, rec_cpu, rec_mem, total_savings)

def main():
    namespace = "demo"

    if namespace in PROTECTED_NAMESPACES:
        print(f"Skipping namespace {namespace} (protected)")
        return


    cpu_usage = get_cpu_usage(namespace)
    mem_usage = get_memory_usage(namespace)
    requests = get_pod_requests(namespace)

    usage_map = {}
    for entry in cpu_usage:
        pod = entry["metric"]["pod"]
        usage_map.setdefault(pod, {})
        usage_map[pod]["cpu_m"] = float(entry["value"][1]) * 1000  # convert CPU cores → m

    for entry in mem_usage:
        pod = entry["metric"]["pod"]
        usage_map.setdefault(pod, {})
        usage_map[pod]["mem_mb"] = int(int(entry["value"][1]) / (1024 * 1024))

    processed = set()

    for pod, data in usage_map.items():
        if pod not in requests:
            continue

        deployment_name = pod.rsplit("-", 2)[0]
        if deployment_name in processed:
            continue
        processed.add(deployment_name)

        req = requests[pod]

        cpu_req = req["cpu_m"]
        mem_req = req["memory_mib"]

        cpu_used = int(data.get("cpu_m", 0))
        mem_used = int(data.get("mem_mb", 0))

        # Apply safety floors
        recommended_cpu = max(int(cpu_used * 1.5), MIN_CPU_M)
        recommended_mem = max(int(mem_used * 1.5), MIN_MEM_MB)

        savings = calculate_savings(cpu_req, recommended_cpu, mem_req, recommended_mem)
        total_savings = round(savings * 3, 2)   # multiply by replicas

        # ----- Label Based Ignore -----
        from recommender import deployment_is_ignored
        if deployment_is_ignored(namespace, deployment_name):
            print(f"Skipping {deployment_name} - marked as ignore")
            continue

        # ----- Savings Threshold -----
        percent_reduction = 0
        if cpu_req > 0:
            percent_reduction = (cpu_req - recommended_cpu) / cpu_req

        if total_savings < MIN_MONTHLY_SAVINGS and percent_reduction < MIN_PERCENT_REDUCTION:
            print(f"Skipping {deployment_name} - savings ${total_savings} too small or <25% reduction")
            continue

        print(f"Will open PR for {deployment_name} with savings ${total_savings}")
        maybe_open_pr(namespace, deployment_name, recommended_cpu, recommended_mem, total_savings)
        
    


        
    


if __name__ == "__main__":
    main()
