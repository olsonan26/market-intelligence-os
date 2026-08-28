"""Mandatory Phase 0 tests (spec section 11)."""
from __future__ import annotations

import unittest
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from mios.contracts.hashing import canonical_json, contract_hash
from mios.contracts.timestamps import (
    NaiveTimestampError, PointInTimeTimestamp, PrecisionInventionError, TimePrecision,
)
from mios.contracts.clocks import DeterministicClock, FourClocks, KnowledgeTimeFabricationError
from mios.contracts.licensing import LicensePolicy, LicenseUse, LicenseViolation, enforce_license
from mios.contracts.schema_registry import SchemaVersionMismatch, check_schema
from mios.contracts.events import CanonicalEvent, SourceRef
from mios.contracts.instruments import InstrumentRef


def ts(dt: datetime, prec=TimePrecision.SECOND, raw=None, tz=None) -> PointInTimeTimestamp:
    return PointInTimeTimestamp(utc=dt, precision=prec, raw_text=raw, source_timezone=tz)


UTC1 = datetime(2026, 1, 5, 14, 30, 0, tzinfo=timezone.utc)


def make_clocks() -> FourClocks:
    return FourClocks(event_time=ts(UTC1), published_at=ts(UTC1), ingested_at=ts(UTC1 + timedelta(seconds=2)),
                      system_time=ts(UTC1 + timedelta(seconds=3)))


def make_event(payload=None) -> CanonicalEvent:
    return CanonicalEvent(
        event_id="evt-0001",
        schema_name="mios.canonical_event",
        schema_version="1.0.0",
        source=SourceRef(source_id="FIXTURE-MARKETDATA-V1", provider="fixture", source_event_id="s1", source_sequence=1),
        clocks=make_clocks(),
        payload=payload or {"price": "100.10", "fixture": True},
        raw_payload_sha256="a" * 64,
        license_policy=LicensePolicy(license_id="FIXTURE-LICENSE", internal_research=True),
        evidence_roots=("a" * 64,),
        instrument=InstrumentRef(instrument_id="FIX-XYZ", symbol="FIXTURE-XYZ", venue="FIXTURE", asset_class="equity"),
        is_test_fixture=True,
    )


class TestNaiveDatetimeRejected(unittest.TestCase):
    def test_naive_rejected(self):
        with self.assertRaises(NaiveTimestampError):
            PointInTimeTimestamp(utc=datetime(2026, 1, 5, 14, 30), precision=TimePrecision.SECOND)

    def test_naive_rejected_in_canonical_json(self):
        with self.assertRaises(ValueError):
            canonical_json({"t": datetime(2026, 1, 5)})


class TestUTCPreservesSource(unittest.TestCase):
    def test_utc_conversion_preserves_raw_text_and_tz(self):
        est = timezone(timedelta(hours=-5))
        t = PointInTimeTimestamp(utc=datetime(2026, 1, 5, 9, 30, tzinfo=est),
                                 precision=TimePrecision.SECOND,
                                 raw_text="2026-01-05 09:30:00 EST", source_timezone="America/New_York")
        self.assertEqual(t.utc.tzinfo, timezone.utc)
        self.assertEqual(t.utc.hour, 14)
        self.assertEqual(t.raw_text, "2026-01-05 09:30:00 EST")
        self.assertEqual(t.source_timezone, "America/New_York")


class TestPrecisionNotInvented(unittest.TestCase):
    def test_second_source_cannot_carry_subsecond(self):
        with self.assertRaises(PrecisionInventionError):
            PointInTimeTimestamp(utc=UTC1.replace(microsecond=123456), precision=TimePrecision.SECOND)

    def test_millisecond_source_cannot_carry_microseconds(self):
        with self.assertRaises(PrecisionInventionError):
            PointInTimeTimestamp(utc=UTC1.replace(microsecond=123456), precision=TimePrecision.MILLISECOND)

    def test_valid_millisecond(self):
        t = PointInTimeTimestamp(utc=UTC1.replace(microsecond=123000), precision=TimePrecision.MILLISECOND)
        self.assertEqual(t.utc.microsecond, 123000)


