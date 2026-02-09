"""Samma Suit CLI — scan skills, verify manifests, check versions.

Usage:
    samma scan <path>           Scan a skill directory or file for security issues
    samma scan-clawhub <slug>   Fetch and scan a ClawHub skill package
    samma verify <path>         Verify a SKILL.md manifest
    samma version               Print version
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import urllib.request
import zipfile
from io import BytesIO
from pathlib import Path

from samma._version import __version__
from samma.sangha.scanner import (
    Finding,
    ScanResult,
    Severity,
    scan_path,
    verify_manifest,
)

# ── Colors ──

_COLORS = {
    Severity.CRITICAL: "\033[91m",  # red
    Severity.HIGH: "\033[93m",      # yellow
    Severity.MEDIUM: "\033[33m",    # orange-ish
    Severity.LOW: "\033[36m",       # cyan
    Severity.INFO: "\033[90m",      # gray
}
_RESET = "\033[0m"
_BOLD = "\033[1m"
_GREEN = "\033[92m"
_RED = "\033[91m"


def _color(severity: Severity) -> str:
    if not sys.stdout.isatty():
        return ""
    return _COLORS.get(severity, "")


def _r() -> str:
    return _RESET if sys.stdout.isatty() else ""


def _b() -> str:
    return _BOLD if sys.stdout.isatty() else ""


# ── Output formatting ──

def _print_finding(f: Finding) -> None:
    sev = f"{_color(f.severity)}{f.severity.value.upper():>8}{_r()}"
    print(f"  {sev}  {f.description}")
    print(f"           {f.file}:{f.line}")
    print(f"           {f.snippet}")
    print()


def _print_result(result: ScanResult) -> None:
    if result.error:
        print(f"{_RED if sys.stdout.isatty() else ''}ERROR: {result.error}{_r()}")
        return

    summary = result.summary()

    print(f"\n{_b()}SANGHA Scan: {result.path}{_r()}")
    print(f"  Files scanned: {summary['files_scanned']}")
    print(f"  Code blocks extracted: {summary['code_blocks_extracted']}")
    print(f"  Total findings: {summary['total_findings']}")

    if result.findings:
        print()
        # Sort by severity (critical first)
        severity_order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
        sorted_findings = sorted(result.findings, key=lambda f: severity_order.index(f.severity))
        for f in sorted_findings:
            _print_finding(f)

    if summary["passed"]:
        status = f"{_GREEN if sys.stdout.isatty() else ''}PASSED{_r()}"
    else:
        status = f"{_RED if sys.stdout.isatty() else ''}FAILED{_r()}"
    print(f"  Result: {status}")
    print()


def _print_result_json(result: ScanResult) -> None:
    summary = result.summary()
    summary["findings_detail"] = [
        {
            "severity": f.severity.value,
            "pattern": f.pattern,
            "description": f.description,
            "file": f.file,
            "line": f.line,
            "snippet": f.snippet,
        }
        for f in result.findings
    ]
    if result.error:
        summary["error"] = result.error
    print(json.dumps(summary, indent=2))


# ── Commands ──

def cmd_scan(args: argparse.Namespace) -> int:
    path = Path(args.path).resolve()
    result = scan_path(path)

    if args.json:
        _print_result_json(result)
    else:
        _print_result(result)

    return 0 if result.passed else 1


def cmd_scan_clawhub(args: argparse.Namespace) -> int:
    slug = args.slug
    # ClawHub packages are at https://clawhub.ai/{owner}/{name}
    # ZIP download convention: https://clawhub.ai/{slug}/archive/main.zip
    url = f"https://clawhub.ai/{slug}/archive/main.zip"

    if not args.json:
        print(f"\n{_b()}Fetching {slug} from ClawHub...{_r()}")

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "samma-cli/" + __version__})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
    except Exception as e:
        if args.json:
            print(json.dumps({"error": f"Failed to fetch {slug}: {e}", "passed": False}))
        else:
            print(f"ERROR: Failed to fetch {slug} from ClawHub: {e}")
        return 1

    with tempfile.TemporaryDirectory(prefix="samma-scan-") as tmpdir:
        try:
            with zipfile.ZipFile(BytesIO(data)) as zf:
                zf.extractall(tmpdir)
        except zipfile.BadZipFile:
            if args.json:
                print(json.dumps({"error": "Invalid ZIP file from ClawHub", "passed": False}))
            else:
                print("ERROR: ClawHub returned an invalid ZIP file")
            return 1

        result = scan_path(Path(tmpdir))
        result.path = slug  # Show the slug, not the tmp path

    if args.json:
        _print_result_json(result)
    else:
        _print_result(result)

    return 0 if result.passed else 1


def cmd_verify(args: argparse.Namespace) -> int:
    path = Path(args.path).resolve()
    result = verify_manifest(path)

    if args.json:
        _print_result_json(result)
    else:
        _print_result(result)

    return 0 if result.passed else 1


def cmd_version(args: argparse.Namespace) -> int:
    if args.json:
        print(json.dumps({"version": __version__}))
    else:
        print(f"samma-suit {__version__}")
    return 0


# ── Main ──

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="samma",
        description="Samma Suit CLI — security scanner for AI agent skills",
    )
    parser.add_argument(
        "--json", action="store_true", default=False,
        help="Output results as JSON",
    )
    sub = parser.add_subparsers(dest="command")

    # scan
    p_scan = sub.add_parser("scan", help="Scan a skill directory or file for security issues")
    p_scan.add_argument("path", help="Path to skill directory or file")

    # scan-clawhub
    p_clawhub = sub.add_parser("scan-clawhub", help="Fetch and scan a ClawHub skill package")
    p_clawhub.add_argument("slug", help="ClawHub slug (e.g. OneZeroEight-ai/cool-skill)")

    # verify
    p_verify = sub.add_parser("verify", help="Verify a SKILL.md manifest")
    p_verify.add_argument("path", help="Path to SKILL.md file")

    # version
    sub.add_parser("version", help="Print samma-suit version")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    commands = {
        "scan": cmd_scan,
        "scan-clawhub": cmd_scan_clawhub,
        "verify": cmd_verify,
        "version": cmd_version,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
