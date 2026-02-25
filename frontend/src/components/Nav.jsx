import { Link, useNavigate } from 'react-router-dom'

export default function Nav() {
  const navigate = useNavigate()
  const name = localStorage.getItem('name') || 'User'

  function logout() {
    localStorage.clear()
    navigate('/login')
  }

  return (
    <nav style={{
      background: '#fff',
      borderBottom: '1px solid var(--border)',
      padding: '0.75rem 1.5rem',
      display: 'flex',
      alignItems: 'center',
      gap: '1.5rem',
    }}>
      <span style={{ fontWeight: 700, fontSize: '1.1rem', color: 'var(--primary)' }}>
        🧘 WellSync
      </span>
      <Link to="/">Dashboard</Link>
      <Link to="/checkin">Check-In</Link>
      <Link to="/logs">Logs</Link>
      <span style={{ marginLeft: 'auto', color: 'var(--muted)', fontSize: '.9rem' }}>
        {name}
      </span>
      <button className="btn btn-secondary" style={{ padding: '0.35rem 1rem', fontSize: '.85rem' }} onClick={logout}>
        Logout
      </button>
    </nav>
  )
}
