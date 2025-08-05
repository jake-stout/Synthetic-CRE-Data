import pandas as pd
import uuid
import random
import os
import sys
import calendar
from dateutil.relativedelta import relativedelta


from faker import Faker
from datetime import datetime, timedelta, date

# ------------ Setup ------------
fake = Faker()
random.seed(42)
output_dir = "data/raw/synthetic/simulated"
os.makedirs(os.path.join(output_dir, "yardi"), exist_ok=True)
os.makedirs(os.path.join(output_dir, "banking"), exist_ok=True)

# ------------ Helper Functions ------------
def random_bool(): return random.choice([True, False])
def random_date(start_days_ago=180, end_days_ago=0):
    return datetime.now() - timedelta(days=random.randint(end_days_ago, start_days_ago))

# ------------ File Paths ------------
coa_path = "data/raw/synthetic/Structured_Chart_of_Accounts.csv"
prop_listing_path = "data/raw/synthetic/Enhanced_Property_Listing.xlsx"

coa_df = pd.read_csv(coa_path)
properties_df = pd.read_excel(prop_listing_path)

# ------------ Utilities ------------
def uid(): return uuid.uuid4().hex
today = datetime.today().date()

# Add property_id if missing
if "property_id" not in properties_df.columns:
    properties_df["property_id"] = [uid() for _ in range(len(properties_df))]

# ------------ Simulate Users ------------
def generate_user(count=None):
    if count is None:
        count = random.randint(5, 10)

    user = []

    def generate_unique_user_ids(count, id_length=6):
        user_ids = set()
        while len(user_ids) < count:
            rand_num = random.randint(0, 10**id_length - 1)
            padded_id = f"U{rand_num:0{id_length}d}"
            user_ids.add(padded_id)
        return list(user_ids)

    # Generate unique user_ids once
    user_ids = generate_unique_user_ids(count)

    for i in range(count):
        user.append({
            "id": uid(),
            "user_id": user_ids[i],
            "user_name": fake.name()
        })

    return pd.DataFrame(user)

# ------------ Simulate Vendors ------------
def generate_vendors(coa, user, num_vendors):  # Make vendor count configurable
    vendor_categories = [
        ("Legal & Regulatory Counsel", ["LLP", "Law Group", "Counsel"], 0.08),
        ("Real Estate Appraisers", ["Realty Advisors", "Appraisal Services"], 0.05),
        ("Title & Escrow Services", ["Title Co.", "Escrow Services", "Closing Group"], 0.05),
        ("Financial & Tax Advisors", ["Capital Advisors", "CPA Group", "Tax Consulting"], 0.07),
        ("Investor Relations Platforms", ["Investor Services", "Capital Partners", "IR Systems"], 0.03),
        ("Market Research & Analytics", ["Analytics Group", "Market Insights", "Data Advisors"], 0.04),
        ("Architecture & Design Firms", ["Design Group", "Studio", "Architects"], 0.08),
        ("General Contractors", ["Construction", "Builders", "Contracting"], 0.10),
        ("Engineering Services", ["Engineering", "Systems Design", "Infrastructure Group"], 0.07),
        ("Environmental Consultants", ["Environmental Group", "Eco Services", "EnviroTech"], 0.03),
        ("Zoning & Permitting Consultants", ["Zoning Group", "Permitting Services", "Code Advisors"], 0.03),
        ("ESG & Sustainability Consultants", ["Green Partners", "Sustainability Group", "ESG Advisors"], 0.03),
        ("Property Management Firms", ["Realty Management", "Asset Group", "Property Services"], 0.08),
        ("Maintenance & Janitorial Vendors", ["Facility Services", "CleanTech", "Maintenance Co."], 0.06),
        ("Security & Surveillance Providers", ["Security Solutions", "Surveillance Group", "CRE Watch"], 0.04),
        ("Leasing Brokers & Tenant Reps", ["Realty", "Leasing Group", "Tenant Advisors"], 0.05),
        ("Software Providers", ["Technologies", "Software Group", "Systems"], 0.05),
        ("Construction Managers", ["Construction Management", "Build Group", "Project Controls"], 0.05),
        ("Landscaping & Outdoor Services", ["Landscaping", "Outdoor Services", "GreenScape"], 0.05),
    ]

    vendors = []

    for _ in range(num_vendors):
        # Select a vendor category
        categories, suffix_lists, category_weights = zip(*vendor_categories)
        idx = random.choices(range(len(categories)), weights=category_weights, k=1)[0]
        vendor_category = categories[idx]
        suffix = random.choice(suffix_lists[idx])
        vendor_name = random.choices(
            population=[f"{fake.last_name()} {suffix}", fake.company()],
            weights=[0.75, 0.25],
            k=1
        )[0]


        # Generate creator and modifier user_ids
        creator = random.choice(user["user_id"].tolist())
        modifier = creator if random.random() < 0.7 else random.choice(user["user_id"].tolist())
        
        # Generate creator and modifier dates
        created_at = fake.date_time_between(start_date="-10y", end_date="now")
        modified_at = fake.date_time_between(start_date=created_at, end_date="now")

        vendors.append({
            "id": uid(),
            "name": vendor_name,
            "service_type": vendor_category,
            "address": fake.address().replace("\n", ", "),  # Flatten line breaks
            "contact_name": fake.name(),
            "contact_email": fake.email(),
            "phone": fake.phone_number(),
            "tax_id": fake.ssn(),
            "vendor_status": random.choices(population=["Active", "Inactive"], weights=[0.9, 0.1], k=1)[0],
            "approved_vendor": random.choice([True, False]),
            "created_by": creator,
            "created_at": created_at,
            "modified_by": modifier,
            "modified_at": modified_at
        })
    return pd.DataFrame(vendors)

