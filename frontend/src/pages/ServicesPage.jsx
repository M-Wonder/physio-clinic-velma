import { useQuery } from '@tanstack/react-query'
import { servicesAPI } from '../api/endpoints'
import { Link } from 'react-router-dom'
import { Clock, DollarSign, Users, AlertCircle } from 'lucide-react'

export default function ServicesPage() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['services'],
    queryFn: () => servicesAPI.list(),
    retry: 2,
  })

  // data is the axios response; data.data is the DRF payload
  const services = data?.data?.results || []

  if (isError) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-20 text-center">
        <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-700 mb-2">Could not load services</h2>
        <p className="text-gray-500 text-sm mb-4">
          {error?.message || 'Please check your connection and try again.'}
        </p>
        <button onClick={() => window.location.reload()}
          className="btn-primary">Retry</button>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold">Our Services</h1>
        <p className="text-gray-500 mt-3 max-w-lg mx-auto">
          Evidence-based physiotherapy across a wide range of specialties.
        </p>
      </div>

      {isLoading ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) =>
            <div key={i} className="card h-64 animate-pulse bg-gray-100" />
          )}
        </div>
      ) : services.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <p className="text-lg">No services found.</p>
          <p className="text-sm mt-2">Run <code className="bg-gray-100 px-2 py-1 rounded">docker compose exec backend python manage.py seed_data</code> to add services.</p>
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map(svc => (
            <div key={svc.id} className="card hover:shadow-md transition-all group">
              <div className="text-4xl mb-3">{svc.icon || '🏥'}</div>
              <h3 className="font-semibold text-gray-900 text-lg mb-2 group-hover:text-emerald-600 transition-colors">
                {svc.name}
              </h3>
              <p className="text-gray-500 text-sm mb-4 line-clamp-2">{svc.short_description}</p>
              <div className="flex items-center gap-4 text-xs text-gray-400 mb-4">
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />{svc.session_duration_minutes} min
                </span>
                {svc.price_per_session > 0 && (
                  <span className="flex items-center gap-1">
                    <DollarSign className="w-3 h-3" />${svc.price_per_session}
                  </span>
                )}
              </div>
              <Link to="/book" className="text-emerald-600 text-sm font-medium hover:underline">
                Book this service →
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}