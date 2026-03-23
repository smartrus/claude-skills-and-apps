---
name: performance-bottleneck-debugger
description: >-
  Uses causal reasoning and distributed tracing analysis to locate the root microservice causing 
  unpredictable latency spikes in complex service meshes. Analyzes trace spans, dependency graphs, 
  and timing correlations to pinpoint bottlenecks that traditional APM tools miss. Trigger when: 
  latency spikes occur, performance bottlenecks need identification, slow microservice investigation, 
  trace analysis required, distributed tracing debug needed, p99 latency investigation, service mesh 
  latency issues, or root cause latency analysis. Do NOT trigger for: general application debugging 
  without latency context, Kubernetes pod lifecycle issues, network connectivity troubleshooting, 
  load testing or capacity planning, or cost optimization.
version: 0.1.0
author: smartrus
tags: [operations, performance, debugging, latency, distributed-tracing, microservices, bottleneck, root-cause]
triggers:
  - latency spike
  - performance bottleneck
  - slow microservice
  - trace analysis
  - distributed tracing debug
  - p99 latency
  - service mesh latency
  - root cause latency
---