# ------------ Simulate Units ------------
def generate_units(properties):
    units = []

    for _, row in properties.iterrows():
        num_units = int(row.get("Units", 0))
        num_floors = int(row.get("Floors", 1))
        total_sq_ft = row.get("Total Sq Ft", 0)
        avg_sq_ft = int(total_sq_ft / num_units) if num_units > 0 else 0
        occupancy_rate = float(row.get("Occupancy", 0)) 
        year_built = int(row.get("Year Built", 1980))

        # Safe fallback if the property has no usable year
        start_renovation_date = datetime(year=year_built, month=1, day=1)

        # Calculate exact number of occupied units
        num_occupied = int(round(occupancy_rate * num_units))
        occupied_indices = set(random.sample(range(num_units), num_occupied))

        for i in range(num_units):
            created_date = fake.date_between(start_date="-10y", end_date="-1y")
            modified_date = fake.date_between(start_date=created_date, end_date="today")
            floor_number = random.randint(1, max(1, num_floors))
            unit_number = f"{floor_number:02d}{i+1:03d}"  # e.g., 03001 = floor 3, unit 1

            is_occupied = i in occupied_indices
            occupancy_status = "Occupied" if is_occupied else "Vacant"

            # Ensure last_renovated is after Year Built and at least a year ago
            last_renovated = fake.date_between(
                start_date=start_renovation_date,
                end_date=datetime.now()
            )
            
            last_occupied = fake.date_between(start_date="-5y", end_date="today") if occupancy_status == "Vacant" else None
            last_vacated = fake.date_between(start_date="-5y", end_date="today") if occupancy_status == "Occupied" else None

            units.append({
                "id": uid(),
                "property_id": row["property_id"],
                "unit_number": unit_number,
                "floor_number": floor_number,
                "sq_ft": avg_sq_ft,
                "occupancy_status": occupancy_status,
                "last_renovated": last_renovated,
                "last_occupied": last_occupied,
                "last_vacated": last_vacated,
                "created_at": created_date,
                "modified_at": modified_date
            })
            
    return pd.DataFrame(units)

# ------------ Simulate Tenants ------------
def generate_tenants(properties_df, units_df):
    tenants = []

    # Prepare unit-level lookup for assigning tenants only to occupied units
    
    occupied_units = units_df[units_df["occupancy_status"] == "Occupied"]
    if occupied_units.empty:
        print("No occupied units available across all properties — cannot assign tenants. Exiting program.")
        sys.exit(1)
    
    available_units = occupied_units.sample(frac=1).reset_index(drop=True)  # Shuffle to randomize
    
    # Define mapping logic
    # Mapping subtypes to broader categories
    subtype_category_map = {
        
        # Commercial
        "Other": "Commercial", 
        
        # Industrial
        "Distribution Center": "Industrial", "Flex Industrial": "Industrial", "Large-Scale Distribution Facility": "Industrial", 
        "Light Industrial": "Industrial", "Multi-Tenant Industrial": "Industrial", "R&D/Flex Industrial": "Industrial", 
        "Stabilized Warehouse": "Industrial", "Warehouse/Distribution": "Industrial", 
        
        # Mixed Use
        "Mixed-Use Office": "Mixed-Use", 
        
        # Office
        "Urban Office": "Office", "Business Park": "Office", "CBD Office": "Office", "Class A Office": "Office", 
        "Class B Office": "Office", "Corporate Office": "Office", "Downtown Office": "Office", "Government/Medical Office": "Office", 
        "Historic Building / CBD Office": "Office", "Medical Office": "Office", 
        "Office Campus": "Office", "Office Park": "Office", "Office Tower": "Office", "Small Office/Creative Space": "Office", 
        "Small Professional Suites": "Office", "Stabilized Government Office": "Office", "Suburban Office": "Office", "Tech Campus": "Office", 
        
        # Retail
        "Flex Space": "Retail", "Street-Level Retail": "Retail", 
    }

    # Category-specific metadata
    industry_map = {
    "Office": [
        "Law Firm", "Accounting", "Architecture", "Consulting", "Corporate HQ", "Financial Services",
        "Tech Startup", "Insurance", "Nonprofit", "Real Estate Brokerage", "Marketing & PR"
    ],
    "Industrial": [
        "Third-Party Logistics (3PL)", "Light Manufacturing", "Auto Parts Distribution",
        "Aerospace Supply Chain", "Food & Beverage Processing", "Packaging & Warehousing",
        "Medical Supplies", "E-commerce Fulfillment"
    ],
    "Retail": [
        "Coffee Shop", "Fitness Studio", "Boutique Retail", "Salon & Spa",
        "Quick-Serve Restaurant", "Pharmacy", "Franchise Retailer", "Pop-Up Retail"
    ],
    "Mixed-Use": [
        "Coworking Operator", "Design Studio", "Tech Lab", "Creative Agency",
        "Local Retail + Office", "Startup HQ", "Nonprofit Hub"
    ],
    "Commercial": [
        "City Government", "Education Services", "Coworking Space", "Job Training Center",
        "Community Organization", "Remote Work Hub", "Startup Incubator"
    ]
}

    move_in_reason_map = {
    "Office": [
        "Lease expiration at prior location", "Desire for upgraded amenities",
        "Strategic relocation closer to clients", "Consolidation due to hybrid work",
        "New regional headquarters", "Better public transit access"
    ],
    "Industrial": [
        "Warehouse capacity expansion", "Consolidating logistics operations",
        "Relocating closer to shipping routes", "Upgrade to high-bay facility",
        "Automation and process redesign", "Temperature-controlled storage needs"
    ],
    "Retail": [
        "Expansion into new market", "Street visibility and foot traffic",
        "New franchise opening", "Proximity to target demographic",
        "Lease buyout opportunity", "Seasonal pop-up location"
    ],
    "Mixed-Use": [
        "Flexible zoning and usage", "Live-work opportunity",
        "Creative space needs", "Integrated customer and back-office location",
        "Growth-stage business flexibility"
    ],
    "Commercial": [
        "Community-focused relocation", "Short-term lease with flexible terms",
        "Alternative use designation", "Shared service model pilot",
        "Strategic public-private initiative"
    ]
}

    # Iterate through available units and assign 1 tenant per occupied unit
    for _, unit in available_units.iterrows():
        property_row = properties_df[properties_df["property_id"] == unit["property_id"]]
        if property_row.empty:
            continue

        property_data = property_row.iloc[0]
        subtype = str(property_data.get("Subtype", "Office"))
        industry_options = industry_map.get(subtype, ["General Business"])
        move_in_reasons = move_in_reason_map.get(subtype, ["Expansion", "Relocation"])

        industry = random.choice(industry_options)
        tenants.append({
            "id": uid(),
            "property_id": unit["property_id"],
            "unit_id": unit["id"],
            "business_name": fake.company(),
            "primary_contact": fake.name(),
            "email": fake.company_email(),
            "phone": fake.phone_number(),
            "industry": industry,
            "annual_revenue": random.choice(["<1M", "1M–5M", "5M–25M", "25M+"]),
            "employee_count": (
                random.randint(5, 30) if subtype == "Retail" else
                random.randint(20, 200) if subtype == "Office" else
                random.randint(50, 500)
            ),
            "lease_start_date": unit["last_vacated"],
            "move_in_reason": random.choice(move_in_reasons)
        })

    return pd.DataFrame(tenants)

