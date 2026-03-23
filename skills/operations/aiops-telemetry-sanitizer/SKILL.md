---
name: aiops-telemetry-sanitizer
description: >-
  Cleanses observability logs and telemetry streams to defend autonomous AIOps agents against 
  adversarial prompt injections and reward-hacking embedded in log data. Scans log lines for 
  injection patterns, suspicious Unicode, and encoded payloads that could manipulate LLM-based 
  alerting or automated remediation systems. Trigger when: log sanitization is needed, telemetry 
  cleansing required, prompt injection suspected in logs, aiops security hardening, log injection 
  defense implementation, adversarial log detection, reward hacking defense needed, or when you need 
  to sanitize telemetry pipelines. Do NOT trigger for: general log aggregation or search, 
  application-level logging configuration, setting up monitoring dashboards, Kubernetes pod debugging, 
  SIEM rule writing, or general security scanning.
version: 0.1.0
author: smartrus
tags: [operations, aiops, telemetry, log-sanitization, prompt-injection, security, observability]
triggers:
  - log sanitization
  - telemetry cleansing
  - prompt injection in logs
  - aiops security
  - log injection defense
  - adversarial logs
  - reward hacking defense
  - sanitize telemetry
---
