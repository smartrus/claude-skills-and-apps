---
name: semantic-schema-mapper
description: >-
  Uses semantic analysis and local embeddings to map ambiguous legacy database columns to modern canonical schemas. 
  Resolves naming inconsistencies (e.g., cust_nm → customer.full_name), infers data types from sample values, 
  and generates migration DDL and ETL transformation logic.
  
  Trigger when: schema mapping, column mapping, legacy database migration, schema translation, canonical schema, 
  field mapping, database schema alignment, map legacy columns.
  
  Do NOT trigger: general SQL query writing, database performance tuning, data visualization, ETL pipeline orchestration 
  without schema context, or data quality checks without mapping needs.
version: 0.1.0
author: smartrus
tags: [data, schema-mapping, legacy-migration, etl, database, semantic-matching, data-modeling]
triggers:
  - schema mapping
  - column mapping
  - legacy database migration
  - schema translation
  - canonical schema
  - field mapping
  - database schema alignment
  - map legacy columns
---
