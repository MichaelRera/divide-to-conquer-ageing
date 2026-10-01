# Running the abstract coding in Perplexity

> **Note (2026-09-28):** the answers are stored in `perplexity/batch_NN_coded.txt` and `gemini/batch_NN_task_coded.txt` (not `returned/`). Import with `python3 ../perplexity_batches.py import "<model>"` and `python3 ../three_coders.py "<model>"`.

Perplexity codes. The analysis runs locally in the notebooks, so the Opus codes never reach Perplexity and blinding holds.

## 0. Settings in Perplexity (important)

- **Model: pick a non-Anthropic model** (GPT or Gemini, for example) and **not Claude**. A Claude model would bring back the correlated-error problem this check is meant to avoid. Pick one model and keep it for every batch.
- **Turn web search off** (Writing mode, or no sources), so the coding rests on the abstract alone.
- Write down the exact model name shown. You need it at step 3.

## 1. Code the batches

The files are in `batches/`: 15 files of 50 records (the last has 48). **Batches 01 and 02 contain the 75 records of the planned 10% subset.** If time is short, these two are enough for the κ.

For each batch:
1. Start a **new thread**, so earlier batches can't drift into later ones.
2. Paste the whole of `PROMPT.md` as the message and attach `batch_NN.txt`. If an attachment fails, paste the batch text below the prompt.
3. Copy the TSV code block from the reply into `returned/batch_NN.tsv`, with the same number as the batch. The backticks can stay; the importer strips them.
4. If the reply is cut short, say "continue from <last review_id>" and append the rest to the same file.

## 2. Import

```bash
python3 perplexity_batches.py import "<exact model name>"
```

The import writes the codes into `data/coding/coding_sheet.xlsx`, with `coder_id = "Perplexity: <model>"`. It refuses unknown or duplicated IDs and lists any record missing from a batch. Re-run it whenever you add batches; it rewrites from all the returned files.

## 3. Validate and analyse

```bash
cd notebooks
jupyter nbconvert --to notebook --execute --inplace 03_validate_coding.ipynb   # errors -> outputs/tables/coding_validation_errors.tsv
jupyter nbconvert --to notebook --execute --inplace 04_compare_distributions.ipynb
jupyter nbconvert --to notebook --execute --inplace 06_kappa.ipynb
```

If 03 lists errors (for example, `level` filled for a P record), send the affected records back to Perplexity with the error message, or correct obvious format slips by hand in `returned/*.tsv` and re-import. Log every manual correction.

Results go to `outputs/tables/`:
- `kappa_independent_vs_opus.tsv`: κ with bootstrap 95% CIs, for the 10% subset and for everything coded.
- `confusion_T_*.tsv`: confusion matrices.
- `distributions_independent_vs_opus.tsv` and `D_scale_observation_by_coder.tsv`.
- `disagreements_T.tsv`: records to adjudicate, with both coders' notes.

## What to report

Name it in the Methods as "an independent coding by <model> via Perplexity (web search disabled), blind to the original codes, using the same written codebook", and give κ for trajectory framing and for the Arm B screen. A human re-coding of the 75 records, if done, remains the stronger check.
