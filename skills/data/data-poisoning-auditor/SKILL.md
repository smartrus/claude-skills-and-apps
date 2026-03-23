---
name: data-poisoning-auditor
description: >-
  Scans AI training data pipelines and datasets to detect bias, data poisoning, label corruption, 
  and statistical anomalies that could compromise autonomous AI decision-making. Generates audit 
  reports with poisoning risk scores and remediation recommendations.
  
  Trigger when: data poisoning, training data audit, dataset bias, label corruption, data integrity check, 
  poisoned data detection, training pipeline audit, adversarial data, dataset contamination.
  
  Do NOT trigger: general data quality profiling without AI/ML context, RAG evaluation (use agentic-rag-evaluator), 
  model performance evaluation, feature engineering, or data visualization.
version: 0.1.0
author: smartrus
tags: [data, ai-safety, data-poisoning, bias-detection, training-data, dataset-audit, ml-security, data-integrity]
triggers:
  - data poisoning
  - training data audit
  - dataset bias
  - label corruption
  - data integrity check
  - poisoned data detection
  - training pipeline audit
  - adversarial data
  - dataset contamination
---
