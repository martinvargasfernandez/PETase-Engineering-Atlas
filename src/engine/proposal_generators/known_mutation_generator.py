import math
import re

from engine.mutation import Mutation


def is_missing(value):
    if value is None:
        return True

    try:
        if isinstance(value, float) and math.isnan(value):
            return True
    except TypeError:
        pass

    value = str(value).strip()

    if value == "":
        return True

    if value.lower() in {"nan", "none", "null", "na", "n/a", "-"}:
        return True

    return False


class KnownMutationGenerator:
    """
    Generates mutation proposals from experimentally reported known mutations.

    This generator is independent from family consensus.
    Known mutations must be proposed even if they are not consensus-derived.
    """

    name = "known_mutation"

    def generate(self, residue):
        proposals = []

        known_mutations = getattr(residue, "known_mutations", None)

        if is_missing(known_mutations):
            return proposals

        mutation_codes = self._parse_known_mutations(known_mutations)

        for mutation_code in mutation_codes:
            parsed = self._parse_mutation_code(mutation_code)

            if parsed is None:
                continue

            wild_type, position, mutant = parsed

            if position != residue.position:
                continue

            if wild_type != residue.reference_residue:
                continue

            proposals.append(
                Mutation(
                    position=position,
                    wild_type=wild_type,
                    mutant=mutant,
                    source=self.name,
                    evidence={
                        "known_mutation": mutation_code,
                        "generator": self.name,
                    },
                )
            )

        return proposals

    def _parse_known_mutations(self, known_mutations):
        """
        Accepts values such as:
        - "R280A"
        - "FAST-PETase:R280A"
        - "R280A; S238F"
        - ["R280A", "S238F"]
        """

        if isinstance(known_mutations, list):
            raw_items = known_mutations
        else:
            text = str(known_mutations)
            raw_items = re.split(r"[;,|]", text)

        mutation_codes = []

        for item in raw_items:
            item = str(item).strip()

            if is_missing(item):
                continue

            if ":" in item:
                item = item.split(":")[-1].strip()

            mutation_codes.append(item)

        return mutation_codes

    def _parse_mutation_code(self, mutation_code):
        """
        Parses mutation labels like R280A.
        """

        match = re.search(r"^([A-Z])(\d+)([A-Z])$", mutation_code.strip().upper())

        if not match:
            return None

        wild_type = match.group(1)
        position = int(match.group(2))
        mutant = match.group(3)

        return wild_type, position, mutant