import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api'

const WORKOUT_TYPES = ['Running', 'Cycling', 'Swimming', 'Weights', 'Yoga', 'HIIT', 'Walking', 'Other']

export default function WorkoutForm() {
  const navigate = useNavigate()
  const today = new Date().toISOString().slice(0, 10)
  const [form, setForm] = useState({ date: today, type: 'Running', duration_min: 30, rpe: 5 })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.post('/workouts/', {
        ...form,
        duration_min: parseInt(form.duration_min),
        rpe: parseInt(form.rpe),
      })
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save workout')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="page-header"><h1>Log Workout</h1></div>
      <div className="card" style={{ maxWidth: 520 }}>
        {error && <div className="alert alert-error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Date</label>
            <input type="date" value={form.date} onChange={e => set('date', e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Type</label>
            <select value={form.type} onChange={e => set('type', e.target.value)}>
              {WORKOUT_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Duration (minutes)</label>
            <input type="number" min="1" max="300" value={form.duration_min} onChange={e => set('duration_min', e.target.value)} required />
          </div>
          <div className="form-group">
            <label>RPE (Rate of Perceived Exertion): {form.rpe}/10</label>
            <input type="range" min="1" max="10" value={form.rpe} onChange={e => set('rpe', e.target.value)} />
          </div>
          <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', marginTop: '.5rem' }} disabled={loading}>
            {loading ? 'Saving...' : 'Save Workout'}
          </button>
        </form>
      </div>
    </div>
  )
}
