The Hermes Agent framework includes a robust integration with the **Atropos** RL training library, enabling the collection of multi-turn trajectories and the training of models on agentic tasks. This integration provides a bridge between the high-level agent loop and RL training pipelines, supporting both standard OpenAI-compatible providers (Phase 1) and raw token-level training with custom tool call parsers (Phase 2).

## Overview of Atropos Integration

The integration is centered around `HermesAgentBaseEnv`, which abstracts the complexities of tool resolution, sandbox management, and conversation orchestration.

### Key Components
*   **`HermesAgentLoop`**: A reusable multi-turn engine that executes the tool-calling loop using standard OpenAI-spec tool calling. It handles tool dispatching via `handle_function_call` from `model_tools.py` [environments/agent_loop.py:119-131]().
*   **`HermesAgentBaseEnv`**: The core abstraction for Atropos environments. It manages the transition between Phase 1 (API-based) and Phase 2 (Local ManagedServer) training [environments/hermes_base_env.py:2-16]().
*   **`ToolContext`**: A per-rollout handle providing reward functions with unrestricted access to the same sandbox session used by the agent [environments/tool_context.py:67-74]().
*   **`resize_tool_pool`**: A utility to manage the global thread pool for tool execution, preventing deadlocks during high-concurrency RL rollouts [environments/agent_loop.py:36-47]().
*   **`rl_training_tool.py`**: A specialized toolset for managing the training lifecycle, including environment discovery, configuration editing, and WandB monitoring [tools/rl_training_tool.py:8-12]().

### Atropos RL Training Loop Architecture

```mermaid
graph TD
    subgraph "Atropos_Core"
        [Atropos_Trainer] --> [HermesAgentBaseEnv]
    end

    subgraph "Hermes_Environment_Core"
        [HermesAgentBaseEnv] --> [HermesAgentLoop]
        [HermesAgentBaseEnv] --> [ToolContext]
        [HermesAgentLoop] --> [handle_function_call]
    end

    subgraph "Tool_Execution_Space"
        [handle_function_call] --> [TerminalTool]
        [handle_function_call] --> [FileTools]
        [handle_function_call] --> [BrowserTool]
    end

    subgraph "Execution_Backends"
        [TerminalTool] --> [ModalBackend]
        [TerminalTool] --> [DockerBackend]
        [TerminalTool] --> [LocalBackend]
    end

    [ToolContext] -- "Verification_Calls" --> [handle_function_call]
    [HermesAgentBaseEnv] -- "compute_reward" --> [ToolContext]
```
Sources: [environments/hermes_base_env.py:2-16](), [environments/agent_loop.py:119-131](), [environments/tool_context.py:67-74](), [environments/agent_loop.py:23-25]()

---

## HermesAgentBaseEnv

`HermesAgentBaseEnv` provides the plumbing shared by all Hermes-specific RL environments. It supports two distinct phases of training:
1.  **Phase 1**: Uses an OpenAI-compatible server (VLLM, SGLang, OpenRouter). The server handles tool call parsing and reasoning extraction natively [environments/agent_loop.py:4-6]().
2.  **Phase 2**: Uses a `ManagedServer` (VLLM) where the client-side `ToolCallParser` extracts structured data from raw model tokens [environments/agent_loop.py:7-12]().

### Configuration and Toolsets
The environment is configured via `HermesAgentEnvConfig`, which includes:
*   **Toolset Distribution**: Allows sampling toolsets per rollout via `distribution` (from `toolset_distributions.py`) or explicit `enabled_toolsets` [environments/hermes_base_env.py:87-102]().
*   **Terminal Backend**: Selects the execution environment (e.g., `modal`, `docker`, `local`) [environments/hermes_base_env.py:120-124]().
*   **Tool Call Parser**: Specifies the parser used for Phase 2 training (e.g., `hermes`, `deepseek_v3`) [environments/hermes_base_env.py:161-167]().
*   **Thread Pool Management**: Resizes the global tool executor via `resize_tool_pool` to prevent thread starvation during parallel evaluations [environments/agent_loop.py:36-47]().

