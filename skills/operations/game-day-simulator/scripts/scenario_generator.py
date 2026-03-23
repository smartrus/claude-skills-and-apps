#!/usr/bin/env python3
"""
Game Day Scenario Generator

Generates structured disaster recovery tabletop exercise scenarios including:
- Inject timelines (timed events with expected responses)
- Scoring rubrics for evaluating team performance
- Scenario briefs for facilitators

Usage:
    python3 scenario_generator.py --scenario-type region-failure --duration 90 --team-size 8
"""

import argparse
import sys
from typing import List, Dict, Any


def generate_inject_timeline(scenario_type: str, duration: int) -> List[Dict[str, Any]]:
    """
    Generate a timeline of timed injects (events) for a given scenario.
    
    Returns list of dicts with keys:
      - time_offset: minutes from start
      - inject_description: what the facilitator reveals
      - expected_response: what the team should do
      - difficulty: "easy" | "medium" | "hard"
    """
    
    scenarios = {
        "region-failure": [
            {
                "time_offset": 0,
                "inject_description": "⚠️  Multi-AZ outage reported in us-east-1. All EC2 instances and RDS primary are unavailable. Health checks failing.",
                "expected_response": "Declare SEV-1. Activate on-call runbook. Verify DNS/traffic routing to us-west-2 standby region.",
                "difficulty": "easy"
            },
            {
                "time_offset": 5,
                "inject_description": "Customers reporting connection timeouts to API. CloudFront caching is masking some failures but miss rate is 15%.",
                "expected_response": "Check CloudFront invalidation status. Verify health check thresholds didn't miss the failover trigger.",
                "difficulty": "medium"
            },
            {
                "time_offset": 15,
                "inject_description": "⚡ HIDDEN: Read replica in us-west-2 is 45 minutes behind primary due to replication lag from before the outage.",
                "expected_response": "Discover lag via replication metrics. Decide: restore from S3 snapshot (30min) vs. accept stale data.",
                "difficulty": "hard"
            },
            {
                "time_offset": 30,
                "inject_description": "Database team reports: cross-region RDS failover completed, but standing queries from cached app servers causing connection storms.",
                "expected_response": "Restart application tier in secondary region. Verify connection pooling configured correctly.",
                "difficulty": "medium"
            },
            {
                "time_offset": 50,
                "inject_description": "Traffic fully shifted to us-west-2. RTO target was 30min. Current recovery: 50min. Post-incident: what's next?",
                "expected_response": "Begin post-incident analysis. Schedule architecture review. Discuss improvements to failover automation.",
                "difficulty": "easy"
            }
        ],
        "db-corruption": [
            {
                "time_offset": 0,
                "inject_description": "⚠️  Application error rate spikes to 8%. Database team reports: query anomalies detected (invalid index stats, corrupt b-tree detected in WAL).",
                "expected_response": "Isolate affected queries. Check recent schema changes. Review last known good backup timestamp.",
                "difficulty": "medium"
            },
            {
                "time_offset": 10,
                "inject_description": "FSCK reveals: 3 corrupt heap pages in high-traffic 'users' table. Estimate: 200-500 user records affected.",
                "expected_response": "Escalate. Query business impact. Prepare notification strategy for affected users.",
                "difficulty": "medium"
            },
            {
                "time_offset": 20,
                "inject_description": "⚡ HIDDEN: Last automated snapshot from 4 hours ago. Also shows corruption (corrupted data was written hours before detection).",
                "expected_response": "Backtrack: when did corruption actually start? Review transaction logs / WAL. Decision: how far back to restore?",
                "difficulty": "hard"
            },
            {
                "time_offset": 35,
                "inject_description": "Restore from 8-hour-old snapshot to staging. Corruption does NOT appear. New snapshot taken. Standby replica rebuilt.",
                "expected_response": "Plan cutover. Validate data consistency. Prepare communication for 4-8 hour data loss window.",
                "difficulty": "medium"
            },
            {
                "time_offset": 60,
                "inject_description": "Primary switched to restored snapshot. Traffic restored. Root cause analysis: investigate bitrot, memory corruption, or WAL archiving issue.",
                "expected_response": "Post-incident: schedule detailed RCA. Plan additional backup validation checks.",
                "difficulty": "easy"
            }
        ],
        "dns-hijack": [
            {
                "time_offset": 0,
                "inject_description": "⚠️  Customer calls: 'api.example.com resolves to wrong IP (1.2.3.4 instead of 10.0.0.5)'. Your monitoring not catching it.",
                "expected_response": "Query DNS records. Check Route53 (or primary DNS provider). Verify authoritative nameserver responses.",
                "difficulty": "easy"
            },
            {
                "time_offset": 8,
                "inject_description": "Investigation: DNS provider account shows unauthorized API key added 2 days ago. Recent record changes: A record, AAAA record, MX record.",
                "expected_response": "Rotate API keys immediately. Check for data exfiltration via wrong MX. Review CloudTrail / audit logs.",
                "difficulty": "hard"
            },
            {
                "time_offset": 20,
                "inject_description": "⚡ HIDDEN: Internal service-to-service DNS is also poisoned. Internal service discovery returning attacker's IP for internal DB endpoints.",
                "expected_response": "Isolate internal network. Flush DNS caches in application tier. Verify service mesh / consul health.",
                "difficulty": "hard"
            },
            {
                "time_offset": 35,
                "inject_description": "Restore correct DNS records. Update TTLs to 60 seconds for rapid rollback capability. Begin forensic investigation.",
                "expected_response": "Communicate to customer. Schedule security investigation. Prepare incident response and IR documentation.",
                "difficulty": "medium"
            }
        ],
        "cert-expiry": [
            {
                "time_offset": 0,
                "inject_description": "⚠️  3:00 AM Saturday: TLS cert for api.example.com expires. HTTPS traffic to API fails. Client apps receive certificate validation errors.",
                "expected_response": "Page on-call. Verify cert-manager status. Check for blocked cert renewal (DNS challenge, rate limit).",
                "difficulty": "easy"
            },
            {
                "time_offset": 8,
                "inject_description": "Service-to-service mTLS: internal services use mTLS certs issued by same CA. Those certs also expired. Service-to-service calls failing.",
                "expected_response": "Identify all affected certificates. Initiate renewal across cert-manager for all services.",
                "difficulty": "hard"
            },
            {
                "time_offset": 15,
                "inject_description": "⚡ HIDDEN: cert-manager pod CrashLooping. Certificate renewal not progressing. ClusterRole permissions insufficient for DNS challenge.",
                "expected_response": "Debug cert-manager logs. Check RBAC. Manually trigger cert renewal or fix permissions.",
                "difficulty": "hard"
            },
            {
                "time_offset": 30,
                "inject_description": "Certificate renewed. Services restarted. mTLS re-established. Document: what failed? Why wasn't this caught pre-expiry?",
                "expected_response": "Review cert-manager monitoring. Set up renewal deadline alerts at 30/14/7 days. Automate cert rotation testing.",
                "difficulty": "medium"
            }
        ],
        "dependency-outage": [
            {
                "time_offset": 0,
                "inject_description": "⚠️  Third-party payment processor API is returning 503 Service Unavailable for all requests. Payment processing is completely blocked.",
                "expected_response": "Alert vendor. Check their status page. Verify our fallback/queue strategy for pending payments.",
                "difficulty": "easy"
            },
            {
                "time_offset": 10,
                "inject_description": "Vendor status page shows: 'Investigating. No ETA.' Your queue of unpaid orders is growing. Customers experiencing checkout failures.",
                "expected_response": "Activate mitigation: queue payments locally. Notify customers of temporary checkout delays. Plan manual reconciliation.",
                "difficulty": "medium"
            },
            {
                "time_offset": 25,
                "inject_description": "Vendor: 'Recovering. Processing backlog.' Outage has lasted 25 minutes. Estimate: 1-2 hours to clear payment queue.",
                "expected_response": "Monitor vendor recovery. Begin replay of queued payments. Verify idempotency to avoid double-charging.",
                "difficulty": "hard"
            }
        ],
        "data-breach": [
            {
                "time_offset": 0,
                "inject_description": "⚠️  Security team alerts: suspicious SQL injection attempts detected in logs. 10K requests to /api/users endpoint with malicious payloads (last 1 hour).",
                "expected_response": "Isolate affected systems. Enable detailed logging. Check if payloads successfully exfiltrated data.",
                "difficulty": "medium"
            },
            {
                "time_offset": 15,
                "inject_description": "Investigation confirms: attacker gained access to user_profiles table. Extracted: 5K user records (names, emails, hashed passwords, encrypted SSNs).",
                "expected_response": "Trigger incident response. Notify legal/compliance. Prepare disclosure. Begin user notification process.",
                "difficulty": "hard"
            },
            {
                "time_offset": 35,
                "inject_description": "Patch deployed (input validation). Attacker's API key revoked. Forensic investigation ongoing. Regulatory notification due in 48-72 hours.",
                "expected_response": "Draft regulatory notification. Prepare call with legal. Plan user communications and credit monitoring offers.",
                "difficulty": "hard"
            }
        ]
    }
    
    template = scenarios.get(scenario_type, [])
    if not template:
        return []

    # Scale inject time offsets proportionally to the requested duration.
    # The template offsets are authored for a reference duration; we stretch
    # or compress them so the last inject lands near the end of the exercise.
    max_template_offset = max(inject['time_offset'] for inject in template) or 1
    # Reserve the final 15% of duration for wrap-up after the last inject
    usable_duration = int(duration * 0.85)
    scale_factor = usable_duration / max_template_offset if max_template_offset > 0 else 1

    scaled = []
    for inject in template:
        scaled_inject = dict(inject)
        scaled_inject['time_offset'] = round(inject['time_offset'] * scale_factor)
        scaled.append(scaled_inject)

    return scaled


