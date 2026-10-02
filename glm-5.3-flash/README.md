# glm-5.3-flash preset

Files: `edit_spec.json` (per-layer strengths), `edit_spec.safetensors` (one unit direction `r`, 4096 float32), `SHA256SUMS`.

Check on CPU, then load:

    python3 ../verify.py .
    export EXL3_ABLIT_RUNTIME=$PWD/edit_spec.json     # the engine reads edit_spec.safetensors next to it
    # then start the Yamz engine as usual (same serve command, same model pack)

No command-line flag exists. The engine hook is switched on by that one environment variable and is off when it is unset. The log prints ` -- ablit runtime: spec <path> active` at load. If you do not see that line, the preset is not active.

    sha256  fe9989cbce800f941ea46eac5200687fb961c51af607b4df9506c59c8b8f4d97  edit_spec.json
    sha256  7ca504e1fa94612c33451856e0bd33c483dd981462af7d9741b098772610c608  edit_spec.safetensors

Setting: one direction, projected out of each attention block output in layers 24-44 (strength 2.14-2.21) and each MLP block output in layers 11-38 (strength 0.90-1.49). Other layers and the MTP layers are untouched. The direction comes from the difference of mean residuals between 400 harmful and 400 harmless prompts, with the harmless-mean component removed. Fitted on the 2.05 bpw EXL3 build, measured on the published 99.73 GB pack: refusals 0/100 with the preset, 81/100 without (100 harmful prompts). Numbers: see the top-level README. Greedy decoding is not recommended.
