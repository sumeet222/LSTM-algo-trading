"""Independent small source-policy fixtures; no bulk raw reconstruction."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"code"))
import boundary
boundary.install()
import unittest
import numpy as np
import pandas as pd
from contract import proxy_closes
from geometry import MINUTE,factor,price_basis,volume_regime


class SourceContractTests(unittest.TestCase):
    def test_completed_bin_proxy_cannot_be_retracted_by_later_bin(self):
        op=pd.Timestamp("2024-01-02 14:30",tz="UTC").value
        present=np.r_[np.arange(58),np.arange(64,120)]
        frame=pd.DataFrame({"timestamp":pd.to_datetime(op+present*MINUTE,utc=True),"close":np.full(len(present),80.)})
        proxies=proxy_closes(frame,op,op+120*MINUTE,np.nan)
        self.assertEqual(proxies[op+58*MINUTE],80.)
        self.assertEqual(proxies[op+59*MINUTE],80.)
        for minute in range(60,64): self.assertNotIn(op+minute*MINUTE,proxies)

    def test_long_samebin_run_and_session_open_gap_remain_missing(self):
        op=pd.Timestamp("2024-01-02 14:30",tz="UTC").value
        present=np.r_[np.arange(2,10),np.arange(16,60)]
        frame=pd.DataFrame({"timestamp":pd.to_datetime(op+present*MINUTE,utc=True),"close":np.full(len(present),80.)})
        proxies=proxy_closes(frame,op,op+60*MINUTE,80.)
        self.assertEqual(proxies,{})

    def test_actions_price_ratio_volume_and_cop_identity(self):
        dates=np.array(["2020-08-28","2020-08-31"])
        f=factor("AAPL",dates); np.testing.assert_array_equal(f,[.25,1.])
        self.assertEqual(100*f[0],25.)
        self.assertAlmostEqual(np.log((110*f[0])/(100*f[0])),np.log(110/100),places=12)
        volume=np.array([80.,80.]); np.testing.assert_array_equal(volume,[80.,80.])
        self.assertNotEqual(*volume_regime("AAPL",dates))
        np.testing.assert_array_equal(price_basis("COP",["2012-04-30","2012-05-01"]),[0,1])
        P,C,O,E=80.,88.,84.,90.
        legs=np.log(np.array([C/P,O/C,E/O]))
        self.assertAlmostEqual(legs.sum(),np.log(E/P),places=12)
        self.assertGreater(np.abs(legs).sum(),abs(legs.sum()))

if __name__=="__main__": unittest.main()
