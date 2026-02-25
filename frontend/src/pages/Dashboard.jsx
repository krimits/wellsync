import { useEffect, useState } from 'react'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Legend, Filler,
} from 'chart.js'
import { Line } from 'react-chartjs-2'
import api from '../api'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

function ReadinessGauge({ score }) {
  const color = score >= 7 ? 'var(--success)' : score >= 4 ? 'var(--primary)' : 'var(--danger)'
  return (
    <div style={{ textAlign: 'center', padding: '1.5rem 0' }}>
      <div style={{ fontSize: '3.5rem', fontWeight: 700, color }}>{score ?? '—'}</div>
      <div style={{ color: 'var(--muted)', fontSize: '.9rem' }}>Readiness / 10</div>
    </div>
  )
}

export default function Dashboard() {
  const name = localStorage.getItem('name') || 'User'
  const [rec, setRec] = useState(null)
  const [insights, setInsights] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/recommendations/today').catch(() => null),
      api.get('/insights').catch(() => null),
    ]).then(([r, i]) => {
      if (r) setRec(r.data)
      if (i) setInsights(i.data)
      setLoading(false)
    })
  }, [])

  const chartLabels = insights?.trends.map(t => t.date.slice(5)) ?? []
  const chartData = {
    labels: chartLabels,
    datasets: [
      {
        label: 'Energy',
        data: insights?.trends.map(t => t.energy) ?? [],
        borderColor: '#4f8ef7',
        backgroundColor: 'rgba(79,142,247,.1)',
        fill: true,
        tension: 0.3,
      },
      {
        label: 'Mood',
        data: insights?.trends.map(t => t.mood) ?? [],
        borderColor: '#a855f7',
        backgroundColor: 'rgba(168,85,247,.07)',
        fill: false,
        tension: 0.3,
      },
    ],
  }
  const chartOptions = {
    responsive: true,
    plugins: { legend: { position: 'top' }, title: { display: false } },
    scales: {
      y: { min: 1, max: 5, ticks: { stepSize: 1 } },
    },
  }

  if (loading) return <p style={{ color: 'var(--muted)' }}>Loading…</p>

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <h2>Good morning, {name}! 👋</h2>

      {/* Readiness + Recommendation */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1rem' }}>
        <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <h3 style={{ marginBottom: '.5rem' }}>Readiness</h3>
          <ReadinessGauge score={rec?.readiness_score} />
          {rec?.intensity && (
            <span style={{
              background: 'var(--bg)', borderRadius: 8, padding: '0.3rem 0.8rem',
              fontSize: '.85rem', fontWeight: 600, color: 'var(--primary)',
            }}>
              {rec.intensity.toUpperCase()} intensity
            </span>
          )}
        </div>
        <div className="card">
          <h3 style={{ marginBottom: '.75rem' }}>Today's Recommendation</h3>
          {rec ? (
            <>
              <p style={{ lineHeight: 1.6 }}>{rec.recommendation}</p>
              <p style={{ marginTop: '.75rem', fontSize: '.8rem', color: 'var(--muted)' }}>
                Source: {rec.source} · {rec.date}
              </p>
            </>
          ) : (
            <p style={{ color: 'var(--muted)' }}>Log a check-in to get your recommendation.</p>
          )}
        </div>
      </div>

      {/* Chart */}
      {insights && insights.trends.length > 0 && (
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Energy & Mood (last 30 days)</h3>
          <Line data={chartData} options={chartOptions} />
        </div>
      )}

      {/* Correlations */}
      {insights && Object.keys(insights.correlations).length > 0 && (
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Correlations</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
            {Object.entries(insights.correlations).map(([key, val]) => (
              <div key={key} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '1.6rem', fontWeight: 700, color: val >= 0 ? 'var(--success)' : 'var(--danger)' }}>
                  {val >= 0 ? '+' : ''}{val}
                </div>
                <div style={{ fontSize: '.8rem', color: 'var(--muted)', marginTop: '.2rem' }}>
                  {key.replace(/_/g, ' ↔ ')}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Workout summary */}
      {insights && (
        <div className="card">
          <h3 style={{ marginBottom: '.75rem' }}>Workout Summary (30 days)</h3>
          <div style={{ display: 'flex', gap: '2rem' }}>
            <div><strong>{insights.workout_summary_30d.total_sessions}</strong> <span style={{ color: 'var(--muted)' }}>sessions</span></div>
            <div><strong>{insights.workout_summary_30d.total_minutes}</strong> <span style={{ color: 'var(--muted)' }}>minutes</span></div>
            <div><strong>{insights.workout_summary_30d.avg_rpe ?? '—'}</strong> <span style={{ color: 'var(--muted)' }}>avg RPE</span></div>
          </div>
        </div>
      )}
    </div>
  )
}
