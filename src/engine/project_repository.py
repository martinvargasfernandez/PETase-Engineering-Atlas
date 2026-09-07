import os
import re
import json
import uuid
import datetime
import shutil
import tempfile
from pathlib import Path
from engine.paths import PROJECT_ROOT
from engine.study_sequence import StudySequence
from engine.project import Project, PersistedSequenceAnalysisResult

def make_safe_slug(name: str) -> str:
    slug = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    slug = re.sub(r'_+', '_', slug)
    slug = slug.strip('_')
    if not slug:
        slug = "project"
    return slug

class ProjectRepository:
    """
    Scientific Service: ProjectRepository

    Handles directory-based serialization and deserialization of Projects,
    ensuring atomic writes, path isolation, and history logging.
    """

    def __init__(self, projects_dir: str = None):
        if projects_dir is not None:
            self.projects_dir = Path(projects_dir).resolve()
        else:
            self.projects_dir = (PROJECT_ROOT / "projects").resolve()
        
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    def _get_safe_path(self, project_id: str, project_name: str) -> Path:
        # Validate UUID
        try:
            uuid.UUID(str(project_id))
        except ValueError:
            raise ValueError(f"Invalid UUID: {project_id}")

        safe_slug = make_safe_slug(project_name)
        folder_name = f"{project_id}__{safe_slug}"
        target_path = (self.projects_dir / folder_name).resolve()

        # Path traversal prevention
        if self.projects_dir not in target_path.parents:
            raise PermissionError("Access denied: Project path escapes projects directory boundaries.")
        return target_path

    def project_exists(self, project_id_or_name_or_path: str) -> bool:
        try:
            self.load_project(project_id_or_name_or_path)
            return True
        except Exception:
            return False

    def create_project(
        self,
        project_name: str,
        study_sequence: "StudySequence",
        sequence_analysis_result: "SequenceAnalysisResult",
        description: str = None,
        project_id: str = None
    ) -> Project:
        # 1. Duck typing validations
        if not hasattr(study_sequence, "study_id") or not hasattr(study_sequence, "normalized_sequence"):
            raise TypeError("study_sequence must implement the StudySequence interface.")
        if not hasattr(sequence_analysis_result, "coordinate_system") or not hasattr(sequence_analysis_result, "to_dict"):
            raise TypeError("sequence_analysis_result must implement the SequenceAnalysisResult interface.")

        # 2. Handle ID validation
        if project_id is not None:
            try:
                uuid.UUID(str(project_id))
                proj_id = str(project_id)
            except ValueError:
                raise ValueError(f"Invalid project_id UUID: {project_id}")
        else:
            proj_id = str(uuid.uuid4())

        final_path = self._get_safe_path(proj_id, project_name)
        if final_path.exists():
            raise FileExistsError(f"Project directory already exists: {final_path}")

        # Ensure no other project has the same project_id in its metadata
        for p in self.list_projects():
            if p["project_id"] == proj_id:
                raise FileExistsError(f"Project with ID {proj_id} already exists.")

        # 3. Create in a temporary directory inside projects_dir to guarantee same-filesystem move
        temp_dir_path = None
        try:
            with tempfile.TemporaryDirectory(dir=str(self.projects_dir)) as temp_dir:
                temp_dir_path = Path(temp_dir)
                
                # Setup subdirectories
                seq_dir = temp_dir_path / "sequence"
                analysis_dir = temp_dir_path / "analysis"
                seq_dir.mkdir(parents=True)
                analysis_dir.mkdir(parents=True)
                
                # Placeholders
                (temp_dir_path / "case_studies").mkdir()
                (temp_dir_path / "notes").mkdir()
                (temp_dir_path / "exports").mkdir()

                # Event Log and Metadata
                now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
                
                # Fetch baseline Atlas and version metadata
                from engine.atlas_position import AtlasPosition
                atlas_version = "3.0"  # default atlas release version
                coordinate_system = sequence_analysis_result.coordinate_system
                analysis_version = sequence_analysis_result.analysis_version

                history = [
                    {
                        "event_id": str(uuid.uuid4()),
                        "event_type": "PROJECT_CREATED",
                        "timestamp": now_str,
                        "project_id": proj_id,
                        "details": f"Project '{project_name}' created.",
                        "software_version": "1.0",
                        "atlas_version": atlas_version
                    },
                    {
                        "event_id": str(uuid.uuid4()),
                        "event_type": "SEQUENCE_SAVED",
                        "timestamp": now_str,
                        "project_id": proj_id,
                        "details": f"Primary StudySequence '{study_sequence.name}' saved.",
                        "software_version": "1.0",
                        "atlas_version": atlas_version
                    },
                    {
                        "event_id": str(uuid.uuid4()),
                        "event_type": "SEQUENCE_ANALYSIS_SAVED",
                        "timestamp": now_str,
                        "project_id": proj_id,
                        "details": "SequenceAnalysisResult and residues table saved.",
                        "software_version": "1.0",
                        "atlas_version": atlas_version
                    }
                ]

                # Populate project metadata
                project_status = [
                    "sequence_available",
                    "analysis_available",
                    "family_classification_available"
                ]

                meta = {
                    "project_id": proj_id,
                    "project_name": project_name,
                    "description": description if description is not None else "",
                    "created_at": now_str,
                    "updated_at": now_str,
                    "atlas_version": atlas_version,
                    "coordinate_system": coordinate_system,
                    "analysis_version": analysis_version,
                    "project_status": project_status,
                    "provenance": {
                        "software_version": "1.0",
                        "schema_version": 1,
                        "sequence_hash": study_sequence.sequence_hash,
                        "classification_method": sequence_analysis_result.classification_method
                    }
                }

                # 4. Write all JSON and FASTA data
                with open(temp_dir_path / "project.json", "w", encoding="utf-8") as f:
                    json.dump(meta, f, sort_keys=True, indent=2)

                with open(temp_dir_path / "history.json", "w", encoding="utf-8") as f:
                    json.dump(history, f, sort_keys=True, indent=2)

                # Sequence folder
                with open(seq_dir / "primary.fasta", "w", encoding="utf-8") as f:
                    f.write(f">{study_sequence.name}\n{study_sequence.normalized_sequence}\n")

                seq_meta = study_sequence.to_dict()
                with open(seq_dir / "metadata.json", "w", encoding="utf-8") as f:
                    json.dump(seq_meta, f, sort_keys=True, indent=2)

                # Analysis folder
                with open(analysis_dir / "sequence_analysis.json", "w", encoding="utf-8") as f:
                    json.dump(sequence_analysis_result.to_dict(include_residue_table=False), f, sort_keys=True, indent=2)

                with open(analysis_dir / "residue_table.json", "w", encoding="utf-8") as f:
                    json.dump(sequence_analysis_result.to_table(), f, sort_keys=True, indent=2)

                # 5. Integrity verification before committing
                with open(temp_dir_path / "project.json", "r", encoding="utf-8") as f:
                    json.load(f)
                with open(temp_dir_path / "history.json", "r", encoding="utf-8") as f:
                    json.load(f)

                # 6. Atomic directory swap
                os.replace(str(temp_dir_path), str(final_path))
        except Exception as e:
            # Clean up destination just in case (atomic replacement handles most failure modes)
            if final_path.exists():
                try:
                    shutil.rmtree(final_path)
                except Exception:
                    pass
            raise e

        return self.load_project(str(final_path))

    def load_project(self, project_id_or_name_or_path: str) -> Project:
        target_path = None

        # Check if parameter is a direct path
        path_check = Path(project_id_or_name_or_path)
        if path_check.exists() and path_check.is_dir():
            target_path = path_check.resolve()
        elif project_id_or_name_or_path.endswith("__" + make_safe_slug(project_id_or_name_or_path.split("__")[-1])):
            target_path = (self.projects_dir / project_id_or_name_or_path).resolve()
        else:
            # 1. Attempt ID UUID lookup
            try:
                uuid.UUID(project_id_or_name_or_path)
                # Search folders matching the <UUID>__ suffix
                matching_dirs = []
                for p in self.projects_dir.iterdir():
                    if p.is_dir() and p.name.startswith(project_id_or_name_or_path + "__"):
                        matching_dirs.append(p)
                if len(matching_dirs) == 1:
                    target_path = matching_dirs[0]
            except ValueError:
                pass

        # 2. Attempt unique name-based display lookup
        if target_path is None:
            matching_projects = []
            for p in self.projects_dir.iterdir():
                if p.is_dir() and (p / "project.json").exists():
                    try:
                        with open(p / "project.json", "r", encoding="utf-8") as f:
                            meta = json.load(f)
                            if meta.get("project_name") == project_id_or_name_or_path:
                                matching_projects.append(p)
                    except Exception:
                        pass
            if len(matching_projects) == 1:
                target_path = matching_projects[0]
            elif len(matching_projects) > 1:
                raise ValueError(
                    f"Ambiguous display-name: multiple projects match the name '{project_id_or_name_or_path}'."
                )

        if target_path is None or not target_path.exists():
            raise FileNotFoundError(f"Project not found for lookup: '{project_id_or_name_or_path}'")

        # Path traversal guard
        if self.projects_dir not in target_path.parents and self.projects_dir != target_path:
            raise PermissionError("Access denied: Project path escapes projects directory boundaries.")

        # Read JSON configuration files
        with open(target_path / "project.json", "r", encoding="utf-8") as f:
            meta = json.load(f)
        with open(target_path / "history.json", "r", encoding="utf-8") as f:
            history = json.load(f)

        # 3. Reconstruct StudySequence
        with open(target_path / "sequence" / "metadata.json", "r", encoding="utf-8") as f:
            seq_meta = json.load(f)
        with open(target_path / "sequence" / "primary.fasta", "r", encoding="utf-8") as f:
            fasta_lines = f.readlines()
            raw_seq = "".join([line.strip() for line in fasta_lines if not line.startswith(">")])

        study_sequence = StudySequence(
            raw_sequence=raw_seq,
            fasta_header=seq_meta.get("fasta_header"),
            name=seq_meta.get("name"),
            description=seq_meta.get("description"),
            source=seq_meta.get("source"),
            metadata=seq_meta.get("metadata"),
            study_id=seq_meta.get("study_id")
        )

        # Hash integrity validation
        persisted_hash = meta.get("provenance", {}).get("sequence_hash")
        if study_sequence.sequence_hash != persisted_hash:
            raise ValueError(
                f"Project Integrity Error: Reconstructed sequence hash ({study_sequence.sequence_hash}) "
                f"does not match the persisted sequence hash ({persisted_hash})."
            )

        # 4. Instantiate read-only analysis result view
        with open(target_path / "analysis" / "sequence_analysis.json", "r", encoding="utf-8") as f:
            analysis_data = json.load(f)
        with open(target_path / "analysis" / "residue_table.json", "r", encoding="utf-8") as f:
            residue_table = json.load(f)

        sequence_analysis_result = PersistedSequenceAnalysisResult(analysis_data, residue_table)

        return Project(
            project_id=meta["project_id"],
            project_name=meta["project_name"],
            description=meta["description"],
            created_at=meta["created_at"],
            updated_at=meta["updated_at"],
            project_path=str(target_path),
            primary_study_sequence=study_sequence,
            sequence_analysis_result=sequence_analysis_result,
            atlas_version=meta["atlas_version"],
            coordinate_system=meta["coordinate_system"],
            analysis_version=meta["analysis_version"],
            project_status=meta["project_status"],
            history=history,
            warnings=meta.get("warnings", [])
        )

    def list_projects(self) -> list[dict]:
        summaries = []
        for p in self.projects_dir.iterdir():
            if p.is_dir() and (p / "project.json").exists():
                try:
                    with open(p / "project.json", "r", encoding="utf-8") as f:
                        meta = json.load(f)
                        summaries.append({
                            "project_id": meta["project_id"],
                            "project_name": meta["project_name"],
                            "description": meta["description"],
                            "created_at": meta["created_at"],
                            "updated_at": meta["updated_at"],
                            "project_path": str(p),
                            "project_status": meta["project_status"]
                        })
                except Exception:
                    pass
        return sorted(summaries, key=lambda x: x["created_at"])
