import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { appointmentsAPI } from '../api/endpoints'
import { format } from 'date-fns'
import { Calendar, Clock, X, RefreshCw } from 'lucide-react'
import { Link } from 'react-router-dom'

const statusColors = {
  scheduled: 'badge-blue', confirmed: 'badge-green',
  completed: 'badge-gray', cancelled: 'badge-red',
  in_progress: 'badge-yellow', rescheduled: 'badge-yellow', no_show: 'badge-red'
}

export default function AppointmentsPage() {
  const [filter, setFilter] = useState('upcoming')
  const qc = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['appointments', filter],
    queryFn: () => {
      const params = filter === 'upcoming' ? { status: 'scheduled' } : filter === 'past' ? { status: 'completed' } : {}
      return appointmentsAPI.list({ ...params, ordering: '-appointment_date' })
    }
  })

  const cancelMutation = useMutation({
    mutationFn: ({ id, reason }) => appointmentsAPI.cancel(id, { reason }),
    onSuccess: () => qc.invalidateQueries(['appointments']),
  })

  const appointments = data?.data?.results || []

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">My Appointments</h1>
        <Link to="/book" className="btn-primary text-sm">New Appointment</Link>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-6">
        {['upcoming', 'past', 'all'].map(f => (
          <button key={f} onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors capitalize
              ${filter === f ? 'bg-emerald-600 text-white' : 'bg-white text-gray-600 border border-gray-200 hover:border-emerald-300'}`}>
            {f}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1,2,3].map(i => <div key={i} className="card h-24 animate-pulse bg-gray-100" />)}
        </div>
      ) : appointments.length === 0 ? (
        <div className="card text-center py-12 text-gray-400">
          <Calendar className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>No appointments found</p>
          <Link to="/book" className="btn-primary mt-4 text-sm inline-block">Book Appointment</Link>
        </div>
      ) : (
        <div className="space-y-4">
          {appointments.map(appt => (
            <div key={appt.id} className="card hover:shadow-md transition-all">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center text-xl shrink-0">
                    🏥
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{appt.doctor_name}</div>
                    <div className="text-sm text-gray-500">{appt.service_name}</div>
                    <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {format(new Date(appt.appointment_date), 'MMM d, yyyy')}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {appt.start_time?.slice(0, 5)}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={statusColors[appt.status] || 'badge-gray'}>{appt.status.replace('_', ' ')}</span>
                  {appt.is_cancellable && (
                    <button
                      onClick={() => { if (window.confirm('Cancel this appointment?')) cancelMutation.mutate({ id: appt.id, reason: '' }) }}
                      className="btn-ghost text-red-500 text-xs py-1 px-2"
                      disabled={cancelMutation.isPending}
                    >
                      <X className="w-3 h-3" /> Cancel
                    </button>
                  )}
                </div>
              </div>
              {appt.reason_for_visit && (
                <p className="text-xs text-gray-400 mt-3 pt-3 border-t border-gray-100">
                  Reason: {appt.reason_for_visit}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
