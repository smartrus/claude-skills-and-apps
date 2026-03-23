---
name: agentic-rag-evaluator
description: >-
  Acts as the verification and grounding layer in Retrieval-Augmented Generation (RAG) pipelines. 
  Evaluates retrieved context chunks for factual accuracy, relevance, and completeness before they reach 
  the generation stage. Detects hallucination risk, stale data, source conflicts, and insufficient context.
  
  Trigger when: rag evaluation, rag quality, retrieval quality check, grounding check, hallucination detection, 
  context verification, rag pipeline audit, retrieval accuracy, evaluate rag.
  
  Do NOT trigger: building RAG pipelines from scratch, vector database setup or tuning, prompt engineering for LLMs, 
  general data quality auditing without RAG context, or training data validation (use data-poisoning-auditor).
version: 0.1.0
author: smartrus
tags: [data, rag, evaluation, hallucination-detection, grounding, retrieval, factual-accuracy, llm-verification]
triggers:
  - rag evaluation
  - rag quality
  - retrieval quality check
  - grounding check
  - hallucination detection
  - context verification
  - rag pipeline audit
  - retrieval accuracy
  - evaluate rag
---