Sources: [environments/hermes_base_env.py:78-183](), [environments/agent_loop.py:36-47]()

---

## Tool Call Parsers (Phase 2)

For Phase 2 training, where models generate raw text instead of structured API responses, the framework employs specialized parsers to extract `ChatCompletionMessageToolCall` objects.

| Parser Name | Format Description | Source |
| :--- | :--- | :--- |
| `hermes` | XML-like tags: `<tool_call>{...}</tool_call>` | [environments/hermes_base_env.py:162]() |
| `deepseek_v3` | Unicode delimiters: `<｜tool▁calls▁begin｜>` ... `<｜tool▁sep｜>` | [environments/hermes_base_env.py:165]() |
| `mistral` | Mistral-specific tool call tokens | [environments/hermes_base_env.py:165]() |
| `llama3_json` | Llama3-specific JSON tool call format | [environments/hermes_base_env.py:165]() |
| `qwen` | Qwen-specific tool call format | [environments/hermes_base_env.py:165]() |

### Reasoning Extraction
The `HermesAgentLoop` includes logic to extract reasoning content from multiple provider formats, including `reasoning_content`, `reasoning`, and OpenRouter style `reasoning_details` [environments/agent_loop.py:81-116]().

Sources: [environments/agent_loop.py:81-116](), [environments/hermes_base_env.py:160-167]()

---

## ToolContext and Reward Functions

The `ToolContext` class provides reward and verification functions with direct access to the same session used by the agent during its rollout. This allows for "agentic verification," where the verifier can run commands, read files, or browse the web to determine if the task was completed successfully.

### Key Methods
*   **`terminal(command, timeout)`**: Runs a command in the rollout's terminal session. It uses a thread helper to avoid deadlocks in backends that use `asyncio.run()` internally [environments/tool_context.py:82-107]().
*   **`read_file(path)`**: Reads a file from the sandbox filesystem [environments/tool_context.py:112-129]().
*   **`write_file(path, content)`**: Writes text content to a file in the sandbox using a shell heredoc [environments/tool_context.py:131-151]().
*   **`upload_file(local_path, remote_path)`**: Uploads binary-safe files to the sandbox using base64 encoding and chunked transfers for large files [environments/tool_context.py:152-205]().

### Threading and Async Safety
Because some execution backends (like Modal or Docker) use `asyncio.run()` internally, `ToolContext` executes tool calls in a separate thread pool (`_tool_executor`) to prevent deadlocks within the Atropos event loop [environments/tool_context.py:44-64]().

Sources: [environments/tool_context.py:1-205](), [environments/agent_loop.py:27-33]()

---

## Context Management and Tool Result Budgeting

To prevent context window overflow during RL training, the framework implements a three-layer tool result persistence system defined in `tools/tool_result_storage.py`.

| Layer | Component | Logic | Source |
| :--- | :--- | :--- | :--- |
| 1. Per-tool Cap | Tool Logic | Tool-specific truncation (e.g., `search_files`) | [tools/tool_result_storage.py:5-8]() |
| 2. Per-result | `maybe_persist_tool_result` | If result > `threshold`, write to sandbox and provide preview | [tools/tool_result_storage.py:122-146]() |
| 3. Per-turn | `enforce_turn_budget` | Spills largest results to disk if turn aggregate > `turn_budget_chars` | [tools/tool_result_storage.py:181-185]() |

### Implementation Detail: Sandbox Persistence
When a tool result is persisted, it is written to the sandbox via `env.execute()` [tools/tool_result_storage.py:78-90](). The framework generates a unique `HERMES_PERSIST_EOF` marker to avoid collisions with the content [tools/tool_result_storage.py:71-75](). The `_write_to_sandbox` function routes data through `stdin` to bypass Linux `MAX_ARG_STRLEN` limits [tools/tool_result_storage.py:78-94]().

Sources: [tools/tool_result_storage.py:1-185](), [environments/agent_loop.py:25](), [tests/tools/test_tool_result_storage.py:127-154]()

