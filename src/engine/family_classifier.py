import math
from engine.family_classification_result import FamilyClassificationResult

class FamilyClassifier:
    """
    Scientific Execution Engine: FamilyClassifier

    Classifies one StudySequence (represented as a ProjectedSequence) into one of the 
    9 standard Atlas families using a normalized, weighted consensus agreement score.
    Discriminatory power of reference positions is computed using Shannon entropy of 
    consensus states across families.
    """

    def __init__(self):
        self.families = [
            "IsPETase-like",
            "LCC-like",
            "Thermobifida-like",
            "Actinomadura-like",
            "Nocardiopsis-like",
            "Amycolatopsis-like",
            "Microbispora-like",
            "Streptomyces-like",
            "Other_bacterial"
        ]

    def classify(self, projected_sequence) -> FamilyClassificationResult:
        # Verify ProjectedSequence duck typing
        if not hasattr(projected_sequence, "study_id") or not hasattr(projected_sequence, "projected_residues"):
            raise TypeError("projected_sequence must implement the ProjectedSequence interface.")

        # Gather mapped study residues
        mapped_residues = [
            pr for pr in projected_sequence.projected_residues 
            if pr.is_mapped and pr.study_position is not None and pr.atlas_position_id is not None
        ]
        
        mapped_positions_used = len(mapped_residues)
        missing_positions = projected_sequence.deletions

        # 1. Compute Shannon entropy weights for reference positions based on consensus states
        position_weights = {}
        for pr in projected_sequence.projected_residues:
            pos_id = pr.atlas_position_id
            if pos_id is None:
                continue

            valid_consensus = []
            for fam in self.families:
                val = pr.family_consensus.get(fam)
                if val not in (None, "", "NA", "-", "nan"):
                    if isinstance(val, str) and len(val) == 1:
                        valid_consensus.append(val)

            if len(valid_consensus) <= 1:
                position_weights[pos_id] = 0.0
            else:
                counts = {}
                for aa in valid_consensus:
                    counts[aa] = counts.get(aa, 0) + 1
                n = len(valid_consensus)
                entropy = 0.0
                for count in counts.values():
                    p = count / n
                    entropy -= p * math.log2(p)
                position_weights[pos_id] = entropy

        # 2. Compute weighted agreement scores
        scores = {fam: 0.0 for fam in self.families}
        max_possible_scores = {fam: 0.0 for fam in self.families}
        informative_counts = {fam: 0 for fam in self.families}
        
        # Track supporting residues matched for predicted family
        family_matches = {fam: [] for fam in self.families}

        for pr in mapped_residues:
            pos_id = pr.atlas_position_id
            study_res = pr.study_residue
            weight = position_weights.get(pos_id, 0.0)

            for fam in self.families:
                c_res = pr.family_consensus.get(fam)
                if c_res not in (None, "", "NA", "-", "nan") and isinstance(c_res, str) and len(c_res) == 1:
                    informative_counts[fam] += 1
                    max_possible_scores[fam] += weight
                    if study_res == c_res:
                        scores[fam] += weight
                        if weight > 0.0:
                            family_matches[fam].append((weight, pr))

        # 3. Normalize scores
        normalized_scores = {}
        for fam in self.families:
            max_score = max_possible_scores[fam]
            normalized_scores[fam] = (scores[fam] / max_score) if max_score > 0.0 else 0.0

        # Sort families by normalized score descending
        ranked = sorted([(val, fam) for fam, val in normalized_scores.items()], reverse=True)
        best_score, best_family = ranked[0]
        second_best_score, second_best_family = ranked[1]
        score_margin = best_score - second_best_score

        # Prepare ranked scores list for result
        ranked_family_scores = [(fam, val) for val, fam in ranked]

        warnings_list = []
        
        # 4. Apply classification logic thresholds
        max_limit = max(max_possible_scores.values()) if max_possible_scores else 0.0
        
        if mapped_positions_used < 50 or max_limit < 5.0:
            predicted_family = "unclassified"
            classification_status = "insufficient_evidence"
            confidence_status = "low"
            warnings_list.append("Insufficient mapped positions or informative consensus data for classification.")
            best_informative = 0
            supporting_residues = []
        elif best_score < 0.35:
            predicted_family = "unclassified"
            classification_status = "insufficient_evidence"
            confidence_status = "low"
            warnings_list.append("Best family consensus agreement is too low (< 35%) for reliable classification.")
            best_informative = 0
            supporting_residues = []
        elif score_margin < 0.08:
            predicted_family = "ambiguous"
            classification_status = "ambiguous"
            confidence_status = "low"
            warnings_list.append(
                f"Classification is ambiguous. Score margin between top candidates ({best_family} vs {second_best_family}) "
                f"is too small ({score_margin:.4f})."
            )
            best_informative = informative_counts[best_family]
            
            # Format supporting residues for top ranked candidate
            raw_supporting = family_matches[best_family]
            supporting_residues = []
            for w, pr in sorted(raw_supporting, key=lambda x: x[0], reverse=True):
                supporting_residues.append({
                    "study_position": pr.study_position,
                    "study_residue": pr.study_residue,
                    "atlas_position_id": pr.atlas_position_id,
                    "weight": w
                })
        else:
            predicted_family = best_family
            classification_status = "classified"
            confidence_status = "high" if score_margin >= 0.20 else "medium"
            best_informative = informative_counts[best_family]

            # Format supporting residues (sorted by discriminatory weight descending)
            raw_supporting = family_matches[best_family]
            supporting_residues = []
            for w, pr in sorted(raw_supporting, key=lambda x: x[0], reverse=True):
                supporting_residues.append({
                    "study_position": pr.study_position,
                    "study_residue": pr.study_residue,
                    "atlas_position_id": pr.atlas_position_id,
                    "weight": w
                })

        if predicted_family == "Other_bacterial":
            warnings_list.append(
                "Matched catch-all Other_bacterial category; this is a highly heterogeneous collection and not a single coherent biological family."
            )

        return FamilyClassificationResult(
            study_id=projected_sequence.study_id,
            predicted_family=predicted_family,
            classification_status=classification_status,
            confidence_status=confidence_status,
            ranked_family_scores=ranked_family_scores,
            best_score=best_score,
            second_best_score=second_best_score,
            score_margin=score_margin,
            mapped_positions_used=mapped_positions_used,
            informative_positions_used=best_informative,
            missing_positions=missing_positions,
            warnings=warnings_list,
            informative_residues=supporting_residues
        )
