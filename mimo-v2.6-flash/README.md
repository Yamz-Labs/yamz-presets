# mimo-v2.6-flash preset

Status: partly validated. Refusal rate, harmless KL and KLD against FP8 are measured on the published pack. Task deltas and over-refusal (XSTest) were not run.

Files: `edit_spec.json` (per-layer strengths), `edit_spec.safetensors` (one unit direction `r`, 4096 float32), `SHA256SUMS`.

    python3 ../verify.py .
    export EXL3_ABLIT_RUNTIME=$PWD/edit_spec.json     # the engine reads edit_spec.safetensors next to it
    # then start the Yamz engine as usual (same serve command, same model pack)

An explicit path wins over a bundled `uncensor_spec.json` in the model folder; `EXL3_ABLIT_RUNTIME=off` or the serve flag `--no-uncensor` disables both. The hook is on when the variable is set. The log prints ` -- ablit runtime: spec <path> active` at load.

Setting: one direction, projected out of each attention block output in layers 11-47 (strength 1.62-1.76) and each MLP/MoE block output in layers 0-46 (strength 0.31-0.80). MTP layers are untouched. The direction was fitted on the pack without the tuning overlay, from 48 per-layer residual differences. The strengths come from an Optuna search over the per-layer strengths.

Measured on the published pack (Ryzen AI Max+ 395):

| Check | Hook off | Hook on |
|---|---|---|
| Refusals, 100 held-out harmful prompts, greedy, 64 tokens | 94/100 | 4/100 |
| KLD vs FP8 reference, 125 held-out rows | 0.0713 | 0.0752 (+5.5 %, CI +4.5 to +6.6) |
| Top-1 agreement with FP8, same rows | 91.99 % | 91.72 % (-0.27 pt) |
| Search harmless KL (100 safe prompts, vs unhooked) | - | 0.102 |

A stronger variant gave 0/100 refusals but did not pass our release gate, so it was not published.

Use the model-card sampling (temperature 1.0, top-p 0.95); greedy decoding is not recommended.

Not measured: MMLU-Pro, GSM8K, IFEval score deltas, XSTest over-refusal. The direction is model-specific; do not reuse the GLM file.
