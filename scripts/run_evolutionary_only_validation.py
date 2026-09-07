import os
import sys
import json
import math
import hashlib
import pathlib
import datetime
import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu, hypergeom

# Ensure path includes root
sys.path.insert(0, os.path.abspath('.'))

# Expected hashes
EXPECTED_POS_HASH = "962274848adfc82668b11c183eeef68ce784822731e2517cb3f0a8d6ebbaa286"
EXPECTED_MUT_HASH = "d7d0fc6c9696ad86ad96a49066d7bc3b9f508d9a9d47287e3e622a78bbe351a0"

def get_sha256(filepath):
    """Compute the SHA256 checksum of a file."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        chunk = f.read(8192)
        while chunk:
            h.update(chunk)
            chunk = f.read(8192)
    return h.hexdigest()

def run_validation():
    print("Starting Phase 3 Retrospective Blinded Validation...")
    
    # 0. Hash Verification
    pos_path = "results/validation/evolutionary_only/frozen_position_ranking.tsv"
    mut_path = "results/validation/evolutionary_only/frozen_mutation_ranking.tsv"
    
    if not os.path.exists(pos_path) or not os.path.exists(mut_path):
        raise FileNotFoundError("Frozen prediction files not found! Ensure Phase 2 completed successfully.")
        
    pos_hash = get_sha256(pos_path)
    mut_hash = get_sha256(mut_path)
    
    print(f"Position file hash: {pos_hash}")
    print(f"Mutation file hash: {mut_hash}")
    
    if pos_hash != EXPECTED_POS_HASH:
        raise ValueError(f"Hash mismatch for position ranking!\nExpected: {EXPECTED_POS_HASH}\nGot:      {pos_hash}")
    if mut_hash != EXPECTED_MUT_HASH:
        raise ValueError(f"Hash mismatch for mutation ranking!\nExpected: {EXPECTED_MUT_HASH}\nGot:      {mut_hash}")
        
    print("Prediction hashes successfully verified. Proceeding with benchmark analysis.")
    
    # Load frozen prediction rankings
    pos_df = pd.read_csv(pos_path, sep="\t")
    mut_df = pd.read_csv(mut_path, sep="\t")
    
    # Filter position ranking to get the 243 eligible positions, sorted by rank
    eligible_df = pos_df[pos_df["eligible"] == True].copy()
    eligible_df = eligible_df.sort_values(by=["rank"])
    eligible_df["eligible_rank"] = range(1, len(eligible_df) + 1)
    eligible_positions_map = {int(r["reference_position"]): int(r["eligible_rank"]) for idx, r in eligible_df.iterrows()}
    
    # Verify eligible count
    if len(eligible_df) != 243:
        raise ValueError(f"Expected 243 eligible positions, but found {len(eligible_df)}")
        
    # Load mapped benchmark
    benchmark_path = "validation/literature_benchmark/benchmark_expansion_v2/mapping/PETase_Validation_Dataset_v2_mapped.tsv"
    bench_df = pd.read_csv(benchmark_path, sep="\t")
    df = bench_df
    
    strict_df = df[(df["effect_class"].isin(["beneficial", "beneficial_with_tradeoff"])) & (df["benchmark_eligibility"] == "eligible_primary")].copy()
    expanded_df = df[(df["effect_class"].isin(["beneficial", "beneficial_with_tradeoff"])) & (df["benchmark_eligibility"].isin(["eligible_primary", "eligible_contextual"]))].copy()
    
    # 1. Audit and Mapping status for every record in the dataset (191 rows)
    # Audited fields: study, scaffold, original mutation, mapped reference position, mapped WT residue, phenotype classification, individual_validation status, evaluable YES/NO, exclusion reason if not evaluable.
    # Note: record_type contains single_mutation, single_mutation_on_specified_background, single_mutation_on_engineered_background, or single_alternate_ancestral_reconstruction.
    # All are individual mutations, but we flag if they are background-dependent (e.g. contextual).
    
    records_audit = []
    for idx, row in bench_df.iterrows():
        candidate_id = row["candidate_id"]
        study = row["study"]
        scaffold = row["scaffold"]
        mutation = row["mutation"]
        pos_val = row["atlas_position"]
        wt_res = row["atlas_wt_residue"] if pd.notna(row["atlas_wt_residue"]) else row["wt_residue"]
        effect = row["effect_class"]
        rec_type = row["record_type"]
        eligibility = row["benchmark_eligibility"]
        
        pos_int = int(pos_val) if pd.notna(pos_val) else None
        
        # A record is beneficial if it has beneficial effect_class
        is_beneficial = effect in ["beneficial", "beneficial_with_tradeoff"]
        
        # Eligibility rule checks
        evaluable = "NO"
        excl_reason = "Not a beneficial mutation"
        
        if is_beneficial:
            if eligibility in ["eligible_primary", "eligible_contextual"]:
                if pos_int in eligible_positions_map:
                    evaluable = "YES"
                    excl_reason = "None"
                else:
                    evaluable = "NO"
                    # Determine why it is not in the eligible universe
                    if pd.isna(pos_val):
                        excl_reason = "Position could not be mapped to reference coordinates"
                    elif pos_int in [160, 206, 237]:
                        excl_reason = "Position is protected catalytic triad (S160, D206, H237)"
                    else:
                        excl_reason = "Position has Family Variability Index FVI=0"
            else:
                evaluable = "NO"
                if eligibility == "corroborating_duplicate":
                    excl_reason = "Corroborating duplicate record excluded to prevent pseudoreplication"
                else:
                    excl_reason = row["exclusion_reason"] if pd.notna(row["exclusion_reason"]) else "Excluded by benchmark mapping rules"
        
        individual_validation = "YES" # All v2 records are individual substitutions
        
        records_audit.append({
            "candidate_id": candidate_id,
            "publication_identifier": study,
            "scaffold": scaffold,
            "original_mutation": mutation,
            "mapped_reference_position": pos_val if pd.notna(pos_val) else "Unmapped",
            "mapped_wt_residue": wt_res if pd.notna(wt_res) else "Unknown",
            "phenotype_classification": effect,
            "individual_validation_status": individual_validation,
            "evaluable": evaluable,
            "exclusion_reason": excl_reason,
            "benchmark_eligibility": eligibility
        })
        
    audit_df = pd.DataFrame(records_audit)
    
    # Split into Strict (primary) and Expanded (includes contextual backgrounds)
    # Strict benchmark includes only eligible_primary records
    strict_audit = audit_df[audit_df["benchmark_eligibility"] == "eligible_primary"].copy()
    expanded_audit = audit_df[audit_df["benchmark_eligibility"].isin(["eligible_primary", "eligible_contextual"])].copy()
    
    # Save benchmark definition files
    output_dir = pathlib.Path("results/validation/evolutionary_only")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    strict_audit.to_csv(output_dir / "benchmark_strict.tsv", sep="\t", index=False)
    expanded_audit.to_csv(output_dir / "benchmark_expanded.tsv", sep="\t", index=False)
    
    # Identify unique evaluable beneficial positions for both Strict and Expanded
    # Deduplicate positions: position counts once
    strict_eval_df = strict_audit[
        (strict_audit["phenotype_classification"].isin(["beneficial", "beneficial_with_tradeoff"])) & 
        (strict_audit["evaluable"] == "YES")
    ]
    strict_eval_positions = sorted(list(set(strict_eval_df["mapped_reference_position"].astype(int))))
    
    expanded_eval_df = expanded_audit[
        (expanded_audit["phenotype_classification"].isin(["beneficial", "beneficial_with_tradeoff"])) & 
        (expanded_audit["evaluable"] == "YES")
    ]
    expanded_eval_positions = sorted(list(set(expanded_eval_df["mapped_reference_position"].astype(int))))
    
    strict_beneficials = strict_audit[strict_audit["phenotype_classification"].isin(["beneficial", "beneficial_with_tradeoff"])]
    strict_unique_pos = set(int(pos) for pos in strict_beneficials["mapped_reference_position"] if pos != "Unmapped")
    
    expanded_beneficials = expanded_audit[expanded_audit["phenotype_classification"].isin(["beneficial", "beneficial_with_tradeoff"])]
    expanded_unique_pos = set(int(pos) for pos in expanded_beneficials["mapped_reference_position"] if pos != "Unmapped")
    
    # Verify and write position recovery strict
    strict_recovery_rows = []
    for pos in strict_eval_positions:
        rk = eligible_positions_map[pos]
        score = eligible_df[eligible_df["reference_position"] == pos]["evolutionary_score"].values[0]
        recovered_10pct = "YES" if rk <= 24 else "NO"
        strict_recovery_rows.append({
            "reference_position": pos,
            "eligible_rank": rk,
            "evolutionary_score": score,
            "recovered_top_10pct": recovered_10pct
        })
    strict_rec_df = pd.DataFrame(strict_recovery_rows)
    strict_rec_df.to_csv(output_dir / "position_recovery_strict.tsv", sep="\t", index=False)
    
    # 2. Statistical Analysis
    # Seed and simulations count
    SEED = 42
    N_SIM = 1000000
    rng = np.random.RandomState(SEED)
    
    # Run null model simulation for Strict Benchmark
    # Top 10% cutoff is 24 (math.floor(0.10 * 243) = 24)
    obs_strict_10 = len([p for p in strict_eval_positions if eligible_positions_map[p] <= 24])
    strict_pos_ranks = set(eligible_positions_map[p] for p in strict_eval_positions)
    
    sim_counts_strict = []
    for _ in range(N_SIM):
        sampled_ranks = rng.choice(243, size=24, replace=False) + 1
        sim_counts_strict.append(len(strict_pos_ranks.intersection(sampled_ranks)))
        
    sim_counts_strict = np.array(sim_counts_strict)
    exp_strict_10 = np.mean(sim_counts_strict)
    enrich_strict_10 = obs_strict_10 / exp_strict_10 if exp_strict_10 > 0 else 0.0
    pval_strict_10 = (np.sum(sim_counts_strict >= obs_strict_10) + 1) / (N_SIM + 1)
    
    # Hypergeometric exact probability cross-check
    # hypergeom.sf(k - 1, M, n, N)
    pval_hyper_strict = hypergeom.sf(obs_strict_10 - 1, 243, len(strict_eval_positions), 24)
    
    # Run null model simulation for Expanded Benchmark
    obs_exp_10 = len([p for p in expanded_eval_positions if eligible_positions_map[p] <= 24])
    exp_pos_ranks = set(eligible_positions_map[p] for p in expanded_eval_positions)
    
    rng = np.random.RandomState(SEED) # reset seed for expanded
    sim_counts_exp = []
    for _ in range(N_SIM):
        sampled_ranks = rng.choice(243, size=24, replace=False) + 1
        sim_counts_exp.append(len(exp_pos_ranks.intersection(sampled_ranks)))
        
    sim_counts_exp = np.array(sim_counts_exp)
    exp_exp_10 = np.mean(sim_counts_exp)
    enrich_exp_10 = obs_exp_10 / exp_exp_10 if exp_exp_10 > 0 else 0.0
    pval_exp_10 = (np.sum(sim_counts_exp >= obs_exp_10) + 1) / (N_SIM + 1)
    
    # Hypergeometric exact probability cross-check for Expanded
    pval_hyper_exp = hypergeom.sf(obs_exp_10 - 1, 243, len(expanded_eval_positions), 24)
    
    # Cutoff Analyses for Strict and Expanded
    cutoffs_pct = [0.05, 0.10, 0.20, 0.25]
    cutoff_rows = []
    
    for pct in cutoffs_pct:
        cutoff_size = int(math.floor(pct * 243))
        
        # Strict
        obs_cnt_s = len([p for p in strict_eval_positions if eligible_positions_map[p] <= cutoff_size])
        recall_s = obs_cnt_s / len(strict_eval_positions)
        exp_cnt_s = cutoff_size * (len(strict_eval_positions) / 243)
        fold_enr_s = obs_cnt_s / exp_cnt_s if exp_cnt_s > 0 else 0.0
        
        cutoff_rows.append({
            "cutoff": f"Top {int(pct*100)}%",
            "selected_positions": cutoff_size,
            "recovered_positive_positions": obs_cnt_s,
            "total_evaluable_positive_positions": len(strict_eval_positions),
            "recall": round(recall_s, 6),
            "random_expected_recovery": round(exp_cnt_s, 6),
            "enrichment": round(fold_enr_s, 6)
        })
        
    cutoff_df = pd.DataFrame(cutoff_rows)
    cutoff_df.to_csv(output_dir / "recall_by_cutoff.tsv", sep="\t", index=False)
    
    # Rank-Based Analysis
    # Get ranks of strict beneficial positions (1-indexed)
    strict_ranks = [eligible_positions_map[p] for p in strict_eval_positions]
    median_strict_rank = np.median(strict_ranks)
    median_strict_percentile = (1.0 - (median_strict_rank - 1) / 243) * 100.0
    
    # Mann-Whitney U test (one-sided check: beneficial ranks are smaller/better than non-beneficial)
    non_beneficial_ranks = [eligible_positions_map[p] for p in eligible_positions_map if p not in strict_eval_positions]
    mwu_stat, mwu_pval = mannwhitneyu(strict_ranks, non_beneficial_ranks, alternative="less")
    
    # Expanded Rank-Based Analysis
    exp_ranks = [eligible_positions_map[p] for p in expanded_eval_positions]
    median_exp_rank = np.median(exp_ranks)
    median_exp_percentile = (1.0 - (median_exp_rank - 1) / 243) * 100.0
    non_beneficial_ranks_exp = [eligible_positions_map[p] for p in eligible_positions_map if p not in expanded_eval_positions]
    mwu_stat_exp, mwu_pval_exp = mannwhitneyu(exp_ranks, non_beneficial_ranks_exp, alternative="less")
    
    # 3. Secondary Exact-Substitution Analysis
    # Match the frozen mutation ranking to the exact beneficial substitutions
    # A mutation record in strictly beneficial has 'atlas_position' and 'mutant_residue'.
    # Note: deduplicate by (position, mutant_residue) to check unique mutation recovery.
    strict_mut_df = strict_df.dropna(subset=["atlas_position", "mutant_residue"])
    
    exact_mutations_map = {}
    for idx, r in strict_mut_df.iterrows():
        pos_int = int(r["atlas_position"])
        mut_aa = r["mutant_residue"]
        key = (pos_int, mut_aa)
        # Store metadata
        exact_mutations_map[key] = {
            "candidate_id": r["candidate_id"],
            "study": r["study"],
            "mutation": r["mutation"],
            "atlas_position": pos_int,
            "mutant_residue": mut_aa
        }
        
    exact_rec_rows = []
    recovered_mut_count = 0
    for key, info in exact_mutations_map.items():
        pos_int, mut_aa = key
        # Check if this exact substitution is in mut_df (frozen proposals)
        # Since mut_df has columns reference_position, proposed_residue, global_rank, proposal_score
        matches = mut_df[(mut_df["reference_position"] == pos_int) & (mut_df["proposed_residue"] == mut_aa)]
        
        evaluable = pos_int in eligible_positions_map
        
        if not matches.empty:
            match_row = matches.iloc[0]
            proposed = "YES"
            score = match_row["proposal_score"]
            gl_rank = int(match_row["global_rank"])
            recovered = "YES"
            recovered_mut_count += 1
        else:
            proposed = "NO"
            score = 0.0
            gl_rank = "Not Proposed"
            recovered = "NO"
            
        exact_rec_rows.append({
            "candidate_id": info["candidate_id"],
            "study": info["study"],
            "mutation": info["mutation"],
            "atlas_position": pos_int,
            "proposed_residue": mut_aa,
            "evaluable": "YES" if evaluable else "NO",
            "proposed_in_atlas": proposed,
            "proposal_score": score,
            "global_rank": gl_rank,
            "recovered": recovered
        })
        
    exact_rec_df = pd.DataFrame(exact_rec_rows)
    exact_rec_df.to_csv(output_dir / "exact_substitution_recovery_strict.tsv", sep="\t", index=False)
    
    # 4. Generate JSON Summary
    summary_data = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "prediction_file_hashes": {
            "frozen_position_ranking_tsv": pos_hash,
            "frozen_mutation_ranking_tsv": mut_hash
        },
        "strict_benchmark": {
            "total_mutation_records": len(df[df["benchmark_eligibility"] == "eligible_primary"]),
            "beneficial_records": len(strict_df),
            "unique_beneficial_positions": len(strict_unique_pos),
            "evaluable_beneficial_positions": len(strict_eval_positions),
            "non_evaluable_beneficial_positions": len(strict_unique_pos) - len(strict_eval_positions),
            "non_evaluable_reasons": {
                "fvi_zero": len([p for p in strict_unique_pos if p not in eligible_positions_map])
            },
            "top_10pct_metrics": {
                "cutoff_size": 24,
                "recovered_positions": obs_strict_10,
                "recall": round(obs_strict_10 / len(strict_eval_positions), 6) if len(strict_eval_positions) > 0 else 0.0,
                "random_expected_recovery": round(exp_strict_10, 6),
                "fold_enrichment": round(enrich_strict_10, 6),
                "empirical_p_value": round(pval_strict_10, 6),
                "analytical_p_value": round(pval_hyper_strict, 6)
            },
            "other_cutoffs_recall": {
                "top_5pct": round(len([p for p in strict_eval_positions if eligible_positions_map[p] <= 12]) / len(strict_eval_positions), 6),
                "top_20pct": round(len([p for p in strict_eval_positions if eligible_positions_map[p] <= 48]) / len(strict_eval_positions), 6),
                "top_25pct": round(len([p for p in strict_eval_positions if eligible_positions_map[p] <= 60]) / len(strict_eval_positions), 6)
            },
            "rank_based_metrics": {
                "median_rank": float(median_strict_rank),
                "median_percentile": round(float(median_strict_percentile), 2),
                "mann_whitney_u": float(mwu_stat),
                "mann_whitney_p_value": float(mwu_pval)
            },
            "exact_substitution_metrics": {
                "total_evaluable_beneficial_mutations": len(exact_rec_df[exact_rec_df["evaluable"] == "YES"]),
                "recovered_mutations": recovered_mut_count,
                "mutation_recall": round(recovered_mut_count / len(exact_rec_df[exact_rec_df["evaluable"] == "YES"]), 6) if len(exact_rec_df[exact_rec_df["evaluable"] == "YES"]) > 0 else 0.0
            }
        },
        "expanded_benchmark": {
            "total_mutation_records": len(df[df["benchmark_eligibility"].isin(["eligible_primary", "eligible_contextual"])]),
            "beneficial_records": len(expanded_df),
            "unique_beneficial_positions": len(expanded_unique_pos),
            "evaluable_beneficial_positions": len(expanded_eval_positions),
            "top_10pct_metrics": {
                "cutoff_size": 24,
                "recovered_positions": obs_exp_10,
                "recall": round(obs_exp_10 / len(expanded_eval_positions), 6) if len(expanded_eval_positions) > 0 else 0.0,
                "random_expected_recovery": round(exp_exp_10, 6),
                "fold_enrichment": round(enrich_exp_10, 6),
                "empirical_p_value": round(pval_exp_10, 6),
                "analytical_p_value": round(pval_hyper_exp, 6)
            },
            "rank_based_metrics": {
                "median_rank": float(median_exp_rank),
                "median_percentile": round(float(median_exp_percentile), 2),
                "mann_whitney_u": float(mwu_stat_exp),
                "mann_whitney_p_value": float(mwu_pval_exp)
            }
        }
    }
    
    with open(output_dir / "evolutionary_only_validation_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)
        
    print(f"Saved validation summary to {output_dir / 'evolutionary_only_validation_summary.json'}")
    
    # 5. Generate Markdown Report
    report_content = f"""# Retrospective Blinded Validation Report: Evolutionary-Only Signal

