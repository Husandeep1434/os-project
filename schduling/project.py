import matplotlib.pyplot as plt

class Process:
    def _init_(self, pid, arrival, burst, priority):
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

def print_gantt(name, gantt):
    print(f"\n{name} Gantt Chart:")
    for pid, start, end in gantt:
        print(f"| {pid} ({start}-{end}) ", end="")
    print("|")