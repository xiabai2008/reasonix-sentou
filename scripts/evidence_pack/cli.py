# -*- coding: utf-8 -*-
"""
evidence_pack CLI 统一入口

用法:
    python scripts/evidence_pack/cli.py harvest --tag T01 --target localhost --claim "admin/admin123"
    python scripts/evidence_pack/cli.py archive evidence/manifest_T01.json
    python scripts/evidence_pack/cli.py report evidence/manifest_T01.json --format md
"""

import argparse
import sys

from . import __version__
from . import evidence_harvest, memory_archive, report_pack


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("usage: evidence-pack <harvest|archive|report> [options]")
        print("       evidence-pack --version")
        return 1

    if argv[0] in ("--version", "-v"):
        print(f"evidence_pack {__version__}")
        return 0

    sub = argv[0]
    rest = argv[1:]

    if sub == "harvest":
        return evidence_harvest.main(rest)
    elif sub == "archive":
        return memory_archive.main(rest)
    elif sub == "report":
        return report_pack.main(rest)
    elif sub in ("--help", "-h", "help"):
        print(__doc__)
        return 0
    else:
        print(f"未知子命令: {sub}", file=sys.stderr)
        print("可用: harvest | archive | report", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())