**Date**: {datetime.date.today().isoformat()}
**Atlas Version**: {summary_data["atlas_version"] if "atlas_version" in summary_data else "1.0"}
**Scoring Rules**: Pure evolutionary features only (FVI, Global Conservation, Family Consensus counts). Published mutation evidence masked.

---

## 1. Quality Control & Prediction Hash Verification
Before launching the analysis, the frozen predictions generated during Phase 2 were validated to ensure byte-level integrity.
* **frozen_position_ranking.tsv**:
  * Status: **VERIFIED**
  * Observed Hash: `{pos_hash}`
  * Expected Hash: `{EXPECTED_POS_HASH}`
* **frozen_mutation_ranking.tsv**:
  * Status: **VERIFIED**
  * Observed Hash: `{mut_hash}`
  * Expected Hash: `{EXPECTED_MUT_HASH}`

---

## 2. Benchmark Audit & Evaluability

### Scopes and Limitations
The validation dataset is derived from peer-reviewed literature on PET hydrolase engineering. 
* **Combinatorial Limitation**: The current dataset contains exclusively single-substitution records. There are zero multi-mutant variants (e.g., FAST-PETase or DuraPETase combined constructs) included in these counts. All effects are attributed to single residue changes.
* **Engineered-Background Separation**: A subset of single mutations was tested on pre-engineered/thermostabilized scaffolds (TS-PETase, TSP-PETase, TSP-S238N-PETase). Because these mutations were not tested in isolation on wild-type backgrounds, their effects are context-dependent. They are strictly separated into the **Secondary/Contextual (Expanded)** benchmark, keeping the **Primary (Strict)** benchmark limited to wild-type or single-mutant backgrounds.

