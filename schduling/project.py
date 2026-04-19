import matplotlib.pyplot as plt

class Process:
    def __init__(self, pid, arrival, burst, priority):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.priority = priority

def fcfs(processes):
    processes.sort(key=lambda x: x.arrival)
    time = 0
    gantt = []

    for p in processes:
        if time < p.arrival:
            time = p.arrival

        start = time
        end = time + p.burst
        gantt.append((p.pid, start, end))
        time = end
    return gantt
def energy_fcfs(gantt):
    energy = 0
    for pid, start, end in gantt:
        energy += (2.0**2) * (end - start)   
    return energy

def priority_scheduling(processes):
    time = 0
    ready = []
    gantt = []
    processes.sort(key=lambda x: x.arrival)

    while processes or ready:
        while processes and processes[0].arrival <= time:
            ready.append(processes.pop(0))

        if ready:
            ready.sort(key=lambda x: x.priority)
            p = ready.pop(0)

            start = time
            end = time + p.burst
            gantt.append((p.pid, start, end))
            time = end
        else:
            time += 1

    return gantt
def energy_priority(gantt):
    energy = 0
    for pid, start, end in gantt:
        energy += (2.0**2) * (end - start)   
    return energy
def eaas(processes):
    time = 0
    ready = []
    gantt = []
    processes.sort(key=lambda x: x.arrival)

    while processes or ready:
        while processes and processes[0].arrival <= time:
            ready.append(processes.pop(0))

        if ready:
            ready.sort(key=lambda x: (x.priority, x.burst))
            p = ready.pop(0)

            start = time
            end = time + p.burst
            gantt.append((p.pid, start, end))
            time = end
        else:
            time += 1

    return gantt
def energy_eaas(gantt):
    energy = 0
    for pid, start, end in gantt:
        burst = end - start

        if burst <= 3:
            freq = 1.0
        elif burst <= 6:
            freq = 1.5
        else:
            freq = 2.0

        energy += (freq**2) * burst

    return energy

def round_robin(processes, time_quantum):
    time = 0
    ready = []
    gantt = []
    processes.sort(key=lambda x: x.arrival)
    rem_burst = {p.pid: p.burst for p in processes}
    unarrived = processes.copy()
    
    if unarrived:
        time = unarrived[0].arrival
        
    while unarrived and unarrived[0].arrival <= time:
        ready.append(unarrived.pop(0))
        
    while ready or unarrived:
        if not ready:
            time = unarrived[0].arrival
            while unarrived and unarrived[0].arrival <= time:
                ready.append(unarrived.pop(0))
                
        p = ready.pop(0)
        start = time
        execute_time = min(rem_burst[p.pid], time_quantum)
        time += execute_time
        rem_burst[p.pid] -= execute_time
        gantt.append((p.pid, start, time))
        
        while unarrived and unarrived[0].arrival <= time:
            ready.append(unarrived.pop(0))
            
        if rem_burst[p.pid] > 0:
            ready.append(p)
            
    return gantt

def energy_rr(gantt):
    energy = 0
    for pid, start, end in gantt:
        energy += (2.0**2) * (end - start)   
    return energy

def calculate_metrics(processes, gantt):
    finish_times = {}
    for pid, start, end in gantt:
        finish_times[pid] = end 
        
    total_tat = 0
    total_wt = 0
    for p in processes:
        ct = finish_times[p.pid]
        tat = ct - p.arrival
        wt = tat - p.burst
        total_tat += tat
        total_wt += wt
        
    n = len(processes)
    if n == 0: return 0, 0
    return total_tat / n, total_wt / n