CREATE TABLE "properties" (
  "id" uuid PRIMARY KEY,
  "name" varchar,
  "address" text,
  "city" varchar,
  "state" varchar,
  "zip" varchar,
  "market" enum,
  "legal_entity" enum,
  "property_type" enum,
  "subtype" enum,
  "status" enum,
  "reserve_requirement" decimal
);

CREATE TABLE "units" (
  "id" uuid PRIMARY KEY,
  "property_id" uuid,
  "unit_number" varchar,
  "floor_number" int,
  "floorplan" varchar,
  "sq_ft" int,
  "occupancy_status" enum,
  "is_model_unit" boolean,
  "last_renovated" date,
  "last_occupied" date,
  "last_vacated" date
);

CREATE TABLE "tenants" (
  "id" uuid PRIMARY KEY,
  "name" varchar,
  "email" varchar,
  "phone" varchar,
  "employer" varchar,
  "income_level" varchar,
  "credit_score" int,
  "background_check_status" enum,
  "move_in_reason" text
);

CREATE TABLE "leases" (
  "id" uuid PRIMARY KEY,
  "tenant_id" uuid,
  "unit_id" uuid,
  "property_id" uuid,
  "start_date" date,
  "end_date" date,
  "deposit_amount" decimal,
  "lease_status" varchar,
  "auto_renew" boolean,
  "lease_type" enum,
  "late_fee_terms" text,
  "early_termination_clause" text,
  "pro_rated_start" boolean,
  "escalation_clause" boolean,
  "expense_reimbursement_clause" boolean
);

CREATE TABLE "glacct" (
  "id" uuid PRIMARY KEY,
  "code" varchar,
  "name" varchar,
  "type" varchar,
  "financial_statement" varchar,
  "normal_balance" varchar,
  "is_cash_account" boolean,
  "is_reserve_account" boolean
);

CREATE TABLE "gltran" (
  "id" uuid PRIMARY KEY,
  "date" date,
  "amount" decimal,
  "debit_credit" varchar,
  "account_id" uuid,
  "property_id" uuid,
  "tenant_id" uuid,
  "vendor_id" uuid,
  "transaction_type" varchar,
  "source_document" varchar,
  "batch_id" uuid,
  "cleared_in_bank" boolean,
  "created_by" varchar,
  "created_at" timestamp,
  "modified_by" varchar,
  "modified_at" timestamp
);

CREATE TABLE "vendors" (
  "id" uuid PRIMARY KEY,
  "name" varchar,
  "service_type" varchar,
  "address" text,
  "contact_name" varchar,
  "contact_email" varchar,
  "phone" varchar,
  "tax_id" varchar,
  "insurance_status" enum,
  "approved_vendor" boolean,
  "created_by" varchar,
  "created_at" timestamp,
  "modified_by" varchar,
  "modified_at" timestamp
);

CREATE TABLE "invoices" (
  "id" uuid PRIMARY KEY,
  "vendor_id" uuid,
  "property_id" uuid,
  "account_id" uuid,
  "invoice_date" date,
  "due_date" date,
  "amount" decimal,
  "status" varchar,
  "gltran_id" uuid,
  "created_by" varchar,
  "created_at" timestamp,
  "modified_by" varchar,
  "modified_at" timestamp
);

CREATE TABLE "checkreg" (
  "id" uuid PRIMARY KEY,
  "vendor_id" uuid,
  "check_number" varchar,
  "check_date" date,
  "amount" decimal,
  "property_id" uuid,
  "gltran_id" uuid,
  "created_by" varchar,
  "created_at" timestamp,
  "modified_by" varchar,
  "modified_at" timestamp
);

CREATE TABLE "charges" (
  "id" uuid PRIMARY KEY,
  "lease_id" uuid,
  "charge_date" date,
  "amount" decimal,
  "charge_type" varchar,
  "gltran_id" uuid,
  "created_by" varchar,
  "created_at" timestamp,
  "modified_by" varchar,
  "modified_at" timestamp
);

CREATE TABLE "receipts" (
  "id" uuid PRIMARY KEY,
  "lease_id" uuid,
  "receipt_date" date,
  "amount" decimal,
  "payment_method" varchar,
  "gltran_id" uuid,
  "created_by" varchar,
  "created_at" timestamp,
  "modified_by" varchar,
  "modified_at" timestamp
);

CREATE TABLE "rentroll" (
  "id" uuid PRIMARY KEY,
  "property_id" uuid,
  "unit_id" uuid,
  "lease_id" uuid,
  "schedule_date" date,
  "rent_amount" decimal,
  "escalated_rent" boolean,
  "escalation_type" enum,
  "cam_recovery" decimal,
  "recovery_type" enum,
  "recoverable_category" varchar,
  "is_pro_rated" boolean,
  "status" varchar
);

CREATE TABLE "budget" (
  "id" uuid PRIMARY KEY,
  "property_id" uuid,
  "fiscal_year" int,
  "version" varchar,
  "approved" boolean
);

CREATE TABLE "budgetline" (
  "id" uuid PRIMARY KEY,
  "budget_id" uuid,
  "account_id" uuid,
  "month" varchar,
  "amount" decimal
);

CREATE TABLE "bank_accounts" (
  "id" uuid PRIMARY KEY,
  "property_id" uuid,
  "bank_name" varchar,
  "account_number_last4" varchar,
  "account_type" varchar,
  "is_operating" boolean,
  "is_reserve" boolean
);

