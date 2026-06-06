from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path


STAGE_ID = "0954I_LEGACY_CARD_UPDATES_ART_RENDER_BLOCK_INACTIVE_SMOKE"
STAGE_TYPE = "legacy_card_updates_art_render_block_inactive_smoke_only"
PASS_STATUS = "LEGACY_CARD_UPDATES_ART_RENDER_BLOCK_INACTIVE_SMOKE_PASS"
NEXT_STAGE = "0954J_LEGACY_CARD_UPDATES_ART_RENDER_BLOCK_INACTIVE_SEAL"
PY_OK = "ALL_0954I_LEGACY_CARD_UPDATES_ART_RENDER_BLOCK_INACTIVE_SMOKE_CHECKS_OK"
PACKAGE_MANIFEST = "docs/audit_packages/legacy_card_updates_to_art_render_block_inactive_smoke_0954I_manifest.json"
ZIP_PATH = "docs/audit_packages/legacy_card_updates_to_art_render_block_inactive_smoke_0954I.zip"

REQUIRED_FILES = [
    "docs/audit/legacy_card_updates_to_art_render_block_inactive_smoke_0954I_report.md",
    "docs/audit/legacy_card_updates_to_art_render_block_inactive_smoke_0954I_result.json",
    "docs/audit/legacy_card_updates_to_art_render_block_inactive_smoke_0954I_checklist.json",
    "scripts/validate_legacy_card_updates_to_art_render_block_inactive_smoke_0954I.py",
    PACKAGE_MANIFEST,
]

SOURCE_FILES = [
    "compatibility/card_updates/legacy_card_updates_art_render_block_inactive_apply_0954H.json",
    "compatibility/card_updates/legacy_card_updates_art_render_block_inactive_apply_manifest_0954H.json",
    "subject_packs/art/render_plans/inactive_art_render_plan_0954H_qinglv_legacy_compat.json",
    "docs/audit/legacy_card_updates_to_art_render_block_inactive_apply_0954H_result.json",
    "docs/audit_packages/legacy_card_updates_to_art_render_block_inactive_apply_0954H_manifest.json",
    "frontend/workbench/fixtures/agent_output_existing_workbench_fixture_0952F_R1.js",
    "frontend/workbench/fixtures/provider_candidate_patch_0952G_R1.js",
    "platform_core/render_blocks/render_block_type_schema_0954C.json",
    "subject_packs/art/topic_contexts/qinglv_china_color_topic_context_0954E.json",
]

MUST_BE_TRUE = [
    "inactive_apply_asset_loaded",
    "legacy_card_blocks_verified",
    "candidate_patch_block_verified",
    "review_gate_block_verified",
    "status_summary_block_verified",
    "inactive_art_render_plan_verified",
    "actions_inert_verified",
    "provider_called_in_source_fixture",
]

MUST_BE_FALSE = [
    "compatibility_runtime_imported",
    "component_grid_behavior_changed",
    "provider_called",
    "provider_called_in_0954I",
    "legacy_0952f_files_moved",
    "legacy_0952g_files_moved",
    "frontend_modified",
    "index_html_modified",
    "existing_frontend_runtime_modified",
    "backend_modified",
    "endpoint_created",
    "memory_read",
    "memory_write",
    "feishu_writeback",
    "formal_scoring",
    "formal_export",
    "server_deploy",
    "seal_performed",
    "seal_allowed",
]

RUNTIME_FILES_TO_SCAN = [
    "frontend/workbench/index.html",
    "frontend/workbench/workbench_dynamic_cards_v1.js",
    "frontend/workbench/workbench_agent_runtime_client_v1.js",
    "frontend/workbench/agent_output_to_existing_workbench_adapter_0952F_R1.js",
    "backend/xiaobei_ai/workbench_agent_runtime.py",
]

FORBIDDEN_RUNTIME_REFS = [
    "legacy_card_updates_to_art_render_block_inactive_smoke_0954I",
    "validate_legacy_card_updates_to_art_render_block_inactive_smoke_0954I",
]

