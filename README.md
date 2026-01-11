# OOP CAT 2: Thinking and Flow of execution

**Task demanded a step-by-step (a-g) where each step requires previous output. Hardest was "(a) dependency recursion" - trace full chain: AuthCore→QueueRelay→EdgeOrchestrator→WebGateway→CloudInference.**

## My Answer;

**1. (a) Dependency Recursion**  
I took my `total_latency()` recursive function and ran it on all components. Added up AuthCore(21)+QueueRelay(27)+EdgeOrchestrator(31)+WebGateway(38)+CloudInference(44) = **161ms total**. **CloudInference dominates** since it's end of chain.

**2. (b) Consensus-RPC**  
Took my 161ms from (a), multiplied by 0.9 = **144.9ms threshold**. Tested if all components stay under it. They do, so consensus passes.

**3. (c) Contention Model**  
Multiplied CPU% by latency for each row, averaged it = **1.02 rate**. Figured this had to stay stable for (b)'s threshold to work under load.

**4. (d) Latency Elasticity**  
Did log(CPU load) vs log(latency) linear fit. Got slope **ε=1.28**. Since >1, means latency grows faster than load (non-linear contention).

**5. (e) Throughput Optimization**  
Took memory variance divided by mean squared = divergence. Divided bandwidth by that and elasticity from (d). Got **847Mbps max**.

**6. (f) Scheduler**  
Built heapq priority queue. For each component calculated contended latency using (d)'s elasticity. Multiplied by (e)'s throughput cap. Sorted highest-first.

**7. (g) Architecture Check**  
If (b) fails OR (c) rate >1.2 OR (d) elasticity >2.0 → print "ARCHITECTURE INVALID". Everything else = safe.

**Special mention: Sora-Large**
