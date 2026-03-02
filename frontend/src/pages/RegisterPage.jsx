import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Activity } from 'lucide-react'
import { authAPI } from '../api/endpoints'
import { useAuthStore } from '../store/authStore'

export default function RegisterPage() {
  const [form, setForm] = useState({ email: '', first_name: '', last_name: '', phone_number: '', password: '', password2: '', gdpr_consent: false })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrors({})
    setLoading(true)
    try {
      const resp = await authAPI.register(form)
      const { user, tokens } = resp.data
      setAuth(user, tokens.access, tokens.refresh)
      navigate('/dashboard')
    } catch (err) {
      const data = err.response?.data?.detail || {}
      setErrors(data)
    } finally {
      setLoading(false)
    }
  }

  const f = (name) => ({ value: form[name], onChange: e => setForm({ ...form, [name]: e.target.value }) })

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50 flex items-center justify-center p-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 text-emerald-600 font-bold text-2xl">
            <Activity className="w-7 h-7" />PhysioClinic
          </Link>
          <h1 className="text-2xl font-bold mt-4">Create your account</h1>
          <p className="text-gray-500 mt-1">Join thousands of patients improving their health</p>
        </div>
        <div className="card shadow-md">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">First Name</label>
                <input className="input" {...f('first_name')} placeholder="John" required />
              </div>
              <div>
                <label className="label">Last Name</label>
                <input className="input" {...f('last_name')} placeholder="Doe" required />
              </div>
            </div>
            <div>
              <label className="label">Email</label>
              <input type="email" className="input" {...f('email')} placeholder="john@example.com" required />
              {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
            </div>
            <div>
              <label className="label">Phone (optional)</label>
              <input type="tel" className="input" {...f('phone_number')} placeholder="+1 555 000 0000" />
            </div>
            <div>
              <label className="label">Password</label>
              <input type="password" className="input" {...f('password')} placeholder="Min 8 characters" required />
            </div>
            <div>
              <label className="label">Confirm Password</label>
              <input type="password" className="input" {...f('password2')} placeholder="Repeat password" required />
              {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password}</p>}
            </div>
            <label className="flex items-start gap-3 cursor-pointer">
              <input type="checkbox" className="mt-1"
                checked={form.gdpr_consent}
                onChange={e => setForm({ ...form, gdpr_consent: e.target.checked })}
                required
              />
              <span className="text-sm text-gray-600">
                I agree to the <a href="#" className="text-emerald-600">Privacy Policy</a> and consent to my health data being processed for treatment purposes.
              </span>
            </label>
            <button type="submit" className="btn-primary w-full py-3" disabled={loading}>
              {loading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>
          <p className="text-center text-sm text-gray-500 mt-4">
            Already have an account? <Link to="/login" className="text-emerald-600 font-medium">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
