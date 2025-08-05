import importlib.util
import pandas as pd
from pathlib import Path


def load_module():
    file_path = Path('scripts/create_synthetic_sample_data.py')
    spec = importlib.util.spec_from_file_location('synthetic', file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generate_vendor_invoices_count():
    module = load_module()
    properties = module.properties_df.head(2).copy()
    vendors = pd.DataFrame([
        {"id": "V1", "service_type": "Legal & Regulatory Counsel", "name": "Vend 1"},
        {"id": "V2", "service_type": "Real Estate Appraisers", "name": "Vend 2"},
    ])
    leases = pd.DataFrame([
        {
            "id": "L1",
            "property_id": properties.iloc[0]["property_id"],
            "lease_start": pd.Timestamp("2024-01-01"),
        },
        {
            "id": "L2",
            "property_id": properties.iloc[1]["property_id"],
            "lease_start": pd.Timestamp("2024-01-01"),
        },
    ])
    inv = module.generate_vendor_invoices(vendors, properties, leases, module.coa_df, 1, 1)
    assert len(inv) == len(properties)
    assert set(inv["property_id"]) == set(properties["property_id"])


def test_generate_cust_invoices_matches_schedule():
    module = load_module()
    lease_start = pd.Timestamp("2024-01-01")
    lease_end = pd.Timestamp("2024-03-31")
    leases = pd.DataFrame([
        {
            "id": "L1",
            "property_id": "P1",
            "unit_id": "U1",
            "tenant_id": "T1",
            "lease_start": lease_start,
            "rent_start_date": lease_start,
            "lease_end": lease_end,
            "monthly_rent": 1000,
            "pro_rated_start": False,
            "payment_timing": "In Advance",
            "lease_type": "Commercial",
        }
    ])
    tenants = pd.DataFrame([{"id": "T1", "business_name": "Tenant1"}])
    sched = module.generate_lease_pymnt_sched(leases, months_out=3)
    cust = module.generate_cust_invoices(sched, leases, tenants)
    assert len(cust) == len(sched)
    assert set(cust["lease_id"]) == {"L1"}
