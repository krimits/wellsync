import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'

export default function Navbar({ user, onLogout }) {
  const navigate = useNavigate()

  const handleLogout = () => {
    localStorage.removeItem('token')
    onLogout()
    navigate('/login')
  }

  return (
    <nav>
      <div className="nav-inner">
        <span className="brand">WellSync</span>
        <div className="nav-links">
          <NavLink to="/">Dashboard</NavLink>
          <NavLink to="/checkin">Check-in</NavLink>
          <NavLink to="/workout">Workout</NavLink>
          <NavLink to="/meal">Meal</NavLink>
          <span style={{ color: 'var(--text-muted)', fontSize: '.8125rem' }}>{user?.name}</span>
          <button className="btn btn-outline btn-sm" onClick={handleLogout}>Logout</button>
        </div>
      </div>
    </nav>
  )
}