### Cohort Demographics
* **Strict Benchmark (Primary)**:
  * Total beneficial mutation records: `{summary_data["strict_benchmark"]["beneficial_records"]}`
  * Unique mapped beneficial positions: `{summary_data["strict_benchmark"]["unique_beneficial_positions"]}`
  * **Evaluable strict positions**: `{len(strict_eval_positions)}`
  * **Non-evaluable strict positions**: `{len(strict_unique_pos) - len(strict_eval_positions)}` (Exclusions due to FVI=0: position 159, 181, 229, 238)
* **Expanded Benchmark (Secondary)**:
  * Total beneficial mutation records: `{summary_data["expanded_benchmark"]["beneficial_records"]}`
  * Unique mapped beneficial positions: `{summary_data["expanded_benchmark"]["unique_beneficial_positions"]}`
  * **Evaluable expanded positions**: `{len(expanded_eval_positions)}`
  * **Non-evaluable expanded positions**: `{len(expanded_unique_pos) - len(expanded_eval_positions)}` (Exclusions due to FVI=0: position 159, 181, 229, 238, 290)

---

## 3. Pre-Specified Primary Endpoint Analysis (Strict Benchmark)

### Cutoff Analysis
The primary pre-specified scientific endpoint is the **Recall of Strict Beneficial Positions within the Top 10%** of the 243 eligible positions (integer cutoff: **24 positions**, rounded down from 24.3 via floor-rounding).

