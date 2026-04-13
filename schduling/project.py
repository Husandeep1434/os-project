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
        energy += (2.0**2) * (end - start)   # always high freq
    return energy