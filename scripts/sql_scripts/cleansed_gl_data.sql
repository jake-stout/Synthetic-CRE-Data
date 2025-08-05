WITH combined_sources AS (
	SELECT
		'Customer Invoice' AS transaction_type,
		id,
		status,
		description
	FROM cust_invoices

	UNION ALL

	SELECT
		'Vendor Invoice' AS transaction_type,
		id,
		status,
		description
	FROM vend_invoices
	
	UNION ALL

	SELECT
		'Receipt' AS transaction_type,
		r.id,
		c.status,
		c.description
	FROM receipts r
	JOIN cust_invoices c
		ON r.invoice_id = c.id

	UNION ALL

	SELECT
		'Check' AS transaction_type,
		cr.id,
		v.status,
		v.description
	FROM checkreg cr
	JOIN vend_invoices v
		ON cr.invoice_id = v.id
)

SELECT
	gl.id,
	gl.date,
	gl.amount,
	gl.debit_credit,
	gl.account_id,
	p."Address" property_address,
	t.business_name,
	v.name vendor_name,
	gl.transaction_type,
	gl.source_document,
	cs.status,
	cs.description,
	gl.batch_id,
	gl.cleared_in_bank,
	gl.created_by,
	gl.created_at,
	gl.modified_by,
	gl.modified_at
FROM gltran gl
	LEFT JOIN properties p
		ON gl.property_id = p.property_id
	LEFT JOIN tenants t
		ON gl.tenant_id::text = t.id
	LEFT JOIN vendors v
		ON gl.vendor_id = v.id
	LEFT JOIN combined_sources cs
		ON gl.transaction_type = cs.transaction_type AND gl.source_document = cs.id

