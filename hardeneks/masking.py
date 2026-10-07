import hashlib
import re
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_HASH = "hash"
_DIGEST_LENGTH = 8

# A "generated suffix" segment: 5+ chars, no vowels, or all hex digits.
# Matches things like "7d9f4b", "xkq2p", "5bffc9a1".
_GENERATED_SEGMENT = re.compile(
    r"^([0-9a-f]{5,}|[^aeiou]{5,})$", re.IGNORECASE
)


# ---------------------------------------------------------------------------
# MaskingConfig
# ---------------------------------------------------------------------------


@dataclass
class MaskingConfig:
    """Parsed representation of the masking config block."""

    mask_namespace_names: bool = False
    mask_resource_names: bool = False
    replace_with: str = _HASH  # "hash" or a single masking character
    excluded_namespaces: list = field(default_factory=list)
    excluded_regex: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "MaskingConfig":
        """Build a MaskingConfig from a raw YAML-parsed dict.

        Expected shape::

            masking:
              constraints:
                mask_namespace_names: true
                mask_resource_names: true
                replace_with: "*"   # or "hash" (default)
              exclude:
                namespaces:
                  - kube-system
                regex: "^system:.*"
        """
        constraints = data.get("constraints", {})
        exclude = data.get("exclude", {})
        replace_with = constraints.get("replace_with") or _HASH
        return cls(
            mask_namespace_names=bool(
                constraints.get("mask_namespace_names", False)
            ),
            mask_resource_names=bool(
                constraints.get("mask_resource_names", False)
            ),
            replace_with=str(replace_with),
            excluded_namespaces=list(exclude.get("namespaces") or []),
            excluded_regex=exclude.get("regex") or None,
        )

    def is_enabled(self) -> bool:
        """Return True if at least one masking constraint is active."""
        return self.mask_namespace_names or self.mask_resource_names


# ---------------------------------------------------------------------------
# Masker
# ---------------------------------------------------------------------------


class Masker:
    """Apply deterministic masking to namespace and resource names.

    Two masking modes are supported via ``replace_with``:

    ``"hash"`` (default)
        Replace the entire name with a truncated SHA-256 hex digest
        (8 characters).  The same input always produces the same digest
        within a run; the original name cannot be recovered.

    Single character (e.g. ``"*"``)
        Partially redact each hyphen-delimited word while keeping the
        first and last character and inserting exactly 5 mask characters
        in between, regardless of the word's original length.
        Generated suffixes (e.g. the ``7d9f4b`` or ``xkq2p`` parts of a
        Pod name) are kept as-is.

        Example with ``"*"``::

            "payment-api"            → "p*****t-a*****i"
            "payment-api-7d9f4b"     → "p*****t-a*****i-7d9f4b"
            "payment-api-7d9f4b-xp"  → "p*****t-a*****i-7d9f4b-xp"
            "ns"                     → "n*****s"
            "prod"                   → "p*****d"

    Exclusion rules are evaluated *before* masking:

    * ``excluded_namespaces`` — explicit allow-list; exact string match.
    * ``excluded_regex`` — compiled regex; ``re.search`` match skips masking.

    Usage::

        cfg = MaskingConfig(
            mask_namespace_names=True,
            mask_resource_names=True,
            replace_with="*",
        )
        masker = Masker(cfg)
        safe_ns   = masker.mask_namespace("my-secret-ns")
        safe_name = masker.mask_resource_name("payment-api-7d9f4b", namespace="prod")
    """

    def __init__(self, config: MaskingConfig):
        self._config = config
        self._compiled_regex: Optional[re.Pattern] = None
        if config.excluded_regex:
            self._compiled_regex = re.compile(config.excluded_regex)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def mask_namespace(self, name: str) -> str:
        """Return a masked namespace name, or the original if excluded/disabled."""
        if not self._config.mask_namespace_names:
            return name
        if self._is_excluded(name):
            return name
        return self._apply(name)

    def mask_resource_name(
        self, name: str, namespace: Optional[str] = None
    ) -> str:
        """Return a masked resource name, or the original if excluded/disabled.

        If *namespace* is provided and that namespace is excluded, the
        resource name is also left unmasked so that results remain
        interpretable for whitelisted namespaces.
        """
        if not self._config.mask_resource_names:
            return name
        if namespace is not None and self._is_excluded(namespace):
            return name
        if self._is_excluded(name):
            return name
        return self._apply(name)

    def mask_namespaces(self, namespaces: list) -> list:
        """Return a new list with all namespace names masked as configured."""
        return [self.mask_namespace(ns) for ns in namespaces]

    def mask_resource_names(
        self, names: list, namespace: Optional[str] = None
    ) -> list:
        """Return a new list with all resource names masked as configured."""
        return [self.mask_resource_name(n, namespace=namespace) for n in names]

    # ------------------------------------------------------------------
    # Masking dispatch
    # ------------------------------------------------------------------

    def _apply(self, value: str) -> str:
        if self._config.replace_with == _HASH:
            return _hash(value)
        return _redact(value, self._config.replace_with)

    # ------------------------------------------------------------------
    # Exclusion check
    # ------------------------------------------------------------------

    def _is_excluded(self, name: str) -> bool:
        if name in self._config.excluded_namespaces:
            return True
        if self._compiled_regex and self._compiled_regex.search(name):
            return True
        return False


