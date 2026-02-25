import { useState } from 'react'
import api from '../api'

const today = new Date().toISOString().split('T')[0]

function RangeInput({ label, name, value, min, max, onChange, hint }) {
  return (
    <div className="form-group">
      <label>{label}: <strong>{value}</strong>{hint && <span style={{ fontWeight: 400, color: 'var(--muted)' }}> {hint}</span>}</label>
      <input
        type="range" name={name}
        min={min} max={max} step={1}
        value={value}
        onChange={e => onChange(name, Number(e.target.value))}
        style={{ accentColor: 'var(--primary)' }}
      />
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '.75rem', color: 'var(--muted)' }}>
        <span>{min}</span><span>{max}</span>
      </div>
    </div>
  )
}

export default function CheckInPage() {
  const [form, setForm] = useState({
    date: today,
    sleep_hours: 7,
    sleep_quality: 3,
    mood: 3,
    energy: 3,
    stress: 3,
  })
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  function handleRange(name, val) {
    setForm(p => ({ ...p, [name]: val }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await api.post('/checkin', form)
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not save check-in')
    } finally {
      setLoading(false)
    }
  }

  if (result) {
    return (
      <div>
        <h2 style={{ marginBottom: '1rem' }}>Daily Check-In</h2>
        <div className="card" style={{ maxWidth: 480 }}>
          <p className="success" style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>✓ Check-in saved!</p>
          <p>Readiness score: <strong style={{ fontSize: '1.5rem', color: 'var(--primary)' }}>
            {result.readiness_score ?? '—'}/10
          </strong></p>
          <p style={{ color: 'var(--muted)', marginTop: '.5rem', fontSize: '.9rem' }}>
            Your AI recommendation will be ready in your dashboard.
          </p>
          <button className="btn btn-secondary" style={{ marginTop: '1.2rem' }} onClick={() => setResult(null)}>
            Log another day
          </button>
        </div>
      </div>
    )
  }

  return (
    <div>
      <h2 style={{ marginBottom: '1rem' }}>Daily Check-In</h2>
      <form className="card" style={{ maxWidth: 480, display: 'flex', flexDirection: 'column', gap: '1.1rem' }} onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Date</label>
          <input type="date" value={form.date} onChange={e => setForm(p => ({ ...p, date: e.target.value }))} required />
        </div>
        <div className="form-group">
          <label>Sleep hours: <strong>{form.sleep_hours}h</strong></label>
          <input
            type="range" min={0} max={12} step={0.5}
            value={form.sleep_hours}
            onChange={e => setForm(p => ({ ...p, sleep_hours: Number(e.target.value) }))}
            style={{ accentColor: 'var(--primary)' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '.75rem', color: 'var(--muted)' }}>
            <span>0h</span><span>12h</span>
          </div>
        </div>
        <RangeInput label="Sleep quality" name="sleep_quality" value={form.sleep_quality} min={1} max={5} onChange={handleRange} hint="(1=poor, 5=great)" />
        <RangeInput label="Mood" name="mood" value={form.mood} min={1} max={5} onChange={handleRange} hint="(1=low, 5=great)" />
        <RangeInput label="Energy" name="energy" value={form.energy} min={1} max={5} onChange={handleRange} hint="(1=exhausted, 5=energised)" />
        <RangeInput label="Stress" name="stress" value={form.stress} min={1} max={5} onChange={handleRange} hint="(1=calm, 5=very stressed)" />
        {error && <p className="error">{error}</p>}
        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? 'Saving…' : 'Save Check-In'}
        </button>
      </form>
    </div>
  )
}
