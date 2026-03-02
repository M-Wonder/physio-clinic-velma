import { Activity, Phone, Mail, MapPin } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300 pt-12 pb-6">
      <div className="max-w-7xl mx-auto px-4 grid md:grid-cols-4 gap-8 mb-8">
        <div>
          <div className="flex items-center gap-2 text-white font-bold text-lg mb-3">
            <Activity className="w-5 h-5 text-emerald-400" />
            PhysioClinic
          </div>
          <p className="text-sm text-gray-400">Professional physiotherapy care with a patient-first approach.</p>
        </div>
        <div>
          <h3 className="text-white font-medium mb-3">Services</h3>
          <ul className="space-y-2 text-sm">
            {['Musculoskeletal', 'Sports Injuries', 'Neurological', 'Pain Management'].map(s => (
              <li key={s}><Link to="/services" className="hover:text-emerald-400 transition-colors">{s}</Link></li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="text-white font-medium mb-3">Quick Links</h3>
          <ul className="space-y-2 text-sm">
            {[['Doctors', '/doctors'], ['Book Appointment', '/book'], ['Patient Portal', '/dashboard']].map(([l, h]) => (
              <li key={h}><Link to={h} className="hover:text-emerald-400 transition-colors">{l}</Link></li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="text-white font-medium mb-3">Contact</h3>
          <ul className="space-y-2 text-sm">
            <li className="flex items-center gap-2"><Phone className="w-4 h-4 text-emerald-400" />+1-555-PHYSIO</li>
            <li className="flex items-center gap-2"><Mail className="w-4 h-4 text-emerald-400" />info@physio.clinic</li>
            <li className="flex items-center gap-2"><MapPin className="w-4 h-4 text-emerald-400" />123 Health Avenue</li>
          </ul>
        </div>
      </div>
      <div className="border-t border-gray-800 pt-4 text-center text-xs text-gray-500">
        © 2025 PhysioClinic. HIPAA & GDPR Compliant.
      </div>
    </footer>
  )
}
