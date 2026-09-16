# Relationship to the original experiment code

This repository is a reproducibility-instrumented revision of the original Set D–WN4 script. The scheduling model, six-segment encoding, decoder, evolutionary operators, uncertainty evaluation, and default population/generation parameters are retained. The selection mechanism was revised to match the formal AEEA described in the manuscript.

The following changes were necessary to answer the reproducibility review comment:

1. The API key was removed from source code and replaced by the `DEEPSEEK_API_KEY` environment variable.
2. The original system prompt, `You are a helpful assistant`, is preserved verbatim and stored as a text file.
3. `max_tokens=8192` is now explicit. The historical script omitted this argument and therefore depended on the provider-side default in effect at the time.
4. The JSON response is represented as an object with an `individuals` array so that it is consistent with JSON-object response mode. The six chromosome segments and feasibility checks are unchanged.
5. The unused `temperature=0.1` attribute from the former agent class was removed. It was never passed to the API. Temperature and top-p are now explicitly recorded as not sent/not applicable for thinking mode.
6. Algorithm and NumPy seeds are command-line parameters. The DeepSeek Chat Completions API does not provide an LLM seed parameter.
7. Provider-returned model names, backend fingerprints, token usage, prompts, final raw outputs, retries, validation results, latency, and date-specific cost estimates are recorded.
8. Product CSV filenames are sorted during loading to make product-type indexing independent of operating-system directory order.
9. Plotting is noninteractive by default so command-line and continuous-integration runs terminate normally.
10. Elite retention, prompt-context extraction, and parent selection now use nondomination rank and normalized crowding distance. Excess valid Agent candidates are trimmed by the same rule, whereas Agent shortfalls are filled with evolutionary offspring.

Because the historical script did not record the provider-returned model identifier, fingerprint, token use, or provider defaults, those facts cannot be reconstructed retrospectively. Results reported as produced by this revised package should therefore be regenerated with archived run logs. Historical results should not be assigned an exact model snapshot or temperature setting without original evidence.