# ---------------------------------------------------------------------------
# Masking implementations
# ---------------------------------------------------------------------------


def _hash(value: str) -> str:
    """Return the first 8 hex characters of the SHA-256 digest of *value*."""
    return hashlib.sha256(value.encode()).hexdigest()[:_DIGEST_LENGTH]


def _redact_word(word: str, char: str) -> str:
    """Redact a single hyphen-free segment.

    Keeps the first and last character and inserts exactly 5 mask
    characters in between, regardless of the original word length.

    Examples with ``char="*"``::

        "api"        → "a*****i"
        "payment"    → "p*****t"
        "production" → "p*****n"
        "ns"         → "n*****s"
        "a"          → "a*****a"  (single char: first == last)
    """
    mask_char = char[0]  # guard: only ever use the first character
    if len(word) == 1:
        return word[0] + mask_char * 5 + word[0]
    return word[0] + mask_char * 5 + word[-1]


def _is_generated_segment(segment: str) -> bool:
    """Return True if *segment* looks like a generated suffix.

    Matches segments that are pure hex (e.g. ``7d9f4b``) or contain no
    vowels (e.g. ``xkq2p``), both at least 5 characters long.
    """
    return bool(_GENERATED_SEGMENT.match(segment))


def _redact(name: str, char: str) -> str:
    """Partially redact *name* using *char* while preserving shape.

    Splits on ``-``, keeps generated-looking trailing segments intact,
    and applies :func:`_redact_word` to the remaining segments.
    """
    segments = name.split("-")

    # Find the index where the generated suffix train begins.
    # Walk from the right: as long as segments look generated, they're kept.
    split_at = len(segments)
    for i in range(len(segments) - 1, -1, -1):
        if _is_generated_segment(segments[i]):
            split_at = i
        else:
            break

    meaningful = segments[:split_at]
    generated = segments[split_at:]

    redacted = [_redact_word(w, char) for w in meaningful]
    return "-".join(redacted + generated)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_masker(config: dict) -> Optional[Masker]:
    """Convenience factory: parse the top-level config dict and return a
    :class:`Masker`, or ``None`` if the ``masking`` key is absent or all
    constraints are disabled.

    Expects the masking block at the top level of the config::

        masking:
          constraints:
            mask_namespace_names: true
            mask_resource_names: true
            replace_with: "*"    # or "hash" (default)
          exclude:
            namespaces:
              - example
            regex: "^system:.*"
    """
    raw = config.get("masking")
    if not raw:
        return None
    masking_config = MaskingConfig.from_dict(raw)
    if not masking_config.is_enabled():
        return None
    return Masker(masking_config)
