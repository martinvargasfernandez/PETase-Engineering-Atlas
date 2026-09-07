import datetime
import uuid

class MDImportConfig:
    """
    Configuration Entity: MDImportConfig

    Holds simulation metadata parameters and provenance fields for MD imports.
    """

    def __init__(
        self,
        simulation_id: str,
        case_study_id: str,
        project_id: str,
        study_id: str,
        software: str,
        software_version: str,
        force_field: str,
        water_model: str,
        temperature_K: float,
        pressure_bar: float,
        timestep_fs: float,
        duration_ns: float,
        ensemble: str,
        ligand_name: str,
        trajectory_path: str = None,
        topology_path: str = None,
        source_directory: str = None,
        notes: str = None,
        provenance: dict = None,
        created_at: str = None
    ):
        self._simulation_id = str(simulation_id) if simulation_id else str(uuid.uuid4())
        self._case_study_id = str(case_study_id)
        self._project_id = str(project_id)
        self._study_id = str(study_id)
        self._software = str(software)
        self._software_version = str(software_version)
        self._force_field = str(force_field)
        self._water_model = str(water_model)
        self._temperature_K = float(temperature_K)
        self._pressure_bar = float(pressure_bar)
        self._timestep_fs = float(timestep_fs)
        self._duration_ns = float(duration_ns)
        self._ensemble = str(ensemble)
        self._ligand_name = str(ligand_name)
        self._trajectory_path = str(trajectory_path) if trajectory_path else ""
        self._topology_path = str(topology_path) if topology_path else ""
        self._source_directory = str(source_directory) if source_directory else ""
        self._notes = str(notes) if notes else ""
        self._provenance = dict(provenance) if provenance else {}
        self._created_at = str(created_at) if created_at else datetime.datetime.now(datetime.timezone.utc).isoformat()

    @property
    def simulation_id(self) -> str: return self._simulation_id
    @property
    def case_study_id(self) -> str: return self._case_study_id
    @property
    def project_id(self) -> str: return self._project_id
    @property
    def study_id(self) -> str: return self._study_id
    @property
    def software(self) -> str: return self._software
    @property
    def software_version(self) -> str: return self._software_version
    @property
    def force_field(self) -> str: return self._force_field
    @property
    def water_model(self) -> str: return self._water_model
    @property
    def temperature_K(self) -> float: return self._temperature_K
    @property
    def pressure_bar(self) -> float: return self._pressure_bar
    @property
    def timestep_fs(self) -> float: return self._timestep_fs
    @property
    def duration_ns(self) -> float: return self._duration_ns
    @property
    def ensemble(self) -> str: return self._ensemble
    @property
    def ligand_name(self) -> str: return self._ligand_name
    @property
    def trajectory_path(self) -> str: return self._trajectory_path
    @property
    def topology_path(self) -> str: return self._topology_path
    @property
    def source_directory(self) -> str: return self._source_directory
    @property
    def notes(self) -> str: return self._notes
    @property
    def provenance(self) -> dict: return dict(self._provenance)
    @property
    def created_at(self) -> str: return self._created_at

    def to_dict(self) -> dict:
        return {
            "simulation_id": self.simulation_id,
            "case_study_id": self.case_study_id,
            "project_id": self.project_id,
            "study_id": self.study_id,
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
            "trajectory_path": self.trajectory_path,
            "topology_path": self.topology_path,
            "source_directory": self.source_directory,
            "notes": self.notes,
            "provenance": self.provenance,
            "created_at": self.created_at
        }
