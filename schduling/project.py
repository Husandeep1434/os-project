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

def main():
    n = int(input("Enter number of processes: "))
    processes = []

    for i in range(n):
        at = int(input(f"Arrival time of P{i+1}: "))
        bt = int(input(f"Burst time of P{i+1}: "))
        pr = int(input(f"Priority of P{i+1}: "))
        processes.append(Process(f"P{i+1}", at, bt, pr))

    
    p1 = [Process(p.pid, p.arrival, p.burst, p.priority) for p in processes]
    fcfs_gantt = fcfs(p1)
    fcfs_energy = energy_fcfs(fcfs_gantt)

  
    p2 = [Process(p.pid, p.arrival, p.burst, p.priority) for p in processes]
    pr_gantt = priority_scheduling(p2)
    pr_energy = energy_priority(pr_gantt)

  
    p3 = [Process(p.pid, p.arrival, p.burst, p.priority) for p in processes]
    eaas_gantt = eaas(p3)
    eaas_energy = energy_eaas(eaas_gantt)

    
    print_gantt("FCFS", fcfs_gantt)
    print_gantt("PRIORITY", pr_gantt)
    print_gantt("EAAS", eaas_gantt)

   
    print("\n\n📊 ENERGY COMPARISON")
    print("-----------------------------------")
    print("Algorithm     Energy")
    print("-----------------------------------")
    print(f"FCFS          {fcfs_energy}")
    print(f"PRIORITY      {pr_energy}")
    print(f"EAAS          {eaas_energy}")
    print("-----------------------------------")

    
    algorithms = ["FCFS", "Priority", "EAAS"]
    energies = [fcfs_energy, pr_energy, eaas_energy]

    plt.bar(algorithms, energies)
    plt.xlabel("Algorithms")
    plt.ylabel("Energy")
    plt.title("Energy Comparison")
    plt.show()


if _name_ == "_main_":
    main()