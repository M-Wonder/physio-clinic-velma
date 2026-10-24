import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  Calendar, ArrowRight, Activity, Move, Dumbbell, Heart,
  ClipboardCheck, UserCheck, TrendingUp, Home as HomeIcon, Building2,
} from 'lucide-react'
import { servicesAPI } from '../api/endpoints'
import { useClinic } from '../api/clinic'
import { formatKES } from '../lib/format'

const PILLARS = [
  { icon: Activity, label: 'Reduce Pain' },
  { icon: Move, label: 'Improve Movement' },
  { icon: Dumbbell, label: 'Build Strength' },
  { icon: Heart, label: 'Live Better' },
]

const DIFFERENT = [
  { icon: ClipboardCheck, title: 'Individual Assessment', desc: 'We take the time to understand your condition, goals and lifestyle.' },
  { icon: UserCheck, title: 'Personalized Treatment Plans', desc: 'Tailored to your needs and designed for real-life results.' },
  { icon: Dumbbell, title: 'Exercise Prescription & Progression', desc: 'Evidence-based exercises to help you build strength, improve movement and prevent recurrence.' },
  { icon: TrendingUp, title: 'Ongoing Monitoring', desc: 'We track your progress and adjust your plan to ensure the best outcomes.' },
]

export default function HomePage() {
  const clinic = useClinic()
  const { data } = useQuery({ queryKey: ['services'], queryFn: () => servicesAPI.list() })
  const services = data?.data?.results || []

  return (
    <div>
      {/* Hero */}
      <section className="bg-gradient-to-br from-brand-900 via-brand-800 to-brand-600 text-white py-20 sm:py-24 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-gold-400 tracking-[0.3em] text-xs sm:text-sm font-semibold mb-5">PHYSIOTHERAPY CLINIC · NAIROBI</p>
          <h1 className="text-4xl sm:text-6xl font-bold mb-6 leading-tight">
            Move Better.<br />
            <span className="text-gold-300">Feel Better.</span>
          </h1>
          <p className="text-lg sm:text-xl text-brand-100 mb-10 max-w-2xl mx-auto">
            At {clinic.name}, we are passionate about helping you move better, reduce pain and regain
            the things that matter most to you. Through evidence-informed care and personalized
            treatment, we support you at every stage of your recovery journey.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/book" className="bg-white text-brand-800 font-bold px-8 py-4 rounded-xl hover:bg-brand-50 transition-colors text-lg flex items-center gap-2 justify-center">
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

      {/* Pillars */}
      <section className="bg-white py-10 border-b border-gray-100">
        <div className="max-w-5xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {PILLARS.map(({ icon: Icon, label }) => (
            <div key={label} className="flex flex-col items-center gap-2">
              <div className="w-12 h-12 rounded-full bg-brand-50 flex items-center justify-center">
                <Icon className="w-6 h-6 text-brand-700" />
              </div>
              <div className="font-semibold text-brand-800 text-sm">{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Services */}
      <section className="py-20 px-4 max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900">Our Services</h2>
          <p className="text-gray-500 mt-3">Personalized physiotherapy, at the clinic or in the comfort of your home</p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.length === 0
            ? [...Array(6)].map((_, i) => <div key={i} className="card h-36 animate-pulse bg-gray-100" />)
            : services.map((svc) => (
              <Link key={svc.id} to="/services" className="card hover:shadow-md transition-shadow group">
                <div className="text-4xl mb-3">{svc.icon || '🏥'}</div>
                <h3 className="font-semibold text-gray-900 mb-1 group-hover:text-brand-600 transition-colors">{svc.name}</h3>
                <p className="text-gray-500 text-sm">{svc.short_description}</p>
              </Link>
            ))}
        </div>
        <div className="text-center mt-8">
          <Link to="/services" className="btn-outline">View All Services</Link>
        </div>
      </section>

      {/* Rates */}
      <section className="bg-brand-50 py-16 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Our Rates</h2>
          <p className="text-gray-500 mb-8">Simple, per-session pricing</p>
          <div className="grid sm:grid-cols-2 gap-6">
            {[
              { icon: Building2, label: 'Clinic Session', price: clinic.rates.clinic },
              { icon: HomeIcon, label: 'Home Visit', price: clinic.rates.home },
            ].map(({ icon: Icon, label, price }) => (
              <div key={label} className="card flex flex-col items-center gap-2">
                <Icon className="w-8 h-8 text-brand-700" />
                <div className="text-gray-600 font-medium">{label}</div>
                <div className="text-3xl font-bold text-brand-800">{formatKES(price)}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* What makes us different */}
      <section className="py-20 px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">What Makes Us Different</h2>
          <div className="grid sm:grid-cols-2 gap-8">
            {DIFFERENT.map(({ icon: Icon, title, desc }) => (
              <div key={title} className="flex gap-4">
                <div className="w-12 h-12 shrink-0 bg-gold-300/30 rounded-full flex items-center justify-center">
                  <Icon className="w-6 h-6 text-gold-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>
                  <p className="text-gray-500 text-sm">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-brand-800 text-white py-16 px-4 text-center">
        <p className="text-2xl sm:text-3xl italic mb-2 text-gold-300">“Because movement matters in every season of life.”</p>
        <p className="text-brand-100 mb-8">Supporting you to move well today for a healthier tomorrow.</p>
        <Link to="/register" className="inline-block bg-white text-brand-800 font-bold px-8 py-3 rounded-xl hover:bg-brand-50 transition-colors">
          Create your account
        </Link>
      </section>
    </div>
  )
}
