# intro-to-mcps

A hands-on learning repository for understanding the Model Context Protocol (MCP) and building agentic systems from first principles.

This repository is a structured experimentation lab for:

- Creating MCP servers
- Connecting LLMs to structured tools
- Designing simple multi-role development swarms
- Understanding the tool invocation lifecycle
- Exploring persona-driven AI workflows

This is not a production framework.
It is a mechanics workshop.

---

## Why This Repository Exists

Most modern agent frameworks abstract away the important parts.

This project intentionally exposes:

- The reasoning loop
- Tool registration and invocation
- The separation between LLM and agent
- The orchestration logic
- The limits of autonomous behavior

If something works, you can trace exactly why it worked.

If something breaks, you can see where.

---

## Repository Structure

first-steps/
  Basic experiments and API exploration.
  Small scripts to understand core MCP and LLM interactions.

development-swarm/
  A simulated multi-role development workflow.

  develop.py
    Main orchestration loop.

  mcps/
    Tool definitions exposed via MCP:
      - dev_tools.py
      - file_tools.py
      - qa_tools.py
      - run_tools.py

  personas/
    Role definitions that shape LLM behavior:
      - developer.md
      - manager.md
      - tester.md

  dev-space/
    Working directory where generated code and tests are written.

utils.py
  Shared helpers used across the swarm.

requirements.txt
  Python dependencies.

---

## Learning Objectives

This repository explores answers to:

- What actually interacts with an MCP server?
- How does an LLM decide to call a tool?
- What is the difference between an LLM and an agent?
- How do multiple personas coordinate via a single orchestration loop?
- How can tools enforce structure and reliability?

---

## How the Development Swarm Works

1. A manager persona defines tasks.
2. A developer persona writes code.
3. A QA persona tests the implementation.
4. MCP tools perform file writes, test execution, and command runs.
5. The orchestrator coordinates the cycle until completion.

Every action flows through explicit tool calls.
There is no hidden automation layer.

---

## Core Concepts Practiced

- Tool registration through MCP
- Structured tool invocation
- Role-based prompting
- Local file manipulation through controlled interfaces
- Test-driven iteration via tool feedback
- Observing the reasoning loop in action

---

## What This Is Not

- A polished framework
- A drop-in agent solution
- A cloud-based automation platform

It is a learning scaffold.

---

## Next Step

For a cleaner, local-first, Ollama-driven evolution of these ideas,
see the mini-claw repository.