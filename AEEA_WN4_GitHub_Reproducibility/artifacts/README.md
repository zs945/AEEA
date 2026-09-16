# Runtime artifacts

Each run creates a separate subdirectory containing:

- `run_manifest.json`: model/provider, access time, prompts, schema, algorithm parameters, environment and source hashes;
- `llm_calls.jsonl`: one record per API attempt, including retries, returned model, fingerprint, tokens, latency and estimated cost;
- `validation_events.jsonl`: parsing/feasibility outcome and accepted candidate count;
- `population_composition.jsonl`: requested, valid and retained Agent counts plus GA refill count for every generation;
- `prompts/*.txt`: the exact full user prompt for every API attempt;
- `raw_outputs/*.txt`: the exact final-answer text returned by the LLM;
- `run_summary.json`: calls, retries, token totals, latency and cost totals;
- `result.pkl` and `pareto_trend.png`: numerical optimization outputs.

Inspect the files for sensitive information before publishing them.
