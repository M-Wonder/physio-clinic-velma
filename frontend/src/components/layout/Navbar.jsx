import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useState } from 'react'
import { Menu, X, Activity, User, LogOut, Calendar, Clipboard } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { authAPI } from '../../api/endpoints'

export default function Navbar() {
  const { user, isAuthenticated, logout, refreshToken } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)

  const handleLogout = async () => {
    try { await authAPI.logout(refreshToken) } catch {}
    logout()
    navigate('/login')
  }

  const navLinks = [
    { to: '/', label: 'Home' },
    { to: '/services', label: 'Services' },
    { to: '/doctors', label: 'Doctors' },
    ...(isAuthenticated ? [
      { to: '/appointments', label: 'Appointments', icon: Calendar },
      { to: '/treatments', label: 'Records', icon: Clipboard },
    ] : []),
  ]

  const isActive = (path) => location.pathname === path

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 text-emerald-600 font-bold text-xl">
            <Activity className="w-6 h-6" />
            <span>PhysioClinic</span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-6">
            {navLinks.map(({ to, label }) => (
              <Link key={to} to={to}
                className={`text-sm font-medium transition-colors ${isActive(to) ? 'text-emerald-600' : 'text-gray-600 hover:text-emerald-600'}`}>
                {label}
              </Link>
            ))}
          </div>

          {/* Auth Actions */}
          <div className="hidden md:flex items-center gap-3">
            {isAuthenticated ? (
              <>
                <Link to="/book" className="btn-primary text-sm py-2">Book Appointment</Link>
                <div className="relative group">
                  <button className="flex items-center gap-2 text-gray-700 hover:text-emerald-600">
                    <User className="w-5 h-5" />
                    <span className="text-sm">{user?.name || user?.email}</span>
                  </button>
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-gray-100 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                    <Link to="/profile" className="flex items-center gap-2 px-4 py-3 text-sm hover:bg-gray-50 rounded-t-xl">
                      <User className="w-4 h-4" /> Profile
                    </Link>
                    <button onClick={handleLogout} className="flex items-center gap-2 px-4 py-3 text-sm text-red-600 hover:bg-red-50 w-full rounded-b-xl">
                      <LogOut className="w-4 h-4" /> Logout
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <>
                <Link to="/login" className="btn-ghost text-sm">Login</Link>
                <Link to="/register" className="btn-primary text-sm">Register</Link>
              </>
            )}
          </div>

          {/* Mobile menu toggle */}
          <button className="md:hidden" onClick={() => setMenuOpen(!menuOpen)}>
            {menuOpen ? <X /> : <Menu />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="md:hidden bg-white border-t border-gray-100 px-4 py-3 space-y-2">
          {navLinks.map(({ to, label }) => (
            <Link key={to} to={to} onClick={() => setMenuOpen(false)}
              className="block py-2 text-gray-700 hover:text-emerald-600">{label}</Link>
          ))}
          {isAuthenticated ? (
            <>
              <Link to="/book" onClick={() => setMenuOpen(false)} className="block py-2 text-emerald-600 font-medium">Book Appointment</Link>
              <button onClick={handleLogout} className="block py-2 text-red-600">Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" onClick={() => setMenuOpen(false)} className="block py-2">Login</Link>
              <Link to="/register" onClick={() => setMenuOpen(false)} className="block py-2 text-emerald-600 font-medium">Register</Link>
            </>
          )}
        </div>
      )}
    </nav>
  )
}