FORBIDDEN_ZIP_PATTERNS = [
    re.compile(r"(^|/)\.env($|[./_-])", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"student[_-]?private", re.IGNORECASE),
    re.compile(r"真实学生数据"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=None)
    return parser.parse_args()


def get_root() -> Path:
    args = parse_args()
    if args.root:
        return Path(args.root).resolve()
    return Path(__file__).resolve().parents[1]


ROOT = get_root()


def read_json(relative_path: str) -> dict:
    with (ROOT / relative_path).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise AssertionError(f"{relative_path} must contain a JSON object")
    return value


def normalize_newlines(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def bytes_match_manifest(path: Path, expected_sha: str, expected_size: int) -> bool:
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() == expected_sha and len(data) == expected_size:
        return True
    return hashlib.sha256(normalize_newlines(data)).hexdigest() == expected_sha


def assert_files_exist() -> None:
    for relative_path in [*REQUIRED_FILES, *SOURCE_FILES]:
        if not (ROOT / relative_path).is_file():
            raise AssertionError(f"missing file: {relative_path}")
    if not (ROOT / ZIP_PATH).is_file():
        raise AssertionError(f"missing zip: {ZIP_PATH}")


def assert_result() -> None:
    result = read_json("docs/audit/legacy_card_updates_to_art_render_block_inactive_smoke_0954I_result.json")
    if result.get("stage_id") != STAGE_ID:
        raise AssertionError("stage_id mismatch")
    if result.get("stage_type") != STAGE_TYPE:
        raise AssertionError("stage_type mismatch")
    if result.get("previous_stage") != "0954H_LEGACY_CARD_UPDATES_ART_RENDER_BLOCK_INACTIVE_APPLY":
        raise AssertionError("previous_stage mismatch")
    if result.get("previous_status") != "LEGACY_CARD_UPDATES_ART_RENDER_BLOCK_INACTIVE_APPLY_PASS":
        raise AssertionError("previous_status mismatch")
    for key in MUST_BE_TRUE:
        if result.get(key) is not True:
            raise AssertionError(f"{key} must be true")
    for key in MUST_BE_FALSE:
        if result.get(key) is not False:
            raise AssertionError(f"{key} must be false")
    expected_counts = {
        "legacy_card_block_count": 12,
        "candidate_patch_block_count": 1,
        "review_gate_block_count": 1,
        "status_summary_block_count": 1,
    }
    for key, expected in expected_counts.items():
        if result.get(key) != expected:
            raise AssertionError(f"{key} mismatch")
    if result.get("inactive_art_render_plan_id") != "inactive_art_render_plan_0954H_qinglv_legacy_compat":
        raise AssertionError("inactive_art_render_plan_id mismatch")
    if result.get("final_status") != PASS_STATUS:
        raise AssertionError("final_status mismatch")
    if result.get("recommended_next_stage") != NEXT_STAGE:
        raise AssertionError("recommended_next_stage mismatch")


def assert_actions_inert(actions: list, label: str) -> None:
    for action in actions:
        if not isinstance(action, dict):
            raise AssertionError(f"{label} action must be object")
        if action.get("enabled") is not False:
            raise AssertionError(f"{label} action enabled must be false")
        if action.get("executes_runtime") is not False:
            raise AssertionError(f"{label} action executes_runtime must be false")
        if action.get("inert_descriptor") is not True:
            raise AssertionError(f"{label} action inert_descriptor must be true")


def assert_0954h_asset_smoke() -> None:
    asset = read_json("compatibility/card_updates/legacy_card_updates_art_render_block_inactive_apply_0954H.json")
    if asset.get("stage_id") != "0954H_LEGACY_CARD_UPDATES_ART_RENDER_BLOCK_INACTIVE_APPLY":
        raise AssertionError("0954H asset stage_id mismatch")
    for key in [
        "compatibility_runtime_imported",
        "component_grid_behavior_changed",
        "provider_called",
        "endpoint_created",
        "memory_read",
        "memory_write",
        "feishu_writeback",
        "formal_export",
        "seal_allowed",
        "legacy_0952f_files_moved",
        "legacy_0952g_files_moved",
    ]:
        if asset.get(key) is not False:
            raise AssertionError(f"0954H asset {key} must be false")
    blocks = asset.get("legacy_card_blocks")
    if not isinstance(blocks, list) or len(blocks) != 12:
        raise AssertionError("0954H asset must contain 12 legacy_card_block entries")
    for block in blocks:
        if block.get("block_type") != "legacy_card_block":
            raise AssertionError("legacy block type mismatch")
        assert_actions_inert(block.get("actions", []), block.get("block_id", "legacy_card_block"))
    candidate = asset.get("candidate_patch_block", {})
    if candidate.get("block_type") != "candidate_patch_block":
        raise AssertionError("candidate_patch_block missing")
    if candidate.get("source", {}).get("provider_called_in_source_fixture") is not True:
        raise AssertionError("source fixture provider flag missing")
    if candidate.get("source", {}).get("provider_called_in_0954H") is not False:
        raise AssertionError("0954H provider flag must be false")
    assert_actions_inert(candidate.get("actions", []), "candidate_patch_block")
    gate = asset.get("review_gate_block", {})
    if gate.get("block_type") != "review_gate_block":
        raise AssertionError("review_gate_block missing")
    assert_actions_inert(gate.get("actions", []), "review_gate_block")
    status = asset.get("status_summary_block", {})
    if status.get("block_type") != "status_summary_block":
        raise AssertionError("status_summary_block missing")
    if status.get("content", {}).get("legacy_card_block_count") != 12:
        raise AssertionError("status summary count mismatch")


def assert_plan_and_sources() -> None:
    plan = read_json("subject_packs/art/render_plans/inactive_art_render_plan_0954H_qinglv_legacy_compat.json")
    if plan.get("plan_id") != "inactive_art_render_plan_0954H_qinglv_legacy_compat":
        raise AssertionError("plan_id mismatch")
    counts = plan.get("render_block_counts", {})
    if counts.get("legacy_card_block") != 12 or counts.get("candidate_patch_block") != 1:
        raise AssertionError("render plan count mismatch")
    for key in ["compatibility_runtime_imported", "runtime_connected", "component_grid_behavior_changed", "provider_called", "endpoint_created", "memory_read", "memory_write", "feishu_writeback", "formal_export", "seal_allowed"]:
        if plan.get(key) is not False:
            raise AssertionError(f"render plan {key} must be false")
    h_result = read_json("docs/audit/legacy_card_updates_to_art_render_block_inactive_apply_0954H_result.json")
    if h_result.get("final_status") != "LEGACY_CARD_UPDATES_ART_RENDER_BLOCK_INACTIVE_APPLY_PASS":
        raise AssertionError("0954H result final_status mismatch")
    h_manifest = read_json("docs/audit_packages/legacy_card_updates_to_art_render_block_inactive_apply_0954H_manifest.json")
    if h_manifest.get("stage_id") != "0954H_LEGACY_CARD_UPDATES_ART_RENDER_BLOCK_INACTIVE_APPLY":
        raise AssertionError("0954H package manifest stage mismatch")


def run_static_checks() -> None:
    subprocess.run([sys.executable, "-m", "py_compile", str(ROOT / "scripts/validate_legacy_card_updates_to_art_render_block_inactive_smoke_0954I.py")], check=True, cwd=ROOT)
    for relative_path in [
        "frontend/workbench/fixtures/agent_output_existing_workbench_fixture_0952F_R1.js",
        "frontend/workbench/fixtures/provider_candidate_patch_0952G_R1.js",
    ]:
        subprocess.run(["node", "--check", str(ROOT / relative_path)], check=True, cwd=ROOT)


def assert_runtime_not_imported() -> None:
    for relative_path in RUNTIME_FILES_TO_SCAN:
        path = ROOT / relative_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for ref in FORBIDDEN_RUNTIME_REFS:
            if ref in text:
                raise AssertionError(f"runtime file references 0954I smoke: {relative_path} -> {ref}")


def assert_report() -> None:
    report = (ROOT / "docs/audit/legacy_card_updates_to_art_render_block_inactive_smoke_0954I_report.md").read_text(encoding="utf-8")
    for phrase in [
        "smoke-only validation",
        "does not execute runtime",
        "12 `legacy_card_block`",
        "provider_called_in_source_fixture=true",
        PY_OK,
    ]:
        if phrase not in report:
            raise AssertionError(f"report missing phrase: {phrase}")


def assert_zip_path_safe(name: str) -> None:
    if "\\" in name:
        raise AssertionError(f"zip path must use forward slashes: {name}")
    if name.startswith("/") or re.match(r"^[A-Za-z]:", name):
        raise AssertionError(f"zip path must be relative: {name}")
    parts = name.split("/")
    if ".." in parts or any(part == "" for part in parts):
        raise AssertionError(f"zip path must not contain empty or parent segments: {name}")
    for pattern in FORBIDDEN_ZIP_PATTERNS:
        if pattern.search(name):
            raise AssertionError(f"zip contains forbidden path pattern: {name}")


def assert_zip_manifest(expected_files: list[str]) -> None:
    manifest = read_json(PACKAGE_MANIFEST)
    if manifest.get("stage_id") != STAGE_ID:
        raise AssertionError("package manifest stage_id mismatch")
    if manifest.get("package_type") != "github_review_audit_package":
        raise AssertionError("package_type mismatch")
    files = manifest.get("files")
    if not isinstance(files, list):
        raise AssertionError("manifest files must be list")
    manifest_paths = {item.get("path") for item in files}
    expected_paths = set(expected_files)
    if manifest_paths != expected_paths:
        raise AssertionError(f"manifest paths mismatch: {sorted(manifest_paths ^ expected_paths)}")
    entries = {}
    for item in files:
        path = item.get("path")
        assert_zip_path_safe(path)
        entries[path] = item
        if path == PACKAGE_MANIFEST and item.get("sha256") == "SELF_REFERENTIAL_MANIFEST":
            continue
        full = ROOT / path
        if not bytes_match_manifest(full, item.get("sha256"), item.get("size_bytes")):
            raise AssertionError(f"manifest sha256 mismatch: {path}")
    with zipfile.ZipFile(ROOT / ZIP_PATH, "r") as archive:
        names = set(archive.namelist())
        for name in names:
            assert_zip_path_safe(name)
        if names != manifest_paths:
            raise AssertionError(f"zip/manifest path mismatch: {sorted(names ^ manifest_paths)}")
        for name in names:
            entry = entries[name]
            data = archive.read(name)
            if name == PACKAGE_MANIFEST and entry.get("sha256") == "SELF_REFERENTIAL_MANIFEST":
                continue
            if entry.get("sha256") != hashlib.sha256(data).hexdigest():
                raise AssertionError(f"zip sha256 mismatch: {name}")
            if entry.get("size_bytes") != len(data):
                raise AssertionError(f"zip size mismatch: {name}")
    if manifest.get("zip_self_entry_count") != len(expected_paths):
        raise AssertionError("zip_self_entry_count mismatch")


def main() -> int:
    try:
        assert_files_exist()
        assert_result()
        assert_0954h_asset_smoke()
        assert_plan_and_sources()
        run_static_checks()
        assert_runtime_not_imported()
        assert_report()
        assert_zip_manifest([*REQUIRED_FILES, *SOURCE_FILES])
    except Exception as exc:
        print(f"0954I_VALIDATION_FAILED: {exc}", file=sys.stderr)
        return 1
    print(PY_OK)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
