import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Activity } from 'lucide-react'
import { authAPI } from '../api/endpoints'
import { useAuthStore } from '../store/authStore'

export default function RegisterPage() {
  const [form, setForm] = useState({
    email: '', first_name: '', last_name: '',
    phone_number: '', password: '', password2: '', gdpr_consent: false
  })
  // BUG FIX: errors must be an object to handle field-level DRF errors
  const [errors, setErrors] = useState({})
  const [globalError, setGlobalError] = useState('')
  const [loading, setLoading] = useState(false)
  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrors({})
    setGlobalError('')
    setLoading(true)
    try {
      const resp = await authAPI.register(form)
      const { user, tokens } = resp.data
      setAuth(user, tokens.access, tokens.refresh)
      navigate('/dashboard')
    } catch (err) {
      const data = err.response?.data
      if (!data) {
        setGlobalError('Network error. Please check your connection.')
        return
      }
      // BUG FIX: DRF returns field errors directly on data, not on data.detail
      // e.g. { email: ['Already exists.'], password: ['Too short.'] }
      // Non-field errors come as data.non_field_errors or data.detail
      if (typeof data === 'object' && !Array.isArray(data)) {
        const { detail, non_field_errors, ...fieldErrors } = data
        if (detail) setGlobalError(detail)
        if (non_field_errors) setGlobalError(non_field_errors[0])
        if (Object.keys(fieldErrors).length) {
          // Flatten array errors to strings
          const flat = {}
          for (const [k, v] of Object.entries(fieldErrors)) {
            flat[k] = Array.isArray(v) ? v[0] : v
          }
          setErrors(flat)
        }
      } else {
        setGlobalError('Registration failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const field = (name) => ({
    value: form[name],
    onChange: e => setForm({ ...form, [name]: e.target.value })
  })

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
          {globalError && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 mb-4 text-sm">
              {globalError}
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">First Name</label>
                <input className="input" {...field('first_name')} placeholder="John" required />
                {errors.first_name && <p className="text-red-500 text-xs mt-1">{errors.first_name}</p>}
              </div>
              <div>
                <label className="label">Last Name</label>
                <input className="input" {...field('last_name')} placeholder="Doe" required />
                {errors.last_name && <p className="text-red-500 text-xs mt-1">{errors.last_name}</p>}
              </div>
            </div>

            <div>
              <label className="label">Email</label>
              <input type="email" className="input" {...field('email')} placeholder="john@example.com" required />
              {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
            </div>

            <div>
              <label className="label">Phone Number <span className="text-gray-400">(optional)</span></label>
              <input type="tel" className="input" {...field('phone_number')} placeholder="+1234567890" />
              {errors.phone_number && <p className="text-red-500 text-xs mt-1">{errors.phone_number}</p>}
            </div>

            <div>
              <label className="label">Password</label>
              <input type="password" className="input" {...field('password')} placeholder="Min 8 characters" required />
              {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password}</p>}
            </div>

            <div>
              <label className="label">Confirm Password</label>
              <input type="password" className="input" {...field('password2')} placeholder="Repeat password" required />
              {errors.password2 && <p className="text-red-500 text-xs mt-1">{errors.password2}</p>}
            </div>

            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                id="gdpr"
                className="mt-1 h-4 w-4 text-emerald-600 rounded border-gray-300"
                checked={form.gdpr_consent}
                onChange={e => setForm({ ...form, gdpr_consent: e.target.checked })}
              />
              <label htmlFor="gdpr" className="text-sm text-gray-600">
                I agree to the{' '}
                <a href="#" className="text-emerald-600 underline">Privacy Policy</a>
                {' '}and consent to data processing.
              </label>
            </div>
            {errors.gdpr_consent && <p className="text-red-500 text-xs">{errors.gdpr_consent}</p>}

            <button type="submit" className="btn-primary w-full py-3" disabled={loading}>
              {loading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>

          <p className="text-center text-sm text-gray-500 mt-4">
            Already have an account?{' '}
            <Link to="/login" className="text-emerald-600 font-medium">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}