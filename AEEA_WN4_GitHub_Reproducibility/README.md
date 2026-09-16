# AEEA–DeepSeek reproducibility package: Set D–WN4

This repository contains the super-large Set D instance under workshop configuration WN4 and the complete AEEA implementation with auditable DeepSeek API logging.

## Reproducibility coverage

Every run records the following information requested during peer review:

- provider, requested model alias, model name returned by the API, backend fingerprint, and UTC access time;
- exact system prompt and every complete user prompt;
- thinking mode, temperature, top-p, maximum output length, response format, and LLM-seed availability;
- algorithm and NumPy random seeds;
- JSON Schema and the subsequent feasibility-check/repair procedure;
- logical calls per generation, API attempts including retries, candidates requested and candidates accepted;
- prompt, completion, reasoning, cache-hit, cache-miss, and total token counts when returned by the API;
- per-attempt latency and total latency;
- estimated API cost when `pricing.json` has been completed and verified;
- code/data SHA-256 hashes, package versions, instance data, raw final outputs, and parsing/validation results.

The final response text is preserved verbatim. Hidden reasoning text is not published; its token count is recorded when supplied by the API.

## Important model-parameter note

The original implementation requests `deepseek-reasoner`, a thinking/reasoning model. DeepSeek documents that `temperature` and `top_p` do not affect thinking mode. This package therefore does not send either parameter and records both as `null` with an explanation. The API does not expose a reproducible random-seed parameter for Chat Completions, so the LLM seed is also recorded as unavailable. The evolutionary algorithm and NumPy seeds remain explicit and controllable.

Model aliases can change at the provider side. For this reason, the package logs both the requested alias and the `model` and `system_fingerprint` returned by every response. Do not describe an exact historical backend version unless it is supported by the corresponding run log.

## Installation

Python 3.10 or later is recommended.

```bash
python -m venv .venv
```

Activate the environment, then install:

```bash
python -m pip install -r requirements.txt
```

Set the API key in the environment. Never place the real key in source code or commit it to GitHub.

PowerShell:

```powershell
$env:DEEPSEEK_API_KEY="your-key"
```

Bash:

```bash
export DEEPSEEK_API_KEY="your-key"
```

Optional API settings are listed in `.env.example`. That file is documentation only; the program reads environment variables directly.

## Pricing configuration

The API response reports tokens but not the historical price schedule. Before the final experimental runs, enter the rates applicable on the actual access date in `pricing.json`, enter the effective date, and set:

```json
"verified_for_experiment_access_date": true
```

Otherwise the run remains valid, but cost is deliberately reported as unavailable instead of being fabricated.

## Running the experiment

Full manuscript configuration:

```bash
python run_experiment.py --seed 4 --population-size 50 --generations 100 --crossover-rate 0.8 --mutation-rate 0.1 --llm-guided-ratio 0.3 --run-id setD_wn4_seed4
```

Short API integration check:

```bash
python run_experiment.py --seed 4 --population-size 6 --generations 2 --run-id smoke_test
```

When the LLM-guided ratio is positive, every evolutionary generation makes one logical Agent call and requests `round(population_size × llm_guided_ratio)` candidates. A failed parse or an empty feasible result triggers a retry, up to five API attempts. If the Agent returns more valid candidates than requested, the excess is removed using nondomination rank and normalized crowding distance. If it returns fewer, evolutionary offspring fill the remaining population positions.

For independent repetitions, use a different `--seed` and a unique `--run-id` for every run. Do not overwrite a previous run directory.

## Selection mechanism

The formal AEEA implementation uses lower nondomination rank followed by larger normalized crowding distance for elite retention, prompt-context extraction, and three-candidate parent tournaments. Original population position breaks any remaining tie. The three objective components are never summed for these decisions. The same rule trims excess valid Agent candidates and selects the final reported set.

## Output structure

Each run is stored under `artifacts/<run-id>/`:

```text
run_manifest.json
llm_calls.jsonl
validation_events.jsonl
population_composition.jsonl
run_summary.json
prompts/
raw_outputs/
result.pkl
pareto_trend.png
```

The JSON and text files can be committed as supplementary reproducibility records. Check them before publication because complete prompts contain the full experimental instance and elite chromosomes.

## Output format

The API is asked for a JSON object with one top-level field:

```json
{
  "individuals": [
    {
      "采购供应商选择": [],
      "产品内部的部装工序顺序": [],
      "部装工序顺序列表": [],
      "部装机器选择列表": [],
      "总装工序顺序列表": [],
      "总装机器选择列表": []
    }
  ]
}
```

The formal schema is available at `schemas/individuals.schema.json`. Instance-specific lengths, domains, precedence constraints, and machine compatibility are checked and, where implemented by the original method, repaired by `output_check2.py`. The system prompt is deliberately preserved verbatim from the original implementation; the domain-specific instructions are contained in the user prompt.

## Security

- `.env` is excluded by `.gitignore`.
- This package contains no API key.
- Revoke and replace any key that has previously appeared in source code, logs, screenshots, or chat records.

## Official API documentation

- Chat Completions: <https://api-docs.deepseek.com/api/create-chat-completion/>
- Thinking mode: <https://api-docs.deepseek.com/guides/thinking_mode/>
- JSON output: <https://api-docs.deepseek.com/guides/json_mode/>
- Pricing: <https://api-docs.deepseek.com/quick_start/pricing>