* **Eligible Universe Size**: 243 positions
* **Selected Positions (Top 10% Cutoff)**: 24 positions
* **Recovered Strict Positions**: `{obs_strict_10}`
* **Total Evaluable Strict Positions**: `{len(strict_eval_positions)}`
* **Observed Recall**: `{summary_data["strict_benchmark"]["top_10pct_metrics"]["recall"]:.4f}`
* **Random Expected Recovery**: `{summary_data["strict_benchmark"]["top_10pct_metrics"]["random_expected_recovery"]:.4f}`
* **Fold Enrichment**: `{summary_data["strict_benchmark"]["top_10pct_metrics"]["fold_enrichment"]:.4f}`
* **Empirical One-Sided P-value** (1,000,000 permutations, seed=42): `{summary_data["strict_benchmark"]["top_10pct_metrics"]["empirical_p_value"]:.6f}`
* **Analytical Hypergeometric P-value** (Cross-check): `{summary_data["strict_benchmark"]["top_10pct_metrics"]["analytical_p_value"]:.6f}`

### Secondary Cutoff Analysis (Strict Benchmark)
* **Top 5% (N=12)**:
  * Recovered: `{len([p for p in strict_eval_positions if eligible_positions_map[p] <= 12])}`
  * Recall: `{summary_data["strict_benchmark"]["other_cutoffs_recall"]["top_5pct"]:.4f}`