def generate_scoring_rubric(scenario_type: str) -> List[Dict[str, Any]]:
    """
    Generate evaluation criteria for scoring team performance.
    
    Returns list of dicts with keys:
      - criterion: evaluation category
      - weight: relative importance (1-5)
      - description: what to assess
      - excellent: example of excellent execution
      - poor: example of poor execution
    """
    
    # Common criteria across all scenarios
    rubric = [
        {
            "criterion": "Detection Speed",
            "weight": 3,
            "description": "How quickly team identified the issue and escalated",
            "excellent": "Issue recognized within 2 minutes, SEV-1 declared immediately",
            "poor": "Issue missed for 10+ minutes, slow escalation path"
        },
        {
            "criterion": "Decision Quality",
            "weight": 4,
            "description": "Quality of decisions made under pressure (runbook adherence, improvisation when needed)",
            "excellent": "Decisions aligned with runbook, good reasoning for deviations",
            "poor": "Panic-driven decisions, ignored documented procedures"
        },
        {
            "criterion": "Communication",
            "weight": 3,
            "description": "Clarity and frequency of status updates to stakeholders",
            "excellent": "Clear, frequent updates to Slack/war room. Transparent about unknowns.",
            "poor": "Radio silence. Contradictory updates. Uninformed stakeholders."
        },
        {
            "criterion": "Procedure Adherence",
            "weight": 2,
            "description": "Following documented runbooks and standard procedures",
            "excellent": "Followed documented procedures. Noted gaps for improvement.",
            "poor": "Ignored runbooks. Made critical decisions without verification."
        },
        {
            "criterion": "RTO/RPO Compliance",
            "weight": 3,
            "description": "Meeting recovery time and data loss objectives",
            "excellent": "Recovery completed within RTO target. Data loss within RPO.",
            "poor": "Significantly exceeded RTO/RPO targets without good justification"
        }
    ]

    # Scenario-specific criteria
    scenario_extras = {
        "data-breach": {
            "criterion": "Regulatory Compliance",
            "weight": 4,
            "description": "Timely notification to legal, compliance, and regulators as required",
            "excellent": "Legal notified within 15 minutes. Disclosure timeline drafted within the hour.",
            "poor": "Legal not engaged. No awareness of notification deadlines."
        },
        "dns-hijack": {
            "criterion": "Containment & Forensics",
            "weight": 3,
            "description": "Speed and thoroughness of isolating compromised systems and preserving evidence",
            "excellent": "API keys rotated immediately. Audit logs preserved. Blast radius mapped.",
            "poor": "Delayed rotation. Evidence overwritten by remediation steps."
        },
        "cert-expiry": {
            "criterion": "Blast Radius Mapping",
            "weight": 3,
            "description": "Identifying all affected certificates and downstream services",
            "excellent": "Full cert inventory produced quickly. All mTLS dependencies identified.",
            "poor": "Focused only on the initial cert. Missed cascading mTLS failures."
        },
    }

    if scenario_type in scenario_extras:
        rubric.append(scenario_extras[scenario_type])

    return rubric


