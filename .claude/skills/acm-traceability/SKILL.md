---
name: acm-traceability
description: Cross-layer traceability queries. Answer "which tests cover X?", "what implements Y?", "find untested paths".
allowed-tools: mcp__acm__acm_stats, mcp__acm__acm_search, mcp__acm__acm_query, mcp__acm__acm_trace, mcp__acm__acm_paths, mcp__acm__acm_query_router
argument-hint: "[traceability question]"
---

Answer the traceability question: $ARGUMENTS

## Step 1: Parse the question type

Determine which traceability pattern applies:
- **Requirement to test**: "Which tests verify requirement X?"
- **Feature to code**: "What code implements feature Y?"
- **Code to test**: "Is function Z tested?"
- **Gap analysis**: "Find untested code" or "Find unimplemented requirements"

## Step 2: Find the anchor node

Call `acm_search(pattern="<entity>")` to find the node the question is about.

## Step 3: Trace across layers

Call `acm_trace(node_id)` to see all cross-layer connections grouped by layer.

## Step 4: Follow specific paths

For targeted questions, call `acm_paths(source, target)` between specific nodes.

## Step 5: Use natural language (optional)

For complex questions, call `acm_query_router(query="<question>")` which uses multi-channel search (graph + text + vector).

## Step 6: Report findings

Present the traceability chain: requirement -> feature -> design -> code -> test. Highlight any gaps in the chain.
