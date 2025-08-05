import os
import pandas as pd
from datetime import date

from create_synthetic_sample_data import (
    coa_df,
    properties_df,
    generate_user,
    generate_vendors,
    generate_units,
    generate_tenants,
    generate_leases,
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

    user = generate_user()
    vendors = generate_vendors(coa_df, user, num_vendors=60)
    units = generate_units(properties_df)
    tenants = generate_tenants(properties_df, units)
    leases = generate_leases(properties_df, tenants, units)

    sched_all = generate_lease_pymnt_sched(leases, months_out=120)
    sched = sched_all[sched_all["schd_dt"].dt.date < date.today()]

    cust_invoices = generate_cust_invoices(sched, leases, tenants)
    vend_invoices = generate_vendor_invoices(
        vendors, properties_df, leases, coa_df, min_invoices=50, max_invoices=300
    )
    checkreg = generate_checkreg(vend_invoices)
    receipts = generate_receipts(cust_invoices)

    gl_data = generate_gltran(cust_invoices, vend_invoices, receipts, checkreg, coa_df)

    gltran = gl_data["gltran"]
    cust_invoices = gl_data["cust_invoices"]
    vend_invoices = gl_data["vend_invoices"]
    receipts = gl_data["receipts"]
    checkreg = gl_data["checkreg"]

    tenants.to_csv(os.path.join(hist_dir, "tenants.csv"), index=False)
    units.to_csv(os.path.join(hist_dir, "units.csv"), index=False)
    leases.to_csv(os.path.join(hist_dir, "leases.csv"), index=False)
    sched.to_csv(os.path.join(hist_dir, "payment_schedule.csv"), index=False)
    vendors.to_csv(os.path.join(hist_dir, "vendors.csv"), index=False)
    cust_invoices.to_csv(os.path.join(hist_dir, "cust_invoices.csv"), index=False)
    vend_invoices.to_csv(os.path.join(hist_dir, "vend_invoices.csv"), index=False)
    checkreg.to_csv(os.path.join(hist_dir, "checkreg.csv"), index=False)
    receipts.to_csv(os.path.join(hist_dir, "receipts.csv"), index=False)
    gltran.to_csv(os.path.join(hist_dir, "gltran.csv"), index=False)
    properties_df.to_csv(os.path.join(hist_dir, "properties.csv"), index=False)

    print("\u2713 Historical synthetic data generated")


if __name__ == "__main__":
    main()