# ------------ Simulate Leases ------------
def generate_leases(properties, tenants, units):
    leases = []

    lease_term_dict = {
        "Office": ([1, 3, 5, 10], [0.2, 0.3, 0.3, 0.2]),
        "Industrial": ([3, 5, 10, 15], [0.1, 0.4, 0.3, 0.2]),
        "Retail": ([1, 3, 5, 10], [0.2, 0.3, 0.3, 0.2]),
        "Mixed-Use": ([1, 3, 5, 10], [0.25, 0.35, 0.25, 0.15]),
        "Commercial": ([1, 3, 5, 10], [0.4, 0.3, 0.2, 0.1])
    }

    rent_per_sqft_by_category = {
        "Office": (25, 45),
        "Industrial": (5, 12),
        "Retail": (20, 60),
        "Mixed-Use": (18, 40),
        "Commercial": (10, 30)
    }

    auto_renew_weights_by_type = {
        "Office": [0.3, 0.7],
        "Retail": [0.4, 0.6],
        "Industrial": [0.2, 0.8],
        "Mixed-Use": [0.35, 0.65],
        "Commercial": [0.35, 0.65]
    }

    category_multiplier_map = {
        "Industrial": 1.0,
        "Office": 1.5,
        "Retail": 2.0,
        "Mixed-Use": 2.0,
        "Commercial": 1.25
    }

    occupied_units = units[units["occupancy_status"] == "Occupied"]

    for _, unit in occupied_units.iterrows():
        tenant = tenants.sample(1).iloc[0]
        credit_score = tenant.get("credit_score", 700)

        # Dates
        start_date = pd.to_datetime(unit.get("last_vacated", today)).date()
        if pd.isna(start_date):
            start_date = today.date()

        property_row = properties[properties["property_id"] == unit["property_id"]]
        if property_row.empty:
            continue

        property = property_row.iloc[0]
        property_type = property.get("Type", "Commercial")
        terms, weights = lease_term_dict.get(property_type, ([1, 3, 5, 10], [0.25, 0.35, 0.25, 0.15]))

        lease_term_years = random.choices(terms, weights)[0]
        end_date = start_date + timedelta(days=lease_term_years * 365)

        # Base rent
        low, high = rent_per_sqft_by_category.get(property_type, (20, 40))
        base_rate = random.uniform(low, high)
        base_rent = (unit["sq_ft"] * base_rate) / 12
        cam_charges = unit["sq_ft"] * 1.5
        monthly_rent = round(base_rent + cam_charges, 2)

        # Deposit
        risk_multiplier = 1 if credit_score >= 750 else 2 if credit_score >= 650 else 3
        category_multiplier = category_multiplier_map.get(property_type, 1.5)
        blended_multiplier = risk_multiplier * category_multiplier
        deposit_by_multiplier = monthly_rent * blended_multiplier
        deposit_by_annual_percent = monthly_rent * 12 * 0.10
        deposit = round(max(deposit_by_multiplier, deposit_by_annual_percent), 2)

        # Lease logic
        lease_status = "Terminated" if end_date < today else "Pending" if start_date > today else "Active"
        auto_renew = random.choices([True, False], weights=auto_renew_weights_by_type.get(property_type, [0.35, 0.65]))[0]
        payment_timing = "In Advance" if property_type in ["Office", "Retail", "Mixed-Use"] else "In Arrears"

        # Escalation
        escalation_type = random.choice(["Fixed %", "CPI", None])
        escalation_rate = 0.03 if escalation_type == "Fixed %" else None

        # NEW: rent logic flags
        fixed_rent_commencement = random.choice([True, False])
        rent_deferral_months = random.choice([0, 0, 1, 2])  # weighted toward 0
        free_rent_months = random.choice([0, 0, 1, 2, 3])   # common options
        pro_rated_start = start_date.day > 1

        # Calculate rent_start_date
        if fixed_rent_commencement:
            rent_start_date = (start_date + relativedelta(months=1)).replace(day=1)
        else:
            rent_start_date = start_date

        rent_start_date += relativedelta(months=rent_deferral_months)

        leases.append({
            "id": uid(),
            "tenant_id": tenant["id"],
            "unit_id": unit["id"],
            "property_id": unit["property_id"],
            "lease_start": start_date,
            "lease_end": end_date,
            "rent_start_date": rent_start_date,
            "deposit_amount": deposit,
            "monthly_rent": monthly_rent,
            "payment_timing": payment_timing,
            "lease_status": lease_status,
            "auto_renew": auto_renew,
            "lease_type": "Commercial",
            "late_fee_terms": "5% after 5 days",
            "early_termination_clause": "2 months rent",
            "pro_rated_start": pro_rated_start,
            "escalation_clause": random.choice([True, False]),
            "expense_reimbursement_clause": random.choice([True, False]),
            "escalation_type": escalation_type,
            "escalation_rate": escalation_rate,
            "fixed_rent_commencement": fixed_rent_commencement,
            "rent_deferral_months": rent_deferral_months,
            "free_rent_months": free_rent_months
        })

    return pd.DataFrame(leases)

