import { useQuery } from '@tanstack/react-query'
import { servicesAPI } from '../api/endpoints'
import { Link } from 'react-router-dom'
import { Clock, DollarSign, Users } from 'lucide-react'

export default function ServicesPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['services'],
    queryFn: () => servicesAPI.list(),
  })
  const services = data?.data?.results || []

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
          {[...Array(6)].map((_,i) => <div key={i} className="card h-64 animate-pulse bg-gray-100" />)}
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
                <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{svc.session_duration_minutes} min</span>
                <span className="flex items-center gap-1"><Users className="w-3 h-3" />{svc.doctor_count} doctors</span>
                {svc.price_per_session > 0 && (
                  <span className="flex items-center gap-1"><DollarSign className="w-3 h-3" />${svc.price_per_session}</span>
                )}
              </div>
              {svc.conditions_treated && (
                <div className="flex flex-wrap gap-1 mb-4">
                  {svc.conditions_treated.split(',').slice(0, 3).map(c => (
                    <span key={c} className="badge-gray text-xs">{c.trim()}</span>
                  ))}
                </div>
              )}
              <Link to={`/book?service=${svc.id}`} className="btn-outline w-full text-sm py-2">
                Book This Service
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
