import { useQuery } from '@tanstack/react-query'
import { servicesAPI } from '../api/endpoints'
import { useClinic } from '../api/clinic'
import { formatKES, splitList } from '../lib/format'
import { Link } from 'react-router-dom'
import { AlertCircle, Building2, Home as HomeIcon } from 'lucide-react'

export default function ServicesPage() {
  const clinic = useClinic()
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
        <button onClick={() => window.location.reload()} className="btn-primary">Retry</button>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold">Our Services</h1>
        <p className="text-gray-500 mt-3 max-w-xl mx-auto">
          Personalized, evidence-informed physiotherapy — at the clinic or in the comfort of your home.
        </p>
        <div className="flex flex-wrap justify-center gap-3 mt-5 text-sm">
          <span className="inline-flex items-center gap-2 bg-brand-50 text-brand-800 px-4 py-2 rounded-full">
            <Building2 className="w-4 h-4" /> Clinic session <strong>{formatKES(clinic.rates.clinic)}</strong>
          </span>
          <span className="inline-flex items-center gap-2 bg-brand-50 text-brand-800 px-4 py-2 rounded-full">
            <HomeIcon className="w-4 h-4" /> Home visit <strong>{formatKES(clinic.rates.home)}</strong>
          </span>
        </div>
      </div>

      {isLoading ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) =>
            <div key={i} className="card h-64 animate-pulse bg-gray-100" />
          )}
        </div>
      ) : services.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <p className="text-lg">Our services are being updated.</p>
          <p className="text-sm mt-2">Please check back shortly or contact the clinic.</p>
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map(svc => (
            <div key={svc.id} className="card hover:shadow-md transition-all group flex flex-col">
              <div className="text-4xl mb-3">{svc.icon || '🏥'}</div>
              <h3 className="font-semibold text-gray-900 text-lg mb-2 group-hover:text-brand-600 transition-colors">
                {svc.name}
              </h3>
              <p className="text-gray-500 text-sm mb-3">{svc.short_description}</p>
              <ul className="text-sm text-gray-600 space-y-1 mb-5 flex-1">
                {splitList(svc.conditions_treated).map(item => (
                  <li key={item} className="flex gap-2">
                    <span className="text-gold-500">•</span>{item}
                  </li>
                ))}
              </ul>
              <Link to={`/book?service=${svc.id}`} className="text-brand-600 text-sm font-medium hover:underline">
                Book this service →
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
