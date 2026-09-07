import os
import re
import json
import uuid
import datetime
import shutil
import tempfile
from pathlib import Path
from engine.project import Project
from engine.case_study_type import CaseStudyType
from engine.persisted_case_study import PersistedCaseStudy
from engine.case_study_update import CaseStudyUpdate
from engine.case_study_status import CaseStudyStatus

def make_safe_slug(name: str) -> str:
    slug = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    slug = re.sub(r'_+', '_', slug)
    slug = slug.strip('_')
    if not slug:
        slug = "case_study"
    return slug

def _to_win_long_path(path: Path) -> Path:
    if not path:
        return path
    if os.name == "nt":
        abs_str = str(path.resolve())
        if not abs_str.startswith("\\\\?\\"):
            if abs_str.startswith("\\\\"):
                return Path("\\\\?\\UNC\\" + abs_str[2:])
            return Path("\\\\?\\" + abs_str)
    return path

class CaseStudyRepository:
    """
    Scientific Service: CaseStudyRepository

    Manages directory-based persistence of CaseStudies within Project folders.
    Ensures path isolation, atomic writes, and history event logging.
    """

    def __init__(self):
        pass

    def _validate_project(self, project) -> Path:
        # Duck typing checks
        if not hasattr(project, "project_id") or not hasattr(project, "project_path") or not hasattr(project, "primary_study_sequence"):
            raise TypeError("project must implement the Project public interface.")
        
        proj_path = Path(project.project_path).resolve()
        case_studies_dir = proj_path / "case_studies"
        case_studies_dir.mkdir(parents=True, exist_ok=True)
        return case_studies_dir

    def _get_safe_path(self, case_studies_dir: Path, case_study_id: str, title: str) -> Path:
        try:
            uuid.UUID(str(case_study_id))
        except ValueError:
            raise ValueError(f"Invalid UUID: {case_study_id}")

        safe_slug = make_safe_slug(title)
        folder_name = f"{case_study_id}__{safe_slug}"
        target_path = (case_studies_dir / folder_name).resolve()

        # Path traversal guard
        if case_studies_dir not in target_path.parents:
            raise PermissionError("Access denied: CaseStudy path escapes project boundaries.")
        return target_path

    def create_case_study(
        self,
        project,
        study_type: CaseStudyType,
        title: str,
        study_id: str = None,
        description: str = None,
        software: str = None,
        software_version: str = None,
        author: str = None,
        parameters: dict = None,
        input_files: list = None,
        provenance: dict = None,
        case_study_id: str = None,
        status: CaseStudyStatus = CaseStudyStatus.ACTIVE
    ) -> PersistedCaseStudy:
        case_studies_dir = self._validate_project(project)

        # 1. Validate study_id matches primary sequence study_id
        primary_study_id = project.primary_study_sequence.study_id
        if study_id is None:
            resolved_study_id = primary_study_id
        else:
            if study_id != primary_study_id:
                raise ValueError(
                    f"study_id ({study_id}) does not match Project primary sequence study_id ({primary_study_id})."
                )
            resolved_study_id = study_id

        # 2. Handle CaseStudy ID
        if case_study_id is not None:
            try:
                uuid.UUID(str(case_study_id))
                cs_id = str(case_study_id)
            except ValueError:
                raise ValueError(f"Invalid case_study_id UUID: {case_study_id}")
        else:
            cs_id = str(uuid.uuid4())

        final_path = self._get_safe_path(case_studies_dir, cs_id, title)
        if final_path.exists():
            raise FileExistsError(f"CaseStudy directory already exists: {final_path}")

        # Ensure no other case study has the same case_study_id in this project
        for cs in self.list_case_studies(project, include_archived=True):
            if cs["case_study_id"] == cs_id:
                raise FileExistsError(f"CaseStudy with ID {cs_id} already exists in this project.")

        # Validate file references structure (ensure stored_in_project is False or handled)
        in_files = []
        if input_files is not None:
            for f in input_files:
                in_files.append({
                    "path": str(f.get("path", "")),
                    "checksum": str(f.get("checksum", "")),
                    "size_bytes": int(f.get("size_bytes", 0)),
                    "stored_in_project": bool(f.get("stored_in_project", False))
                })

        # 3. Create temp directory inside case_studies_dir
        temp_dir_path = None
        try:
            with tempfile.TemporaryDirectory(dir=str(case_studies_dir)) as temp_dir:
                temp_dir_path = Path(temp_dir)
                
                # Create subdirectories
                (temp_dir_path / "inputs").mkdir()
                (temp_dir_path / "results").mkdir()
                (temp_dir_path / "attachments").mkdir()
                (temp_dir_path / "exports").mkdir()

                # Generate event log and metadata
                now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
                
                history = [
                    {
                        "event_id": str(uuid.uuid4()),
                        "event_type": "CASE_STUDY_CREATED",
                        "timestamp": now_str,
                        "case_study_id": cs_id,
                        "details": f"CaseStudy '{title}' created.",
                        "software_version": "1.0",
                        "atlas_version": "3.0"
                    }
                ]
                if len(in_files) > 0:
                    history.append({
                        "event_id": str(uuid.uuid4()),
                        "event_type": "FILE_REFERENCE_ADDED",
                        "timestamp": now_str,
                        "case_study_id": cs_id,
                        "details": f"Imported {len(in_files)} external file reference(s).",
                        "software_version": "1.0",
                        "atlas_version": "3.0"
                    })

                meta = {
                    "case_study_id": cs_id,
                    "project_id": project.project_id,
                    "study_id": resolved_study_id,
                    "study_type": CaseStudyType(study_type).value,
                    "title": title,
                    "description": description if description is not None else "",
                    "created_at": now_str,
                    "updated_at": now_str,
                    "software": software if software is not None else "",
                    "software_version": software_version if software_version is not None else "",
                    "author": author if author is not None else "",
                    "parameters": parameters if parameters is not None else {},
                    "input_files": in_files,
                    "result_files": [],
                    "residue_level_evidence": [],
                    "global_metrics": {},
                    "warnings": [],
                    "provenance": provenance if provenance is not None else {
                        "software_version": "1.0",
                        "schema_version": 1
                    },
                    "archived": status == CaseStudyStatus.ARCHIVED,
                    "status": CaseStudyStatus(status).value,
                    "superseded_by_case_study_id": "",
                    "representative_structure": None
                }

                # 4. Serialize to disk
                with open(temp_dir_path / "metadata.json", "w", encoding="utf-8") as f:
                    json.dump(meta, f, sort_keys=True, indent=2)

                with open(temp_dir_path / "history.json", "w", encoding="utf-8") as f:
                    json.dump(history, f, sort_keys=True, indent=2)

                # 5. Atomic directory replace
                os.replace(str(temp_dir_path), str(final_path))
        except Exception as e:
            if final_path.exists():
                try:
                    shutil.rmtree(final_path)
                except Exception:
                    pass
            raise e

        return self.load_case_study(project, cs_id)

    def load_case_study(self, project, case_study_id_or_path: str) -> PersistedCaseStudy:
        case_studies_dir = self._validate_project(project)
        target_path = None

        path_check = Path(case_study_id_or_path)
        if path_check.exists() and path_check.is_dir():
            target_path = path_check.resolve()
        elif case_study_id_or_path.endswith("__" + make_safe_slug(case_study_id_or_path.split("__")[-1])):
            target_path = (case_studies_dir / case_study_id_or_path).resolve()
        else:
            # Match UUID prefix
            try:
                uuid.UUID(case_study_id_or_path)
                for p in case_studies_dir.iterdir():
                    if p.is_dir() and p.name.startswith(case_study_id_or_path + "__"):
                        target_path = p
                        break
            except ValueError:
                pass

        if target_path is None or not target_path.exists():
            raise FileNotFoundError(f"CaseStudy not found: '{case_study_id_or_path}'")

        # Path traversal guard
        if case_studies_dir not in target_path.parents and case_studies_dir != target_path:
            raise PermissionError("Access denied: CaseStudy directory escapes project bounds.")

        # Read configuration (Read-only)
        with open(target_path / "metadata.json", "r", encoding="utf-8") as f:
            meta = json.load(f)
        with open(target_path / "history.json", "r", encoding="utf-8") as f:
            history = json.load(f)

        # Integrity project mapping check
        if meta["project_id"] != project.project_id:
            raise ValueError(
                f"CaseStudy Project ID mismatch: metadata={meta['project_id']}, project={project.project_id}"
            )

        status_val = meta.get("status", None)
        status = CaseStudyStatus(status_val) if status_val else None
        superseded_by_case_study_id = meta.get("superseded_by_case_study_id", None)
        representative_structure = meta.get("representative_structure", None)

        return PersistedCaseStudy(
            case_study_id=meta["case_study_id"],
            project_id=meta["project_id"],
            study_id=meta["study_id"],
            study_type=CaseStudyType(meta["study_type"]),
            title=meta["title"],
            description=meta["description"],
            created_at=meta["created_at"],
            updated_at=meta["updated_at"],
            software=meta["software"],
            software_version=meta["software_version"],
            author=meta["author"],
            parameters=meta["parameters"],
            input_files=meta["input_files"],
            result_files=meta["result_files"],
            residue_level_evidence=meta["residue_level_evidence"],
            global_metrics=meta["global_metrics"],
            warnings=meta.get("warnings", []),
            provenance=meta["provenance"],
            case_study_path=str(target_path),
            history=history,
            archived=meta.get("archived", False),
            status=status,
            superseded_by_case_study_id=superseded_by_case_study_id,
            representative_structure=representative_structure
        )

    def list_case_studies(self, project, include_archived: bool = False, status: CaseStudyStatus = None) -> list[dict]:
        case_studies_dir = self._validate_project(project)
        summaries = []
        for p in case_studies_dir.iterdir():
            if p.is_dir() and (p / "metadata.json").exists():
                try:
                    with open(p / "metadata.json", "r", encoding="utf-8") as f:
                        meta = json.load(f)
                        is_archived = meta.get("archived", False)
                        status_val = meta.get("status", None)
                        if status_val:
                            cs_status = CaseStudyStatus(status_val)
                        else:
                            cs_status = CaseStudyStatus.ARCHIVED if is_archived else CaseStudyStatus.ACTIVE

                        # Filter by status if requested; otherwise enforce legacy archived exclusion
                        if status is not None:
                            if cs_status != status:
                                continue
                        else:
                            if cs_status == CaseStudyStatus.ARCHIVED and not include_archived:
                                continue

                        summaries.append({
                            "case_study_id": meta["case_study_id"],
                            "project_id": meta["project_id"],
                            "study_id": meta["study_id"],
                            "study_type": meta["study_type"],
                            "title": meta["title"],
                            "description": meta["description"],
                            "created_at": meta["created_at"],
                            "updated_at": meta["updated_at"],
                            "case_study_path": str(p),
                            "archived": cs_status == CaseStudyStatus.ARCHIVED,
                            "status": cs_status.value
                        })
                except Exception:
                    pass
        return sorted(summaries, key=lambda x: x["created_at"])

    def case_study_exists(self, project, case_study_id: str) -> bool:
        try:
            self.load_case_study(project, case_study_id)
            return True
        except Exception:
            return False

    def archive_case_study(self, project, case_study_id: str) -> PersistedCaseStudy:
        cs = self.load_case_study(project, case_study_id)
        if cs.status == CaseStudyStatus.ARCHIVED:
            raise ValueError(f"Case study '{case_study_id}' is already archived.")
        return self.set_status(project, case_study_id, CaseStudyStatus.ARCHIVED, reason="Archived via legacy API")

    def set_status(
        self,
        project,
        case_study_id: str,
        new_status: CaseStudyStatus,
        reason: str = None,
        superseded_by_case_study_id: str = None
    ) -> PersistedCaseStudy:
        cs = self.load_case_study(project, case_study_id)
        current_status = cs.status
        new_status = CaseStudyStatus(new_status)

        # Idempotency
        if current_status == new_status:
            return cs

        # Transition validation
        if current_status == CaseStudyStatus.ARCHIVED:
            raise ValueError("An archived case study cannot transition to any other status.")
        
        if current_status == CaseStudyStatus.SUPERSEDED and new_status == CaseStudyStatus.ACTIVE:
            raise ValueError("A superseded case study cannot transition back to active.")
        
        if current_status == CaseStudyStatus.ACTIVE and new_status == CaseStudyStatus.DRAFT:
            raise ValueError("An active case study cannot transition back to draft.")

        if new_status == CaseStudyStatus.SUPERSEDED:
            if not superseded_by_case_study_id:
                raise ValueError("superseded_by_case_study_id is required to transition to superseded.")
            if superseded_by_case_study_id == cs.case_study_id:
                raise ValueError("A case study cannot supersede itself.")
            if not self.case_study_exists(project, superseded_by_case_study_id):
                raise ValueError(f"Replacement case study '{superseded_by_case_study_id}' not found.")
            
            replacement = self.load_case_study(project, superseded_by_case_study_id)
            if replacement.study_id != cs.study_id:
                raise ValueError("Replacement case study must have the same study_id.")
            if replacement.study_type != cs.study_type:
                raise ValueError("Replacement case study must have the same study_type.")
            if replacement.status != CaseStudyStatus.ACTIVE:
                raise ValueError("Replacement case study must be in status ACTIVE.")

        # Perform atomic update on disk
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        metadata_path = Path(cs.case_study_path) / "metadata.json"
        history_path = Path(cs.case_study_path) / "history.json"

        with open(metadata_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        with open(history_path, "r", encoding="utf-8") as f:
            history = json.load(f)

        meta["status"] = new_status.value
        meta["archived"] = new_status == CaseStudyStatus.ARCHIVED
        meta["updated_at"] = now_str
        
        if new_status == CaseStudyStatus.SUPERSEDED:
            meta["superseded_by_case_study_id"] = superseded_by_case_study_id

        # Map transition history event
        if new_status == CaseStudyStatus.ACTIVE:
            event_type = "CASE_STUDY_ACTIVATED"
            details = f"CaseStudy '{cs.title}' activated."
        elif new_status == CaseStudyStatus.SUPERSEDED:
            event_type = "CASE_STUDY_SUPERSEDED"
            details = f"CaseStudy '{cs.title}' superseded by '{superseded_by_case_study_id}'."
        elif new_status == CaseStudyStatus.ARCHIVED:
            event_type = "CASE_STUDY_ARCHIVED"
            details = f"CaseStudy '{cs.title}' archived."
        else:
            event_type = "CASE_STUDY_STATUS_CHANGED"
            details = f"Status changed from {current_status.value} to {new_status.value}."

        history.append({
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": now_str,
            "case_study_id": cs.case_study_id,
            "details": details,
            "previous_status": current_status.value,
            "new_status": new_status.value,
            "reason": reason if reason else "",
            "superseded_by_case_study_id": superseded_by_case_study_id if superseded_by_case_study_id else "",
            "software_version": "1.0",
            "atlas_version": "3.0"
        })

        temp_meta_path = metadata_path.with_suffix(".tmp")
        temp_hist_path = history_path.with_suffix(".tmp")

        try:
            with open(temp_meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, sort_keys=True, indent=2)
            with open(temp_hist_path, "w", encoding="utf-8") as f:
                json.dump(history, f, sort_keys=True, indent=2)

            os.replace(str(temp_meta_path), str(metadata_path))
            os.replace(str(temp_hist_path), str(history_path))
        except Exception as e:
            if temp_meta_path.exists():
                temp_meta_path.unlink()
            if temp_hist_path.exists():
                temp_hist_path.unlink()
            raise e

        return self.load_case_study(project, cs.case_study_id)

    def add_results(
        self,
        project: Project,
        case_study_id: str,
        update: CaseStudyUpdate
    ) -> PersistedCaseStudy:
        # Load existing case study (performs basic project/bounds checks)
        cs = self.load_case_study(project, case_study_id)
        if cs.status in [CaseStudyStatus.ARCHIVED, CaseStudyStatus.SUPERSEDED]:
            raise ValueError(f"Cannot update CaseStudy '{case_study_id}' in status: {cs.status.value}")

        # Load raw files for in-place atomic updates
        metadata_path = Path(cs.case_study_path) / "metadata.json"
        history_path = Path(cs.case_study_path) / "history.json"

        with open(metadata_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        with open(history_path, "r", encoding="utf-8") as f:
            history = json.load(f)

        # 1. Validation of updates
        # Residue level checks
        for r in update.residue_level_evidence:
            if "position" not in r:
                raise ValueError("Residue level evidence must contain a 'position' integer.")
        
        # Result file reference checks and path isolation
        for rf in update.result_files:
            if "path" not in rf:
                raise ValueError("Result file reference must specify a 'path'.")
            if rf.get("stored_in_project", False):
                resolved_rf = Path(rf["path"]).resolve()
                if Path(project.project_path).resolve() not in resolved_rf.parents:
                    raise PermissionError("Access denied: referenced file escapes project directory boundaries.")

        # Representative structure request processing
        struct_req = update.representative_structure_request
        new_file_created = False
        dest_path = None
        prev_file_to_delete = None
        
        if struct_req is not None:
            source_path_str = struct_req.get("source_path")
            if not source_path_str:
                raise ValueError("representative_structure_request must contain a 'source_path'.")
            
            source_path = Path(source_path_str).resolve()
            if not source_path.exists() or not source_path.is_file():
                raise FileNotFoundError(f"Source structure file not found: '{source_path_str}'")
            
            ext = source_path.suffix.lower()
            if ext not in [".pdb", ".cif"]:
                raise ValueError(f"Unsupported structure file format: {ext}. Only .pdb and .cif are allowed.")
            
            # 1. Calculate checksum and size of source file BEFORE copying (Option A content-addressing)
            import hashlib
            sha256_hash = hashlib.sha256()
            with open(source_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            checksum = sha256_hash.hexdigest()
            size_bytes = source_path.stat().st_size

            # Check if there is an existing identical representative structure registered (idempotency check)
            prev_struct = meta.get("representative_structure")
            if prev_struct and prev_struct.get("checksum_sha256") == checksum:
                same_fields = (
                    prev_struct.get("structure_type") == struct_req.get("structure_type") and
                    prev_struct.get("protein_chain") == struct_req.get("protein_chain") and
                    prev_struct.get("ligand_resname") == struct_req.get("ligand_resname") and
                    prev_struct.get("ligand_chain") == struct_req.get("ligand_chain") and
                    prev_struct.get("ligand_residue_number") == struct_req.get("ligand_residue_number") and
                    prev_struct.get("description", "") == struct_req.get("description", "")
                )
                if same_fields:
                    # Idempotent: return case study unchanged
                    return self.load_case_study(project, cs.case_study_id)

            # Sanitize destination filename with checksum prefix to avoid filename collisions
            safe_stem = make_safe_slug(source_path.stem)
            dest_filename = f"{checksum}___{safe_stem}{ext}"
            
            attachments_dir = Path(cs.case_study_path) / "attachments"
            attachments_dir.mkdir(parents=True, exist_ok=True)
            dest_path = attachments_dir / dest_filename
            
            # Keep previous file reference for deletion after successful commit
            prev_rel_path = prev_struct.get("relative_path") if prev_struct else None
            if prev_rel_path and prev_rel_path != f"attachments/{dest_filename}":
                prev_file_to_delete = Path(cs.case_study_path) / prev_rel_path

            # Copy file only if not already copied on disk
            new_file_created = not _to_win_long_path(dest_path).exists()
            if new_file_created:
                shutil.copy2(_to_win_long_path(source_path), _to_win_long_path(dest_path))
            
            try:
                # Double-check size and checksum of copied file to ensure integrity
                sha256_hash_dest = hashlib.sha256()
                with open(_to_win_long_path(dest_path), "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash_dest.update(byte_block)
                checksum_dest = sha256_hash_dest.hexdigest()
                size_bytes_dest = _to_win_long_path(dest_path).stat().st_size
                
                if checksum_dest != checksum or size_bytes_dest != size_bytes:
                    raise IOError("Copied file integrity check failed (checksum/size mismatch).")
                
                # Construct RepresentativeStructure (validates schema/ligands)
                from engine.representative_structure import RepresentativeStructure
                rep_struct_obj = RepresentativeStructure(
                    relative_path=f"attachments/{dest_filename}",
                    structure_type=struct_req.get("structure_type"),
                    protein_chain=struct_req.get("protein_chain"),
                    checksum_sha256=checksum,
                    size_bytes=size_bytes,
                    ligand_resname=struct_req.get("ligand_resname"),
                    ligand_chain=struct_req.get("ligand_chain"),
                    ligand_residue_number=struct_req.get("ligand_residue_number"),
                    description=struct_req.get("description", "")
                )
                
                # Set in metadata
                meta["representative_structure"] = rep_struct_obj.to_dict()
                
                # Append history event (portable parameters only, no source path)
                history.append({
                    "event_id": str(uuid.uuid4()),
                    "event_type": "REPRESENTATIVE_STRUCTURE_UPDATED",
                    "timestamp": update.created_at,
                    "case_study_id": cs.case_study_id,
                    "details": f"Representative structure updated to 'attachments/{dest_filename}' ({struct_req.get('structure_type')}).",
                    "software_version": "1.0",
                    "atlas_version": "3.0"
                })
                
            except Exception as e:
                # Rollback file copy if validation fails
                if new_file_created and dest_path and _to_win_long_path(dest_path).exists():
                    try:
                        _to_win_long_path(dest_path).unlink()
                    except Exception:
                        pass
                raise e

        # 2. Perform additive merges
        # residue_level_evidence append
        existing_evidence = meta.setdefault("residue_level_evidence", [])
        for e in update.residue_level_evidence:
            record = dict(e)
            record["update_id"] = update.update_id
            record["timestamp"] = update.created_at
            record["source"] = update.source
            record["method"] = update.method
            existing_evidence.append(record)

        # global_metrics key-clash merge (structured records)
        existing_metrics = meta.setdefault("global_metrics", {})
        for k, v in update.global_metrics.items():
            new_record = {
                "value": v,
                "update_id": update.update_id,
                "created_at": update.created_at,
                "source": update.source,
                "method": update.method,
                "method_version": update.method_version
            }
            if k in existing_metrics:
                cur_val = existing_metrics[k]
                if isinstance(cur_val, list):
                    existing_metrics[k] = cur_val + [new_record]
                else:
                    existing_metrics[k] = [cur_val, new_record]
            else:
                existing_metrics[k] = new_record

        # result_files append with automatic provenance fields
        existing_results = meta.setdefault("result_files", [])
        for r_file in update.result_files:
            existing_results.append({
                "path": str(r_file.get("path", "")),
                "checksum": str(r_file.get("checksum", "")),
                "size_bytes": int(r_file.get("size_bytes", 0)),
                "stored_in_project": bool(r_file.get("stored_in_project", False)),
                "update_id": update.update_id,
                "created_at": update.created_at,
                "source": update.source,
                "method": update.method,
                "method_version": update.method_version
            })

        # warnings append (structured warnings records)
        existing_warnings = meta.setdefault("warnings", [])
        for w in update.warnings:
            existing_warnings.append({
                "message": str(w),
                "update_id": update.update_id,
                "created_at": update.created_at,
                "source": update.source
            })

        # notes append
        existing_notes = meta.setdefault("notes", [])
        for n in update.notes:
            existing_notes.append({
                "note": str(n),
                "timestamp": update.created_at,
                "update_id": update.update_id
            })

        # provenance append
        prov = meta.setdefault("provenance", {})
        updates_prov = prov.setdefault("updates", [])
        updates_prov.append({
            "update_id": update.update_id,
            "created_at": update.created_at,
            "source": update.source,
            "method": update.method,
            "method_version": update.method_version,
            "provenance": dict(update.provenance)
        })

        # Update metadata timestamp
        meta["updated_at"] = update.created_at

        # Append history event
        history.append({
            "event_id": str(uuid.uuid4()),
            "event_type": "RESULTS_UPDATED",
            "timestamp": update.created_at,
            "case_study_id": cs.case_study_id,
            "details": f"Imported CaseStudy results payload. Added {len(update.residue_level_evidence)} residue rows and {len(update.result_files)} result files.",
            "software_version": "1.0",
            "atlas_version": "3.0"
        })

        # 3. Write changes atomically using temporary files
        temp_meta = metadata_path.with_suffix(".tmp")
        temp_hist = history_path.with_suffix(".tmp")
 
        try:
            with open(temp_meta, "w", encoding="utf-8") as f:
                json.dump(meta, f, sort_keys=True, indent=2)
            with open(temp_hist, "w", encoding="utf-8") as f:
                json.dump(history, f, sort_keys=True, indent=2)
        except Exception as e:
            if temp_meta.exists():
                temp_meta.unlink()
            if temp_hist.exists():
                temp_hist.unlink()
            # Rollback newly created file if metadata writing failed
            if new_file_created and dest_path and dest_path.exists():
                try:
                    dest_path.unlink()
                except Exception:
                    pass
            raise e

        meta_replaced = False
        try:
            os.replace(str(temp_meta), str(metadata_path))
            meta_replaced = True
            
            os.replace(str(temp_hist), str(history_path))
            
            # Clean up obsolete previous file after successful save
            if prev_file_to_delete and prev_file_to_delete.exists():
                try:
                    prev_file_to_delete.unlink()
                except Exception:
                    pass
        except Exception as e:
            if temp_meta.exists():
                try:
                    temp_meta.unlink()
                except Exception:
                    pass
            if temp_hist.exists():
                try:
                    temp_hist.unlink()
                except Exception:
                    pass
            # Rollback newly created file if metadata writing failed and was NOT committed
            if not meta_replaced and new_file_created and dest_path and dest_path.exists():
                try:
                    dest_path.unlink()
                except Exception:
                    pass
            raise e
 
        return self.load_case_study(project, cs.case_study_id)

    def resolve_representative_structure_path(
        self,
        project,
        case_study_id: str,
    ) -> Path:
        """
        Safely retrieves and resolves the absolute path to the representative structure file,
        applying Windows long-path prefix before checking filesystem existence.
        """
        cs = self.load_case_study(project, case_study_id)
        rep_struct = cs.representative_structure
        if not rep_struct:
            raise ValueError("No representative structure registered for this Case Study.")
            
        # Get path string from dict or value object
        if isinstance(rep_struct, dict):
            rel_path_str = rep_struct.get("relative_path")
        else:
            rel_path_str = getattr(rep_struct, "relative_path", None)
            
        if not rel_path_str:
            raise ValueError("Empty persisted relative path.")
            
        # Lexical validation
        p = Path(rel_path_str)
        if p.is_absolute():
            raise ValueError("Absolute persisted path.")
        if ".." in p.parts:
            raise ValueError("Path traversal component.")
        if not p.parts or p.parts[0] != "attachments":
            raise ValueError("Path outside attachments/.")
        if p.suffix.lower() != ".pdb":
            raise ValueError("Unsupported suffix.")
            
        # Construct path under Case Study folder
        full_path = Path(cs.case_study_path) / p
        
        # Apply Windows long-path handling BEFORE existence checks
        long_path = _to_win_long_path(full_path)
        
        # Check target existence
        if not long_path.exists():
            raise FileNotFoundError(f"Missing file: {rel_path_str}")
        if not long_path.is_file():
            raise ValueError("Target is not a regular file.")
            
        # Canonical containment check (safe for long paths)
        resolved_cs_dir = Path(cs.case_study_path).resolve()
        resolved_file_dir = long_path.resolve()
        
        clean_cs = Path(str(resolved_cs_dir).replace("\\\\?\\", ""))
        clean_file = Path(str(resolved_file_dir).replace("\\\\?\\", ""))
        
        if clean_cs not in clean_file.parents and clean_cs != clean_file:
            raise PermissionError("Containment violation.")
            
        return long_path

