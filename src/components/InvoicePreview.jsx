import React from 'react'

function InvoicePreview({ data, summary }) {
  return (
    <div className="invoice-container">
      {/* Top Header Section */}
      <div className="invoice-top-row">
        <div className="business-info">
          {data.business.logo && (
            <img src={data.business.logo} alt="Logo" className="invoice-logo" />
          )}
          <h1 className="business-name">{data.business.name}</h1>
          <p className="address">{data.business.address}</p>
          {data.business.trn && <p className="trn">TRN: {data.business.trn}</p>}
        </div>
        <div className="invoice-title-block">
          <h1>Invoice</h1>
          <div className="invoice-number"># {data.invoiceNumber}</div>
          <div className="balance-due-top">
            <label>Balance Due</label>
            <div className="amount">{data.currency?.symbol || '$'}{summary.total.toFixed(2)}</div>
          </div>
        </div>
      </div>

      {/* Bill To / Ship To Grid */}
      <div className="info-grid">
        <div className="bill-to">
          <div className="label-title">Bill To</div>
          <p className="client-name">{data.client.name}</p>
          <p className="address">{data.client.address}</p>
          {data.client.trn && <p className="trn">TRN: {data.client.trn}</p>}
        </div>
        {data.client.deliveryAddress && (
          <div className="ship-to">
            <div className="label-title">Ship To</div>
            <p className="address">{data.client.deliveryAddress}</p>
          </div>
        )}
      </div>

      {/* Meta Details (Date/Terms) */}
      <div className="meta-grid">
        <div className="meta-row">
          <label>Invoice Date:</label>
          <span>{data.date}</span>
        </div>
        <div className="meta-row">
          <label>Terms:</label>
          <span>{data.terms}</span>
        </div>
      </div>

      {/* Items Table */}
      <table className="items-table">
        <thead>
          <tr>
            <th style={{ width: '50px' }}>#</th>
            <th>Item & Description</th>
            <th className="text-right" style={{ width: '80px' }}>Qty</th>
            <th className="text-right" style={{ width: '120px' }}>Rate</th>
            <th className="text-right" style={{ width: '120px' }}>Amount</th>
          </tr>
        </thead>
        <tbody>
          {data.items.map((item, index) => (
            <tr key={index}>
              <td>{index + 1}</td>
              <td>
                <span className="item-main-desc">{item.description || 'New Item'}</span>
                {item.subDescription && (
                  <span className="item-sub-desc">{item.subDescription}</span>
                )}
              </td>
              <td className="text-right">{item.quantity.toFixed(2)}</td>
              <td className="text-right">{item.price.toFixed(2)}</td>
              <td className="text-right">{(item.quantity * item.price).toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Summary Section */}
      <div className="summary-container">
        <div className="summary-table">
          <div className="summary-row">
            <span>Sub Total</span>
            <span>{summary.subtotal.toFixed(2)}</span>
          </div>
          <div className="summary-row">
            <span>Tax Rate</span>
            <span>{data.taxRate.toFixed(2)}%</span>
          </div>
          <div className="summary-row total">
            <span>Total</span>
            <span>{data.currency?.symbol || '$'}{summary.total.toFixed(2)}</span>
          </div>
        </div>
        <div className="balance-due-stripe">
          <span>Balance Due</span>
          <span>{data.currency?.symbol || '$'}{summary.total.toFixed(2)}</span>
        </div>
      </div>

      {/* Footer Details */}
      <div className="footer-section">
        {data.notes && (
          <div className="notes-block">
            <h4>Notes</h4>
            <p>{data.notes}</p>
          </div>
        )}
        {data.termsAndConditions && (
          <div className="tc-block">
            <h4>Terms & Conditions</h4>
            <p>{data.termsAndConditions}</p>
          </div>
        )}
      </div>

      {/* Enhanced Footer: Stamp, Bank Details, and Customer Signature */}
      <div className="invoice-footer-grid">
        <div className="footer-left">
          {data.showStampAndSignature && (
            <div className="stamp-signature-container">
              {data.sellerStamp && (
                <div className="stamp-block">
                  <img src={data.sellerStamp} alt="Seller Stamp" className="invoice-stamp" />
                  <span className="label">Company Stamp</span>
                </div>
              )}
              {data.sellerSignature && (
                <div className="signature-block">
                  <img src={data.sellerSignature} alt="Seller Signature" className="invoice-signature" />
                  <span className="label">Authorized Signature</span>
                </div>
              )}
            </div>
          )}

          {(data.bankDetails.bankName || data.bankDetails.accountNumber) && (
            <div className="bank-details-display">
              <h4>Bank Details</h4>
              <div className="bank-grid">
                {data.bankDetails.bankName && <><span className="label">Bank:</span> <span>{data.bankDetails.bankName}</span></>}
                {data.bankDetails.accountName && <><span className="label">A/C Name:</span> <span>{data.bankDetails.accountName}</span></>}
                {data.bankDetails.accountNumber && <><span className="label">A/C No:</span> <span>{data.bankDetails.accountNumber}</span></>}
                {data.bankDetails.iban && <><span className="label">IBAN:</span> <span>{data.bankDetails.iban}</span></>}
                {data.bankDetails.swift && <><span className="label">SWIFT/BIC:</span> <span>{data.bankDetails.swift}</span></>}
                {data.bankDetails.branch && <><span className="label">Branch:</span> <span>{data.bankDetails.branch}</span></>}
              </div>
            </div>
          )}
        </div>

        <div className="footer-right">
          <div className="customer-signature">
            <div className="signature-line"></div>
            <div className="label-main">Customer Signature (As Acceptance)</div>
            <div className="label-sub">Authorized Signature & Company Stamp</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default InvoicePreview
