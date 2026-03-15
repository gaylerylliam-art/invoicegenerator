import React, { useState, useEffect } from 'react'
import { Plus, Trash2, Download, Copy, LogOut, History, FileText, Save } from 'lucide-react'
import InvoiceForm from './components/InvoiceForm'
import InvoicePreview from './components/InvoicePreview'
import Auth from './components/Auth'
import PastInvoices from './components/PastInvoices'
import { generatePDF } from './utils/pdfGenerator'
import { supabase } from './lib/supabaseClient'
import { currencies } from './utils/currencies'

const initialInvoiceData = {
  invoiceNumber: 'INV-000001',
  date: new Date().toISOString().substr(0, 10),
  currency: currencies.find(c => c.code === 'USD') || { code: 'USD', symbol: '$', name: 'United States Dollar' },
  business: {
    name: 'Zylker Design Labs',
    address: '14B, Northern Street\nGreater South Avenue\nNew York 10001\nU.S.A',
    logo: null,
    trn: ''
  },
  client: {
    name: 'Jack Little',
    address: '3242 Chandler Hollow Road\nPittsburgh\n15222 Pennsylvania',
    deliveryAddress: '3242 Chandler Hollow Road\nPittsburgh\n15222 Pennsylvania',
    logo: null,
    trn: ''
  },
  items: [
    { description: 'Brochure Design', subDescription: 'Brochure design - Single sided (Color)', quantity: 1, price: 900 }
  ],
  taxRate: 5,
  terms: 'Due on Receipt',
  notes: 'Thanks for your business.',
  termsAndConditions: 'All payments must be made in full before the commencement of any design work.',
  showStampAndSignature: false,
  sellerStamp: null,
  sellerSignature: null,
  bankDetails: {
    bankName: '',
    accountName: '',
    accountNumber: '',
    iban: '',
    swift: '',
    branch: ''
  }
}

function App() {
  const [session, setSession] = useState(null)
  const [data, setData] = useState(initialInvoiceData)
  const [summary, setSummary] = useState({ subtotal: 0, tax: 0, total: 0 })
  const [view, setView] = useState('generator') // 'generator' or 'history'
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
    })

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
    })

    return () => subscription.unsubscribe()
  }, [])

  useEffect(() => {
    const subtotal = data.items.reduce((acc, item) => acc + (item.quantity * item.price), 0)
    const tax = (subtotal * data.taxRate) / 100
    const total = subtotal + tax
    setSummary({ subtotal, tax, total })
  }, [data])

  const handleUpdate = (field, value) => {
    setData(prev => {
      const newData = { ...prev }
      if (field.includes('.')) {
        const [obj, key] = field.split('.')
        newData[obj] = { ...newData[obj], [key]: value }
      } else {
        newData[field] = value
      }
      return newData
    })
  }

  const handleSaveInvoice = async () => {
    if (!session) return
    setSaving(true)
    try {
      const { error } = await supabase.from('invoices').insert([
        { 
          user_id: session.user.id, 
          invoice_data: { ...data, ...summary } 
        }
      ])
      if (error) throw error
      alert('Invoice saved successfully!')
    } catch (error) {
      alert('Error saving invoice: ' + error.message)
    } finally {
      setSaving(false)
    }
  }

  const handleUpdateItem = (index, field, value) => {
    setData(prev => {
      const newItems = [...prev.items]
      newItems[index] = { ...newItems[index], [field]: value }
      return { ...prev, items: newItems }
    })
  }

  const handleAddItem = () => {
    setData(prev => ({
      ...prev,
      items: [...prev.items, { description: '', subDescription: '', quantity: 1, price: 0 }]
    }))
  }

  const handleRemoveItem = (index) => {
    setData(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index)
    }))
  }

  const handleCopy = () => {
    const symbol = data.currency?.symbol || '$'
    const text = `Invoice ${data.invoiceNumber}\nDate: ${data.date}\n\nFrom: ${data.business.name}\nTo: ${data.client.name}\n\nTotal: ${symbol}${summary.total.toFixed(2)}`
    navigator.clipboard.writeText(text)
    alert('Invoice summary copied to clipboard!')
  }

  const handleLogout = async () => {
    await supabase.auth.signOut()
    setView('generator')
  }

  if (!session) {
    return <Auth />
  }

  return (
    <div className="app-container">
      <nav className="top-nav">
        <div className="nav-logo">
          <FileText className="icon-rust" size={24} />
          <span>Professional Invoice</span>
        </div>
        <div className="nav-actions">
          <button onClick={() => setView('generator')} className={view === 'generator' ? 'active' : ''}>
            <Plus size={18} /> New Invoice
          </button>
          <button onClick={() => setView('history')} className={view === 'history' ? 'active' : ''}>
            <History size={18} /> Past Invoices
          </button>
          <button onClick={handleLogout} className="btn-logout">
            <LogOut size={18} /> Logout
          </button>
        </div>
      </nav>

      {view === 'history' ? (
        <PastInvoices 
          userId={session.user.id} 
          onSelectInvoice={(invData) => {
            setData(invData)
            setView('generator')
          }} 
        />
      ) : (
        <main className="main-grid">
          <section className="form-section">
            <div className="form-header-actions">
              <h2>Invoice Details</h2>
              <button 
                onClick={handleSaveInvoice} 
                className="btn-save" 
                disabled={saving}
                title="Save to History"
              >
                <Save size={18} /> {saving ? 'Saving...' : 'Save'}
              </button>
            </div>
            <InvoiceForm 
              data={data} 
              onUpdate={handleUpdate}
              onUpdateItem={handleUpdateItem}
              onAddItem={handleAddItem}
              onRemoveItem={handleRemoveItem}
            />
          </section>
          
          <section className="preview-section">
            <div className="preview-header">
              <h2>Live Preview</h2>
              <div className="actions">
                <button onClick={handleCopy} className="btn-secondary" title="Copy Summary">
                  <Copy size={18} /> Copy
                </button>
                <button onClick={() => generatePDF('invoice-preview')} className="btn-primary">
                  <Download size={18} /> Download PDF
                </button>
              </div>
            </div>
            <div id="invoice-preview" className="preview-content">
              <InvoicePreview data={data} summary={summary} />
            </div>
          </section>
        </main>
      )}
      
      <footer>
        <p>&copy; 2024 Professional Invoice Generator. Connected to Supabase.</p>
      </footer>
    </div>
  )
}

export default App
