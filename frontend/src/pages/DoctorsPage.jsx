import { useQuery } from '@tanstack/react-query'
import { doctorsAPI } from '../api/endpoints'
import { Link } from 'react-router-dom'
import { Star, Clock, User } from 'lucide-react'

export default function DoctorsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['doctors'],
    queryFn: () => doctorsAPI.list({ is_accepting_patients: true }),
  })
  const doctors = data?.data?.results || []

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold">Our Doctors</h1>
        <p className="text-gray-500 mt-3">Meet our team of experienced physiotherapists</p>
      </div>
      {isLoading ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1,2,3].map(i => <div key={i} className="card h-80 animate-pulse bg-gray-100" />)}
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {doctors.map(doc => (
            <div key={doc.id} className="card hover:shadow-md transition-all">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-16 h-16 rounded-2xl bg-emerald-100 flex items-center justify-center text-2xl">
                  {doc.avatar_url ? <img src={doc.avatar_url} className="w-full h-full rounded-2xl object-cover" alt="" /> : '👨‍⚕️'}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Dr. {doc.user?.first_name} {doc.user?.last_name}</h3>
                  <p className="text-sm text-gray-500">{doc.years_experience} years experience</p>
                  {doc.is_accepting_patients ? (
                    <span className="badge-green text-xs mt-1">Accepting Patients</span>
                  ) : (
                    <span className="badge-red text-xs mt-1">Fully Booked</span>
                  )}
                </div>
              </div>
              <p className="text-gray-500 text-sm mb-4 line-clamp-3">{doc.bio || 'Experienced physiotherapist dedicated to patient recovery.'}</p>
              {doc.specialty_names?.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-4">
                  {doc.specialty_names.slice(0, 2).map(s => (
                    <span key={s} className="badge-blue text-xs">{s}</span>
                  ))}
                </div>
              )}
              <div className="text-sm text-gray-400 mb-4">
                <Clock className="w-3 h-3 inline mr-1" />
                Available:{' '}
                {doc.schedules?.filter(s => s.is_available).map(s => s.day_name?.slice(0, 3)).join(', ') || 'See schedule'}
              </div>
              <Link to={`/book?doctor=${doc.id}`} className="btn-primary w-full text-sm py-2 justify-center">
                Book Appointment
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
