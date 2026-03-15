import React from 'react'
import { Plus, Trash2, Upload, Globe } from 'lucide-react'
import CurrencySelector from './CurrencySelector'

function InvoiceForm({ data, onUpdate, onUpdateItem, onAddItem, onRemoveItem }) {
  const handleLogoUpload = (field, e) => {
    const file = e.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        onUpdate(field, reader.result)
      }
      reader.readAsDataURL(file)
    }
  }

  return (
    <div className="invoice-form">
      <div className="form-group-section">
        <h3>Business Details</h3>
        <div className="logo-upload">
          <label htmlFor="business-logo" className="logo-label">
            {data.business.logo ? (
              <img src={data.business.logo} alt="Logo Preview" className="logo-preview-img" />
            ) : (
              <div className="logo-placeholder">
                <Upload size={20} />
                <span>Business Logo</span>
              </div>
            )}
          </label>
          <input type="file" id="business-logo" onChange={(e) => handleLogoUpload('business.logo', e)} accept="image/*" hidden />
        </div>
        <input 
          type="text" 
          placeholder="Business Name" 
          value={data.business.name} 
          onChange={(e) => onUpdate('business.name', e.target.value)} 
        />
        <input 
          type="text" 
          placeholder="Business TRN / Tax ID" 
          value={data.business.trn} 
          onChange={(e) => onUpdate('business.trn', e.target.value)} 
        />
        <textarea 
          placeholder="Business Address" 
          value={data.business.address} 
          onChange={(e) => onUpdate('business.address', e.target.value)} 
        />
      </div>

      <div className="form-group-section">
        <h3>Client Details</h3>
        <input 
          type="text" 
          placeholder="Client Name" 
          value={data.client.name} 
          onChange={(e) => onUpdate('client', { ...data.client, name: e.target.value })} 
        />
        <input 
          type="text" 
          placeholder="Client TRN / Tax ID" 
          value={data.client.trn} 
          onChange={(e) => onUpdate('client', { ...data.client, trn: e.target.value })} 
        />
        <textarea 
          placeholder="Client Address" 
          value={data.client.address} 
          onChange={(e) => onUpdate('client.address', e.target.value)} 
        />
        <textarea 
          placeholder="Delivery Address (if different)" 
          value={data.client.deliveryAddress} 
          onChange={(e) => onUpdate('client.deliveryAddress', e.target.value)} 
        />
      </div>

      <div className="form-row">
        <div className="form-group flex-2">
          <CurrencySelector 
            selectedCurrency={data.currency} 
            onSelect={(c) => onUpdate('currency', c)} 
          />
        </div>
        <div className="form-group">
          <label>Invoice #</label>
          <input 
            type="text" 
            value={data.invoiceNumber} 
            onChange={(e) => onUpdate('invoiceNumber', e.target.value)} 
          />
        </div>
        <div className="form-group">
          <label>Date</label>
          <input 
            type="date" 
            value={data.date} 
            onChange={(e) => onUpdate('date', e.target.value)} 
          />
        </div>
      </div>

      <div className="items-section">
        <div className="items-header">
          <h3>Line Items</h3>
          <button onClick={onAddItem} className="btn-icon-text">
            <Plus size={16} /> Add Item
          </button>
        </div>
        
        {data.items.map((item, index) => (
          <div key={index} className="item-row">
            <input 
              className="col-desc"
              type="text" 
              placeholder="Description (Main)" 
              value={item.description} 
              onChange={(e) => onUpdateItem(index, 'description', e.target.value)} 
            />
            <input 
              className="col-qty"
              type="number" 
              placeholder="Qty" 
              value={item.quantity} 
              onChange={(e) => onUpdateItem(index, 'quantity', parseFloat(e.target.value) || 0)} 
            />
            <input 
              className="col-price"
              type="number" 
              placeholder="Price" 
              value={item.price} 
              onChange={(e) => onUpdateItem(index, 'price', parseFloat(e.target.value) || 0)} 
            />
            <button onClick={() => onRemoveItem(index)} className="btn-danger" title="Remove">
              <Trash2 size={16} />
            </button>
            <input 
              className="col-full"
              type="text" 
              placeholder="Sub-description (Additional details)" 
              value={item.subDescription || ''} 
              onChange={(e) => onUpdateItem(index, 'subDescription', e.target.value)} 
            />
          </div>
        ))}
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Tax Rate (%)</label>
          <input 
            type="number" 
            value={data.taxRate} 
            onChange={(e) => onUpdate('taxRate', parseFloat(e.target.value) || 0)} 
          />
        </div>
        <div className="form-group">
          <label>Payment Terms</label>
          <input 
            type="text" 
            value={data.terms} 
            onChange={(e) => onUpdate('terms', e.target.value)} 
          />
        </div>
      </div>

      <div className="form-group-section">
        <h3>Bank Details</h3>
        <input 
          type="text" 
          placeholder="Bank Name" 
          value={data.bankDetails.bankName} 
          onChange={(e) => onUpdate('bankDetails', { ...data.bankDetails, bankName: e.target.value })} 
        />
        <input 
          type="text" 
          placeholder="Account Name" 
          value={data.bankDetails.accountName} 
          onChange={(e) => onUpdate('bankDetails', { ...data.bankDetails, accountName: e.target.value })} 
        />
        <input 
          type="text" 
          placeholder="Account Number" 
          value={data.bankDetails.accountNumber} 
          onChange={(e) => onUpdate('bankDetails', { ...data.bankDetails, accountNumber: e.target.value })} 
        />
        <div className="form-row">
          <input 
            type="text" 
            placeholder="IBAN" 
            value={data.bankDetails.iban} 
            onChange={(e) => onUpdate('bankDetails', { ...data.bankDetails, iban: e.target.value })} 
          />
          <input 
            type="text" 
            placeholder="SWIFT / BIC" 
            value={data.bankDetails.swift} 
            onChange={(e) => onUpdate('bankDetails', { ...data.bankDetails, swift: e.target.value })} 
          />
        </div>
        <input 
          type="text" 
          placeholder="Branch (Optional)" 
          value={data.bankDetails.branch} 
          onChange={(e) => onUpdate('bankDetails', { ...data.bankDetails, branch: e.target.value })} 
        />
      </div>

      <div className="form-group-section">
        <h3>Stamp & Signature</h3>
        <div className="checkbox-group">
          <label className="checkbox-label">
            <input 
              type="checkbox" 
              checked={data.showStampAndSignature} 
              onChange={(e) => onUpdate('showStampAndSignature', e.target.checked)} 
            />
            Display Seller Stamp and Signature
          </label>
        </div>
        
        {data.showStampAndSignature && (
          <div className="form-row mt-1">
            <div className="form-group">
              <label className="sub-label">Company Stamp</label>
              <label className="logo-label">
                <input 
                  type="file" 
                  accept="image/*" 
                  onChange={(e) => handleLogoUpload('sellerStamp', e)} 
                  hidden 
                />
                {data.sellerStamp ? (
                  <div className="logo-placeholder">
                    <img src={data.sellerStamp} alt="Stamp" className="logo-preview-img" />
                  </div>
                ) : (
                  <div className="logo-placeholder">
                    <Upload size={20} />
                    <span>Upload Stamp</span>
                  </div>
                )}
              </label>
            </div>
            
            <div className="form-group">
              <label className="sub-label">Authorized Signature</label>
              <label className="logo-label">
                <input 
                  type="file" 
                  accept="image/*" 
                  onChange={(e) => handleLogoUpload('sellerSignature', e)} 
                  hidden 
                />
                {data.sellerSignature ? (
                  <div className="logo-placeholder">
                    <img src={data.sellerSignature} alt="Signature" className="logo-preview-img" />
                  </div>
                ) : (
                  <div className="logo-placeholder">
                    <Upload size={20} />
                    <span>Upload Signature</span>
                  </div>
                )}
              </label>
            </div>
          </div>
        )}
      </div>

      <div className="form-group-section">
        <h3>Terms & Notes</h3>
        <textarea 
          placeholder="Notes" 
          value={data.notes} 
          onChange={(e) => onUpdate('notes', e.target.value)} 
        />
        <textarea 
          placeholder="Terms & Conditions" 
          value={data.termsAndConditions} 
          onChange={(e) => onUpdate('termsAndConditions', e.target.value)} 
        />
      </div>
    </div>
  )
}

export default InvoiceForm
