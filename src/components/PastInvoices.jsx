import React, { useEffect, useState } from 'react'
import { supabase } from '../lib/supabaseClient'
import { FileText, Download, Calendar } from 'lucide-react'

function PastInvoices({ userId, onSelectInvoice }) {
  const [invoices, setInvoices] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchInvoices()
  }, [userId])

  const fetchInvoices = async () => {
    try {
      const { data, error } = await supabase
        .from('invoices')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
      
      if (error) throw error
      setInvoices(data || [])
    } catch (error) {
      console.error('Error fetching invoices:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="loading-state">Loading your invoices...</div>

  return (
    <div className="past-invoices">
      <h3>Past Invoices</h3>
      {invoices.length === 0 ? (
        <p className="empty-state">No invoices found. Create your first one!</p>
      ) : (
        <div className="invoice-list">
          {invoices.map((inv) => (
            <div key={inv.id} className="invoice-list-item" onClick={() => onSelectInvoice(inv.invoice_data)}>
              <FileText size={20} className="icon-rust" />
              <div className="item-info">
                <span className="item-number">#{inv.invoice_data.invoiceNumber}</span>
                <span className="item-date">
                  <Calendar size={12} /> {new Date(inv.created_at).toLocaleDateString()}
                </span>
              </div>
              <span className="item-total">${inv.invoice_data.total?.toFixed(2) || '0.00'}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default PastInvoices
