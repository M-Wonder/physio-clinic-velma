import { useQuery } from '@tanstack/react-query'
import { doctorsAPI } from '../api/endpoints'
import { Link } from 'react-router-dom'
import { Star, Clock, AlertCircle } from 'lucide-react'

export default function DoctorsPage() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['doctors'],
    queryFn: () => doctorsAPI.list({ is_accepting_patients: true }),
    retry: 2,
  })
  const doctors = data?.data?.results || []

  if (isError) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-20 text-center">
        <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-700 mb-2">Could not load doctors</h2>
        <p className="text-gray-500 text-sm mb-4">
          {error?.message || 'Please check your connection and try again.'}
        </p>
        <button onClick={() => window.location.reload()} className="btn-primary">Retry</button>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold">Our Doctors</h1>
        <p className="text-gray-500 mt-3">Meet our team of experienced physiotherapists</p>
      </div>

      {isLoading ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => <div key={i} className="card h-64 animate-pulse bg-gray-100" />)}
        </div>
      ) : doctors.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <p className="text-lg">No doctors found.</p>
          <p className="text-sm mt-2">Run <code className="bg-gray-100 px-2 py-1 rounded">docker compose exec backend python manage.py seed_data</code> to add doctors.</p>
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {doctors.map(doc => (
            <div key={doc.id} className="card hover:shadow-md transition-all">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-14 h-14 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700 font-bold text-xl">
                  {doc.user?.first_name?.[0]}{doc.user?.last_name?.[0]}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">
                    Dr. {doc.user?.first_name} {doc.user?.last_name}
                  </h3>
                  <div className="flex items-center gap-1 text-yellow-400 text-xs">
                    <Star className="w-3 h-3 fill-current" />
                    <span className="text-gray-500">{doc.years_experience} yrs experience</span>
                  </div>
                </div>
              </div>

              {doc.specialty_names?.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-3">
                  {doc.specialty_names.map(s => (
                    <span key={s} className="text-xs bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full">
                      {s}
                    </span>
                  ))}
                </div>
              )}

              <p className="text-gray-500 text-sm mb-4 line-clamp-2">{doc.bio}</p>

              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-500 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {doc.schedules?.length > 0
                    ? `${doc.schedules.length} days/week`
                    : 'Schedule TBD'}
                </div>
                {doc.is_accepting_patients && (
                  <Link to="/book" className="btn-primary text-sm py-1.5 px-3">
                    Book Now
                  </Link>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}