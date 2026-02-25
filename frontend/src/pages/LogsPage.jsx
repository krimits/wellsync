import { useState } from 'react'
import api from '../api'

const today = new Date().toISOString().split('T')[0]

export default function LogsPage() {
  const [tab, setTab] = useState('workout')

  const [workout, setWorkout] = useState({ date: today, type: 'running', duration_min: 30, rpe: 5 })
  const [meal, setMeal] = useState({ date: today, meal_type: 'lunch', quality: 3, notes: '' })
  const [wMsg, setWMsg] = useState('')
  const [mMsg, setMMsg] = useState('')
  const [loading, setLoading] = useState(false)

  async function submitWorkout(e) {
    e.preventDefault()
    setWMsg('')
    setLoading(true)
    try {
      await api.post('/workout', { ...workout, duration_min: Number(workout.duration_min), rpe: Number(workout.rpe) })
      setWMsg('Workout logged!')
    } catch (err) {
      setWMsg(err.response?.data?.detail || 'Error')
    } finally {
      setLoading(false)
    }
  }

  async function submitMeal(e) {
    e.preventDefault()
    setMMsg('')
    setLoading(true)
    try {
      await api.post('/meal', { ...meal, quality: Number(meal.quality) })
      setMMsg('Meal logged!')
    } catch (err) {
      setMMsg(err.response?.data?.detail || 'Error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2 style={{ marginBottom: '1rem' }}>Activity Logs</h2>

      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
        {['workout', 'meal'].map(t => (
          <button
            key={t} className={`btn ${tab === t ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setTab(t)} style={{ textTransform: 'capitalize' }}
          >
            {t === 'workout' ? '🏋️ Workout' : '🥗 Meal'}
          </button>
        ))}
      </div>

      {tab === 'workout' && (
        <form className="card" style={{ maxWidth: 420, display: 'flex', flexDirection: 'column', gap: '1rem' }} onSubmit={submitWorkout}>
          <div className="form-group">
            <label>Date</label>
            <input type="date" value={workout.date} onChange={e => setWorkout(p => ({ ...p, date: e.target.value }))} required />
          </div>
          <div className="form-group">
            <label>Type</label>
            <select value={workout.type} onChange={e => setWorkout(p => ({ ...p, type: e.target.value }))}>
              {['running', 'cycling', 'swimming', 'weightlifting', 'yoga', 'hiit', 'walking', 'other'].map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Duration (min)</label>
            <input type="number" min={1} max={600} value={workout.duration_min}
              onChange={e => setWorkout(p => ({ ...p, duration_min: e.target.value }))} required />
          </div>
          <div className="form-group">
            <label>RPE (1-10): <strong>{workout.rpe}</strong></label>
            <input type="range" min={1} max={10} step={1} value={workout.rpe}
              onChange={e => setWorkout(p => ({ ...p, rpe: Number(e.target.value) }))}
              style={{ accentColor: 'var(--primary)' }} />
          </div>
          {wMsg && <p className={wMsg.includes('!') ? 'success' : 'error'}>{wMsg}</p>}
          <button className="btn btn-primary" type="submit" disabled={loading}>Log Workout</button>
        </form>
      )}

      {tab === 'meal' && (
        <form className="card" style={{ maxWidth: 420, display: 'flex', flexDirection: 'column', gap: '1rem' }} onSubmit={submitMeal}>
          <div className="form-group">
            <label>Date</label>
            <input type="date" value={meal.date} onChange={e => setMeal(p => ({ ...p, date: e.target.value }))} required />
          </div>
          <div className="form-group">
            <label>Meal type</label>
            <select value={meal.meal_type} onChange={e => setMeal(p => ({ ...p, meal_type: e.target.value }))}>
              {['breakfast', 'lunch', 'dinner', 'snack'].map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Quality (1-5): <strong>{meal.quality}</strong></label>
            <input type="range" min={1} max={5} step={1} value={meal.quality}
              onChange={e => setMeal(p => ({ ...p, quality: Number(e.target.value) }))}
              style={{ accentColor: 'var(--primary)' }} />
          </div>
          <div className="form-group">
            <label>Notes (optional)</label>
            <input type="text" value={meal.notes} onChange={e => setMeal(p => ({ ...p, notes: e.target.value }))} />
          </div>
          {mMsg && <p className={mMsg.includes('!') ? 'success' : 'error'}>{mMsg}</p>}
          <button className="btn btn-primary" type="submit" disabled={loading}>Log Meal</button>
        </form>
      )}
    </div>
  )
}
