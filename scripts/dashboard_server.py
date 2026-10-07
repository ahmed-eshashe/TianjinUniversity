#!/usr/bin/env python3
"""
Real-Time Web UI Dashboard for Multi-Agent AI Research System
DEX-ROB Lab | Tianjin University
Zero external dependencies beyond standard library + pyyaml.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import yaml

ROOT_DIR = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT_DIR / "research_state"
PORT = 8501


def get_gpu_info():
    """Query live GPU telemetry via nvidia-smi."""
    try:
        res = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,utilization.gpu,temperature.gpu", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, check=True
        )
        line = res.stdout.strip().split("\n")[0]
        name, total, used, util, temp = [x.strip() for x in line.split(",")]
        return {
            "name": name,
            "memory_total_mb": float(total),
            "memory_used_mb": float(used),
            "memory_percent": round((float(used) / float(total)) * 100, 1),
            "gpu_util_percent": int(util),
            "temp_c": int(temp)
        }
    except Exception:
        return {
            "name": "NVIDIA GPU (Offline / Query Failed)",
            "memory_total_mb": 8192,
            "memory_used_mb": 0,
            "memory_percent": 0.0,
            "gpu_util_percent": 0,
            "temp_c": 0
        }


def get_research_data():
    """Load research state YAML files."""
    data = {}
    files = {
        "status": STATE_DIR / "project_status.yaml",
        "hypotheses": STATE_DIR / "hypotheses.yaml",
        "experiments": STATE_DIR / "experiment_matrix.yaml",
        "claims": STATE_DIR / "paper_claims.yaml",
    }
    for key, path in files.items():
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data[key] = yaml.safe_load(f)
            except Exception as e:
                data[key] = {"error": str(e)}
        else:
            data[key] = {}

    data["gpu"] = get_gpu_info()
    data["agents"] = [
        {"id": "research_lead", "name": "Research Lead", "role": "Orchestrator & Hypothesis Guardian", "status": "ACTIVE", "icon": "👑", "color": "#38bdf8"},
        {"id": "literature_agent", "name": "Literature Specialist", "role": "SOTA Taxonomy & BibTeX Mining", "status": "IDLE", "icon": "📚", "color": "#a855f7"},
        {"id": "rl_agent", "name": "RL & Control Specialist", "role": "MDP Formulation & PPO/Impedance", "status": "IDLE", "icon": "🧠", "color": "#ec4899"},
        {"id": "experiment_agent", "name": "Experiment Specialist", "role": "Ablation Plans & Seed Budgeting", "status": "IDLE", "icon": "📐", "color": "#f59e0b"},
        {"id": "simulation_agent", "name": "Isaac Sim / PhysX 5", "role": "FEM Deformable Mesh & USD Scene", "status": "IDLE", "icon": "🤖", "color": "#10b981"},
        {"id": "training_agent", "name": "Training Specialist", "role": "Vectorized Headless GPU Execution", "status": "IDLE", "icon": "⚡", "color": "#6366f1"},
        {"id": "analysis_agent", "name": "Scientific Analysis", "role": "Statistical Rigor & IEEE Plots", "status": "IDLE", "icon": "📊", "color": "#14b8a6"},
        {"id": "ros_agent", "name": "ROS 2 & Hardware", "role": "1kHz CAN Loop & Safety Interlocks", "status": "IDLE", "icon": "🦾", "color": "#ef4444"},
        {"id": "paper_agent", "name": "Paper Specialist", "role": "IEEE LaTeX Manuscript Drafting", "status": "IDLE", "icon": "📝", "color": "#8b5cf6"},
    ]
    return data


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DEX-ROB Lab | Multi-Agent AI Research Control Center</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    body { background-color: #0b0f19; color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .glass { background: rgba(17, 24, 39, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
    .glass-card { background: rgba(30, 41, 59, 0.5); backdrop-filter: blur(8px); border: 1px solid rgba(255, 255, 255, 0.05); }
    .glow-cyan { box-shadow: 0 0 15px rgba(56, 189, 248, 0.2); }
    .glow-purple { box-shadow: 0 0 15px rgba(168, 85, 247, 0.2); }
    .pulse-dot { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: .4; transform: scale(0.9); } }
  </style>
</head>
<body class="min-h-screen pb-12">

  <!-- Header -->
  <header class="glass sticky top-0 z-50 px-6 py-4 border-b border-slate-800">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center space-x-4">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center text-white font-bold text-xl shadow-lg">
          <i class="fa-solid fa-robot"></i>
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <h1 class="text-xl font-bold tracking-tight text-white">DEX-ROB Lab AI Research Swarm</h1>
            <span class="px-2 py-0.5 text-xs font-semibold rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800">Tianjin University</span>
          </div>
          <p class="text-xs text-slate-400">Autonomous Bimanual Tomato Slicing RL | Target: <span class="text-indigo-400 font-medium">IEEE ICRA / IROS 2027</span></p>
        </div>
      </div>

      <!-- Live GPU & System Monitor -->
      <div class="flex items-center space-x-4">
        <div class="glass-card px-3 py-1.5 rounded-lg flex items-center space-x-3 text-xs">
          <i class="fa-solid fa-microchip text-emerald-400"></i>
          <div>
            <div class="text-slate-400">GPU VRAM</div>
            <div class="font-bold text-slate-200" id="gpu-vram">Loading...</div>
          </div>
          <div class="w-16 bg-slate-700 h-2 rounded-full overflow-hidden">
            <div id="gpu-bar" class="bg-emerald-500 h-full w-0 transition-all duration-500"></div>
          </div>
        </div>

        <div class="glass-card px-3 py-1.5 rounded-lg flex items-center space-x-2 text-xs">
          <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 pulse-dot"></span>
          <span class="font-medium text-slate-300">Live State Sync</span>
        </div>

        <button onclick="refreshData()" class="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-medium text-white transition flex items-center space-x-1.5">
          <i class="fa-solid fa-rotate"></i>
          <span>Refresh</span>
        </button>
      </div>
    </div>
  </header>

  <!-- Main Container -->
  <main class="max-w-7xl mx-auto px-6 mt-6 space-y-6">

    <!-- Active Agents Grid -->
    <section>
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-400 flex items-center space-x-2">
          <i class="fa-solid fa-network-wired text-cyan-400"></i>
          <span>The 9 Specialized Research Agents</span>
        </h2>
        <span class="text-xs text-slate-500">Decision Hierarchy: Human Researchers &gt; Research Lead &gt; Specialists</span>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5" id="agents-grid">
        <!-- Rendered via JS -->
      </div>
    </section>

    <!-- Two-Column Layout: Milestones & Scientific Hypotheses -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

      <!-- Milestones & Progress -->
      <section class="glass rounded-xl p-5 border border-slate-800 space-y-4">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <h2 class="text-base font-bold text-white flex items-center space-x-2">
            <i class="fa-solid fa-list-check text-indigo-400"></i>
            <span>Project Milestones & Sprint Progress</span>
          </h2>
          <span class="text-xs px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 font-medium" id="milestones-count">7 Milestones</span>
        </div>
        <div class="space-y-3" id="milestones-container">
          <!-- Rendered via JS -->
        </div>
      </section>

      <!-- Hypotheses & Falsification Matrix -->
      <section class="glass rounded-xl p-5 border border-slate-800 space-y-4">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <h2 class="text-base font-bold text-white flex items-center space-x-2">
            <i class="fa-solid fa-flask-vial text-purple-400"></i>
            <span>Falsifiable Scientific Hypotheses</span>
          </h2>
          <span class="text-xs px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 font-medium" id="hypotheses-count">3 Registered</span>
        </div>
        <div class="space-y-3" id="hypotheses-container">
          <!-- Rendered via JS -->
        </div>
      </section>

    </div>

    <!-- Registered Experiment Matrix -->
    <section class="glass rounded-xl p-5 border border-slate-800 space-y-4">
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <h2 class="text-base font-bold text-white flex items-center space-x-2">
            <i class="fa-solid fa-vial text-emerald-400"></i>
            <span>Registered Experiment Matrix (Isaac Lab & Physical Testbed)</span>
          </h2>
          <p class="text-xs text-slate-400 mt-0.5">Every experiment is constrained to at least 5 distinct random seeds and mandatory baselines</p>
        </div>
        <div class="flex items-center space-x-2">
          <span class="text-xs px-2.5 py-1 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 font-semibold" id="experiments-count">8 Experiments</span>
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs text-slate-300">
          <thead class="bg-slate-900 text-slate-400 uppercase font-semibold text-[10px] tracking-wider border-b border-slate-800">
            <tr>
              <th class="py-2.5 px-3">ID</th>
              <th class="py-2.5 px-3">Experiment Name</th>
              <th class="py-2.5 px-3">Category</th>
              <th class="py-2.5 px-3">Algorithm</th>
              <th class="py-2.5 px-3">Envs / Seeds</th>
              <th class="py-2.5 px-3">Target Metric</th>
              <th class="py-2.5 px-3">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800 font-mono" id="experiments-table">
            <!-- Rendered via JS -->
          </tbody>
        </table>
      </div>
    </section>

    <!-- Paper Claims & Scientific Integrity Audit -->
    <section class="glass rounded-xl p-5 border border-slate-800 space-y-4">
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <h2 class="text-base font-bold text-white flex items-center space-x-2">
            <i class="fa-solid fa-file-shield text-amber-400"></i>
            <span>Paper Claims Traceability Audit (Zero Hallucination Shield)</span>
          </h2>
          <p class="text-xs text-slate-400 mt-0.5">No claim is marked verified without verifiable proof from experimental run data</p>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4" id="claims-container">
        <!-- Rendered via JS -->
      </div>
    </section>

  </main>

  <script>
    async function loadData() {
      try {
        const res = await fetch('/api/state');
        const data = await res.json();
        renderDashboard(data);
      } catch (err) {
        console.error("Failed to load research state:", err);
      }
    }

    function renderDashboard(data) {
      // GPU
      const gpu = data.gpu || {};
      document.getElementById('gpu-vram').textContent = `${gpu.memory_used_mb || 0} / ${gpu.memory_total_mb || 8192} MB (${gpu.temp_c || 0}°C)`;
      document.getElementById('gpu-bar').style.width = `${gpu.memory_percent || 0}%`;

      // Agents
      const agentsGrid = document.getElementById('agents-grid');
      agentsGrid.innerHTML = data.agents.map(a => `
        <div class="glass-card rounded-xl p-3.5 flex items-start space-x-3 transition hover:border-slate-700">
          <div class="w-9 h-9 rounded-lg flex items-center justify-center text-lg flex-shrink-0" style="background: ${a.color}20; color: ${a.color}">
            ${a.icon}
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between">
              <h3 class="text-xs font-bold text-white truncate">${a.name}</h3>
              <span class="text-[9px] px-1.5 py-0.5 rounded font-semibold ${a.status === 'ACTIVE' ? 'bg-cyan-950 text-cyan-400 border border-cyan-800' : 'bg-slate-800 text-slate-400'}">${a.status}</span>
            </div>
            <p class="text-[11px] text-slate-400 mt-0.5 line-clamp-1">${a.role}</p>
          </div>
        </div>
      `).join('');

      // Milestones
      const milestones = data.status?.milestones || [];
      document.getElementById('milestones-count').textContent = `${milestones.length} Milestones`;
      const mContainer = document.getElementById('milestones-container');
      mContainer.innerHTML = milestones.map(m => `
        <div class="glass-card p-3 rounded-lg space-y-1.5">
          <div class="flex items-center justify-between text-xs">
            <div class="flex items-center space-x-2">
              <span class="font-mono text-cyan-400 font-bold">${m.id}</span>
              <span class="font-medium text-slate-200">${m.title}</span>
            </div>
            <span class="text-[10px] px-2 py-0.5 rounded-full font-semibold ${
              m.status === 'COMPLETED' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' :
              (m.status === 'IN_PROGRESS' ? 'bg-amber-950 text-amber-400 border border-amber-800' : 'bg-slate-800 text-slate-400')
            }">${m.status}</span>
          </div>
          <div class="flex items-center justify-between text-[11px] text-slate-400">
            <span>Agent: <strong class="text-slate-300">${m.assigned_agent}</strong> | Target: ${m.target_date}</span>
            <span class="font-bold text-slate-300">${m.progress_percent}%</span>
          </div>
          <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div class="h-full bg-indigo-500 rounded-full" style="width: ${m.progress_percent}%"></div>
          </div>
        </div>
      `).join('');

      // Hypotheses
      const hypotheses = data.hypotheses?.hypotheses || [];
      document.getElementById('hypotheses-count').textContent = `${hypotheses.length} Registered`;
      const hContainer = document.getElementById('hypotheses-container');
      hContainer.innerHTML = hypotheses.map(h => `
        <div class="glass-card p-3 rounded-lg space-y-1.5">
          <div class="flex items-center justify-between text-xs">
            <div class="flex items-center space-x-2">
              <span class="font-mono text-purple-400 font-bold">${h.id}</span>
              <span class="font-bold text-slate-100">${h.title}</span>
            </div>
            <span class="text-[10px] px-2 py-0.5 rounded-full font-semibold ${
              h.status === 'SUPPORTED' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-cyan-950 text-cyan-400 border border-cyan-800'
            }">${h.status}</span>
          </div>
          <p class="text-[11px] text-slate-300 leading-relaxed font-sans">${h.statement}</p>
          <div class="text-[10px] text-slate-400 pt-1 border-t border-slate-800 flex justify-between">
            <span>Experiments: <span class="text-indigo-300">${h.associated_experiments?.join(', ')}</span></span>
          </div>
        </div>
      `).join('');

      // Experiments Table
      const experiments = data.experiments?.experiments || [];
      document.getElementById('experiments-count').textContent = `${experiments.length} Registered`;
      const eTable = document.getElementById('experiments-table');
      eTable.innerHTML = experiments.map(e => `
        <tr class="hover:bg-slate-800/40 transition">
          <td class="py-2.5 px-3 font-bold text-cyan-400">${e.id}</td>
          <td class="py-2.5 px-3 font-sans text-slate-200">${e.name}</td>
          <td class="py-2.5 px-3"><span class="px-1.5 py-0.5 text-[10px] rounded bg-slate-800 text-slate-300 font-semibold">${e.category}</span></td>
          <td class="py-2.5 px-3 text-slate-300">${e.algorithm}</td>
          <td class="py-2.5 px-3">${e.num_envs} envs / ${e.seeds?.length} seeds</td>
          <td class="py-2.5 px-3 text-indigo-300">${e.primary_metric}: &gt;= ${e.target_metric_value}</td>
          <td class="py-2.5 px-3">
            <span class="px-2 py-0.5 text-[10px] rounded-full font-semibold ${
              e.status === 'COMPLETED' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' :
              (e.status === 'RUNNING' ? 'bg-cyan-950 text-cyan-400 border border-cyan-800' : 'bg-slate-800 text-slate-400')
            }">${e.status}</span>
          </td>
        </tr>
      `).join('');

      // Paper Claims
      const claims = data.claims?.claims || [];
      const cContainer = document.getElementById('claims-container');
      cContainer.innerHTML = claims.map(c => `
        <div class="glass-card p-3.5 rounded-lg space-y-2">
          <div class="flex items-center justify-between text-xs">
            <span class="font-mono text-amber-400 font-bold">${c.id} · ${c.paper_section}</span>
            <span class="text-[10px] px-2 py-0.5 rounded-full font-semibold ${
              c.status === 'VERIFIED' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-amber-950 text-amber-400 border border-amber-800'
            }">${c.status}</span>
          </div>
          <p class="text-xs text-slate-200 leading-relaxed">${c.statement}</p>
          <div class="pt-2 border-t border-slate-800 text-[10px] text-slate-400 space-y-0.5">
            <div>Required Exps: <strong class="text-cyan-300">${c.required_experiments?.join(', ')}</strong></div>
            <div>Statistical Rigor: <span class="text-slate-300">${c.statistical_test}</span></div>
          </div>
        </div>
      `).join('');
    }

    function refreshData() {
      loadData();
    }

    // Auto-refresh every 8 seconds
    loadData();
    setInterval(loadData, 8000);
  </script>
</body>
</html>
"""


class DashboardHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
        elif parsed.path == "/api/state":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode("utf-8"))
        elif parsed.path == "/api/state":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            data = get_research_data()
            self.wfile.write(json.dumps(data).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Silence routine request logging
        return


def run_server(port=PORT):
    server = HTTPServer(("0.0.0.0", port), DashboardHandler)
    print(f"\n==================================================================")
    print(f"  DEX-ROB Lab Multi-Agent Web Dashboard Online!")
    print(f"  URL: http://localhost:{port}")
    print(f"  Live Sync: research_state/ + GPU telemetry (RTX 5060)")
    print(f"==================================================================\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down dashboard server...")
        server.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run_server(port)
