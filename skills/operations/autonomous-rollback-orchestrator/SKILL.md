---
name: autonomous-rollback-orchestrator
description: >-
  Triggers automated remediation and rollback pipelines when real-time health metrics breach 
  Service Level Objectives (SLOs). Designs rollback decision trees, configures metric-based triggers, 
  and generates runbooks for autonomous incident response that minimize MTTR while respecting 
  human-in-the-loop checkpoints. Trigger when: automated rollback needed, SLO breach detected, 
  rollback orchestration required, autonomous remediation needed, metric-based rollback decisions, 
  rollback pipeline design, rollback decision trees, or canary rollback scenarios. Do NOT trigger for: 
  manual incident response workflows, general CI/CD pipeline setup, Terraform drift detection, 
  application performance tuning, or monitoring/alerting configuration.
version: 0.1.0
author: smartrus
tags: [operations, sre, rollback, slo, remediation, incident-response, mttr, automation]
triggers:
  - automated rollback
  - slo breach
  - rollback orchestration
  - autonomous remediation
  - metric-based rollback
  - rollback pipeline
  - rollback decision tree
  - canary rollback
---
