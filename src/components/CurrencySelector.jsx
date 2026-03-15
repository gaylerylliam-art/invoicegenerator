import React, { useState, useRef, useEffect } from 'react'
import { ChevronDown, Search } from 'lucide-react'
import { currencies } from '../utils/currencies'

function CurrencySelector({ selectedCurrency, onSelect }) {
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const dropdownRef = useRef(null)

  const filteredCurrencies = currencies.filter(c => 
    c.code.toLowerCase().includes(searchTerm.toLowerCase()) || 
    c.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className="currency-selector-container" ref={dropdownRef}>
      <label>Currency <span className="required-star">*</span></label>
      <div 
        className={`currency-display ${isOpen ? 'active' : ''}`} 
        onClick={() => setIsOpen(!isOpen)}
      >
        <span>{selectedCurrency.code} {selectedCurrency.name}</span>
        <ChevronDown size={18} />
      </div>

      {isOpen && (
        <div className="currency-dropdown">
          <div className="search-container">
            <Search size={16} className="search-icon" />
            <input 
              type="text" 
              placeholder="Search currency..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              autoFocus
            />
          </div>
          <div className="currency-list">
            <div 
              className="currency-option default-option"
              onClick={() => {
                onSelect(currencies.find(c => c.code === 'USD'))
                setIsOpen(false)
                setSearchTerm('')
              }}
            >
              [Default Currency]
            </div>
            {filteredCurrencies.map((c) => (
              <div 
                key={c.code} 
                className={`currency-option ${selectedCurrency.code === c.code ? 'selected' : ''}`}
                onClick={() => {
                  onSelect(c)
                  setIsOpen(false)
                  setSearchTerm('')
                }}
              >
                <span className="code">{c.code}</span>
                <span className="name">{c.name}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default CurrencySelector
