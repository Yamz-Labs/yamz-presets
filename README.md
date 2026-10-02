<p align="center"><img src="https://raw.githubusercontent.com/Yamz-Labs/.github/main/profile/yamz-banner.png" alt="Yamz Labs" width="100%"></p>

# Yamz steering presets

Optional activation-steering presets for the Yamz engine (an ExLlamaV3 fork for AMD Strix Halo). A preset is a small file pair: one direction in the model's residual stream and a per-layer strength. The engine subtracts that direction while the model runs. It changes how often the model refuses. Nothing else.

What you get: on the published GLM-5.3-Flash pack, refusals fall from 81/100 to 0/100 (100 harmful prompts, same protocol). On the published MiMo pack they fall from 94/100 to 4/100. On GLM the hook costs under 1 % of decode (not measured on MiMo), one switch turns it off, and the files are small.

- The model weights are never modified. The Hugging Face packs are plain quantisations of the base models, under the base licences. The `-Uncensored` repositories on Hugging Face hold the same unmodified shards plus a copy of the preset next to them (`uncensor_spec.json`, `uncensor_direction.st`); the engine applies it at load and `EXL3_ABLIT_RUNTIME=off` (or `--no-uncensor`) switches it off.
- The hook is part of the public engine and is off by default. These presets are not part of the engine and not part of the weights.
- Presets here are MIT, like the code.

## Presets

| Model | Status | Folder |
|---|---|---|
| GLM-5.3-Flash | validated on the published pack (refusals 0/100, base 81/100; numbers below) | `glm-5.3-flash/` |
| MiMo-V2.6-Flash | partly validated on the published pack (refusals 4/100, base 94/100; KLD +5.5 %; no task deltas) | `mimo-v2.6-flash/` |

## Enable

1. Run the engine with the matching model pack.
2. Check the files: `python3 verify.py glm-5.3-flash` (CPU, standard library only; checks schema, direction and sha256).
3. Set `EXL3_ABLIT_RUNTIME=/path/to/glm-5.3-flash/edit_spec.json` before the normal serve command. An explicit path wins over a bundled `uncensor_spec.json` in the model folder; `EXL3_ABLIT_RUNTIME=off` or the serve flag `--no-uncensor` disables both.
4. Look for ` -- ablit runtime: spec ... active` in the log. No line, no steering.

Unset the variable and restart to turn it off (a bundled `uncensor_spec.json` in the model folder would still apply: use `off`). The model then runs exactly as published.

## Measured effect: glm-5.3-flash

Fitted on a smaller (2.05 bpw) EXL3 quantisation of the model, then measured on the published GLM pack (99.73 GB, bundled as `uncensor_spec.json`).

| Run | Result |
|---|---|
| base model, no hook (regex detector) | refuses 46/50 = 92 %; 4 misses are soft refusals |
| fit + held-out test, 2.05 bpw build | refusals 2/100 (base 92-96 %); KL 0.0206 on 200 prompts; XSTest over-refusal 5.5 % (base 13.5 %) |
| published pack, bundled spec loads from the public tree | hook active, 34 hooked blocks |
| published pack, 100 harmful prompts, 64 greedy tokens | refusals 0/100 with the preset; 81/100 without |

Cost at run time: decode -0.1 to -0.3 %, prefill within noise (microbenchmark). Quantisation does not bring refusals back: 29/100 on the 2.05 bpw build against 27/100 in bf16 for an earlier setting.

## Limits

- Small sample: 100 harmful prompts. Intervals are wide. On the published pack only refusals were measured: over-refusal (XSTest), task scores and the KL of the edit were not.
- Refusal is counted by a regex detector. Soft refusals and partial answers can slip through either way.
- Greedy decoding is not recommended with or without a preset; use the sampling on the model card (temperature 1.0, top-p 0.95).
- English prompts only. Prompt sets: AdvBench, HarmBench, JBB (harmful); XSTest-safe, Alpaca (harmless).
- The preset is a blunt, global edit. It lowers over-refusal and refusal together. It is not a safety evaluation and not a statement about what the model will or will not produce.
- Tested on gfx1151 with ROCm only, with the Yamz engine only. A preset fitted on one model does not transfer to another.
- A hash proves the file is the one we measured. It proves nothing about your pack. If your quantisation differs, measure again.

## Responsible use

You decide how to use a preset, and you answer for it under the laws that apply to you. The intended uses are research, evaluation and private deployment. Do not use it to produce content that is illegal where you live, to target people, or in a public service without your own filtering and moderation. The files come as is, without warranty (see LICENSE).

## Removal and contact

We remove a preset on request from the base-model authors or a rights holder, on a valid legal notice, or if we find it causes harm we did not measure. Open an issue in this repository to ask. Removed presets are listed in `REMOVED.md` with the date and the reason.