---

## RL Training Lifecycle Management

The `tools/rl_training_tool.py` module provides the agent with the ability to manage the full RL lifecycle.

### RL Lifecycle Tool Integration

```mermaid
graph LR
    [AIAgent] -- "rl_list_environments" --> [AST_Scanner]
    [AST_Scanner] -- "finds" --> [EnvironmentInfo]
    [AIAgent] -- "rl_start_training" --> [RunState]
    [RunState] -- "manages" --> [Trainer_Process]
    [RunState] -- "manages" --> [API_Process]
    [RunState] -- "manages" --> [Env_Process]
    [AIAgent] -- "rl_check_status" --> [WandB_Metrics]
```

### Key Lifecycle Tools
*   **`rl_list_environments`**: Uses AST scanning to find all `BaseEnv` subclasses in the `environments/` directory [tools/rl_training_tool.py:158-205]().
*   **`rl_edit_config`**: Allows tuning hyperparameters while preventing modification of `LOCKED_FIELDS` (infrastructure settings like `rollout_server_url` or `tokenizer_name`) [tools/rl_training_tool.py:72-108]().
*   **`rl_start_training`**: Orchestrates the startup of the API server, trainer, and environment rollout workers via `subprocess.Popen` [tools/rl_training_tool.py:348-420]().
*   **`rl_check_status`**: Monitors the status of the spawned processes and fetches WandB metrics, with a rate limit of 30 minutes to prevent excessive polling [tools/rl_training_tool.py:422-489]().
*   **`rl_test_inference`**: Allows testing an environment with inference steps using OpenRouter to validate setup before committing to full training [tools/rl_training_tool.py:540-600]().

Sources: [tools/rl_training_tool.py:1-600](), [rl_cli.py:113-170](), [website/docs/user-guide/features/rl-training.md:123-126]()

---

## Benchmark Environments

The framework includes several pre-integrated benchmark environments.

### TerminalBench 2.0 (`TerminalBench2Env`)
Evaluates agents on challenging terminal tasks using Docker images and test suites.
*   **Sandbox**: Uses Modal for per-task cloud-isolated sandboxes [environments/benchmarks/terminalbench_2/terminalbench2_env.py:28]().
*   **Reward**: Binary (1.0 for pass, 0.0 for fail) based on `test.sh` results [environments/benchmarks/terminalbench_2/terminalbench2_env.py:29]().
*   **Concurrency**: Uses `max_concurrent_tasks` to limit Modal sandbox creations [environments/benchmarks/terminalbench_2/terminalbench2_env.py:122-128]().

### TBLite (`TBLiteEvalEnv`)
A lightweight version of TerminalBench focused on faster iteration.
*   **Dataset**: Uses `NousResearch/openthoughts-tblite` [environments/benchmarks/tblite/local.yaml:16-34]().
*   **Reward**: Test Pass/Fail verification.

### YC-Bench
A long-horizon benchmark where the agent acts as a startup CEO.
*   **Interface**: Agent interacts via a CLI simulation.
*   **Scoring**: Survival duration plus normalized final funds.

### Benchmark Summary Table

| Environment | Primary Tools | Dataset | Reward Signal | Source |
| :--- | :--- | :--- | :--- | :--- |
| `TerminalBench2` | Terminal, File | `NousResearch/terminal-bench-2` | Binary Test Pass/Fail | [environments/benchmarks/terminalbench_2/terminalbench2_env.py:1-137]() |
| `TBLite` | Terminal, File | `NousResearch/openthoughts-tblite` | Test Pass/Fail | [environments/benchmarks/tblite/local.yaml:16-34]() |
| `YCBench` | Terminal | CLI Simulation | Survival + Funds | [website/docs/user-guide/features/rl-training.md:17-18]() |

Sources: [environments/benchmarks/terminalbench_2/terminalbench2_env.py:1-137](), [environments/hermes_base_env.py:1-25](), [tools/rl_training_tool.py:158-205]()