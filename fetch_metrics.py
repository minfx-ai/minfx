#!/usr/bin/env python3
"""
Fetch latest time series data from Minfx/Neptune backend(s).

Takes an experiment identifier (UUID, custom_run_id, or sys/id like "RUN-123")
and one or more tokens, then fetches and displays the latest timestamps for all series.
When multiple backends are provided, compares the data across all backends.

Usage:
    source venv/bin/activate
    python analyze/fetch_metrics.py --token <token> --project <workspace/project> --run <run_id>

Example with single backend:
    python analyze/fetch_metrics.py \\
        --token "TOKEN" \\
        --project "WORKSPACE/PROJECT" \\
        --run "RUN-123"

Example with multiple backends (comma-separated):
    python analyze/fetch_metrics.py \\
        --token "TOKEN1,TOKEN2" \\
        --project "WORKSPACE/PROJECT" \\
        --run "RUN-123"

Example with multiple backends (multiple --token flags):
    python analyze/fetch_metrics.py \\
        --token "TOKEN1" \\
        --token "TOKEN2" \\
        --project "WORKSPACE/PROJECT" \\
        --run "RUN-123"

Example with multiple backends and different projects:
    python analyze/fetch_metrics.py \\
        --token "TOKEN1" \\
        --token "TOKEN2" \\
        --project "WORKSPACE1/PROJECT1" \\
        --project "WORKSPACE2/PROJECT2" \\
        --run "RUN-123"

Example with multiple backends and different runs:
    python analyze/fetch_metrics.py \\
        --token "TOKEN1" \\
        --token "TOKEN2" \\
        --project "WORKSPACE/PROJECT" \\
        --run "RUN-123" \\
        --run "RUN-456"
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from datetime import timezone
from typing import Any
from zoneinfo import ZoneInfo

import minfx.neptune_v2 as neptune
from minfx.neptune_v2 import BackendConfig
from minfx.neptune_v2.internal.credentials import Credentials

# Module logger
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging with appropriate level and format."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def get_backend_url(token: str) -> str:
    """Extract the API URL from a token for display purposes."""
    try:
        creds = Credentials.from_token(token)
        return creds.api_url_opt or creds.token_origin_address
    except Exception:
        return "unknown"


def format_timestamp(timestamp_millis: int) -> str:
    """Format millisecond timestamp as ISO datetime in CET timezone."""
    cet = ZoneInfo("Europe/Berlin")
    dt_utc = datetime.fromtimestamp(timestamp_millis / 1000, tz=timezone.utc)
    dt_cet = dt_utc.astimezone(cet)
    return dt_cet.isoformat(sep=" ")


def get_all_series_paths(structure: dict, prefix: str = "") -> list[tuple[str, str]]:
    """Recursively extract all series paths and their types from the structure.

    Returns list of (path, type_name) tuples.
    """
    results = []
    for key, value in structure.items():
        full_path = f"{prefix}/{key}" if prefix else key
        if isinstance(value, dict):
            # Recurse into nested namespaces
            results.extend(get_all_series_paths(value, full_path))
        else:
            # It's an attribute - get its type name
            type_name = type(value).__name__
            results.append((full_path, type_name))
    return results


def fetch_series_last_entry(run, path: str) -> tuple | None:
    """Fetch the last entry from a series.

    Returns (step, timestamp, value, count) or None if not available.
    """
    try:
        attr = run[path]
        # Check if it's a series type that supports fetch_values
        if hasattr(attr, "fetch_values"):
            logger.debug(f"Fetching values for: {path}")
            df = attr.fetch_values(include_timestamp=True, progress_bar=False)
            if len(df) > 0:
                last_row = df.iloc[-1]
                step = last_row.get("step")
                timestamp = last_row.get("timestamp")
                value = last_row.get("value")
                # Convert timestamp to milliseconds if it's a datetime
                ts_millis = None
                if timestamp is not None:
                    if hasattr(timestamp, "timestamp"):
                        ts_millis = int(timestamp.timestamp() * 1000)
                    else:
                        ts_millis = int(timestamp)
                logger.debug(f"  -> {len(df)} entries, last at step {step}")
                return (step, ts_millis, value, len(df))
    except Exception as e:
        logger.warning(f"Could not fetch {path}: {e}")
    return None


def fetch_all_series_from_run(run) -> dict[str, tuple[float, int, Any, int, str]]:
    """Fetch all series data from a run.

    Returns dict mapping path -> (step, timestamp_millis, value, count, type).
    """
    logger.info("Fetching run structure...")
    structure = run.get_structure()

    all_paths = get_all_series_paths(structure)
    logger.info(f"Found {len(all_paths)} total attributes")

    # Filter to only series types
    series_types = {"FloatSeries", "StringSeries"}
    series_paths = [(p, t) for p, t in all_paths if t in series_types]
    logger.info(f"Found {len(series_paths)} series attributes to fetch")

    results = {}
    for i, (path, attr_type) in enumerate(series_paths):
        logger.info(f"[{i+1}/{len(series_paths)}] Fetching: {path}")
        entry = fetch_series_last_entry(run, path)
        if entry:
            step, ts_millis, value, count = entry
            results[path] = (step, ts_millis, value, count, attr_type)

    logger.info(f"Successfully fetched {len(results)} series with data")
    return results


def compare_backends_data(
    all_data: dict[str, dict[str, tuple]], backend_names: list[str]
) -> list[dict]:
    """Compare data across multiple backends.

    Args:
        all_data: Dict mapping backend_name -> {path -> (step, ts, value, count, type)}
        backend_names: List of backend names in order.

    Returns:
        List of comparison dicts with differences highlighted.
    """
    # Collect all unique paths
    all_paths = set()
    for data in all_data.values():
        all_paths.update(data.keys())

    comparisons = []
    for path in sorted(all_paths):
        comparison = {"path": path, "backends": {}, "match": True}

        values_seen = []
        for name in backend_names:
            data = all_data.get(name, {})
            if path in data:
                step, ts_millis, value, count, attr_type = data[path]
                comparison["backends"][name] = {
                    "step": step,
                    "timestamp_millis": ts_millis,
                    "value": value,
                    "count": count,
                    "type": attr_type,
                }
                values_seen.append((step, ts_millis, value, count))
            else:
                comparison["backends"][name] = None
                comparison["match"] = False

        # Check if all backends have same data
        if len(values_seen) > 1 and comparison["match"]:
            first = values_seen[0]
            for other in values_seen[1:]:
                if first != other:
                    comparison["match"] = False
                    break

        comparisons.append(comparison)

    return comparisons


def main():
    parser = argparse.ArgumentParser(
        description="Fetch latest time series data from Minfx/Neptune server(s)"
    )
    parser.add_argument(
        "--token",
        "-t",
        action="append",
        required=True,
        help="Base64-encoded Neptune API token (can be specified multiple times, "
        "or use comma-separated tokens)",
    )
    parser.add_argument(
        "--project",
        "-p",
        action="append",
        required=True,
        help="Project identifier (e.g., 'workspace/project'). Can be specified once "
        "for all backends, or once per backend to use different projects.",
    )
    parser.add_argument(
        "--run",
        "-r",
        action="append",
        required=True,
        help="Run identifier (UUID, custom_run_id, or sys/id like 'RUN-13'). "
        "Can be specified once for all backends, or once per backend to use different runs.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose output",
    )
    args = parser.parse_args()

    # Setup logging based on verbosity
    setup_logging(verbose=args.verbose)

    # Parse all tokens (handle comma-separated and multiple --token flags)
    all_tokens = []
    for token_arg in args.token:
        # Split by comma for comma-separated tokens
        for token in token_arg.split(","):
            token = token.strip()
            if token:
                all_tokens.append(token)

    if not all_tokens:
        logger.error("No valid tokens provided")
        sys.exit(1)

    # Parse all projects
    all_projects = []
    for project_arg in args.project:
        project = project_arg.strip()
        if project:
            all_projects.append(project)

    if not all_projects:
        logger.error("No valid projects provided")
        sys.exit(1)

    # Validate project count: either 1 (used for all) or matches token count
    if len(all_projects) == 1:
        # Use same project for all backends
        all_projects = all_projects * len(all_tokens)
    elif len(all_projects) != len(all_tokens):
        logger.error(
            f"Project count ({len(all_projects)}) must be 1 or match "
            f"token count ({len(all_tokens)})"
        )
        sys.exit(1)

    # Parse all runs (handle comma-separated and multiple --run flags)
    all_runs = []
    for run_arg in args.run:
        for run_id in run_arg.split(","):
            run_id = run_id.strip()
            if run_id:
                all_runs.append(run_id)

    if not all_runs:
        logger.error("No valid runs provided")
        sys.exit(1)

    # Validate run count: either 1 (used for all) or matches token count
    if len(all_runs) == 1:
        # Use same run for all backends
        all_runs = all_runs * len(all_tokens)
    elif len(all_runs) != len(all_tokens):
        logger.error(
            f"Run count ({len(all_runs)}) must be 1 or match "
            f"token count ({len(all_tokens)})"
        )
        sys.exit(1)

    # Format runs display
    unique_runs = list(dict.fromkeys(all_runs))
    runs_display = unique_runs[0] if len(unique_runs) == 1 else ", ".join(all_runs)
    logger.info(f"Starting fetch_metrics for run(s): {runs_display}")
    logger.info(f"Number of backends: {len(all_tokens)}")

    # Show backend URLs, projects and runs
    for i, (token, project, run_id) in enumerate(
        zip(all_tokens, all_projects, all_runs)
    ):
        url = get_backend_url(token)
        logger.info(f"  Backend {i}: {url} -> {project} -> {run_id}")

    logger.info("")

    # Create backend configs with projects and runs
    backends = [
        (BackendConfig(api_token=token), project, run_id)
        for token, project, run_id in zip(all_tokens, all_projects, all_runs)
    ]

    # Fetch data from each backend separately
    # (with_id is not supported with multiple backends, so we connect one at a time)
    all_backend_data = {}
    backend_names = []
    backend_runs = {}

    for i, (backend_config, project, run_id) in enumerate(backends):
        backend_url = get_backend_url(backend_config.api_token)
        backend_name = f"backend_{i}"

        logger.info(
            f"[{backend_name}] Connecting to {backend_url} ({project}, {run_id})..."
        )

        try:
            run = neptune.init_run(
                with_id=run_id,
                project=project,
                backends=[backend_config],
                mode="read-only",
                capture_stdout=False,
                capture_stderr=False,
                capture_hardware_metrics=False,
                capture_traceback=False,
            )
            logger.info(f"[{backend_name}] Connected successfully")
        except Exception as e:
            logger.error(f"[{backend_name}] Failed to connect: {e}")
            continue

        try:
            data = fetch_all_series_from_run(run)
            all_backend_data[backend_name] = data
            backend_names.append(backend_name)
            backend_runs[backend_name] = run_id
            logger.info(f"[{backend_name}] Fetched {len(data)} series")
        except Exception as e:
            logger.error(f"[{backend_name}] Error fetching data: {e}")
        finally:
            logger.info(f"[{backend_name}] Closing connection...")
            run.stop()
            logger.info(f"[{backend_name}] Done")

        logger.info("")

    if not all_backend_data:
        logger.error("No data retrieved from any backend")
        sys.exit(1)

    # Output results
    if len(all_backend_data) == 1:
        # Single backend - simple output
        backend_name = list(all_backend_data.keys())[0]
        data = all_backend_data[backend_name]
        output_single_backend(
            args, data, backend_name, all_projects[0], backend_runs[backend_name]
        )
    else:
        # Multiple backends - comparison output
        output_multi_backend_comparison(
            args, all_backend_data, backend_names, all_projects, backend_runs
        )


def output_single_backend(
    args, data: dict, backend_name: str, project: str, run_id: str
) -> None:
    """Output results for a single backend."""
    # Convert to list and sort by timestamp
    results = []
    for path, (step, ts_millis, value, count, attr_type) in data.items():
        ts_str = format_timestamp(ts_millis) if ts_millis else "N/A"
        results.append((path, ts_str, ts_millis or 0, step, value, count, attr_type))

    results.sort(key=lambda x: x[2], reverse=True)

    if args.json:
        output = {
            "project": project,
            "run_id": run_id,
            "backend": backend_name,
            "total_series": len(results),
            "series": [
                {
                    "path": path,
                    "last_timestamp": ts_str,
                    "timestamp_millis": ts_millis,
                    "step": step,
                    "value": value,
                    "entry_count": count,
                    "type": attr_type,
                }
                for path, ts_str, ts_millis, step, value, count, attr_type in results
            ],
        }
        logger.info(json.dumps(output, indent=2, default=str))
    else:
        logger.info("=" * 115)
        logger.info(f"Project: {project}")
        logger.info(f"Run: {run_id}")
        logger.info(f"Backend: {backend_name}")
        logger.info(f"Total series: {len(results)}")
        logger.info("=" * 115)
        logger.info("")
        logger.info("LAST LOGGED ENTRIES (sorted by timestamp, most recent first):")
        logger.info("-" * 115)
        logger.info(
            f"{'Series Path':<55} {'Last Timestamp':<35} {'Step':<10} {'Value':<15} {'Count'}"
        )
        logger.info("-" * 115)

        for path, ts_str, _, step, value, count, attr_type in results:
            val_str = format_value(value)
            step_str = format_step(step)
            path_display = path if len(path) <= 55 else "..." + path[-52:]
            logger.info(
                f"{path_display:<55} {ts_str:<35} {step_str:<10} {val_str:<15} {count}"
            )

        logger.info("-" * 115)

        if results:
            latest = results[0]
            logger.info("")
            logger.info("OVERALL LAST LOGGED ENTRY:")
            logger.info(f"  Path: {latest[0]}")
            logger.info(f"  Timestamp: {latest[1]}")
            logger.info(f"  Step: {latest[3]}")
            logger.info(f"  Value: {latest[4]}")


def output_multi_backend_comparison(
    args,
    all_data: dict[str, dict],
    backend_names: list[str],
    projects: list[str],
    backend_runs: dict[str, str],
) -> None:
    """Output comparison results for multiple backends."""
    comparisons = compare_backends_data(all_data, backend_names)

    # Count matches and mismatches
    matches = sum(1 for c in comparisons if c["match"])
    mismatches = len(comparisons) - matches

    # Format projects display
    unique_projects = list(dict.fromkeys(projects))  # Remove duplicates, preserve order
    if len(unique_projects) == 1:
        projects_display = unique_projects[0]
    else:
        projects_display = ", ".join(
            f"{name}:{proj}" for name, proj in zip(backend_names, projects)
        )

    # Format runs display
    runs_list = [backend_runs[name] for name in backend_names]
    unique_runs = list(dict.fromkeys(runs_list))
    if len(unique_runs) == 1:
        runs_display = unique_runs[0]
    else:
        runs_display = ", ".join(
            f"{name}:{backend_runs[name]}" for name in backend_names
        )

    if args.json:
        output = {
            "projects": projects,
            "runs": backend_runs,
            "backends": backend_names,
            "total_series": len(comparisons),
            "matching": matches,
            "mismatches": mismatches,
            "comparisons": comparisons,
        }
        logger.info(json.dumps(output, indent=2, default=str))
    else:
        logger.info("=" * 115)
        logger.info(f"Project(s): {projects_display}")
        logger.info(f"Run(s): {runs_display}")
        logger.info(f"Backends compared: {', '.join(backend_names)}")
        logger.info(f"Total series: {len(comparisons)}")
        logger.info(f"Matching: {matches}")
        logger.info(f"Mismatches: {mismatches}")
        logger.info("=" * 115)
        logger.info("")

        if mismatches > 0:
            logger.info("MISMATCHED SERIES:")
            logger.info("-" * 115)
            for comp in comparisons:
                if not comp["match"]:
                    logger.info(f"\n  Path: {comp['path']}")
                    for name in backend_names:
                        backend_data = comp["backends"].get(name)
                        if backend_data:
                            ts_str = (
                                format_timestamp(backend_data["timestamp_millis"])
                                if backend_data["timestamp_millis"]
                                else "N/A"
                            )
                            logger.info(
                                f"    [{name}] step={backend_data['step']}, "
                                f"ts={ts_str}, "
                                f"value={format_value(backend_data['value'])}, "
                                f"count={backend_data['count']}"
                            )
                        else:
                            logger.info(f"    [{name}] NOT PRESENT")
            logger.info("-" * 115)
            logger.info("")

        logger.info("ALL SERIES (sorted by path):")
        logger.info("-" * 130)
        logger.info(
            f"{'Series Path':<50} {'Match':<6} {'Last Timestamp':<35} {'Step':<10} {'Value':<15} {'Count'}"
        )
        logger.info("-" * 130)

        for comp in sorted(comparisons, key=lambda x: x["path"]):
            path = comp["path"]
            path_display = path if len(path) <= 50 else "..." + path[-47:]

            if comp["match"]:
                # Get data from first backend (all are the same)
                first_backend = next(
                    (name for name in backend_names if comp["backends"].get(name)),
                    None,
                )
                if first_backend:
                    data = comp["backends"][first_backend]
                    ts_str = (
                        format_timestamp(data["timestamp_millis"])
                        if data["timestamp_millis"]
                        else "N/A"
                    )
                    step_str = format_step(data["step"])
                    val_str = format_value(data["value"])
                    logger.info(
                        f"{path_display:<50} {'YES':<6} {ts_str:<35} {step_str:<10} {val_str:<15} {data['count']}"
                    )
            else:
                # Mismatched - details shown above
                logger.info(f"{path_display:<50} {'NO':<6} {'(see above)':<35}")

        logger.info("-" * 130)


def format_value(value) -> str:
    """Format a value for display."""
    if isinstance(value, float):
        return f"{value:.6f}"
    elif isinstance(value, str):
        return repr(value[:12]) + "..." if len(value) > 12 else repr(value)
    else:
        return str(value)


def format_step(step) -> str:
    """Format a step value for display."""
    if isinstance(step, (int, float)) and step is not None:
        return f"{step:.0f}"
    return str(step)


if __name__ == "__main__":
    main()
