import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Calendar, FileText, User, Clock, Plus, ArrowRight } from 'lucide-react'
import { appointmentsAPI } from '../api/endpoints'
import { useAuthStore } from '../store/authStore'
import { format } from 'date-fns'

const statusColors = {
  scheduled: 'badge-blue', confirmed: 'badge-green',
  completed: 'badge-gray', cancelled: 'badge-red', in_progress: 'badge-yellow'
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const { data, isLoading } = useQuery({
    queryKey: ['appointments', 'upcoming'],
    queryFn: () => appointmentsAPI.list({ status: 'scheduled', ordering: 'appointment_date' }),
  })

  const appointments = data?.data?.results || []

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold">Good {getTimeOfDay()}, {user?.name?.split(' ')[0]}!</h1>
          <p className="text-gray-500 mt-1">Here's your health overview</p>
        </div>
        <Link to="/book" className="btn-primary w-fit">
          <Plus className="w-4 h-4" />
          Book Appointment
        </Link>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { icon: Calendar, label: 'Upcoming', value: appointments.length, color: 'text-emerald-600', bg: 'bg-emerald-50' },
          { icon: FileText, label: 'Records', value: '—', color: 'text-blue-600', bg: 'bg-blue-50' },
          { icon: Clock, label: 'Next Visit', value: appointments[0]?.appointment_date ? format(new Date(appointments[0].appointment_date), 'MMM d') : '—', color: 'text-purple-600', bg: 'bg-purple-50' },
          { icon: User, label: 'My Doctor', value: appointments[0]?.doctor_name?.replace('Dr. ', '') || '—', color: 'text-orange-600', bg: 'bg-orange-50' },
        ].map(({ icon: Icon, label, value, color, bg }) => (
          <div key={label} className="card flex items-center gap-3">
            <div className={`w-10 h-10 rounded-xl ${bg} flex items-center justify-center`}>
              <Icon className={`w-5 h-5 ${color}`} />
            </div>
            <div>
              <p className="text-xs text-gray-500">{label}</p>
              <p className="font-semibold text-gray-900">{value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Upcoming Appointments */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-gray-900">Upcoming Appointments</h2>
          <Link to="/appointments" className="text-sm text-emerald-600 flex items-center gap-1 hover:underline">
            View all <ArrowRight className="w-3 h-3" />
          </Link>
        </div>
        {isLoading ? (
          <div className="space-y-3">
            {[1,2,3].map(i => <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />)}
          </div>
        ) : appointments.length === 0 ? (
          <div className="text-center py-10 text-gray-400">
            <Calendar className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>No upcoming appointments</p>
            <Link to="/book" className="btn-primary mt-4 text-sm">Book now</Link>
          </div>
        ) : (
          <div className="space-y-3">
            {appointments.slice(0, 5).map(appt => (
              <div key={appt.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                <div>
                  <p className="font-medium text-gray-900">{appt.doctor_name}</p>
                  <p className="text-sm text-gray-500">{appt.service_name || 'Physiotherapy'}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium">{format(new Date(appt.appointment_date), 'MMM d, yyyy')}</p>
                  <p className="text-xs text-gray-500">{appt.start_time?.slice(0, 5)}</p>
                </div>
                <span className={statusColors[appt.status] || 'badge-gray'}>{appt.status}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function getTimeOfDay() {
  const h = new Date().getHours()
  if (h < 12) return 'morning'
  if (h < 17) return 'afternoon'
  return 'evening'
}
