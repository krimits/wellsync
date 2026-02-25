import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api'

export default function CheckInForm() {
  const navigate = useNavigate()
  const today = new Date().toISOString().slice(0, 10)
  const [form, setForm] = useState({ date: today, sleep_hours: 7, sleep_quality: 3, mood: 3, energy: 3, stress: 3 })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.post('/checkins/', {
        ...form,
        sleep_hours: parseFloat(form.sleep_hours),
        sleep_quality: parseInt(form.sleep_quality),
        mood: parseInt(form.mood),
        energy: parseInt(form.energy),
        stress: parseInt(form.stress),
      })
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save check-in')
    } finally {
      setLoading(false)
    }
  }

  const ScaleInput = ({ label, field, min = 1, max = 5 }) => (
    <div className="form-group">
      <label>{label}: {form[field]}</label>
      <input type="range" min={min} max={max} value={form[field]} onChange={e => set(field, e.target.value)} />
    </div>
  )

  return (
    <div className="container">
      <div className="page-header"><h1>Daily Check-in</h1></div>
      <div className="card" style={{ maxWidth: 520 }}>
        {error && <div className="alert alert-error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Date</label>
            <input type="date" value={form.date} onChange={e => set('date', e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Sleep hours: {form.sleep_hours}</label>
            <input type="range" min="0" max="12" step="0.5" value={form.sleep_hours} onChange={e => set('sleep_hours', e.target.value)} />
          </div>
          <ScaleInput label="Sleep quality" field="sleep_quality" />
          <ScaleInput label="Mood" field="mood" />
          <ScaleInput label="Energy" field="energy" />
          <ScaleInput label="Stress" field="stress" />
          <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', marginTop: '.5rem' }} disabled={loading}>
            {loading ? 'Saving...' : 'Save Check-in'}
          </button>
        </form>
      </div>
    </div>
  )
}
