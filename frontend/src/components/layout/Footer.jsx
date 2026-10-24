import { Phone, Mail, MapPin, MessageCircle } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useClinic } from '../../api/clinic'
import { whatsappLink } from '../../lib/format'

const SERVICE_LINKS = [
  'Musculoskeletal Physiotherapy',
  'Neurological Rehabilitation',
  "Women's Health Physiotherapy",
  'Rehabilitation & Recovery',
  'Hands-On & Soft Tissue Therapy',
  'Home Physiotherapy',
]

export default function Footer() {
  const clinic = useClinic()
  const wa = whatsappLink(clinic.whatsapp)

  return (
    <footer className="bg-brand-900 text-gray-300 pt-12 pb-6">
      <div className="max-w-7xl mx-auto px-4 grid md:grid-cols-4 gap-8 mb-8">
        <div>
          <div className="flex items-center gap-3 mb-3">
            <img src="/logo-mark.png" alt="" className="h-10 w-10 rounded-full bg-white p-0.5" />
            <div className="leading-tight">
              <div className="text-white font-extrabold tracking-wide">NEUROMOTION</div>
              <div className="text-[9px] tracking-[0.25em] text-gold-400">PHYSIOTHERAPY CLINIC</div>
            </div>
          </div>
          <p className="text-sm text-gray-400 italic">{clinic.tagline}</p>
        </div>
        <div>
          <h3 className="text-white font-medium mb-3">Services</h3>
          <ul className="space-y-2 text-sm">
            {SERVICE_LINKS.map((s) => (
              <li key={s}><Link to="/services" className="hover:text-gold-400 transition-colors">{s}</Link></li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="text-white font-medium mb-3">Quick Links</h3>
          <ul className="space-y-2 text-sm">
            {[['Our Therapists', '/doctors'], ['Book Appointment', '/book'], ['Patient Portal', '/dashboard']].map(([l, h]) => (
              <li key={h}><Link to={h} className="hover:text-gold-400 transition-colors">{l}</Link></li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="text-white font-medium mb-3">Get in touch</h3>
          <ul className="space-y-2 text-sm">
            {clinic.phone && (
              <li className="flex items-center gap-2"><Phone className="w-4 h-4 text-gold-400" />
                <a href={`tel:${clinic.phone.replace(/\s/g, '')}`} className="hover:text-gold-400">{clinic.phone}</a></li>
            )}
            {wa && (
              <li className="flex items-center gap-2"><MessageCircle className="w-4 h-4 text-gold-400" />
                <a href={wa} target="_blank" rel="noreferrer" className="hover:text-gold-400">WhatsApp us</a></li>
            )}
            {clinic.email && (
              <li className="flex items-center gap-2"><Mail className="w-4 h-4 text-gold-400" />
                <a href={`mailto:${clinic.email}`} className="hover:text-gold-400 break-all">{clinic.email}</a></li>
            )}
            {clinic.address && (
              <li className="flex items-center gap-2"><MapPin className="w-4 h-4 text-gold-400" />{clinic.address}</li>
            )}
          </ul>
        </div>
      </div>
      <div className="border-t border-white/10 pt-4 text-center text-xs text-gray-400">
        © {new Date().getFullYear()} {clinic.name}. Your health information is kept confidential.
      </div>
    </footer>
  )
}