# ------------ Simulate Rent Roll ------------ 
"""
def generate_rentroll(properties_df, leases_df):
    rentroll = []
    today = datetime.now().date()

    for _, lease in leases_df.iterrows():
        # Simulate 6 months of rent from lease start
        lease_start = lease.get("start_date", today - timedelta(days=180))
        lease_end = lease.get("end_date", today + timedelta(days=365))
        lease_term_months = (lease_end.year - lease_start.year) * 12 + lease_end.month - lease_start.month

        base_rent = random.randint(1500, 12000)  # CRE monthly base rent
        cam_charge = round(random.uniform(0.5, 3.5) * 100, 2)  # CAM recovery
        utility_charge = round(random.uniform(50, 500), 2)
        escalation_type = random.choice(["CPI", "Fixed %", None])
        escalation_pct = round(random.uniform(2, 4), 2) if escalation_type == "Fixed %" else 0

        for i in range(min(6, lease_term_months)):
            schedule_date = (lease_start + timedelta(days=30 * i)).replace(day=1)

            # Simulate rent escalation
            if escalation_type == "Fixed %":
                effective_rent = int(base_rent * ((1 + escalation_pct / 100) ** i))
            elif escalation_type == "CPI":
                cpi_adjustment = random.uniform(0.98, 1.05)
                effective_rent = int(base_rent * cpi_adjustment ** i)
            else:
                effective_rent = base_rent

            # Status logic: posted/collected if in past, projected if in future
            if schedule_date < today:
                status = random.choice(["Posted", "Collected"])
            else:
                status = "Projected"

            rentroll.extend([
                {
                    "id": uid(),
                    "property_id": lease["property_id"],
                    "unit_id": lease["unit_id"],
                    "lease_id": lease["id"],
                    "schedule_date": schedule_date,
                    "type": "Base Rent",
                    "amount": effective_rent,
                    "status": status
                },
                {
                    "id": uid(),
                    "property_id": lease["property_id"],
                    "unit_id": lease["unit_id"],
                    "lease_id": lease["id"],
                    "schedule_date": schedule_date,
                    "type": "CAM Recovery",
                    "amount": cam_charge,
                    "status": status
                },
                {
                    "id": uid(),
                    "property_id": lease["property_id"],
                    "unit_id": lease["unit_id"],
                    "lease_id": lease["id"],
                    "schedule_date": schedule_date,
                    "type": "Utilities",
                    "amount": utility_charge,
                    "status": status
                }
            ])

    return pd.DataFrame(rentroll)
"""

