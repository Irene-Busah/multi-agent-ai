# Multi-Agent AI
A hands-on journey into designing, building, orchestrating, and deploying production-grade multi-agent AI systems using Python, Microsoft Foundry, and Azure Agent Framework.


## Course Case Study - Larkspur Mutual
An insurer with one agent in production and four problems you will recognize. Every section opens
with a Larkspur chapter and closes with the Azure design.

- One agent in production. Claims intake - answers policyholders, records a loss.

Additional Problems
1. Complex claims desk - A factory fire takes days of assessment, in several sessions.
2. Partners and brokers - Partner agents to connect, broker data to keep apart.
3. Money and regulators - Large payouts, exceptions, and 'why was this decided?'


## Course Map
1. Path 1 - Architect production-grade multi-agent AI solutions in Azure.
    - Stateful agentic loops
    - Orchestration patterns
    - Task decomposition and collaboration
    - Agent communication with A2A

2. Build production-grade multi-agent capabilities with Microsoft Foundry
    - Advance prompting
    - Tool ecosystems with MCP
    - Advanced RAG with Azure AI Search 
    - Memory architectures with Cosmos DB

3. Deploy and govern enterprise agentic AI solutions on Azure
    - CI/CD with GitHub Actions
    - Zero-trust security
    - Responsible AI governance with content safety
    - Agent lifecycle governance

4. Monitor, evaluate, and operate multi-agent AI solutions in Azure
    - Observability with OpenTelemetry
    - Evaluation frameworks
    - Performance & Cost
    - Human-in-the-loop with Power Automate and Teams
    - Production incidents


## What is an Agent?
Model        + Instructions                + Tools    = Agent (A name and a version, stored in the project: claims-intake v3)
gpt-5.4        who it is, what it must do.   MCP, knowledge, functions


The four step loop - every module builds on it
1. YOU - Create a response on the conversation(Fire at Vantor's Hamburgh plant).
2. Agent - Answers with a function call item (get_policy('VM-2291'))
3. Your Code - Runs it, returns a function call output (the policy document as text)
4. Agent - More calls or a message item (Covered, section 4.2, reserve $180K)
5. Repeat until a message or a budget says stop

- Agent: a name and a version; created with the project client.
- Conversation: The history, kept by the service as items.
- Response: One step of work; sync, streaming or background
- Item: message, function call, function call output, reasoning


