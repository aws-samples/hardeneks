import hashlib

from hardeneks.masking import (
    MaskingConfig,
    Masker,
    build_masker,
    _redact,
    _redact_word,
    _is_generated_segment,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:8]


# ---------------------------------------------------------------------------
# MaskingConfig.from_dict
# ---------------------------------------------------------------------------


class TestMaskingConfigFromDict:
    def test_defaults_when_empty(self):
        cfg = MaskingConfig.from_dict({})
        assert cfg.mask_namespace_names is False
        assert cfg.mask_resource_names is False
        assert cfg.replace_with == "hash"
        assert cfg.excluded_namespaces == []
        assert cfg.excluded_regex is None

    def test_constraints_parsed(self):
        cfg = MaskingConfig.from_dict(
            {
                "constraints": {
                    "mask_namespace_names": True,
                    "mask_resource_names": True,
                }
            }
        )
        assert cfg.mask_namespace_names is True
        assert cfg.mask_resource_names is True

    def test_replace_with_hash_explicit(self):
        cfg = MaskingConfig.from_dict(
            {"constraints": {"replace_with": "hash"}}
        )
        assert cfg.replace_with == "hash"

    def test_replace_with_char(self):
        cfg = MaskingConfig.from_dict({"constraints": {"replace_with": "*"}})
        assert cfg.replace_with == "*"

    def test_replace_with_defaults_to_hash_when_absent(self):
        cfg = MaskingConfig.from_dict({"constraints": {}})
        assert cfg.replace_with == "hash"

    def test_replace_with_defaults_to_hash_when_null(self):
        cfg = MaskingConfig.from_dict({"constraints": {"replace_with": None}})
        assert cfg.replace_with == "hash"

    def test_exclude_namespaces_parsed(self):
        cfg = MaskingConfig.from_dict(
            {"exclude": {"namespaces": ["kube-system", "default"]}}
        )
        assert cfg.excluded_namespaces == ["kube-system", "default"]

    def test_exclude_regex_parsed(self):
        cfg = MaskingConfig.from_dict({"exclude": {"regex": "^system:.*"}})
        assert cfg.excluded_regex == "^system:.*"

    def test_null_regex_normalised_to_none(self):
        cfg = MaskingConfig.from_dict({"exclude": {"regex": None}})
        assert cfg.excluded_regex is None

    def test_null_namespaces_normalised_to_empty(self):
        cfg = MaskingConfig.from_dict({"exclude": {"namespaces": None}})
        assert cfg.excluded_namespaces == []


class TestMaskingConfigIsEnabled:
    def test_disabled_when_both_off(self):
        assert MaskingConfig().is_enabled() is False

    def test_enabled_when_namespace_masking_on(self):
        assert MaskingConfig(mask_namespace_names=True).is_enabled() is True

    def test_enabled_when_resource_masking_on(self):
        assert MaskingConfig(mask_resource_names=True).is_enabled() is True


# ---------------------------------------------------------------------------
# Masker.mask_namespace
# ---------------------------------------------------------------------------


class TestMaskerMaskNamespace:
    def test_returns_original_when_disabled(self):
        masker = Masker(MaskingConfig(mask_namespace_names=False))
        assert masker.mask_namespace("my-ns") == "my-ns"

    def test_returns_hash_when_enabled(self):
        masker = Masker(MaskingConfig(mask_namespace_names=True))
        assert masker.mask_namespace("my-ns") == _sha("my-ns")

    def test_excluded_namespace_not_masked(self):
        cfg = MaskingConfig(
            mask_namespace_names=True,
            excluded_namespaces=["my-ns"],
        )
        assert Masker(cfg).mask_namespace("my-ns") == "my-ns"

    def test_regex_excluded_namespace_not_masked(self):
        cfg = MaskingConfig(
            mask_namespace_names=True, excluded_regex="^system:.*"
        )
        assert Masker(cfg).mask_namespace("system:masters") == "system:masters"

    def test_non_excluded_namespace_masked(self):
        cfg = MaskingConfig(
            mask_namespace_names=True,
            excluded_namespaces=["safe-ns"],
        )
        assert Masker(cfg).mask_namespace("unsafe-ns") == _sha("unsafe-ns")

    def test_deterministic(self):
        masker = Masker(MaskingConfig(mask_namespace_names=True))
        assert masker.mask_namespace("abc") == masker.mask_namespace("abc")

    def test_different_inputs_produce_different_hashes(self):
        masker = Masker(MaskingConfig(mask_namespace_names=True))
        assert masker.mask_namespace("ns-a") != masker.mask_namespace("ns-b")


# ---------------------------------------------------------------------------
# Masker.mask_resource_name
# ---------------------------------------------------------------------------


