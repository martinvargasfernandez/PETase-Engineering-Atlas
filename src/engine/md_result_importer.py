import os
from pathlib import Path
from engine.case_study_update import CaseStudyUpdate
from engine.md_import_config import MDImportConfig

# Import individual parsers
from engine.rmsd_parser import RmsdParser
from engine.rmsf_parser import RmsfParser
from engine.rg_parser import RgParser
from engine.sasa_parser import SasaParser
from engine.contacts_parser import ContactsParser
from engine.hbonds_parser import HbondsParser
from engine.residue_energy_parser import ResidueEnergyParser

class SimulationSummary:
    """
    Representation structure for simulation metadata, stored independently in global_metrics.
    """
    def __init__(self, config: MDImportConfig):
        self.simulation_id = config.simulation_id
        self.software = config.software
        self.software_version = config.software_version
        self.force_field = config.force_field
        self.water_model = config.water_model
        self.temperature_K = config.temperature_K
        self.pressure_bar = config.pressure_bar
        self.timestep_fs = config.timestep_fs
        self.duration_ns = config.duration_ns
        self.ensemble = config.ensemble
        self.ligand_name = config.ligand_name
        self.notes = config.notes

    def to_dict(self) -> dict:
        return {
            "simulation_id": self.simulation_id,
            "software": self.software,
            "software_version": self.software_version,
            "force_field": self.force_field,
            "water_model": self.water_model,
            "temperature_K": self.temperature_K,
            "pressure_bar": self.pressure_bar,
            "timestep_fs": self.timestep_fs,
            "duration_ns": self.duration_ns,
            "ensemble": self.ensemble,
            "ligand_name": self.ligand_name,
            "notes": self.notes
        }

class MDResultImporter:
    """
    Orchestration Engine: MDResultImporter

    Delegates CSV/TSV parsing to specialized parser modules and packages the raw
    outputs into a unified CaseStudyUpdate payload.
    """

    def __init__(self):
        self.rmsd_parser = RmsdParser()
        self.rmsf_parser = RmsfParser()
        self.rg_parser = RgParser()
        self.sasa_parser = SasaParser()
        self.contacts_parser = ContactsParser()
        self.hbonds_parser = HbondsParser()
        self.residue_energy_parser = ResidueEnergyParser()

    def import_results(
        self,
        config: MDImportConfig,
        rmsd_file: str = None,
        rmsf_file: str = None,
        rg_file: str = None,
        sasa_file: str = None,
        contacts_file: str = None,
        hbonds_file: str = None,
        residue_energy_file: str = None,
        metadata_file: str = None
    ) -> CaseStudyUpdate:

        global_metrics = {}
        residue_level_evidence = []
        result_files = []
        warnings = []
        notes = []

        # Common trace metadata dictionary embedded in metrics/evidence
        sim_trace = {
            "simulation_id": config.simulation_id,
            "software": config.software,
            "force_field": config.force_field,
            "temperature_K": config.temperature_K,
            "duration_ns": config.duration_ns
        }

        # Save SimulationSummary metadata independently
        summary = SimulationSummary(config)
        global_metrics["simulation_summary"] = summary.to_dict()

        # 1. Parse RMSD (Global raw series)
        if rmsd_file:
            path = Path(rmsd_file)
            rmsd_data = self.rmsd_parser.parse(str(path), warnings)
            global_metrics["rmsd_series"] = rmsd_data
            result_files.append({
                "path": str(path.resolve()),
                "checksum": "",
                "size_bytes": os.path.getsize(str(path)),
                "stored_in_project": False
            })

        # 2. Parse Radius of Gyration (Global raw series)
        if rg_file:
            path = Path(rg_file)
            rg_data = self.rg_parser.parse(str(path), warnings)
            global_metrics["rg_series"] = rg_data
            result_files.append({
                "path": str(path.resolve()),
                "checksum": "",
                "size_bytes": os.path.getsize(str(path)),
                "stored_in_project": False
            })

        # 3. Parse SASA (Global raw series)
        if sasa_file:
            path = Path(sasa_file)
            sasa_data = self.sasa_parser.parse(str(path), warnings)
            global_metrics["sasa_series"] = sasa_data
            result_files.append({
                "path": str(path.resolve()),
                "checksum": "",
                "size_bytes": os.path.getsize(str(path)),
                "stored_in_project": False
            })

        # 4. Parse RMSF
        if rmsf_file:
            path = Path(rmsf_file)
            rmsf_records = self.rmsf_parser.parse(str(path), warnings, sim_trace)
            residue_level_evidence.extend(rmsf_records)
            result_files.append({
                "path": str(path.resolve()),
                "checksum": "",
                "size_bytes": os.path.getsize(str(path)),
                "stored_in_project": False
            })

        # 5. Parse Contacts
        if contacts_file:
            path = Path(contacts_file)
            contact_records = self.contacts_parser.parse(str(path), warnings, sim_trace)
            residue_level_evidence.extend(contact_records)
            result_files.append({
                "path": str(path.resolve()),
                "checksum": "",
                "size_bytes": os.path.getsize(str(path)),
                "stored_in_project": False
            })

        # 6. Parse H-Bonds
        if hbonds_file:
            path = Path(hbonds_file)
            hbond_records = self.hbonds_parser.parse(str(path), warnings, sim_trace)
            residue_level_evidence.extend(hbond_records)
            result_files.append({
                "path": str(path.resolve()),
                "checksum": "",
                "size_bytes": os.path.getsize(str(path)),
                "stored_in_project": False
            })

        # 7. Parse Residue Energy
        if residue_energy_file:
            path = Path(residue_energy_file)
            energy_records = self.residue_energy_parser.parse(str(path), warnings, sim_trace)
            residue_level_evidence.extend(energy_records)
            result_files.append({
                "path": str(path.resolve()),
                "checksum": "",
                "size_bytes": os.path.getsize(str(path)),
                "stored_in_project": False
            })

        # Register trajectory input paths strictly as metadata references
        trajectory_files = []
        if config.trajectory_path:
            trajectory_files.append({
                "path": config.trajectory_path,
                "checksum": "",
                "size_bytes": 0,
                "stored_in_project": False
            })
        if config.topology_path:
            trajectory_files.append({
                "path": config.topology_path,
                "checksum": "",
                "size_bytes": 0,
                "stored_in_project": False
            })

        if config.notes:
            notes.append(config.notes)

        return CaseStudyUpdate(
            source="MDResultImporter",
            method="parse_tabular_simulation_results",
            method_version="1.0",
            residue_level_evidence=residue_level_evidence,
            global_metrics=global_metrics,
            result_files=result_files,
            warnings=warnings,
            provenance={
                "simulation_id": config.simulation_id,
                "water_model": config.water_model,
                "timestep_fs": config.timestep_fs,
                "ensemble": config.ensemble,
                "ligand_name": config.ligand_name,
                "topology_path": config.topology_path,
                "trajectory_path": config.trajectory_path,
                "source_directory": config.source_directory,
                "notes": config.notes
            },
            notes=notes
        )