CREATE TABLE "bank_transactions" (
  "id" uuid PRIMARY KEY,
  "bank_account_id" uuid,
  "transaction_date" date,
  "description" text,
  "amount" decimal,
  "type" varchar,
  "balance_after" decimal,
  "matched_gltran_id" uuid,
  "created_by" varchar,
  "created_at" timestamp,
  "modified_by" varchar,
  "modified_at" timestamp
);

CREATE TABLE "bank_balances" (
  "id" uuid PRIMARY KEY,
  "bank_account_id" uuid,
  "date" date,
  "balance" decimal
);

CREATE TABLE "reconciliations" (
  "id" uuid PRIMARY KEY,
  "property_id" uuid,
  "bank_account_id" uuid,
  "reconciliation_date" date,
  "reconciled_by" varchar,
  "variance" decimal,
  "note" text,
  "created_by" varchar,
  "created_at" timestamp,
  "modified_by" varchar,
  "modified_at" timestamp
);

COMMENT ON TABLE "properties" IS 'Represents managed properties; tied to legal entity';

COMMENT ON TABLE "units" IS 'Rent amount is derived from rentroll schedule';

COMMENT ON TABLE "tenants" IS 'Tenant information for risk, collections, and payment analysis';

COMMENT ON TABLE "leases" IS 'Describes contractual lease terms';

COMMENT ON TABLE "gltran" IS 'GL transaction detail with source context';

COMMENT ON TABLE "vendors" IS 'Captures vendor relationship and compliance data';

COMMENT ON TABLE "rentroll" IS 'One row per unit per billing period; tracks historical and escalated rents, CAM recoveries';

ALTER TABLE "units" ADD FOREIGN KEY ("property_id") REFERENCES "properties" ("id");

ALTER TABLE "leases" ADD FOREIGN KEY ("tenant_id") REFERENCES "tenants" ("id");

ALTER TABLE "leases" ADD FOREIGN KEY ("unit_id") REFERENCES "units" ("id");

ALTER TABLE "leases" ADD FOREIGN KEY ("property_id") REFERENCES "properties" ("id");

ALTER TABLE "gltran" ADD FOREIGN KEY ("account_id") REFERENCES "glacct" ("id");

ALTER TABLE "gltran" ADD FOREIGN KEY ("property_id") REFERENCES "properties" ("id");

ALTER TABLE "gltran" ADD FOREIGN KEY ("tenant_id") REFERENCES "tenants" ("id");

ALTER TABLE "gltran" ADD FOREIGN KEY ("vendor_id") REFERENCES "vendors" ("id");

ALTER TABLE "invoices" ADD FOREIGN KEY ("vendor_id") REFERENCES "vendors" ("id");

ALTER TABLE "invoices" ADD FOREIGN KEY ("property_id") REFERENCES "properties" ("id");

ALTER TABLE "invoices" ADD FOREIGN KEY ("account_id") REFERENCES "glacct" ("id");

ALTER TABLE "invoices" ADD FOREIGN KEY ("gltran_id") REFERENCES "gltran" ("id");

ALTER TABLE "checkreg" ADD FOREIGN KEY ("vendor_id") REFERENCES "vendors" ("id");

ALTER TABLE "checkreg" ADD FOREIGN KEY ("property_id") REFERENCES "properties" ("id");

ALTER TABLE "checkreg" ADD FOREIGN KEY ("gltran_id") REFERENCES "gltran" ("id");

ALTER TABLE "charges" ADD FOREIGN KEY ("lease_id") REFERENCES "leases" ("id");

ALTER TABLE "charges" ADD FOREIGN KEY ("gltran_id") REFERENCES "gltran" ("id");

ALTER TABLE "receipts" ADD FOREIGN KEY ("lease_id") REFERENCES "leases" ("id");

ALTER TABLE "receipts" ADD FOREIGN KEY ("gltran_id") REFERENCES "gltran" ("id");

ALTER TABLE "rentroll" ADD FOREIGN KEY ("property_id") REFERENCES "properties" ("id");

ALTER TABLE "rentroll" ADD FOREIGN KEY ("unit_id") REFERENCES "units" ("id");

ALTER TABLE "rentroll" ADD FOREIGN KEY ("lease_id") REFERENCES "leases" ("id");

ALTER TABLE "budget" ADD FOREIGN KEY ("property_id") REFERENCES "properties" ("id");

ALTER TABLE "budgetline" ADD FOREIGN KEY ("budget_id") REFERENCES "budget" ("id");

ALTER TABLE "budgetline" ADD FOREIGN KEY ("account_id") REFERENCES "glacct" ("id");

ALTER TABLE "bank_accounts" ADD FOREIGN KEY ("property_id") REFERENCES "properties" ("id");

ALTER TABLE "bank_transactions" ADD FOREIGN KEY ("bank_account_id") REFERENCES "bank_accounts" ("id");

ALTER TABLE "bank_transactions" ADD FOREIGN KEY ("matched_gltran_id") REFERENCES "gltran" ("id");

ALTER TABLE "bank_balances" ADD FOREIGN KEY ("bank_account_id") REFERENCES "bank_accounts" ("id");

ALTER TABLE "reconciliations" ADD FOREIGN KEY ("property_id") REFERENCES "properties" ("id");

ALTER TABLE "reconciliations" ADD FOREIGN KEY ("bank_account_id") REFERENCES "bank_accounts" ("id");