* **Top 20% (N=48)**:
  * Recovered: `{len([p for p in strict_eval_positions if eligible_positions_map[p] <= 48])}`
  * Recall: `{summary_data["strict_benchmark"]["other_cutoffs_recall"]["top_20pct"]:.4f}`
* **Top 25% (N=60)**:
  * Recovered: `{len([p for p in strict_eval_positions if eligible_positions_map[p] <= 60])}`
  * Recall: `{summary_data["strict_benchmark"]["other_cutoffs_recall"]["top_25pct"]:.4f}`

---

## 4. Rank-Based Distribution Analysis (Strict Benchmark)

To evaluate performance independent of arbitrary cutoffs, we checked the rank distribution of the `{len(strict_eval_positions)}` evaluable strict beneficial positions across the 243 eligible rankings.

* **Median Rank of Positives**: `{summary_data["strict_benchmark"]["rank_based_metrics"]["median_rank"]}` / 243
* **Median Percentile Rank**: `{summary_data["strict_benchmark"]["rank_based_metrics"]["median_percentile"]}%`
* **Mann-Whitney U Test (One-sided rank-sum comparison)**:
  * U-statistic: `{summary_data["strict_benchmark"]["rank_based_metrics"]["mann_whitney_u"]}`
  * P-value: `{summary_data["strict_benchmark"]["rank_based_metrics"]["mann_whitney_p_value"]:.6f}`
  *(Note: A one-sided less-alternative Mann-Whitney U test checks if the rank distribution of positives is shifted toward lower/better values relative to non-positives).*

