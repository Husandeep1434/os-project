from flask import Flask, request, jsonify, render_template
import project
from project import Process

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json
    
    processes = []
    for p in data:
        processes.append(Process(p['id'], int(p['arrival']), int(p['burst']), int(p['priority'])))
        
    def copy_procs():
        return [Process(p.pid, p.arrival, p.burst, p.priority) for p in processes]
    
    p1 = copy_procs()
    fcfs_gantt = project.fcfs(p1)
    fcfs_energy = project.energy_fcfs(fcfs_gantt)
    fcfs_tat, fcfs_wt = project.calculate_metrics(processes, fcfs_gantt)
    
    p2 = copy_procs()
    pr_gantt = project.priority_scheduling(p2)
    pr_energy = project.energy_priority(pr_gantt)
    pr_tat, pr_wt = project.calculate_metrics(processes, pr_gantt)
    
    p3 = copy_procs()
    eaas_gantt = project.eaas(p3)
    eaas_energy = project.energy_eaas(eaas_gantt)
    eaas_tat, eaas_wt = project.calculate_metrics(processes, eaas_gantt)
    
    return jsonify({
        "fcfs": {"gantt": fcfs_gantt, "energy": fcfs_energy, "tat": fcfs_tat, "wt": fcfs_wt},
        "priority": {"gantt": pr_gantt, "energy": pr_energy, "tat": pr_tat, "wt": pr_wt},
        "eaas": {"gantt": eaas_gantt, "energy": eaas_energy, "tat": eaas_tat, "wt": eaas_wt}
    })

if __name__ == '__main__':
    app.run(debug=True)
