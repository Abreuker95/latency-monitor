Serverless AIOps Network Observability Platform

Introduction

This product represents a completely decoupled, serverless Network Operations Center (NOC) Dashboard. The solution connects legacy backend network telemetry with AIOps by using cloud-based runners to perform latency tests, processing telemetry by a Large Language Model (LLM), and sending state updates to both headless frontend and asynchronous ChatOps channels.

The whole stack operates independently without any database and server in the background.

Core Architecture & Components

Stateless Telemetry Engine: Uses temporary GitHub Actions virtual environment with a proprietary Python TCP-socket script to ping all global endpoints (Google, DNS, regional servers).

LLM-Based Incident Triage: Directly integrates with Google Gemini 2.5 Flash REST API. The engine sends raw latencies and packet loss information to the LLM, which works as an automated Level 1 NOC Engineer, providing plain-text executive reports about network status.

ChatOps for Enterprises: Designed to work in a remote-asynchronous manner. In case of packet loss or network degradation, the Python engine generates a JSON webhook that is sent directly to the specified Discord incident management channel.

Frontend Decoupling: The data is serialized into static JSON files (latency_data.json, alerts.json, ai_report.json) and deployed to the repository. A headless WordPress frontend retrieves this data from JSON files and renders real-time graphs and logs in a terminal-style way by using timestamp cache-busting.

Automated Log Management & Failsafe Schemas: Includes automatic log rotation and built-in schema-validation logic to manage rolling data migration without breaking down the pipeline.

Data Flow

CRON Trigger: GitHub Actions wakes up hourly (or on manual dispatch).

Execution: Python environment is spun up and dependencies (requests) are installed.

Polling: Dashboard_test.py pings targets and updates historical CSV telemetry.

Evaluation: State is evaluated. If degradation is detected, a webhook is fired to Discord and alerts.json is updated to trigger a red frontend UI state.

AIOps: analyze_logs.py feeds the 24-hour CSV telemetry to Google Gemini.

Archival: The AI's response is appended to a self-rotating log array.

Deployment: The cloud runner commits the new JSON files back to the repository.

Client-Side Rendering: The static frontend dynamically fetches the raw JSON data and populates the UI via vanilla JavaScript and Chart.js.

Engineering Solutions Implemented

Going Around Web Application Firewall & Cloud: Early efforts at directing traffic from the APIs were thwarted by Web Application Firewall implementations by vendors specifically targeting CI/CD runners. Managed to implement pivot for the LLM framework around an authorized REST API with versioning in place.

Processing Transient State: Given that cloud runners destroy their state each time they run, the solution implemented was one which involved log rotation and deduplication based on file I/O and strict type checking (dictionary to list).

CDN Cache Invalidation: Implemented JavaScript cache-busting (?t=${timestamp}) on the frontend to force edge servers to deliver the newest JSON payloads immediately after a CI/CD run, preventing UI staleness.

Future Roadmap

Use matrix-strategy workflows to perform latency testing between multiple regions (US vs. EU vs. APAC).

Move from flat CSV files to a serverless time series database (like Supabase).

Package the Python engine as a small Docker container for internal Proxmox and AWS deployment.
