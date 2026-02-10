"""SANGHA scanner — static analysis for skill security vetting.

Extracts code blocks from markdown (SKILL.md), scans Python and
JavaScript/TypeScript source for dangerous patterns, and returns
severity-rated findings.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Finding:
    severity: Severity
    pattern: str
    description: str
    file: str
    line: int
    snippet: str


@dataclass
class ScanResult:
    path: str
    findings: list[Finding] = field(default_factory=list)
    files_scanned: int = 0
    code_blocks_extracted: int = 0
    error: Optional[str] = None

    @property
    def passed(self) -> bool:
        return not any(
            f.severity in (Severity.CRITICAL, Severity.HIGH) for f in self.findings
        )

    def summary(self) -> dict:
        counts = {s.value: 0 for s in Severity}
        for f in self.findings:
            counts[f.severity.value] += 1
        return {
            "path": self.path,
            "passed": self.passed,
            "files_scanned": self.files_scanned,
            "code_blocks_extracted": self.code_blocks_extracted,
            "findings": counts,
            "total_findings": len(self.findings),
        }


# ── Dangerous patterns ──
# (regex, severity, description)
DANGEROUS_PATTERNS: list[tuple[str, Severity, str]] = [
    # Code execution
    (r"\beval\s*\(", Severity.CRITICAL, "eval() — arbitrary code execution"),
    (r"\bexec\s*\(", Severity.CRITICAL, "exec() — arbitrary code execution"),
    (r"(?<!re\.)\bcompile\s*\(", Severity.HIGH, "compile() — dynamic code compilation"),
    (r"\b__import__\s*\(", Severity.HIGH, "__import__() — dynamic import"),

    # Shell execution
    (r"\bos\.system\s*\(", Severity.CRITICAL, "os.system() — shell command execution"),
    (r"\bos\.popen\s*\(", Severity.CRITICAL, "os.popen() — shell command execution"),
    (r"\bos\.exec[lv]p?e?\s*\(", Severity.CRITICAL, "os.exec*() — process replacement"),
    (r"\bsubprocess\.", Severity.HIGH, "subprocess — shell/process execution"),

    # Network access
    (r"\brequests\.(get|post|put|patch|delete|head|options)\s*\(", Severity.HIGH, "requests — outbound HTTP call"),
    (r"\bhttpx\.(get|post|put|patch|delete|head|options|AsyncClient|Client)\b", Severity.HIGH, "httpx — outbound HTTP call"),
    (r"\burllib\.request\.", Severity.HIGH, "urllib — outbound HTTP call"),
    (r"\bsocket\.socket\s*\(", Severity.CRITICAL, "raw socket — unrestricted network access"),

    # Deserialization
    (r"\bpickle\.loads?\s*\(", Severity.CRITICAL, "pickle.load() — unsafe deserialization"),
    (r"\byaml\.load\s*\((?!.*Loader\s*=\s*yaml\.SafeLoader)", Severity.HIGH, "yaml.load() without SafeLoader"),
    (r"\bmarshal\.loads?\s*\(", Severity.CRITICAL, "marshal.load() — unsafe deserialization"),

    # Filesystem destructive
    (r"\bshutil\.rmtree\s*\(", Severity.HIGH, "shutil.rmtree() — recursive directory deletion"),
    (r"\bos\.remove\s*\(", Severity.MEDIUM, "os.remove() — file deletion"),
    (r"\bos\.unlink\s*\(", Severity.MEDIUM, "os.unlink() — file deletion"),
    (r"\bos\.rmdir\s*\(", Severity.MEDIUM, "os.rmdir() — directory deletion"),

    # Namespace manipulation
    (r"\bglobals\s*\(\s*\)\s*\[", Severity.HIGH, "globals()[] — namespace manipulation"),
    (r"\blocals\s*\(\s*\)\s*\[", Severity.MEDIUM, "locals()[] — namespace manipulation"),
    (r"\bsetattr\s*\(", Severity.MEDIUM, "setattr() — dynamic attribute setting"),

    # C-level / ctypes
    (r"\bctypes\.", Severity.HIGH, "ctypes — C library access"),

    # Dynamic imports
    (r"\bimportlib\.import_module\s*\(", Severity.MEDIUM, "importlib.import_module() — dynamic import"),

    # File writes (informational — not always dangerous)
    (r"\bopen\s*\([^)]*['\"][wa]['\"]", Severity.LOW, "open() with write mode"),
]

# ── JavaScript / TypeScript dangerous patterns ──
JS_DANGEROUS_PATTERNS: list[tuple[str, Severity, str]] = [
    # Code execution
    (r"\beval\s*\(", Severity.CRITICAL, "eval() — arbitrary code execution"),
    (r"\bnew\s+Function\s*\(", Severity.CRITICAL, "new Function() — dynamic code execution"),

    # Shell execution
    (r"\bchild_process\b", Severity.CRITICAL, "child_process — shell/process execution"),
    (r"\bexecSync\s*\(", Severity.CRITICAL, "execSync() — synchronous shell execution"),
    (r"\bexec\s*\(", Severity.HIGH, "exec() — shell command execution"),
    (r"\bspawn\s*\(", Severity.HIGH, "spawn() — process execution"),
    (r"\bspawnSync\s*\(", Severity.HIGH, "spawnSync() — synchronous process execution"),
    (r"\bexecFile\s*\(", Severity.HIGH, "execFile() — file execution"),

    # Network access
    (r"\bfetch\s*\(", Severity.HIGH, "fetch() — outbound network call"),
    (r"\baxios[\.\(]", Severity.HIGH, "axios — outbound HTTP call"),
    (r"\bhttp\.request\s*\(", Severity.HIGH, "http.request() — outbound HTTP call"),
    (r"\bhttps\.request\s*\(", Severity.HIGH, "https.request() — outbound HTTP call"),
    (r"\bhttp\.get\s*\(", Severity.HIGH, "http.get() — outbound HTTP call"),
    (r"\bhttps\.get\s*\(", Severity.HIGH, "https.get() — outbound HTTP call"),
    (r"\bnew\s+WebSocket\s*\(", Severity.HIGH, "WebSocket — outbound network connection"),
    (r"\bXMLHttpRequest\b", Severity.HIGH, "XMLHttpRequest — outbound network call"),

    # Filesystem access
    (r"\bfs\.readFileSync\s*\(", Severity.HIGH, "fs.readFileSync() — filesystem read"),
    (r"\bfs\.writeFileSync\s*\(", Severity.HIGH, "fs.writeFileSync() — filesystem write"),
    (r"\bfs\.readFile\s*\(", Severity.MEDIUM, "fs.readFile() — async filesystem read"),
    (r"\bfs\.writeFile\s*\(", Severity.MEDIUM, "fs.writeFile() — async filesystem write"),
    (r"\bfs\.unlinkSync\s*\(", Severity.HIGH, "fs.unlinkSync() — file deletion"),
    (r"\bfs\.rmdirSync\s*\(", Severity.HIGH, "fs.rmdirSync() — directory deletion"),
    (r"\bfs\.rmSync\s*\(", Severity.HIGH, "fs.rmSync() — recursive deletion"),

    # Sensitive file access
    (r"""['"]\.env['"]""", Severity.HIGH, "'.env' — sensitive environment file access"),
    (r"""['"]MEMORY\.md['"]""", Severity.HIGH, "'MEMORY.md' — agent memory file access"),
    (r"""['"]USER\.md['"]""", Severity.HIGH, "'USER.md' — user data file access"),
    (r"""['"]\.claude['"/]""", Severity.HIGH, "'.claude' — Claude config directory access"),

    # Environment variable access
    (r"\bprocess\.env\b", Severity.MEDIUM, "process.env — environment variable access"),

    # Obfuscation
    (r"\bBuffer\.from\s*\([^)]*['\"]base64['\"]", Severity.HIGH, "Buffer.from(base64) — potential obfuscation"),
    (r"\batob\s*\(", Severity.MEDIUM, "atob() — base64 decode, potential obfuscation"),
    (r"\bbtoa\s*\(", Severity.LOW, "btoa() — base64 encode"),

    # Dynamic require/import
    (r"\brequire\s*\(\s*[^'\"]", Severity.MEDIUM, "require() with dynamic argument"),

    # Prototype pollution
    (r"\b__proto__\b", Severity.HIGH, "__proto__ — prototype pollution risk"),
    (r"\bconstructor\s*\[", Severity.HIGH, "constructor[] — prototype pollution risk"),
]

