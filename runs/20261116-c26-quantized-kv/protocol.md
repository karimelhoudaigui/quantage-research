# C26 prospective quantized-KV resource pilot, 2026-11-16

Question: can the official Qwen3-8B-Q4_K_M complete one recorded second-repair call at context 6144 on the 8 GiB Apple M2 when both K and V caches are q8_0 and Flash Attention is explicitly enabled?

Prior failures kept unchanged: C24 (full GPU placement 99, KV f16) aborted with MetalInsufficientMemory at the first prompt ubatch and produced no proposition; C25 (30 GPU layers, KV f16) hit the 180 s request deadline without a complete response. Neither is a mathematical or QPU failure. Their raw records are not modified here.

This cycle starts from the SAME recorded C24 development state: public case 417127d82203, its typed current model state, its verifier feedback, and the same instructions. No initial or first-patch resampling is performed. That state is development data only, never a new heldout test.

## Prospective configuration (fixed before the call)

- runtime: llama.cpp b12359, acquired and hash-pinned by the C22 public acquisition
- model: official Qwen3-8B-Q4_K_M GGUF, hash-pinned
- context 6144, batch 128, ubatch 128
- GPU layers requested 99, device MTL0, CPU threads 4
- `--flash-attn on`
- `--cache-type-k q8_0`
- `--cache-type-v q8_0`
- one output cap 1024 tokens including at most 768 printable-ASCII diagnosis characters
- sampler: seed = first 8 hex of SHA256(case id) + 2, temperature 0.7, top-k 20, top-p 0.8, min-p 0, repeat penalty 1.0
- grammar: the frozen generic patch grammar (diagnosis + literal edits)

The three runtime options are documented in the official b12359 server README: `--flash-attn [on|off|auto]`, `--cache-type-k`, `--cache-type-v`. The local binary help is archived verbatim in native-help.json, which records that all three flags exist. Documented runtime behaviour: quantized V cache requires Flash Attention, and some backends additionally require the head dimension to be divisible by the cache block size. Those are compatibility conditions, not a guarantee that Metal will execute the model nor that the memory will fit in 8 GiB.

## Execution bound

Exactly one new guided call. One owned local server, no network beyond 127.0.0.1, `--offline`, process-group ownership by the outer bounded runner. Watchdogs: per-request 180 s, phase 420 s, outer group 480 s, TERM then KILL reaping. No retry, no fabricated response, no token imputation. If the server cannot become ready, or the request times out, the cycle is recorded blocked or partial with whatever was actually observed.

## Records

The driver writes raw.jsonl, generation.json, patch-schema.json, patch-grammar.gbnf, native-flags.json, server.stdout.txt, server.stderr.txt and the HTTP request/response pair. Loader evidence is parsed from server.stderr.txt to report offloaded layers, a positive Metal model buffer, Flash Attention enablement and the requested cache types. `device` stays "unverified" when loader evidence is absent; requesting Metal is not observing Metal.

## Analysis after the call

If a complete response exists, replay the literal recorded states (actual 4B initial + actual 8B first patch + new patch), enumerate the original n=4 cube, execute the two final solvers, and compare selected candidates. Attribute costs to reused and new calls; keep C24's failed attempt and C22's unknown separately. If no complete response exists, report the failure and the observed resource evidence only.

## Non-claims

No fit or speed guarantee. No heldout generalization, no H23 result. No isolated causal effect of KV precision: Flash Attention was already auto-enabled in C24 and several settings change together. No QPU, no external spending, no push, no publication, no external message. This is posthoc development, not a natural-language semantic certificate.