def generate_lease_pymnt_sched(leases_df, months_out):
    schedule = []

    for _, lease in leases_df.iterrows():
        lease_id = lease["id"]
        property_id = lease["property_id"]
        unit_id = lease["unit_id"]
        tenant_id = lease["tenant_id"]

        lease_start = pd.to_datetime(lease.get("lease_start", today))
        rent_start = pd.to_datetime(lease.get("rent_start_date", lease_start))
        lease_end = pd.to_datetime(lease.get("lease_end", lease_start + timedelta(days=730)))

        monthly_rent = lease.get("monthly_rent", 10000)
        escalation_type = lease.get("escalation_type")
        escalation_rate = lease.get("escalation_rate", 0.03 if escalation_type == "Fixed %" else 0)
        pay_in_advance = lease.get("payment_timing", "In Advance") == "In Advance"
        free_rent_months = lease.get("free_rent_months", 0)
        pro_rated_start = lease.get("pro_rated_start", False)

        first_bill_month = rent_start.replace(day=1)
        lease_term_months = (lease_end.year - first_bill_month.year) * 12 + (lease_end.month - first_bill_month.month)

        for i in range(min(months_out, lease_term_months + 1)):
            bill_month = first_bill_month + relativedelta(months=i)
            bill_period_start = bill_month
            bill_period_end = (bill_month + relativedelta(months=1)) - timedelta(days=1)

            # Check if this is within free rent period
            if i < free_rent_months:
                continue

            # Escalation logic
            if escalation_type == "Fixed %" and i >= 12:
                effective_rent = round(monthly_rent * (1 + escalation_rate))
            elif escalation_type == "CPI" and i >= 12:
                cpi = random.uniform(1.01, 1.04)
                effective_rent = round(monthly_rent * cpi)
            else:
                effective_rent = monthly_rent

            # Proration only for the first month
            is_prorated = False
            if i == 0 and pro_rated_start:
                days_in_month = calendar.monthrange(lease_start.year, lease_start.month)[1]
                proration_factor = (days_in_month - lease_start.day + 1) / days_in_month
                effective_rent = round(effective_rent * proration_factor, 2)
                is_prorated = True

            # Billing date logic
            bill_date = bill_month if pay_in_advance else bill_month + relativedelta(months=1)

            schedule.append({
                "id": uid(),
                "lease_id": lease_id,
                "property_id": property_id,
                "unit_id": unit_id,
                "tenant_id": tenant_id,
                "schd_dt": bill_date,
                "pymnt_amt": effective_rent,
                "escal_type": escalation_type,
                "is_prorated": is_prorated,
                "bill_period_start": bill_period_start,
                "bill_period_end": bill_period_end,
                "billing_basis": "Advance" if pay_in_advance else "Arrears",
                "yr": bill_month.year,
                "mo_txt": bill_month.strftime("%B")
            })

    return pd.DataFrame(schedule)

# ------------ Simulate Customer Invoices ------------
def generate_cust_invoices(payment_schedule, leases, tenants):
    cust_invoices = []

    for _, payment in payment_schedule.iterrows():
        lease_id = payment["lease_id"]
        tenant_id = payment.get("tenant_id")
        property_id = payment.get("property_id")
        unit_id = payment.get("unit_id")
        invoice_date = payment["schd_dt"].date()
        amount_due = payment["pymnt_amt"]
        billing_start = payment["bill_period_start"]
        billing_end = payment["bill_period_end"]
        billing_basis = payment["billing_basis"]
        is_prorated = payment["is_prorated"]

        due_date = invoice_date + timedelta(days=random.choice([5, 7, 10]))

        days_past_due = (today - due_date).days
        if days_past_due <= 0:
            status = "Unpaid"
        elif days_past_due <= 30:
            status = random.choices(["Unpaid", "Paid"], weights=[0.7, 0.3])[0]
        else:
            status = random.choices(["Paid", "Overdue"], weights=[0.7, 0.3])[0]

        lease_row = leases[leases["id"] == lease_id]
        tenant_row = tenants[tenants["id"] == tenant_id]

        lease_type = lease_row.iloc[0]["lease_type"] if not lease_row.empty else "Commercial"
        tenant_name = tenant_row.iloc[0]["business_name"] if not tenant_row.empty else "Tenant"

        description = f"{lease_type} rent due for {tenant_name} covering {billing_start.strftime('%b %Y')}"
        if is_prorated:
            description += " (prorated)"
        if billing_basis == "Advance":
            description += " — billed in advance"
        elif billing_basis == "Arrears":
            description += " — billed in arrears"

        cust_invoices.append({
            "id": uid(),
            "invoice_date": invoice_date,
            "due_date": due_date,
            "tenant_id": tenant_id,
            "property_id": property_id,
            "unit_id": unit_id,
            "lease_id": lease_id,
            "billing_period_start": billing_start,
            "billing_period_end": billing_end,
            "amount_due": amount_due,
            "status": status,
            "payment_date": None,
            "description": description
        })

    return pd.DataFrame(cust_invoices)

