import { Link } from 'react-router-dom'
import { Calendar, Award, Shield, Clock, ArrowRight, Star } from 'lucide-react'

const services = [
  { icon: '🦴', name: 'Musculoskeletal Rehab', desc: 'Restore movement and function after injury' },
  { icon: '⚽', name: 'Sports Injury', desc: 'Specialized care for athletes' },
  { icon: '🧠', name: 'Neurological Rehab', desc: 'Recovery for neurological conditions' },
  { icon: '❤️', name: 'Cardiopulmonary', desc: 'Heart and lung rehabilitation' },
  { icon: '💊', name: 'Pain Management', desc: 'Multidisciplinary pain relief' },
  { icon: '👴', name: 'Geriatric Care', desc: 'Specialized care for older adults' },
]

export default function HomePage() {
  return (
    <div>
      {/* Hero */}
      <section className="bg-gradient-to-br from-emerald-600 to-teal-700 text-white py-24 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl font-bold mb-6 leading-tight">
            Expert Physiotherapy<br />
            <span className="text-emerald-200">Tailored to You</span>
          </h1>
          <p className="text-xl text-emerald-100 mb-10 max-w-2xl mx-auto">
            Comprehensive rehabilitation services with experienced therapists. Book your appointment online in minutes.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/book" className="bg-white text-emerald-700 font-bold px-8 py-4 rounded-xl hover:bg-emerald-50 transition-colors text-lg flex items-center gap-2 justify-center">
              <Calendar className="w-5 h-5" />
              Book Appointment
            </Link>
            <Link to="/services" className="border-2 border-white text-white font-bold px-8 py-4 rounded-xl hover:bg-white/10 transition-colors text-lg flex items-center gap-2 justify-center">
              Our Services
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="bg-white py-10 border-b border-gray-100">
        <div className="max-w-5xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {[['2,500+', 'Patients Treated'], ['12+', 'Years Experience'], ['4', 'Expert Doctors'], ['98%', 'Satisfaction Rate']].map(([v, l]) => (
            <div key={l}>
              <div className="text-3xl font-bold text-emerald-600">{v}</div>
              <div className="text-gray-500 text-sm mt-1">{l}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Services */}
      <section className="py-20 px-4 max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900">Our Services</h2>
          <p className="text-gray-500 mt-3">Comprehensive physiotherapy across 7 specialties</p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map(({ icon, name, desc }) => (
            <div key={name} className="card hover:shadow-md transition-shadow group cursor-pointer">
              <div className="text-4xl mb-3">{icon}</div>
              <h3 className="font-semibold text-gray-900 mb-1 group-hover:text-emerald-600 transition-colors">{name}</h3>
              <p className="text-gray-500 text-sm">{desc}</p>
            </div>
          ))}
        </div>
        <div className="text-center mt-8">
          <Link to="/services" className="btn-outline">View All Services</Link>
        </div>
      </section>

      {/* Why us */}
      <section className="bg-emerald-50 py-20 px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Why Choose PhysioClinic?</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: Award, title: 'Expert Therapists', desc: 'Certified physiotherapists with specialized training in their respective fields.' },
              { icon: Clock, title: 'Flexible Scheduling', desc: 'Book appointments online 24/7. Evening and weekend slots available.' },
              { icon: Shield, title: 'HIPAA Compliant', desc: 'Your medical data is encrypted and protected with enterprise-grade security.' },
            ].map(({ icon: Icon, title, desc }) => (
              <div key={title} className="text-center">
                <div className="w-14 h-14 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Icon className="w-7 h-7 text-emerald-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
                <p className="text-gray-500 text-sm">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 text-center">
        <h2 className="text-3xl font-bold mb-4">Ready to Start Your Recovery?</h2>
        <p className="text-gray-500 mb-8 max-w-lg mx-auto">Join thousands of patients who've regained their quality of life with our expert care.</p>
        <Link to="/register" className="btn-primary text-base px-8 py-3">Get Started Today</Link>
      </section>
    </div>
  )
}
