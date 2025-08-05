import importlib.util
import pandas as pd
from pathlib import Path


def load_module():
    file_path = Path('scripts/create_synthetic_sample_data.py')
    spec = importlib.util.spec_from_file_location('synthetic', file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generate_lease_pymnt_sched_length_and_proration():
    module = load_module()
    lease_start = pd.Timestamp('2023-01-15')
    lease_end = pd.Timestamp('2023-12-31')
    df = pd.DataFrame([{
        'id': 'L1',
        'property_id': 'P1',
        'unit_id': 'U1',
        'tenant_id': 'T1',
        'lease_start': lease_start,
        'rent_start_date': lease_start,
        'lease_end': lease_end,
        'monthly_rent': 1000,
        'pro_rated_start': True,
        'payment_timing': 'In Advance'
    }])
    sched = module.generate_lease_pymnt_sched(df, months_out=12)
    assert len(sched) == 12
    assert bool(sched.iloc[0]['is_prorated']) is True
    assert sched.iloc[0]['schd_dt'].month == 1


def test_generate_lease_pymnt_sched_escalation():
    module = load_module()
    lease_start = pd.Timestamp('2023-01-01')
    lease_end = pd.Timestamp('2025-12-31')
    df = pd.DataFrame([
        {
            'id': 'L1',
            'property_id': 'P1',
            'unit_id': 'U1',
            'tenant_id': 'T1',
            'lease_start': lease_start,
            'rent_start_date': lease_start,
            'lease_end': lease_end,
            'monthly_rent': 1000,
            'pro_rated_start': False,
            'payment_timing': 'In Advance',
            'escalation_type': 'Fixed %',
            'escalation_rate': 0.10,
        }
    ])
    sched = module.generate_lease_pymnt_sched(df, months_out=25)
    assert sched.iloc[0]['pymnt_amt'] == 1000
    assert sched.iloc[12]['pymnt_amt'] == 1100
    assert sched.iloc[24]['pymnt_amt'] == 1210