# Combine all patterns for universal scanning
ALL_DANGEROUS_PATTERNS = DANGEROUS_PATTERNS + JS_DANGEROUS_PATTERNS


# ── Code block extraction ──

_CODE_BLOCK_RE = re.compile(
    r"```(?:python|py|bash|sh|shell|javascript|js|typescript|ts|jsx|tsx)?\s*\n(.*?)```",
    re.DOTALL,
)


def extract_code_blocks(markdown: str) -> list[str]:
    """Extract fenced code blocks from markdown content."""
    return _CODE_BLOCK_RE.findall(markdown)


# ── Manifest verification ──

_REQUIRED_FRONTMATTER = ["skill_id", "name", "version", "author"]

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def verify_manifest(path: Path) -> ScanResult:
    """Verify a SKILL.md manifest has required frontmatter fields."""
    result = ScanResult(path=str(path))

    if not path.exists():
        result.error = f"File not found: {path}"
        return result

    content = path.read_text(encoding="utf-8")

    match = _FRONTMATTER_RE.match(content)
    if not match:
        result.findings.append(Finding(
            severity=Severity.HIGH,
            pattern="frontmatter",
            description="Missing YAML frontmatter block (--- ... ---)",
            file=str(path),
            line=1,
            snippet=content[:80],
        ))
        return result

    frontmatter = match.group(1)
    for field_name in _REQUIRED_FRONTMATTER:
        pattern = rf"^{field_name}\s*:"
        if not re.search(pattern, frontmatter, re.MULTILINE):
            result.findings.append(Finding(
                severity=Severity.HIGH,
                pattern="frontmatter",
                description=f"Missing required field: {field_name}",
                file=str(path),
                line=1,
                snippet=frontmatter[:80],
            ))

    # Also scan embedded code blocks
    blocks = extract_code_blocks(content)
    result.code_blocks_extracted = len(blocks)
    for i, block in enumerate(blocks):
        _scan_source(block, f"{path}::block[{i}]", result)

    return result