# ------------ Simulate Vendor Invoices ------------
def generate_vendor_invoices(vendors, properties_df, leases, coa, min_invoices, max_invoices):
    vend_invoices = []

    vendor_gl_mapping = {
        "Legal & Regulatory Counsel": (["60220", "60230", "60325", "60415", "60520", "60530", "60615", "60715"], [0.02, 0.02, 0.02, 0.04, 0.05, 0.15, 0.5, 0.15]),
        "Real Estate Appraisers": (["60210", "60520", "60530"], [0.7, 0.15, 0.15]),
        "Title & Escrow Services": (["60265", "60620", "60520", "60530"], [0.4, 0.4, 0.1, 0.1]),
        "Financial & Tax Advisors": (["60510", "60515", "60715", "60520", "60530"], [0.25, 0.2, 0.45, 0.05, 0.05]),
        "Investor Relations Platforms": (["60115", "60720"], [0.2, 0.8]),
        "Market Research & Analytics": (["60810", "60815"], [0.4, 0.6]),
        "Architecture & Design Firms": (["60215", "60220", "60235", "60415"], [0.6, 0.2, 0.1, 0.1]),
        "General Contractors": (["50210", "60235", "60240"], [0.15, 0.8, 0.05]),
        "Engineering Services": (["60225"], [1.0]),
        "Environmental Consultants": (["60255", "60260", "60525"], [0.75, 0.125, 0.125]),
        "Zoning & Permitting Consultants": (["60230", "60250", "60265"], [0.25, 0.375, 0.375]),
        "ESG & Sustainability Consultants": (["60410", "60415", "60420"], [0.5, 0.25, 0.25]),
        "Property Management Firms": (["50130", "50135"], [0.5, 0.5]),
        "Maintenance & Janitorial Vendors": (["50120", "50210", "50235"], [0.3, 0.3, 0.4]),
        "Security & Surveillance Providers": (["50220", "50240"], [0.4, 0.6]),
        "Leasing Brokers & Tenant Reps": (["50110", "50125"], [0.5, 0.5]),
        "Software Providers": (["60120", "60315", "60320"], [0.4, 0.3, 0.3]),
        "Construction Managers": (["60240"], [1.0]),
        "Landscaping & Outdoor Services": (["50120", "50210"], [0.8, 0.2]),
    }

    for _, property_row in properties_df.iterrows():
        num_invoices = random.randint(min_invoices, max_invoices)

        for _ in range(num_invoices):
            
            vendor_row = vendors.sample(1).iloc[0]
            property_row = properties_df.sample(1).iloc[0]

            vendor_category = vendor_row["service_type"]
            gls, gl_weights = vendor_gl_mapping.get(vendor_category, ([], []))
            chosen_gl = random.choices(gls, weights=gl_weights, k=1)[0] if gls else None

            coa_info = coa[coa["acct_number"].astype(str) == chosen_gl]
            coa_info = coa_info.iloc[0].to_dict() if not coa_info.empty else {
                "acct_number": chosen_gl,
                "acct_name": "Unknown",
                "acct_class": "Unclassified",
                "acct_type": "Unknown"
            }

            lease_start = leases[leases["property_id"] == property_row["property_id"]]["lease_start"].min()
            lease_start = lease_start if pd.notna(lease_start) else date.today() - relativedelta(years=2)
            invoice_date = fake.date_between(start_date=lease_start, end_date="today")
            due_date = invoice_date + timedelta(days=random.choice([15, 30]))
            amount_due = round(random.uniform(500, 10000), 2)

            # Simulate payment status
            days_past_due = (today - due_date).days
            if days_past_due <= 0:
                status = "Unpaid"
            elif days_past_due <= 30:
                status = random.choices(["Unpaid", "Paid"], [0.7, 0.3])[0]
            else:
                status = random.choices(["Paid", "Overdue"], [0.7, 0.3])[0]

            description = f"{vendor_category} invoice for {property_row.get('property_name', 'Property')}"

            vend_invoices.append({
                "id": uid(),
                "invoice_date": invoice_date,
                "due_date": due_date,
                "property_id": property_row["property_id"],
                "vendor_id": vendor_row["id"],
                "vendor_name": vendor_row["name"],
                "amount_due": amount_due,
                "status": status,
                "payment_date": None,
                "description": description,
                "gl_account": coa_info["acct_number"],
                "gl_account_name": coa_info["acct_name"],
                "gl_class": coa_info["acct_class"],
                "gl_type": coa_info["acct_type"]
            })

    return pd.DataFrame(vend_invoices)

# ------------ Simulate Check Register ------------ (based on invoices that are marked "Paid")
def generate_checkreg(vend_invoices):
    checkreg = []
    paid_invoices = vend_invoices[vend_invoices["status"] == "Paid"]
    for idx, inv in paid_invoices.iterrows():
        lag_choice = random.choices(
            ["on_time", "late_30", "late_60", "late_90"],
            weights=[0.70, 0.15, 0.10, 0.05],
        )[0]
        if lag_choice == "on_time":
            lag_days = random.randint(0, max(0, (inv["due_date"] - inv["invoice_date"]).days))
        elif lag_choice == "late_30":
            lag_days = random.randint(1, 30)
        elif lag_choice == "late_60":
            lag_days = random.randint(31, 60)
        else:
            lag_days = random.randint(90, 120)
        check_date = inv["due_date"] + timedelta(days=lag_days)
        vend_invoices.at[idx, "payment_date"] = check_date
        checkreg.append({
            "id": uid(),
            "invoice_id": inv["id"],
            "vendor_id": inv["vendor_id"],
            "check_number": str(random.randint(10000, 99999)),
            "check_date": check_date,
            "amount": inv["amount_due"],
            "property_id": inv["property_id"],
            "gltran_id": None,
            "created_by": "system",
            "created_at": datetime.now(),
            "modified_by": "system",
            "modified_at": datetime.now()
        })
    return pd.DataFrame(checkreg)