class TestMaskerMaskResourceName:
    def test_returns_original_when_disabled(self):
        masker = Masker(MaskingConfig(mask_resource_names=False))
        assert masker.mask_resource_name("pod-xyz") == "pod-xyz"

    def test_returns_hash_when_enabled(self):
        masker = Masker(MaskingConfig(mask_resource_names=True))
        assert masker.mask_resource_name("pod-xyz") == _sha("pod-xyz")

    def test_excluded_namespace_skips_masking_of_resource(self):
        cfg = MaskingConfig(
            mask_resource_names=True,
            excluded_namespaces=["safe-ns"],
        )
        masker = Masker(cfg)
        assert (
            masker.mask_resource_name("my-pod", namespace="safe-ns")
            == "my-pod"
        )

    def test_non_excluded_namespace_masks_resource(self):
        cfg = MaskingConfig(
            mask_resource_names=True,
            excluded_namespaces=["safe-ns"],
        )
        masker = Masker(cfg)
        assert masker.mask_resource_name(
            "my-pod", namespace="other-ns"
        ) == _sha("my-pod")

    def test_excluded_resource_name_not_masked(self):
        cfg = MaskingConfig(
            mask_resource_names=True,
            excluded_namespaces=["safe-ns"],
        )
        masker = Masker(cfg)
        # "safe-ns" is also in excluded_namespaces, so the name itself
        # matches the exclusion list → not masked
        assert masker.mask_resource_name("safe-ns") == "safe-ns"

    def test_regex_excluded_resource_not_masked(self):
        cfg = MaskingConfig(
            mask_resource_names=True, excluded_regex="^system:.*"
        )
        masker = Masker(cfg)
        assert (
            masker.mask_resource_name("system:node-proxier")
            == "system:node-proxier"
        )


# ---------------------------------------------------------------------------
# Masker.mask_namespaces / mask_resource_names (list helpers)
# ---------------------------------------------------------------------------


class TestMaskerListHelpers:
    def test_mask_namespaces_list(self):
        masker = Masker(MaskingConfig(mask_namespace_names=True))
        result = masker.mask_namespaces(["ns-a", "ns-b"])
        assert result == [_sha("ns-a"), _sha("ns-b")]

    def test_mask_resource_names_list(self):
        masker = Masker(MaskingConfig(mask_resource_names=True))
        result = masker.mask_resource_names(["pod-1", "pod-2"])
        assert result == [_sha("pod-1"), _sha("pod-2")]

    def test_mask_resource_names_list_with_excluded_namespace(self):
        cfg = MaskingConfig(
            mask_resource_names=True, excluded_namespaces=["safe"]
        )
        masker = Masker(cfg)
        result = masker.mask_resource_names(
            ["pod-1", "pod-2"], namespace="safe"
        )
        assert result == ["pod-1", "pod-2"]


# ---------------------------------------------------------------------------
# build_masker
# ---------------------------------------------------------------------------


def _cfg(masking_block: dict) -> dict:
    """Wrap a masking block in the expected top-level structure."""
    return {"masking": masking_block}


# ---------------------------------------------------------------------------
# _redact_word
# ---------------------------------------------------------------------------


class TestRedactWord:
    def test_single_char_uses_itself_as_both_ends(self):
        assert _redact_word("a", "*") == "a*****a"

    def test_two_chars(self):
        assert _redact_word("ab", "*") == "a*****b"

    def test_three_chars(self):
        assert _redact_word("api", "*") == "a*****i"

    def test_short_word(self):
        assert _redact_word("prod", "*") == "p*****d"

    def test_long_word(self):
        assert _redact_word("payment", "*") == "p*****t"

    def test_very_long_word(self):
        assert _redact_word("production", "*") == "p*****n"

    def test_always_exactly_five_mask_chars(self):
        for word in ["a", "ab", "abc", "abcd", "abcde", "abcdefgh"]:
            result = _redact_word(word, "*")
            assert result.count("*") == 5, f"failed for {word!r}: {result!r}"

    def test_different_char(self):
        assert _redact_word("payment", "#") == "p#####t"


# ---------------------------------------------------------------------------
# _is_generated_segment
# ---------------------------------------------------------------------------


class TestIsGeneratedSegment:
    def test_hex_segment(self):
        assert _is_generated_segment("7d9f4b") is True

    def test_no_vowel_segment(self):
        assert _is_generated_segment("xkq2p") is True

    def test_short_segment_not_generated(self):
        assert _is_generated_segment("api") is False

    def test_regular_word_not_generated(self):
        assert _is_generated_segment("payment") is False

    def test_four_chars_not_generated(self):
        assert _is_generated_segment("7d9f") is False


