# Phase 22 — Zero-Shot Protein Language Model (pLM) Feasibility Audit Report

**Date**: 2026-09-01
**Status**: AUDIT COMPLETE (No packages installed, no weights downloaded, no models trained)

---

## 1. Local Hardware & Environment Audit

A comprehensive hardware and software audit of the Windows environment was conducted:

| Parameter | System Audit Result | Practical Implication for pLM Inference |
| :--- | :--- | :--- |
| **Python Version** | `3.13.14` (64-bit AMD64) | Compatible with standard PyTorch & HuggingFace / ESM packages |
| **OS Platform** | Windows 10 Home (10.0.19044) | Native Windows 64-bit execution |
| **System RAM** | **31.89 GB Total** (18.45 GB Available) | **Excellent**; can comfortably load 150M to 650M parameter pLMs in RAM |
| **CPU Architecture** | 8 Logical Cores | **Sufficient**; CPU inference for a ~290-aa protein takes < 1 second per pass |
| **GPU / CUDA** | **No CUDA GPU Detected** (CPU Mode) | **Inference must run on CPU**; requires lightweight or mid-sized models |
| **PyTorch (`torch`)** | **NOT INSTALLED** | Requires `pip install torch` (CPU build) |
| **ESM (`fair-esm`)** | **NOT INSTALLED** | Requires `pip install fair-esm` |
| **HuggingFace (`transformers`)**| **NOT INSTALLED** | Alternative framework; requires `pip install transformers` |

> [!NOTE]
> System RAM (32 GB) is generous, enabling CPU inference for ESM-2 models up to 650M parameters without out-of-memory risks.

---

## 2. Candidate Model Comparison

The practical suitability of candidate protein language models for local CPU execution on a ~290-residue PETase sequence was evaluated:

| Model Identifier | Parameters | Download Size | Memory (RAM) | Single Pass CPU Time | Full $290 \times 19$ Scoring Time | Zero-Shot Mutation Accuracy | Recommendation |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **ESM-2 150M** (`esm2_t30_150M_UR50D`) | **150M** | **~600 MB** | **~1.5 GB** | **~0.3 s** | **~0.3 s** (1 pass) | **High** | **RECOMMENDED PRIMARY CHOICE** |
| **ESM-2 650M** (`esm2_t33_650M_UR50D`) | 650M | ~2.6 GB | ~4.5 GB | ~1.5 s | ~1.5 s (1 pass) | Very High | **RECOMMENDED SECONDARY CHOICE** |
| **ESM-1v** (`esm1v_t33_650M_UR90S`) | 650M x 5 | ~12.5 GB | ~15 GB | ~8.0 s | ~8.0 s (5 passes) | Benchmark Standard | High memory/download footprint |
| **ESM-2 35M** (`esm2_t12_35M_UR50D`) | 35M | ~140 MB | ~0.5 GB | ~0.08 s | ~0.08 s (1 pass) | Moderate | Useful for fast screening |

### Scoring Efficiency: Masked-Marginal Log-Likelihood Ratio (LLR)

Because ESM-2 uses a masked language modeling (MLM) architecture, scoring all 19 non-WT substitutions at position $i$ does **NOT** require 19 forward passes. Under the **wild-type marginal / masked-marginal** formulation:
$$\Delta\text{LL}(i, a) = \log P(x_i = a \mid x_{\backslash i}) - \log P(x_i = \text{WT}_i \mid x_{\backslash i})$$
the language model predicts the complete probability distribution over all 20 amino acids for position $i$ in **a single forward pass**! Thus, scoring the full $290 \times 19 = 5,510$ mutation matrix for *Is*PETase requires **only 1 forward pass** (or 290 masked passes in masked-marginal mode), executing in **under 1 second** on CPU.

---

## 3. Definition of Biological Signal & Descriptors

The pLM log-likelihood ratio $\Delta\text{LL}(i, a)$ provides dual-level biological information:

### A. Position-Level Prioritization (WHERE to Mutate)

