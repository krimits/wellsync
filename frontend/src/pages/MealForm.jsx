import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api'

const MEAL_TYPES = ['breakfast', 'lunch', 'dinner', 'snack']

export default function MealForm() {
  const navigate = useNavigate()
  const today = new Date().toISOString().slice(0, 10)
  const [form, setForm] = useState({ date: today, meal_type: 'lunch', quality: 3, notes: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.post('/meals/', {
        ...form,
        quality: parseInt(form.quality),
        notes: form.notes || null,
      })
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save meal')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="page-header"><h1>Log Meal</h1></div>
      <div className="card" style={{ maxWidth: 520 }}>
        {error && <div className="alert alert-error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Date</label>
            <input type="date" value={form.date} onChange={e => set('date', e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Meal type</label>
            <select value={form.meal_type} onChange={e => set('meal_type', e.target.value)}>
              {MEAL_TYPES.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Quality: {form.quality}/5</label>
            <input type="range" min="1" max="5" value={form.quality} onChange={e => set('quality', e.target.value)} />
          </div>
          <div className="form-group">
            <label>Notes (optional)</label>
            <textarea rows="3" value={form.notes} onChange={e => set('notes', e.target.value)} placeholder="What did you eat?" />
          </div>
          <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', marginTop: '.5rem' }} disabled={loading}>
            {loading ? 'Saving...' : 'Save Meal'}
          </button>
        </form>
      </div>
    </div>
  )
}