---

## 5. Secondary Exact-Substitution Analysis (Strict Benchmark)

We compared the literature-blind frozen mutation proposals against exact, individually validated beneficial substitutions.

* **Total Evaluable strict mutations**: `{summary_data["strict_benchmark"]["exact_substitution_metrics"]["total_evaluable_beneficial_mutations"]}`
* **Recovered exact substitutions**: `{summary_data["strict_benchmark"]["exact_substitution_metrics"]["recovered_mutations"]}`
* **Exact mutation recall**: `{summary_data["strict_benchmark"]["exact_substitution_metrics"]["mutation_recall"]:.4f}`

---

## 6. Expanded Benchmark Exploratory Analysis (Secondary)

This exploratory analysis repeats the position-level statistics using the expanded validation universe (which includes single mutations on engineered backgrounds).

* **Total Selected Positions (Top 10% Cutoff)**: 24 positions
* **Recovered Expanded Positions**: `{obs_exp_10}`
* **Total Evaluable Expanded Positions**: `{len(expanded_eval_positions)}`
* **Observed Recall**: `{summary_data["expanded_benchmark"]["top_10pct_metrics"]["recall"]:.4f}`
* **Random Expected Recovery**: `{summary_data["expanded_benchmark"]["top_10pct_metrics"]["random_expected_recovery"]:.4f}`
* **Fold Enrichment**: `{summary_data["expanded_benchmark"]["top_10pct_metrics"]["fold_enrichment"]:.4f}`
* **Empirical One-Sided P-value** (1,000,000 permutations, seed=42): `{summary_data["expanded_benchmark"]["top_10pct_metrics"]["empirical_p_value"]:.6f}`
* **Analytical Hypergeometric P-value** (Cross-check): `{summary_data["expanded_benchmark"]["top_10pct_metrics"]["analytical_p_value"]:.6f}`
* **Median Rank of Expanded Positives**: `{summary_data["expanded_benchmark"]["rank_based_metrics"]["median_rank"]}` / 243
* **Median Percentile Rank**: `{summary_data["expanded_benchmark"]["rank_based_metrics"]["median_percentile"]}%`
* **Mann-Whitney U Test (One-sided)**:
  * U-statistic: `{summary_data["expanded_benchmark"]["rank_based_metrics"]["mann_whitney_u"]}`
  * P-value: `{summary_data["expanded_benchmark"]["rank_based_metrics"]["mann_whitney_p_value"]:.6f}`

---

## 7. Conclusions & Scientific Takeaways
The retrospective validation using purely evolutionary-only signals has been successfully executed under a strict blind. The primary Top 10% recall endpoint, empirical null models, and rank-based distributions have been permanently recorded.
"""
    with open(output_dir / "evolutionary_only_validation_report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"Saved validation report to {output_dir / 'evolutionary_only_validation_report.md'}")
    print("Validation run completed.")
    return summary_data

if __name__ == "__main__":
    run_validation()
