# Fulfillment Hub

A simple fulfillment control tower for XYZ e-commerce operations.

## Problem
Warehouse teams often struggle with disjointed tools, leading to missed priority SLAs, unchecked inventory mismatches, and delayed courier pickups.

## Solution
Fulfillment Hub acts as a single pane of glass ("Control Tower") directing warehouse workers' attention only to what needs immediate action.

## Product Decisions
- **Control tower**: We focus on actionable metrics (needs attention) rather than vanity charts.
- **Priority/SLA visibility**: Urgent orders visually pop and are prioritized automatically based on SLAs.
- **Inventory availability**: Validates stock before picking to prevent dead-ends. Includes a backup transfer workflow.
- **Picking accuracy**: Highlights variants explicitly and requires confirmation.
- **Staging/pickup**: Dedicated view for packages waiting for courier.
- **Exceptions**: Simple tracking for operational issues.

## How to run
```bash
pip install -r requirements.txt
streamlit run app.py
```
