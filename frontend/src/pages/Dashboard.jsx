import React, { useEffect, useState } from 'react'
import { Line } from 'react-chartjs-2'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js'
import api from '../api'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/dashboard/').then(({ data }) => setStats(data)).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="container"><p style={{ padding: '3rem', textAlign: 'center' }}>Loading...</p></div>
  if (!stats) return null

  const checkins = [...(stats.recent_checkins || [])].reverse()

  const chartData = {
    labels: checkins.map(c => c.date),
    datasets: [
      { label: 'Mood', data: checkins.map(c => c.mood), borderColor: '#4f46e5', backgroundColor: 'rgba(79,70,229,.08)', fill: true, tension: .3 },
      { label: 'Energy', data: checkins.map(c => c.energy), borderColor: '#22c55e', backgroundColor: 'rgba(34,197,94,.08)', fill: true, tension: .3 },
      { label: 'Stress', data: checkins.map(c => c.stress), borderColor: '#ef4444', backgroundColor: 'rgba(239,68,68,.08)', fill: true, tension: .3 },
    ],
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: { y: { min: 0, max: 5, ticks: { stepSize: 1 } } },
    plugins: { legend: { position: 'bottom' } },
  }

  return (
    <div className="container">
      <div className="page-header"><h1>Dashboard</h1></div>

      <div className="stats-grid">
        <div className="card stat-card">
          <div className="stat-value">{stats.total_checkins}</div>
          <div className="stat-label">Check-ins</div>
        </div>
        <div className="card stat-card">
          <div className="stat-value">{stats.total_workouts}</div>
          <div className="stat-label">Workouts</div>
        </div>
        <div className="card stat-card">
          <div className="stat-value">{stats.total_meals}</div>
          <div className="stat-label">Meals</div>
        </div>
        <div className="card stat-card">
          <div className="stat-value">{stats.avg_sleep_hours ?? '—'}</div>
          <div className="stat-label">Avg Sleep (hrs)</div>
        </div>
      </div>

      {checkins.length > 0 ? (
        <div className="card">
          <h3 style={{ marginBottom: '.25rem' }}>Wellness Trends</h3>
          <p style={{ fontSize: '.8125rem', color: 'var(--text-muted)' }}>Last {checkins.length} check-ins</p>
          <div className="chart-container">
            <Line data={chartData} options={chartOptions} />
          </div>
        </div>
      ) : (
        <div className="card empty-state">
          <p>No check-ins yet. Start by logging your first daily check-in!</p>
        </div>
      )}

      {stats.recent_workouts?.length > 0 && (
        <div className="card" style={{ marginTop: '1.5rem' }}>
          <h3 style={{ marginBottom: '.75rem' }}>Recent Workouts</h3>
          <table>
            <thead><tr><th>Date</th><th>Type</th><th>Duration</th><th>RPE</th></tr></thead>
            <tbody>
              {stats.recent_workouts.map(w => (
                <tr key={w.id}><td>{w.date}</td><td>{w.type}</td><td>{w.duration_min} min</td><td>{w.rpe}/10</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {stats.recent_meals?.length > 0 && (
        <div className="card" style={{ marginTop: '1.5rem', marginBottom: '2rem' }}>
          <h3 style={{ marginBottom: '.75rem' }}>Recent Meals</h3>
          <table>
            <thead><tr><th>Date</th><th>Type</th><th>Quality</th><th>Notes</th></tr></thead>
            <tbody>
              {stats.recent_meals.map(m => (
                <tr key={m.id}><td>{m.date}</td><td>{m.meal_type}</td><td>{m.quality}/5</td><td>{m.notes || '—'}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