def generate_scenario_brief(scenario_type: str, duration: int, team_size: int) -> str:
    """
    Generate a complete scenario brief combining context, timeline, and scoring.
    """
    
    scenario_titles = {
        "region-failure": "Multi-Region Failover Drill: us-east-1 Complete Outage",
        "db-corruption": "Database Corruption Detection & Recovery",
        "dns-hijack": "DNS Hijack Response: Unauthorized Record Changes",
        "cert-expiry": "Certificate Expiration Cascade",
        "dependency-outage": "Third-Party Service Outage (Payment Processor)",
        "data-breach": "Security Incident Response: Data Breach"
    }
    
    scenario_contexts = {
        "region-failure": """
SCENARIO CONTEXT
Architecture: Multi-region deployment (primary: us-east-1, standby: us-west-2)
- Primary region: RDS Multi-AZ, ELB, 12 EC2 instances
- Standby region: RDS standby read replica, preconfigured DNS failover
- SLA: 99.95% uptime (≈22 minutes downtime/month)
- RTO: 30 minutes
- RPO: 15 minutes
Team Roles: DNS/Routing (1), Database (2), Infrastructure (2), Application (2), Communications (1)
""",
        "db-corruption": """
SCENARIO CONTEXT
Database: PostgreSQL 14 RDS in us-west-2
- Automated daily snapshots (7-day retention)
- WAL archiving to S3 (30-day retention)
- Cross-region read replica in us-east-1
- Replication lag threshold: <5 seconds (alert at >10s)
- RTO: 1 hour
- RPO: 15 minutes
Team Roles: Database (3), Backup/Restore (1), Application (2), Communications (1)
""",
        "dns-hijack": """
SCENARIO CONTEXT
DNS Provider: Route53 (AWS)
- Authoritative for api.example.com and internal domains
- External-facing API: api.example.com
- Internal services: discovery.internal (Consul DNS)
- Multiple nameservers: ns1/ns2.example.com
Team Roles: Security (1), DNS/Networking (2), Infrastructure (2), Incident Response (2)
""",
        "cert-expiry": """
SCENARIO CONTEXT
Certificate Management: cert-manager on Kubernetes
- External cert (api.example.com): issued by Let's Encrypt, 90-day validity
- Internal mTLS: internal CA, 365-day certificates
- Service count: 12 microservices using mTLS
- Renewal window: cert-manager attempts renewal at 30 days before expiry
Team Roles: Kubernetes (2), Security/PKI (1), Application (2), Incident Response (1)
""",
        "dependency-outage": """
SCENARIO CONTEXT
Dependency: Stripe API for payment processing
- Current implementation: synchronous calls (3-second timeout)
- Fallback strategy: queue to SQS, async retry (documented but not tested)
- Payment volume: ~500 transactions/minute during peak
- Notification process: customers notified via email if payment delayed >2min
Team Roles: Payments (2), Backend (2), Incident Response (1), Customer Support (1)
""",
        "data-breach": """
SCENARIO CONTEXT
Systems: Web application + PostgreSQL backend
- Application: Node.js (Express), deployed on Kubernetes
- Authentication: JWT tokens, OAuth for social login
- Sensitive data: user profiles (names, emails, SSNs - encrypted at rest)
- Incident response: IR playbook exists; legal/compliance contact list prepared
Team Roles: Security (2), Incident Response (1), Backend/Database (2), Legal/Compliance (1), Communications (1)
"""
    }

    # Enforce minimum duration: each inject needs at least 2 minutes of spacing.
    # Look up inject count for this scenario to compute the floor.
    _inject_counts = {
        "region-failure": 5, "db-corruption": 5, "dns-hijack": 4,
        "cert-expiry": 4, "dependency-outage": 3, "data-breach": 3,
    }
    inject_count = _inject_counts.get(scenario_type, 3)
    min_duration = inject_count * 2
    if duration < min_duration:
        print(
            f"Warning: --duration {duration} is too short for {inject_count} injects. "
            f"Minimum recommended: {min_duration} minutes. Clamping to {min_duration}.",
            file=sys.stderr
        )
        duration = min_duration

    output = f"""
🔴 SIMULATION / EXERCISE — NOT A REAL INCIDENT 🔴
THIS IS A DRILL — DO NOT EXECUTE IN PRODUCTION
================================================================

GAME DAY SCENARIO BRIEF
{scenario_titles.get(scenario_type, "Unknown Scenario")}

Exercise Duration: {duration} minutes
Team Size: {team_size} participants
Difficulty Level: MEDIUM-TO-HARD

{scenario_contexts.get(scenario_type, "[No context provided]")}

================================================================
FACILITATOR REMINDERS
================================================================
✓ Notify NOC/SOC before starting
✓ All injects are scheduled (NOT reactive to team actions)
✓ Mark any real incidents immediately; pause the drill
✓ Debrief planned for after exercise concludes
✓ Post-exercise report will compare expected vs. actual responses

================================================================
INJECT TIMELINE
================================================================
"""
    
    timeline = generate_inject_timeline(scenario_type, duration)
    for i, inject in enumerate(timeline, 1):
        output += f"""
Inject #{i} @ {inject['time_offset']} minutes
  Description: {inject['inject_description']}
  Expected Response: {inject['expected_response']}
  Difficulty: {inject['difficulty'].upper()}
"""
    
    output += f"""
================================================================
SCORING RUBRIC
================================================================
"""
    
    rubric = generate_scoring_rubric(scenario_type)
    total_weight = sum(r["weight"] for r in rubric)
    
    for criterion in rubric:
        output += f"""
{criterion['criterion']} (Weight: {criterion['weight']}/{total_weight})
  Description: {criterion['description']}
  Excellent: {criterion['excellent']}
  Poor: {criterion['poor']}
"""
    
    output += f"""
================================================================
AFTER ACTION REVIEW (AAR) TEMPLATE
================================================================

1. TIMELINE REVIEW
   What actually happened vs. what was planned?
   [Facilitator: walk through inject timeline, note actual vs. expected decisions]

2. DECISION ANALYSIS
   What were the critical decision points?
   Did the team make the right calls? Why/why not?
   [Discuss at least 3-5 key decisions]

3. GAP ANALYSIS
   What procedures were unclear or missing?
   What caused hesitation or delays?
   [List 3-5 gaps to address]

4. ACTION ITEMS
   What will we improve?
   [Assign owners, due dates]

5. LEARNING OUTCOMES
   What did the team learn?
   [Capture key insights]

================================================================
END OF SCENARIO BRIEF
"""
    
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Generate disaster recovery game day scenarios"
    )
    parser.add_argument(
        "--scenario-type",
        required=True,
        choices=["region-failure", "db-corruption", "dns-hijack", "cert-expiry", "dependency-outage", "data-breach"],
        help="Type of scenario to generate"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Exercise duration in minutes (default: 60)"
    )
    parser.add_argument(
        "--team-size",
        type=int,
        default=5,
        help="Number of participants (default: 5)"
    )
    
    args = parser.parse_args()

    # Validate inputs
    if args.duration <= 0:
        print("Error: --duration must be a positive integer (minutes).", file=sys.stderr)
        sys.exit(1)
    if args.team_size <= 0:
        print("Error: --team-size must be a positive integer.", file=sys.stderr)
        sys.exit(1)

    # Generate and print scenario brief
    brief = generate_scenario_brief(args.scenario_type, args.duration, args.team_size)
    print(brief)


if __name__ == "__main__":
    main()