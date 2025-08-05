import os
import pandas as pd
import random
from datetime import date

from create_synthetic_sample_data import (
    coa_df,
    generate_lease_pymnt_sched,
    generate_cust_invoices,
    generate_vendor_invoices,
    generate_checkreg,
    generate_receipts,
    generate_gltran,
)


def main():
    hist_dir = os.path.join("data/raw/synthetic/historical", "yardi")
    os.makedirs(hist_dir, exist_ok=True)

    properties = pd.read_csv(os.path.join(hist_dir, "properties.csv"))
    vendors = pd.read_csv(os.path.join(hist_dir, "vendors.csv"))
    leases = pd.read_csv(os.path.join(hist_dir, "leases.csv"), parse_dates=["lease_start", "lease_end", "rent_start"])
    tenants = pd.read_csv(os.path.join(hist_dir, "tenants.csv"))

    sched_all = generate_lease_pymnt_sched(leases, months_out=120)
    sched = sched_all[sched_all["schd_dt"].dt.date == date.today()]

    if not sched.empty:
        cust_inv_new = generate_cust_invoices(sched, leases, tenants)
    else:
        cust_inv_new = pd.DataFrame(columns=[
            "id",
            "invoice_date",
            "due_date",
            "tenant_id",
            "property_id",
            "unit_id",
            "lease_id",
            "billing_period_start",
            "billing_period_end",
            "amount_due",
            "status",
            "payment_date",
            "description",
        ])

    vend_inv_new = generate_vendor_invoices(
        vendors, properties, leases, coa_df, min_invoices=5, max_invoices=15
    )
    vend_inv_new["invoice_date"] = date.today()
    vend_inv_new["due_date"] = vend_inv_new["invoice_date"] + pd.to_timedelta(
        [random.choice([15, 30]) for _ in range(len(vend_inv_new))], unit="d"
    )

    checkreg_new = generate_checkreg(vend_inv_new)
    receipts_new = generate_receipts(cust_inv_new)

    gl_data = generate_gltran(cust_inv_new, vend_inv_new, receipts_new, checkreg_new, coa_df)

    gltran_new = gl_data["gltran"]
    cust_inv_new = gl_data["cust_invoices"]
    vend_inv_new = gl_data["vend_invoices"]
    receipts_new = gl_data["receipts"]
    checkreg_new = gl_data["checkreg"]

    def append_csv(name, new_df):
        path = os.path.join(hist_dir, f"{name}.csv")
        if os.path.exists(path):
            existing = pd.read_csv(path)
            combined = pd.concat([existing, new_df], ignore_index=True)
        else:
            combined = new_df
        combined.to_csv(path, index=False)

    append_csv("cust_invoices", cust_inv_new)
    append_csv("vend_invoices", vend_inv_new)
    append_csv("checkreg", checkreg_new)
    append_csv("receipts", receipts_new)
    append_csv("gltran", gltran_new)

    print("\u2713 Daily transactions generated")


if __name__ == "__main__":
    main()
