"""knowledge: An open-source Python SDK for Open Knowledge Format (OKF) documents."""

from knowledge._version import __version__
from knowledge.exceptions import KnowledgeError, ParseError
from knowledge.okf import OKFParser, OKFSerializer
from knowledge.passes import CompilerPass, Diagnostic, PassManager, PassResult, Phase, Severity

__all__ = [
    "__version__",
    "KnowledgeError",
    "ParseError",
    "OKFParser",
    "OKFSerializer",
    "Phase",
    "CompilerPass",
    "PassResult",
    "Severity",
    "Diagnostic",
    "PassManager",
]