# ------------ Simulate Receipts ------------ (simulate receipts from leases)
def generate_receipts(cust_invoices):
    receipts = []
    paid_invoices = cust_invoices[cust_invoices["status"] == "Paid"]
    for idx, inv in paid_invoices.iterrows():
        lag_choice = random.choices(
            ["on_time", "late_30", "late_60", "late_90"],
            weights=[0.70, 0.15, 0.10, 0.05],
        )[0]
        if lag_choice == "on_time":
            lag_days = random.randint(0, max(0, (inv["due_date"] - inv["invoice_date"]).days))
        elif lag_choice == "late_30":
            lag_days = random.randint(1, 30)
        elif lag_choice == "late_60":
            lag_days = random.randint(31, 60)
        else:
            lag_days = random.randint(90, 120)
        receipt_date = inv["due_date"] + timedelta(days=lag_days)
        cust_invoices.at[idx, "payment_date"] = receipt_date
        receipts.append({
            "id": uid(),
            "invoice_id": inv["id"],
            "tenant_id": inv["tenant_id"],
            "receipt_id": str(random.randint(10000,99999)),
            "receipt_date": receipt_date,
            "amount": inv["amount_due"],
            "payment_method": random.choice(["ACH", "Check", "Credit Card"]),
            "property_id": inv["property_id"],
            "gltran_id": None,
            "created_by": "system",
            "created_at": datetime.now(),
            "modified_by": "system",
            "modified_at": datetime.now()
        })
    return pd.DataFrame(receipts)

# ------------ Simulate GL Transactions ------------
def generate_gltran(cust_invoices, vend_invoices, receipts, checkreg, coa_df):
    gl_entries = []

    def resolve_account(name):
        match = coa_df[coa_df["acct_name"].str.contains(name, case=False, na=False)]
        return match.iloc[0]["acct_name"] if not match.empty else name

    def create_entry(source, source_id, property_id, amount, debit_acct, credit_acct, tenant_id=None, vendor_id=None):
        batch_id = uid()
        timestamp = datetime.now()
        cleared = random_bool()

        for entry_type, acct in [("Debit", debit_acct), ("Credit", credit_acct)]:
            gl_entries.append({
                "id": uid(),
                "date": timestamp.date(),
                "amount": amount,
                "debit_credit": entry_type,
                "account_id": resolve_account(acct),
                "property_id": property_id,
                "tenant_id": tenant_id,
                "vendor_id": vendor_id,
                "transaction_type": source,
                "source_document": source_id,
                "batch_id": batch_id,
                "cleared_in_bank": cleared,
                "created_by": "system",
                "created_at": timestamp,
                "modified_by": "system",
                "modified_at": timestamp
            })
        return batch_id

    for i, row in cust_invoices.iterrows():
        if row["status"] == "Paid":
            gl_id = create_entry("Customer Invoice", row["id"], row["property_id"], row["amount_due"],
                                 "Tenant Receivable", "Rent Revenue", tenant_id=row["tenant_id"])
            cust_invoices.at[i, "gltran_id"] = gl_id

    for i, row in vend_invoices.iterrows():
        if row["status"] == "Paid":
            gl_id = create_entry("Vendor Invoice", row["id"], row["property_id"], row["amount_due"],
                                 row["gl_account_name"], "Accounts Payable", vendor_id=row["vendor_id"])
            vend_invoices.at[i, "gltran_id"] = gl_id

    for i, row in receipts.iterrows():
        gl_id = create_entry(
            "Receipt",
            row["id"],
            row["property_id"],
            row["amount"],
            "Cash",
            "Tenant Receivable",
            tenant_id=row["tenant_id"],
        )
        receipts.at[i, "gltran_id"] = gl_id

    for i, row in checkreg.iterrows():
        gl_id = create_entry("Check", row["id"], row["property_id"], row["amount"],
                                "Accounts Payable", "Cash", vendor_id=row["vendor_id"])
        checkreg.at[i, "gltran_id"] = gl_id

    return {
        "gltran": pd.DataFrame(gl_entries),
        "cust_invoices": cust_invoices,
        "vend_invoices": vend_invoices,
        "receipts": receipts,
        "checkreg": checkreg
    }

# ------------ Simulate Budget & Budget Line ------------ (per property x COA x month)
def generate_budget(properties, coa):
    budget = []
    budgetline = []
    fiscal_year = datetime.now().year
    for _, prop in properties.iterrows():
        budget_id = uid()
        budget.append({
            "id": budget_id,
            "property_id": prop["property_id"],
            "fiscal_year": fiscal_year,
            "version": "Initial",
            "approved": random_bool()
        })
        for _, acct in coa.sample(10).iterrows():
            for month in range(1, 13):
                budgetline.append({
                    "id": uid(),
                    "budget_id": budget_id,
                    "account_id": acct["acct_name"],
                    "month": f"{month:02d}",
                    "amount": round(random.uniform(500, 5000), 2)
                })
    return pd.DataFrame(budget), pd.DataFrame(budgetline)

# ------------ Simulate Bank Accounts ------------
def generate_bank_accounts(properties):
    accounts = []
    for _, prop in properties.iterrows():
        for t in ["Operating", "Reserve"]:
            accounts.append({
                "id": uid(),
                "property_id": prop["property_id"],
                "bank_name": random.choice(["Bank of America", "Chase", "Wells Fargo"]),
                "account_number_last4": str(random.randint(1000, 9999)),
                "acct_type": t,
                "is_operating": t == "Operating",
                "is_reserve": t == "Reserve"
            })
    return pd.DataFrame(accounts)