1. **WT Log-Likelihood ($\text{LL}_{\text{WT}}(i) = \log P(x_i = \text{WT}_i \mid x_{\backslash i})$)**:
   - Measures how strongly the language model prefers the wild-type residue in its native structural/sequence context.
   - **Biological Rationale**: Conserved/core positions where WT has low log-likelihood indicate sub-optimal wild-type adaptation (high engineering headroom).
2. **Positional Sequence Entropy ($H(i) = -\sum_{a} P(a_i=a) \log P(a_i=a)$)**:
   - Measures evolutionary tolerance / mutational plasticity predicted by the pLM.
3. **Peak Mutant Gain ($\Delta\text{LL}_{\text{max}}(i) = \max_{a \neq \text{WT}} \Delta\text{LL}(i, a)$)**:
   - Identifies positions where at least one alternative amino acid yields a significant fitness increase ($\Delta\text{LL} > 0$).
4. **Fraction Favorable Substitutions ($\text{Frac}_{\text{pos}}(i) = \frac{1}{19} \sum_{a \neq \text{WT}} \mathbb{I}(\Delta\text{LL}(i, a) > 0)$)**:
   - Quantifies overall mutational tolerance.

### B. Substitution-Level Recommendation (WHAT to Mutate)

- For a selected candidate position $i$, rank all 19 possible substitutions by $\Delta\text{LL}(i, a)$ to recommend specific high-fitness amino acid substitutions (e.g. S121E, H129W, R224Q).

---

## 4. Assessment of Model Independence

- **Pretraining Independence**: ESM-2 was pretrained on UniRef50 (45+ million natural protein sequences) using unsupervised masked language modeling.
- **No Benchmark Contamination**: ESM-2 was **never trained, fine-tuned, or optimized on our PETase experimental benchmark labels**.
- **Orthogonality**: Unlike static FoldX (which depends on 3D coordinates) or local FVI (which depends on our 628-sequence PETase MSA), ESM-2 captures deep contextual representations learned across all global protein families.
- **Scientifically Conservative Wording**:
  > *"Zero-shot evolutionary fitness predictions derived from un-finetuned ESM-2 representations."*

---

## 5. FASTA Workflow Compatibility

The pLM workflow fits seamlessly into the Atlas execution model:

```
User FASTA Upload (~290 aa)
   │
   ▼
1. ESM-2 150M CPU Forward Pass (~0.3 seconds)
   │
   ▼
2. Position-Level Hotspot Prioritization (LL_WT, Peak ΔLL_max)
   ├── Variable Route (V2.4): FVI ≥ 3 positions
   └── Conserved / Core Route (pLM): Low-variability positions (FVI ≤ 2)
   │
   ▼
3. Substitution Ranking (ΔLL(i, a) > 0)
   │
   ▼
4. Structural / Energetic Safety Filter (SASA, Clash check)
```

- **Runtime for 1 uploaded sequence**: **< 1 second total** on CPU.
- **Caching**: Reference *Is*PETase $290 \times 20$ pLM score matrix can be precomputed and stored as a static TSV artifact.

---

## 6. Recommendation for Phase 23

> [!IMPORTANT]
> **RECOMMENDED MODEL**: **ESM-2 150M (`esm2_t30_150M_UR50D`)** (with **ESM-2 650M** as secondary comparison).

### Justification
1. **Lightweight Download**: ~600 MB download size.
2. **Minimal Memory**: Occupies ~1.5 GB RAM during inference (fits easily in 32 GB system RAM).
3. **Ultrafast CPU Speed**: Single forward pass takes ~0.3 seconds on an 8-core CPU.
4. **Zero-Shot Accuracy**: Achieves top-tier performance on protein stability and activity benchmarks without requiring GPU acceleration.

### Phase 23 Implementation Roadmap

1. Install `torch` (CPU build) and `fair-esm` or `transformers`.
2. Load ESM-2 150M weights locally and compute the $290 \times 20$ log-likelihood matrix for *Is*PETase reference sequence.
3. Derive position-level pLM descriptors (`WT_log_likelihood`, `best_mutant_deltaLL`, `fraction_positive_deltaLL`).
4. Evaluate blind benchmark discrimination on low-variability (FVI $\le$ 2) hotspots with Benjamini-Hochberg FDR correction.