# ── Core scanning ──

def _is_string_literal_line(line: str) -> bool:
    """Check if the line is primarily a string/regex definition (not executable code)."""
    stripped = line.strip()
    # Tuple entries in pattern lists: (r"...", ...)
    if stripped.startswith("(r\"") or stripped.startswith("(r'"):
        return True
    # Raw string assignments: FOO = r"..."
    if re.match(r"^\w+\s*=\s*r[\"']", stripped):
        return True
    # JS regex assignments: const FOO = /pattern/
    if re.match(r"^(?:const|let|var)\s+\w+\s*=\s*/", stripped):
        return True
    return False


def _is_comment_line(line: str) -> bool:
    """Check if a line is a comment in Python, JS, or shell."""
    stripped = line.strip()
    return stripped.startswith("#") or stripped.startswith("//")


def _scan_source(source: str, filename: str, result: ScanResult) -> None:
    """Scan a source string for dangerous patterns (Python + JS/TS)."""
    for line_num, line in enumerate(source.splitlines(), start=1):
        stripped = line.strip()
        if _is_comment_line(stripped):
            continue
        if _is_string_literal_line(stripped):
            continue
        for pattern, severity, description in ALL_DANGEROUS_PATTERNS:
            if re.search(pattern, line):
                result.findings.append(Finding(
                    severity=severity,
                    pattern=pattern,
                    description=description,
                    file=filename,
                    line=line_num,
                    snippet=line.strip()[:120],
                ))


_SOURCE_EXTENSIONS = {".py", ".js", ".ts", ".mjs", ".cjs", ".jsx", ".tsx"}
_MARKDOWN_EXTENSIONS = {".md"}


def scan_path(path: Path) -> ScanResult:
    """Scan a file or directory for security issues.

    For directories: scans all source files (.py, .js, .ts, etc.) and
    extracts code from .md files.
    For files: scans source directly or extracts code blocks from .md.
    """
    result = ScanResult(path=str(path))

    if not path.exists():
        result.error = f"Path not found: {path}"
        return result

    files: list[Path] = []
    if path.is_file():
        files = [path]
    else:
        for ext in _SOURCE_EXTENSIONS:
            files.extend(sorted(path.rglob(f"*{ext}")))
        for ext in _MARKDOWN_EXTENSIONS:
            files.extend(sorted(path.rglob(f"*{ext}")))

    for f in files:
        content = f.read_text(encoding="utf-8", errors="replace")
        result.files_scanned += 1

        if f.suffix in _SOURCE_EXTENSIONS:
            _scan_source(content, str(f), result)
        elif f.suffix in _MARKDOWN_EXTENSIONS:
            blocks = extract_code_blocks(content)
            result.code_blocks_extracted += len(blocks)
            for i, block in enumerate(blocks):
                _scan_source(block, f"{f}::block[{i}]", result)

    return result
