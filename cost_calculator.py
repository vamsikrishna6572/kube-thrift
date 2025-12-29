CPU_PRICE_PER_HOUR = 0.04        # $ per vCPU hour
MEM_PRICE_PER_GB_HOUR = 0.005    # $ per GB hour
HOURS_IN_MONTH = 730


def calculate_savings(request_cpu_m, actual_cpu_m, request_mem_mb, actual_mem_mb):
    cpu_saved = max((request_cpu_m - actual_cpu_m) / 1000, 0)
    mem_saved_gb = max((request_mem_mb - actual_mem_mb) / 1024, 0)

    cpu_money = cpu_saved * CPU_PRICE_PER_HOUR * HOURS_IN_MONTH
    mem_money = mem_saved_gb * MEM_PRICE_PER_GB_HOUR * HOURS_IN_MONTH

    return round(cpu_money + mem_money, 2)
