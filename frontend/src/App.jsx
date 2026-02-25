import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import api from './api'
import Navbar from './components/Navbar'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import CheckInForm from './pages/CheckInForm'
import WorkoutForm from './pages/WorkoutForm'
import MealForm from './pages/MealForm'

function ProtectedRoute({ user, children }) {
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  const [user, setUser] = useState(null)
  const [checking, setChecking] = useState(true)

  const fetchUser = async () => {
    const token = localStorage.getItem('token')
    if (!token) { setChecking(false); return }
    try {
      const { data } = await api.get('/auth/me')
      setUser(data)
    } catch {
      localStorage.removeItem('token')
    } finally {
      setChecking(false)
    }
  }

  useEffect(() => { fetchUser() }, [])

  if (checking) return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>Loading...</div>

  return (
    <BrowserRouter>
      {user && <Navbar user={user} onLogout={() => setUser(null)} />}
      <Routes>
        <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login onAuth={fetchUser} />} />
        <Route path="/register" element={user ? <Navigate to="/" replace /> : <Register onAuth={fetchUser} />} />
        <Route path="/" element={<ProtectedRoute user={user}><Dashboard /></ProtectedRoute>} />
        <Route path="/checkin" element={<ProtectedRoute user={user}><CheckInForm /></ProtectedRoute>} />
        <Route path="/workout" element={<ProtectedRoute user={user}><WorkoutForm /></ProtectedRoute>} />
        <Route path="/meal" element={<ProtectedRoute user={user}><MealForm /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
