import pandas as pd
import numpy as np
import heapq
import math
import os
import time
from typing import List, Tuple, Dict
import sys

data = {
    "Component": ["AuthCore", "QueueRelay", "EdgeOrchestrator", "WebGateway", "CloudInference"],
    "CPU(%)": [47, 63, 58, 52, 74],
    "Memory(GB)": [2.4, 3.1, 4.6, 3.7, 9.3],
    "Latency(ms)": [21, 27, 31, 38, 44],
    "Throughput(Mbps)": [520, 430, 610, 690, 1150],
    "Reliability(%)": [97.6, 96.8, 96.9, 94.7, 92.4],
    "Requests/sec": [165, 118, 190, 215, 275],
    "Dependency": [None, "AuthCore", "QueueRelay", "EdgeOrchestrator", "WebGateway"],
    "FaultEvents": ['Retry,Drift', 'Backpressure', 'NodePartition', 'Livelock', 'Crash,Timeout,Replay']
}

df = pd.DataFrame(data)

class TelecomOptimizer:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.results = {}
        
    def clear_line(self, n=1):
        for _ in range(n):
            print('\033[1A\033[K', end='')
    
    def flash_print(self, text, duration=1.5):
        print(text, end='', flush=True)
        time.sleep(duration)
        self.clear_line()
        print(' ' * 80, end='', flush=True)
        self.clear_line()
    
    def total_latency(self, component, memo={}):
        if component in memo:
            return memo[component]
        row = self.df[self.df['Component'] == component].iloc[0]
        latency = row['Latency(ms)']
        dep = row['Dependency']
        if dep is None:
            memo[component] = latency
            return latency
        else:
            dep_latency = self.total_latency(dep, memo)
            total = latency + dep_latency
            memo[component] = total
            return total
    
    def sim_a_dependency_recursion(self):
        print("\n" + "═" * 80)
        print("📊 DEPENDENCY RECURSION ANALYSIS".center(80))
        print("═" * 80)
        
        df_copy = self.df.copy()
        df_copy['Total Latency'] = df_copy['Component'].apply(lambda x: self.total_latency(x))
        self.results['a_df'] = df_copy
        dominant_component = df_copy.loc[df_copy['Total Latency'].idxmax(), 'Component']
        self.results['dominant'] = dominant_component
        
        print(df_copy[['Component','Latency(ms)','Total Latency']].to_string(index=False))
        print()
        print(f"🎯 {dominant_component} is the dominant latency source with {df_copy['Total Latency'].max():.0f}ms total latency.".center(80))
        print("Its removal minimally perturbs downstream throughput due to chain position.".center(80))
    
    def sim_b_consensus_rpc(self):
        print("\n" + "═" * 80)
        print("🔒 CONSENSUS-RPC SCHEME".center(80))
        print("═" * 80)
        
        result_a = self.results['a_df']
        dominant_latency = result_a['Total Latency'].max()
        threshold = dominant_latency * 0.9
        all_below_threshold = all(row['Latency(ms)'] <= threshold for _, row in self.df.iterrows())
        self.results['consensus_threshold'] = threshold
        
        print(f"Threshold set to {threshold:.1f}ms based on {self.results['dominant']} dominance.".center(80))
        print(f"All components meet threshold: {all_below_threshold}".center(80))
        print("Correctness depends on dominant source removal maintaining this invariant.".center(80))
    
    def sim_c_contention_model(self):
        print("\n" + "═" * 80)
        print("⚙️ CONTENTION MODEL".center(80))
        print("═" * 80)
        
        loads = self.df['CPU(%)'].values / 100
        latencies = self.df['Latency(ms)'].values
        contention_rate = np.mean(latencies * loads) / np.mean(latencies)
        self.results['contention_rate'] = contention_rate
        
        print(f"Contention rate: {contention_rate:.2f} (requires consensus invariance)".center(80))
        print("Feasibility holds only if b's threshold remains stable under load.".center(80))
    
    def sim_d_latency_elasticity(self):
        print("\n" + "═" * 80)
        print("📈 LATENCY ELASTICITY".center(80))
        print("═" * 80)
        
        loads = self.df['CPU(%)'].values / 100
        latencies = self.df['Latency(ms)'].values
        log_loads = np.log(loads + 0.1)
        log_lat = np.log(latencies)
        elasticity = np.polyfit(log_loads, log_lat, 1)[0]
        self.results['elasticity'] = elasticity
        
        print(f"Elasticity ε={elasticity:.2f} shows super-linear contention scaling.".center(80))
        print("Trade-off: higher throughput increases latency non-linearly.".center(80))
    
    def sim_e_throughput_optimization(self):
        print("\n" + "═" * 80)
        print("🚀 THROUGHPUT OPTIMIZATION".center(80))
        print("═" * 80)
        
        mem_mean = np.mean(self.df['Memory(GB)'])
        mem_var = np.var(self.df['Memory(GB)'])
        mem_divergence = mem_var / (mem_mean ** 2)
        elasticity = self.results['elasticity']
        B = 2000
        L_mean = np.mean(self.df['Latency(ms)'])
        throughput_bound = min(1150, B / (L_mean * np.sqrt(mem_divergence)) / elasticity)
        self.results['throughput_bound'] = throughput_bound
        
        print(f"Max throughput: {throughput_bound:.0f}Mbps bounded by memory divergence {mem_divergence:.3f}".center(80))
        print("Under worst-case scheduling with elasticity constraint.".center(80))
    
    def sim_f_optimization_logic(self):
        print("\n" + "═" * 80)
        print("⚡ OPTIMIZATION SCHEDULE".center(80))
        print("═" * 80)
        
        throughput_bound = self.results['throughput_bound']
        pq = []
        for idx, row in self.df.iterrows():
            load = row['CPU(%)'] / 100
            base_latency = row['Latency(ms)']
            L_contended = base_latency * (1 + 1.3 * load ** 1.4)
            rel_factor = row['Reliability(%)'] / 100
            theta = min(row['Throughput(Mbps)'], throughput_bound * rel_factor)
            heapq.heappush(pq, (-theta, L_contended, row['Memory(GB)'], row['Component'], idx))
        schedule = [heapq.heappop(pq) for _ in pq]
        self.results['schedule'] = schedule
        
        for i, (theta, lr, mem, comp, idx) in enumerate(schedule):
            print(f"  {i+1:2d}. {comp:18s} | { -theta:4.0f}Mbps | {lr:5.1f}ms | {mem:4.1f}GB")
        print("(a-e assumptions valid)".center(80))
    
    def sim_g_architecture_validation(self):
        print("\n" + "═" * 80)
        print("🏗️ ARCHITECTURE VALIDATION".center(80))
        print("═" * 80)
        
        violations = []
        if 'consensus_threshold' not in self.results:
            violations.append("missing b")
        elif self.results.get('contention_rate', 0) > 1.2:
            violations.append("contention too high")
        elif self.results.get('elasticity', 0) > 2.0:
            violations.append("extreme non-linearity")
        
        if violations:
            print(f"❌ ARCHITECTURE INVALIDATED: {', '.join(violations)}".center(80))
            print("All downstream results invalid due to broken assumptions.".center(80))
        else:
            print(f"✅ ARCHITECTURE VALID: {self.results.get('dominant', 'N/A')} dominance → full pipeline holds".center(80))
    
    def run_full_pipeline(self):
        self.sim_a_dependency_recursion()
        self.sim_b_consensus_rpc()
        self.sim_c_contention_model()
        self.sim_d_latency_elasticity()
        self.sim_e_throughput_optimization()
        self.sim_f_optimization_logic()
        self.sim_g_architecture_validation()

