# Reviewer reproducibility checklist

| Requested item | Recorded location |
|---|---|
| Exact provider | `run_manifest.json` and every `llm_calls.jsonl` record |
| Requested model/version | `run_manifest.json` |
| Model returned by provider | `llm_calls.jsonl`; unique values summarized in `run_summary.json` |
| Backend fingerprint | `llm_calls.jsonl` and `run_summary.json` |
| Access date/time | UTC timestamps in manifest, calls, and summary |
| System prompt | `prompts/system_prompt.txt` and manifest |
| Complete user prompts | `artifacts/<run-id>/prompts/*.txt` |
| Temperature/top-p | Manifest and call request records (`null`, not applicable in thinking mode) |
| Maximum output length | Manifest and call request records |
| Random seeds | Manifest (algorithm and NumPy); LLM seed recorded as unavailable |
| JSON schema | `schemas/individuals.schema.json` and manifest |
| Calls per generation | Call records and per-generation summary |
| Candidates per call | Call and validation records |
| Selection mechanism | `aeea_selection.py` and `selection_rule` fields in `run_manifest.json` |
| Agent overfill/shortfall handling | `population_composition.jsonl`, `run_experiment.py`, README, and `agent_candidate_count_handling` in `run_manifest.json` |
| Retries | One call record per API attempt and retry totals in summary |
| Parsing procedure | Source code, manifest, and parse-status fields |
| Context size | Elite-context count, prompt characters, and API prompt-token count per call |
| Token consumption | Call records and run summary |
| Latency | Call records and run summary |
| API cost | Call and run summaries after date-specific `pricing.json` verification |
| Code and instances | Repository source and CSV files, with hashes in manifest |
| Raw LLM outputs | `artifacts/<run-id>/raw_outputs/*.txt` |