# ---------------------------------------------------------------------------
# _redact (full name)
# ---------------------------------------------------------------------------


class TestRedact:
    def test_simple_two_segment_name(self):
        assert _redact("payment-api", "*") == "p*****t-a*****i"

    def test_generated_suffix_preserved(self):
        assert _redact("payment-api-7d9f4b", "*") == "p*****t-a*****i-7d9f4b"

    def test_pod_name_with_two_suffixes(self):
        result = _redact("payment-api-7d9f4b-xkq2p", "*")
        assert result == "p*****t-a*****i-7d9f4b-xkq2p"

    def test_short_name_single_segment(self):
        assert _redact("prod", "*") == "p*****d"

    def test_two_char_segment(self):
        assert _redact("ns", "*") == "n*****s"

    def test_three_char_namespace(self):
        assert _redact("dev", "*") == "d*****v"

    def test_no_generated_suffix(self):
        assert _redact("my-service", "*") == "m*****y-s*****e"


# ---------------------------------------------------------------------------
# Masker — char mode
# ---------------------------------------------------------------------------


class TestMaskerCharMode:
    def _masker(self, char="*"):
        return Masker(
            MaskingConfig(
                mask_namespace_names=True,
                mask_resource_names=True,
                replace_with=char,
            )
        )

    def test_namespace_redacted(self):
        assert self._masker().mask_namespace("production") == "p*****n"

    def test_resource_name_redacted(self):
        assert (
            self._masker().mask_resource_name("payment-api")
            == "p*****t-a*****i"
        )

    def test_pod_with_generated_suffix(self):
        assert (
            self._masker().mask_resource_name("payment-api-7d9f4b-xkq2p")
            == "p*****t-a*****i-7d9f4b-xkq2p"
        )

    def test_excluded_namespace_not_redacted(self):
        masker = Masker(
            MaskingConfig(
                mask_namespace_names=True,
                replace_with="*",
                excluded_namespaces=["production"],
            )
        )
        assert masker.mask_namespace("production") == "production"

    def test_excluded_namespace_skips_resource_redaction(self):
        masker = Masker(
            MaskingConfig(
                mask_resource_names=True,
                replace_with="*",
                excluded_namespaces=["production"],
            )
        )
        assert (
            masker.mask_resource_name("payment-api", namespace="production")
            == "payment-api"
        )

    def test_different_char(self):
        masker = Masker(
            MaskingConfig(mask_namespace_names=True, replace_with="#")
        )
        # always exactly 5 mask chars
        assert masker.mask_namespace("production") == "p#####n"

    def test_hash_mode_still_works_after_char_mode_tests(self):
        masker = Masker(
            MaskingConfig(mask_namespace_names=True, replace_with="hash")
        )
        assert masker.mask_namespace("production") == _sha("production")


# ---------------------------------------------------------------------------
# build_masker — replace_with threaded through
# ---------------------------------------------------------------------------


class TestBuildMasker:
    def test_returns_none_when_key_absent(self):
        assert build_masker({}) is None

    def test_returns_none_when_masking_key_absent(self):
        assert build_masker({"rules": {}}) is None

    def test_returns_none_when_all_disabled(self):
        config = _cfg(
            {
                "constraints": {
                    "mask_namespace_names": False,
                    "mask_resource_names": False,
                }
            }
        )
        assert build_masker(config) is None

    def test_returns_masker_when_namespace_masking_enabled(self):
        config = _cfg({"constraints": {"mask_namespace_names": True}})
        masker = build_masker(config)
        assert isinstance(masker, Masker)

    def test_returns_masker_when_resource_masking_enabled(self):
        config = _cfg({"constraints": {"mask_resource_names": True}})
        assert isinstance(build_masker(config), Masker)

    def test_exclude_namespaces_threaded_through(self):
        config = _cfg(
            {
                "constraints": {"mask_namespace_names": True},
                "exclude": {"namespaces": ["example"]},
            }
        )
        masker = build_masker(config)
        assert masker.mask_namespace("example") == "example"
        assert masker.mask_namespace("other") == _sha("other")

    def test_exclude_regex_threaded_through(self):
        config = _cfg(
            {
                "constraints": {"mask_namespace_names": True},
                "exclude": {"regex": "^kube-"},
            }
        )
        masker = build_masker(config)
        assert masker.mask_namespace("kube-system") == "kube-system"
        assert masker.mask_namespace("prod") == _sha("prod")

    def test_replace_with_char_threaded_through(self):
        config = _cfg(
            {
                "constraints": {
                    "mask_namespace_names": True,
                    "replace_with": "*",
                }
            }
        )
        masker = build_masker(config)
        # always exactly 5 mask chars between first and last
        assert masker.mask_namespace("production") == "p*****n"
