"""Command-line interface for creating, updating, and removing OKF bundles.

Usage
-----
::

    # Create a bundle from a URL
    knowledge create https://example.com/docs.html ./my-bundle

    # Create with a different model
    knowledge create --model claude-3-opus-20240229 docs.html ./my-bundle

    # Create and validate
    knowledge create --validate docs.html ./my-bundle

    # Update an existing bundle
    knowledge update docs.html ./my-bundle

    # Remove specific concepts
    knowledge remove obsolete-section out-of-date-topic ./my-bundle

Architecture
------------
Each ``cmd_*`` function corresponds to one subcommand.  All
subcommands share the ``--model`` flag (positioned on the main
parser for convenience).  Error handling is centralised in
:func:`main`: any ``Exception`` thrown by a command is caught,
logged, and causes a non-zero exit code.

Logging is configured in :func:`main` with ``%(message)s`` format
and writes to stderr, keeping stdout clean for future pipe-friendly
output.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time

from knowledge import Knowledge
from knowledge.llm.manager import KnowledgeBundleManager
from knowledge.version import DEFAULT_MODEL

logger = logging.getLogger(__name__)

MAX_LABEL_LENGTH = 50
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_PARTIAL = 2


def _shorten_label(label: str) -> str:
    """Truncate *label* to :obj:`MAX_LABEL_LENGTH` characters, appending ``...``."""
    if len(label) > MAX_LABEL_LENGTH:
        return label[: MAX_LABEL_LENGTH - 3] + "..."
    return label


def _source_label(source: str) -> str:
    """Extract a short display label from a source string (URL or file path)."""
    label = source.split("/")[-1] if "/" in source else source
    return _shorten_label(label)


def cmd_create(args: argparse.Namespace) -> None:
    """Create an OKF bundle from a source with progress feedback.

    Logs elapsed time and concept count.  If ``--validate`` is set,
    runs :meth:`~knowledge.kmd.bundle.BundleSerializer.validate` and
    reports any structural issues.
    """
    knowledge = Knowledge(model=args.model)
    source_label = _source_label(args.input)

    logger.info("Creating bundle from %s...", source_label)
    t0 = time.time()
    count = knowledge.create_bundle(args.input, args.output)
    elapsed = time.time() - t0
    logger.info("done (%.1fs)", elapsed)
    logger.info("Wrote %d concepts to %s", count, args.output)

    if args.validate:
        from knowledge.kmd.bundle import BundleSerializer

        issues = BundleSerializer().validate(args.output)
        if issues:
            logger.warning("Validation: %d issue(s)", len(issues))
            for issue in issues:
                logger.warning("  ! %s", issue)
        else:
            logger.info("Validation: OK")


def cmd_update(args: argparse.Namespace) -> None:
    """Update an existing OKF bundle by re-extracting from source.

    .. warning::

        ``update`` performs a **complete replacement** of the bundle
        contents.  Any concepts present in the old bundle but not in
        the new extraction will be removed.  Edit concept files by hand
        before updating if you need to preserve them.
    """
    knowledge = Knowledge(model=args.model)
    source_label = _source_label(args.input)

    logger.info("Updating bundle from %s...", source_label)
    t0 = time.time()
    count = knowledge.update(args.input, args.bundle_dir)
    elapsed = time.time() - t0
    logger.info("done (%.1fs)", elapsed)
    logger.info("Wrote %d concepts to %s", count, args.bundle_dir)


def cmd_remove(args: argparse.Namespace) -> int:
    """Remove concepts from an existing OKF bundle by ID.

    The ``--model`` flag is accepted but ignored: removal is a local
    filesystem operation that does not call the LLM.

    Returns :data:`EXIT_PARTIAL` if any requested concept ID was
    not found in the bundle, so that typos are visible to operators
    using the CLI from scripts.
    """
    label = _shorten_label(", ".join(args.concept_ids))

    logger.info("Removing concepts [%s]...", label)
    t0 = time.time()
    manager = KnowledgeBundleManager(model=args.model)
    written, unknowns = manager.remove_with_unknowns(args.concept_ids, args.bundle_dir)
    elapsed = time.time() - t0
    logger.info("done (%.1fs)", elapsed)
    logger.info("Wrote %d concepts to %s", written, args.bundle_dir)

    if unknowns:
        logger.warning(
            "%d requested concept ID(s) were not found in the bundle:",
            len(unknowns),
        )
        for unknown in unknowns:
            logger.warning("  - %s", unknown)
        return EXIT_PARTIAL
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        description="knowledge — OKF bundle creation tool",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"LLM model to use (default: {DEFAULT_MODEL})",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create", help="Create an OKF bundle from a URL or file")
    p_create.add_argument("input", help="URL or file path")
    p_create.add_argument("output", help="Output directory for the bundle")
    p_create.add_argument("--validate", action="store_true", help="Validate bundle after writing")
    p_create.set_defaults(func=cmd_create)

    p_update = sub.add_parser("update", help="Update an existing bundle from a source")
    p_update.add_argument("input", help="URL or file path")
    p_update.add_argument("bundle_dir", help="Existing bundle directory to update")
    p_update.set_defaults(func=cmd_update)

    p_remove = sub.add_parser("remove", help="Remove concepts from a bundle")
    p_remove.add_argument("concept_ids", nargs="+", help="Concept ID(s) to remove")
    p_remove.add_argument("bundle_dir", help="Bundle directory to modify")
    p_remove.set_defaults(func=cmd_remove)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse arguments, run command, handle errors.

    Returns the process exit code.  All uncaught exceptions are
    logged to stderr and produce :data:`EXIT_ERROR`.  Successful
    commands return :data:`EXIT_OK`.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        stream=sys.stderr,
    )
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except Exception as exc:
        logger.error(str(exc))
        return EXIT_ERROR
    if result is None:
        return EXIT_OK
    return int(result)


if __name__ == "__main__":
    sys.exit(main())
