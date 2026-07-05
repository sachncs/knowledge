"""CLI — create, update, and remove commands with progress feedback."""

from __future__ import annotations

import argparse
import logging
import sys
import time

from knowledge import Knowledge

logger = logging.getLogger(__name__)


def cmd_create(args: argparse.Namespace) -> None:
    """Create an OKF bundle from a source with progress feedback."""
    knowledge = Knowledge(model=args.model)
    source_label = args.input.split("/")[-1] if "/" in args.input else args.input
    if len(source_label) > 50:
        source_label = source_label[:47] + "..."

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
    """Update an existing OKF bundle by re-extracting from source."""
    knowledge = Knowledge(model=args.model)
    source_label = args.input.split("/")[-1] if "/" in args.input else args.input
    if len(source_label) > 50:
        source_label = source_label[:47] + "..."

    logger.info("Updating bundle from %s...", source_label)
    t0 = time.time()
    count = knowledge.update(args.input, args.bundle_dir)
    elapsed = time.time() - t0
    logger.info("done (%.1fs)", elapsed)
    logger.info("Wrote %d concepts to %s", count, args.bundle_dir)


def cmd_remove(args: argparse.Namespace) -> None:
    """Remove concepts from an existing OKF bundle."""
    knowledge = Knowledge()
    label = ", ".join(args.concept_ids)
    if len(label) > 50:
        label = label[:47] + "..."

    logger.info("Removing concepts [%s]...", label)
    t0 = time.time()
    count = knowledge.remove(args.concept_ids, args.bundle_dir)
    elapsed = time.time() - t0
    logger.info("done (%.1fs)", elapsed)
    logger.info("Wrote %d concepts to %s", count, args.bundle_dir)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="knowledge — OKF bundle creation tool",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o",
        help="LLM model to use (default: gpt-4o)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create", help="Create an OKF bundle from a URL or file")
    p_create.add_argument("input", help="URL or file path")
    p_create.add_argument("output", help="Output directory for the bundle")
    p_create.add_argument(
        "--validate", action="store_true", help="Validate bundle after writing"
    )
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


def main(argv: list[str] | None = None) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        stream=sys.stderr,
    )
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except Exception as exc:
        logger.error(str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()