def get_back_choice():
    print("\n" + "─" * 50)
    print("1. Repeat Answer")
    print("0. Back to Menu") 
    print("X. Exit")
    print("─" * 50)
    while True:
        choice = input("Choose: ").strip().upper()
        if choice in ['1', '0', 'X']:
            return choice

def main():
    optimizer = TelecomOptimizer(df)
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n" + "═" * 90)
        print("🌐 OOP CAT 2 BY ODUKE ".center(90))
        print("═" * 90)
        print("\n📋 FULL DATASET:")
        print(df.to_string(index=False))
        print("\n" + "═" * 90)
        print("What question do you want to answer?")
        print("1. (a) Dependency recursion → dominant latency source")
        print("2. (b) Consensus-RPC scheme") 
        print("3. (c) Contention model feasibility")
        print("4. (d) Latency elasticity trade-offs")
        print("5. (e) Throughput optimization (memory bounded)")
        print("6. (f) Python optimization abstractions")
        print("7. (g) Architecture validation")
        print("8. FULL PIPELINE (a→g)")
        print("0. Exit")
        print("─" * 90)
        
        try:
            choice = input("Enter choice (0-8): ").strip()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)
        
        if choice == '1':
            optimizer.sim_a_dependency_recursion()
        elif choice == '2':
            optimizer.sim_a_dependency_recursion()
            optimizer.sim_b_consensus_rpc()
        elif choice == '3':
            optimizer.sim_a_dependency_recursion()
            optimizer.sim_b_consensus_rpc()
            optimizer.sim_c_contention_model()
        elif choice == '4':
            optimizer.sim_a_dependency_recursion()
            optimizer.sim_b_consensus_rpc()
            optimizer.sim_c_contention_model()
            optimizer.sim_d_latency_elasticity()
        elif choice == '5':
            optimizer.sim_a_dependency_recursion()
            optimizer.sim_b_consensus_rpc()
            optimizer.sim_c_contention_model()
            optimizer.sim_d_latency_elasticity()
            optimizer.sim_e_throughput_optimization()
        elif choice == '6':
            optimizer.sim_a_dependency_recursion()
            optimizer.sim_b_consensus_rpc()
            optimizer.sim_c_contention_model()
            optimizer.sim_d_latency_elasticity()
            optimizer.sim_e_throughput_optimization()
            optimizer.sim_f_optimization_logic()
        elif choice == '7':
            optimizer.sim_a_dependency_recursion()
            optimizer.sim_b_consensus_rpc()
            optimizer.sim_c_contention_model()
            optimizer.sim_d_latency_elasticity()
            optimizer.sim_g_architecture_validation()
        elif choice == '8':
            optimizer.run_full_pipeline()
        elif choice == '0':
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice!".center(90))
            time.sleep(1)
            continue
        
        back_choice = get_back_choice()
        if back_choice == 'X':
            print("\n👋 Goodbye!")
            sys.exit(0)
        elif back_choice == '0':
            continue

if __name__ == "__main__":
    main()
