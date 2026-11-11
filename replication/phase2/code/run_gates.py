"""Auditable synthetic gates with one explicit result per independent fixture."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import boundary
boundary.install()
import importlib
import json
import unittest
import traceback


class RecordedResult(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs); self.records=[]
    def addSuccess(self,test):
        super().addSuccess(test); self.records.append({"test":test.id(),"status":"PASS"})
    def addFailure(self,test,err):
        super().addFailure(test,err); self.records.append({"test":test.id(),"status":"FAIL","detail":"".join(traceback.format_exception(*err))})
    def addError(self,test,err):
        super().addError(test,err); self.records.append({"test":test.id(),"status":"FAIL","detail":"".join(traceback.format_exception(*err))})


class BoundaryTests(unittest.TestCase):
    def test_original_namespace_is_blocked(self):
        with self.assertRaises(ImportError): importlib.import_module("lstm_data")
    def test_nonallowlisted_project_file_is_blocked_without_read(self):
        with self.assertRaises(PermissionError): (boundary.ROOT/"src/FORBIDDEN_BOUNDARY_PROBE").open()
    def test_market_year_allowlist(self):
        self.assertEqual(len(boundary.MONTHS),174)
        for month in ("2010-06","2025-01","2026-01"):
            with self.assertRaises(PermissionError): boundary.data_path("canonical",month)


if __name__=="__main__":
    suite=unittest.defaultTestLoader.discover(str(boundary.PHASE/"tests"),pattern="test_*.py")
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(BoundaryTests))
    result=unittest.TextTestRunner(verbosity=2,resultclass=RecordedResult).run(suite)
    if not isinstance(result,RecordedResult): raise TypeError("Recorded test result required")
    receipt={"status":"PASS" if result.wasSuccessful() else "FAIL","tests":result.testsRun,"records":result.records,"real_fits":0}
    (boundary.PHASE/"audit/synthetic_gates.json").write_text(json.dumps(receipt,indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)