# ------------ Simulate Bank Transactions ------------ 
def generate_bank_transactions(bank_accounts):
    transactions = []
    for _, acct in bank_accounts.iterrows():
        balance = 50000
        for _ in range(10):
            amt = round(random.uniform(-5000, 5000), 2)
            balance += amt
            transactions.append({
                "id": uid(),
                "bank_account_id": acct["id"],
                "transaction_date": random_date().date(),
                "description": fake.sentence(),
                "amount": amt,
                "type": "Credit" if amt > 0 else "Debit",
                "balance_after": round(balance, 2),
                "matched_gltran_id": None,
                "created_by": "system",
                "created_at": datetime.now(),
                "modified_by": "system",
                "modified_at": datetime.now()
            })
    return pd.DataFrame(transactions)

# ------------ Simulate Bank Balances ------------ 
def generate_bank_balances(bank_accounts):
    balances = []
    for _, acct in bank_accounts.iterrows():
        for i in range(5):
            balances.append({
                "id": uid(),
                "bank_account_id": acct["id"],
                "date": datetime.now().date() - timedelta(days=i*7),
                "balance": round(random.uniform(10000, 100000), 2)
            })
    return pd.DataFrame(balances)

# ------------ Simulate Bank Reconciliations ------------  
def generate_reconciliations(properties, bank_accounts):
    recs = []
    for _, prop in properties.iterrows():
        acct = bank_accounts[bank_accounts["property_id"] == prop["property_id"]].sample(1).iloc[0]
        recs.append({
            "id": uid(),
            "property_id": prop["property_id"],
            "bank_account_id": acct["id"],
            "reconciliation_date": datetime.now().date(),
            "reconciled_by": fake.name(),
            "variance": round(random.uniform(-500, 500), 2),
            "note": fake.sentence(),
            "created_by": "system",
            "created_at": datetime.now(),
            "modified_by": "system",
            "modified_at": datetime.now()
        })
    return pd.DataFrame(recs)

# Once all tables are generated, we'll save them in the next step


# ------------ Run All ------------
def generate_all():
    user = generate_user()
    vendors = generate_vendors(coa_df, user, num_vendors=60)
    units = generate_units(properties_df)
    tenants = generate_tenants(properties_df, units)
    leases = generate_leases(properties_df, tenants, units)
    pmnt_sched = generate_lease_pymnt_sched(leases, months_out=24)
    cust_invoices = generate_cust_invoices(pmnt_sched, leases, tenants)
    vend_invoices = generate_vendor_invoices(vendors, properties_df, leases, coa_df, min_invoices=50, max_invoices=300)
    checkreg = generate_checkreg(vend_invoices)
    receipts = generate_receipts(cust_invoices)
    # budget, budgetline = generate_budget(properties_df, coa_df)
    # bank_accounts = generate_bank_accounts(properties_df)
    # bank_transactions = generate_bank_transactions(bank_accounts)
    # bank_balances = generate_bank_balances(bank_accounts)
    # reconciliations = generate_reconciliations(properties_df, bank_accounts)

    gl_data = generate_gltran(cust_invoices, vend_invoices, receipts, checkreg, coa_df)
    gltran = gl_data["gltran"]
    cust_invoices = gl_data["cust_invoices"]
    vend_invoices = gl_data["vend_invoices"]
    receipts = gl_data["receipts"]
    checkreg = gl_data["checkreg"]

    tenants.to_csv(os.path.join(output_dir, "yardi/tenants.csv"), index=False)
    units.to_csv(os.path.join(output_dir, "yardi/units.csv"), index=False)
    leases.to_csv(os.path.join(output_dir, "yardi/leases.csv"), index=False)
    pmnt_sched.to_csv(os.path.join(output_dir, "yardi/payment_schedule.csv"), index=False)
    vendors.to_csv(os.path.join(output_dir, "yardi/vendors.csv"), index=False)
    cust_invoices.to_csv(os.path.join(output_dir, "yardi/cust_invoices.csv"), index=False)
    vend_invoices.to_csv(os.path.join(output_dir, "yardi/vend_invoices.csv"), index=False)
    checkreg.to_csv(os.path.join(output_dir, "yardi/checkreg.csv"), index=False)
    receipts.to_csv(os.path.join(output_dir, "yardi/receipts.csv"), index=False)
    gltran.to_csv(os.path.join(output_dir, "yardi/gltran.csv"), index=False)
    # budget.to_csv(os.path.join(output_dir, "yardi/budget.csv"), index=False)
    # budgetline.to_csv(os.path.join(output_dir, "yardi/budgetline.csv"), index=False)
    properties_df.to_csv(os.path.join(output_dir, "yardi/properties.csv"), index=False)
    # bank_accounts.to_csv(os.path.join(output_dir, "banking/bank_accounts.csv"), index=False)
    # bank_transactions.to_csv(os.path.join(output_dir, "banking/bank_transactions.csv"), index=False)
    # bank_balances.to_csv(os.path.join(output_dir, "banking/bank_balances.csv"), index=False)
    # reconciliations.to_csv(os.path.join(output_dir, "banking/reconciliations.csv"), index=False)

    print("\u2713 All synthetic data tables exported successfully.")

# Execute the script when called directly
if __name__ == "__main__":
    generate_all()