class TestDecimalDeterminism(unittest.TestCase):
    def test_decimal_serializes_exactly(self):
        b = canonical_json({"px": Decimal("100.10")})
        self.assertIn(b"100.10", b)

    def test_identical_serializations_identical_hashes(self):
        e1, e2 = make_event(), make_event()
        self.assertEqual(e1.content_hash(), e2.content_hash())
        self.assertEqual(contract_hash(e1.to_canonical_dict()), contract_hash(e2.to_canonical_dict()))

    def test_different_payloads_different_hashes(self):
        self.assertNotEqual(make_event().content_hash(), make_event({"price": "100.11", "fixture": True}).content_hash())


class TestLicenseEnforcement(unittest.TestCase):
    def test_missing_policy_denies_non_test_use(self):
        with self.assertRaises(LicenseViolation):
            enforce_license(None, LicenseUse.INTERNAL_RESEARCH)

    def test_missing_policy_allows_test_fixture(self):
        enforce_license(None, LicenseUse.TEST_FIXTURE)

    def test_prohibited_redistribution_rejected(self):
        pol = LicensePolicy(license_id="L1", internal_research=True, redistribution=False)
        with self.assertRaises(LicenseViolation):
            enforce_license(pol, LicenseUse.REDISTRIBUTION)


class TestSchemaVersioning(unittest.TestCase):
    def test_mismatch_fails_explicitly(self):
        with self.assertRaises(SchemaVersionMismatch):
            check_schema("mios.canonical_event", "9.9.9")
        with self.assertRaises(SchemaVersionMismatch):
            check_schema("mios.unknown", "1.0.0")


class TestKnowledgeTimeNeverFabricated(unittest.TestCase):
    def test_fabricated_ingest_time_rejected(self):
        with self.assertRaises(KnowledgeTimeFabricationError):
            FourClocks(event_time=ts(UTC1), published_at=ts(UTC1), ingested_at=ts(UTC1),
                       system_time=ts(UTC1), ingested_at_genuine_capture=False)


class TestDeterministicClock(unittest.TestCase):
    def test_repeated_runs_byte_identical(self):
        def run() -> bytes:
            clock = DeterministicClock(UTC1, step_seconds=1.5)
            seq = [clock.now().isoformat() for _ in range(5)]
            return canonical_json(seq)
        self.assertEqual(run(), run())


class TestNoLiveOrderExposure(unittest.TestCase):
    def test_import_exposes_no_live_order(self):
        import mios
        from mios.guards.no_live_authority import assert_package_exposes_no_live_order
        assert_package_exposes_no_live_order(mios)

    def test_tree_scan_clean(self):
        import mios, os
        from mios.guards.no_live_authority import scan_tree_for_live_authority
        root = os.path.dirname(os.path.dirname(mios.__file__))
        result = scan_tree_for_live_authority(root)
        self.assertTrue(result["clean"], result["findings"])


class TestEventContractGuards(unittest.TestCase):
    def test_event_requires_evidence_root(self):
        with self.assertRaises(ValueError):
            CanonicalEvent(event_id="e", schema_name="mios.canonical_event", schema_version="1.0.0",
                           source=SourceRef(source_id="s", provider="p"), clocks=make_clocks(),
                           payload={}, raw_payload_sha256="a" * 64,
                           license_policy=LicensePolicy(license_id="L"), evidence_roots=tuple())

    def test_event_requires_raw_hash(self):
        with self.assertRaises(ValueError):
            CanonicalEvent(event_id="e", schema_name="mios.canonical_event", schema_version="1.0.0",
                           source=SourceRef(source_id="s", provider="p"), clocks=make_clocks(),
                           payload={}, raw_payload_sha256="short",
                           license_policy=LicensePolicy(license_id="L"), evidence_roots=("a" * 64,))


if __name__ == "__main__":
    unittest.main()
