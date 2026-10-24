/**
 * BookAppointmentPage — multi-step appointment booking flow.
 * Step 1: Select Service
 * Step 2: Select Therapist
 * Step 3: Pick Date & Time
 * Step 4: Confirm (clinic session or home visit, with address for home visits)
 */
import { useState, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { servicesAPI, doctorsAPI, appointmentsAPI } from '../api/endpoints'
import { useClinic } from '../api/clinic'
import { formatKES } from '../lib/format'
import { format, addDays } from 'date-fns'
import { ChevronLeft, ChevronRight, Check, Calendar, Clock } from 'lucide-react'

// Home Physiotherapy defaults to a home visit; everything else to the clinic (patient can change it).
const visitTypeFor = (svc) => (svc?.slug === 'home-physiotherapy' ? 'home' : 'clinic')

const STEPS = ['Service', 'Therapist', 'Date & Time', 'Confirm']

export default function BookAppointmentPage() {
  const [step, setStep] = useState(0)
  const [selected, setSelected] = useState({ service: null, doctor: null, date: null, time: null, reason: '', visitType: 'clinic', homeAddress: '' })
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  // Pre-select from URL params
  const { data: svcData } = useQuery({ queryKey: ['services'], queryFn: () => servicesAPI.list() })
  useEffect(() => {
    const did = searchParams.get('doctor')
    if (did) { setSelected(s => ({ ...s, doctor: { id: parseInt(did) } })); setStep(2) }
  }, [])
  useEffect(() => {
    const sid = searchParams.get('service')
    if (!sid || !svcData) return
    const svc = (svcData.data?.results || []).find(x => x.id === parseInt(sid))
    if (svc) {
      setSelected(s => s.service ? s : { ...s, service: svc, visitType: visitTypeFor(svc) })
      setStep(st => (st === 0 ? 1 : st))
    }
  }, [svcData])

  const bookMutation = useMutation({
    mutationFn: (data) => appointmentsAPI.book(data),
    onSuccess: () => navigate('/appointments?booked=1'),
  })

  const handleBook = () => {
    bookMutation.mutate({
      doctor_id: selected.doctor.id,
      service_id: selected.service.id,
      appointment_date: selected.date,
      start_time: selected.time,
      reason_for_visit: selected.reason,
      visit_type: selected.visitType,
      home_address: selected.visitType === 'home' ? selected.homeAddress : '',
    })
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-2">Book Appointment</h1>
      <p className="text-gray-500 mb-8">Complete the steps below to schedule your visit</p>

      {/* Step Indicator */}
      <div className="flex items-center gap-2 mb-8 overflow-x-auto pb-2">
        {STEPS.map((s, i) => (
          <div key={s} className="flex items-center gap-2 shrink-0">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors
              ${i < step ? 'bg-brand-600 text-white' : i === step ? 'bg-brand-100 text-brand-700 border-2 border-brand-600' : 'bg-gray-100 text-gray-400'}`}>
              {i < step ? <Check className="w-4 h-4" /> : i + 1}
            </div>
            <span className={`text-sm ${i === step ? 'font-medium text-brand-700' : 'text-gray-400'}`}>{s}</span>
            {i < STEPS.length - 1 && <div className={`w-8 h-0.5 ${i < step ? 'bg-brand-600' : 'bg-gray-200'}`} />}
          </div>
        ))}
      </div>

      {/* Steps */}
      <div className="card">
        {step === 0 && <ServiceStep selected={selected} onSelect={svc => { setSelected(s => ({ ...s, service: svc, visitType: visitTypeFor(svc) })); setStep(1) }} />}
        {step === 1 && <TherapistStep selected={selected} onSelect={doc => { setSelected(s => ({ ...s, doctor: doc })); setStep(2) }} />}
        {step === 2 && <DateTimeStep selected={selected} onSelect={(date, time) => { setSelected(s => ({ ...s, date, time })); setStep(3) }} />}
        {step === 3 && (
          <ConfirmStep
            selected={selected}
            onReasonChange={r => setSelected(s => ({ ...s, reason: r }))}
            onVisitTypeChange={v => setSelected(s => ({ ...s, visitType: v }))}
            onAddressChange={a => setSelected(s => ({ ...s, homeAddress: a }))}
            onConfirm={handleBook}
            loading={bookMutation.isPending}
            error={bookMutation.error?.response?.data?.error}
          />
        )}
      </div>

      {step > 0 && (
        <button onClick={() => setStep(step - 1)} className="btn-ghost mt-4">
          <ChevronLeft className="w-4 h-4" /> Back
        </button>
      )}
    </div>
  )
}

function ServiceStep({ selected, onSelect }) {
  const { data } = useQuery({ queryKey: ['services'], queryFn: () => servicesAPI.list() })
  const services = data?.data?.results || []
  return (
    <div>
      <h2 className="font-semibold text-gray-900 mb-4">Select a Service</h2>
      <div className="space-y-3">
        {services.map(svc => (
          <button key={svc.id} onClick={() => onSelect(svc)}
            className={`w-full text-left p-4 rounded-xl border-2 transition-all
              ${selected?.service?.id === svc.id ? 'border-brand-500 bg-brand-50' : 'border-gray-200 hover:border-brand-300'}`}>
            <div className="flex items-center gap-3">
              <span className="text-2xl">{svc.icon || '🏥'}</span>
              <div>
                <div className="font-medium">{svc.name}</div>
                <div className="text-sm text-gray-500">{svc.short_description}</div>
              </div>
              <ChevronRight className="w-4 h-4 text-gray-400 ml-auto" />
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}

function TherapistStep({ selected, onSelect }) {
  const { data } = useQuery({
    queryKey: ['doctors'],
    queryFn: () => doctorsAPI.list({ is_accepting_patients: true })
  })
  const doctors = data?.data?.results || []
  return (
    <div>
      <h2 className="font-semibold text-gray-900 mb-4">Select a Therapist</h2>
      <div className="space-y-3">
        {doctors.map(doc => (
          <button key={doc.id} onClick={() => onSelect(doc)}
            className={`w-full text-left p-4 rounded-xl border-2 transition-all
              ${selected?.doctor?.id === doc.id ? 'border-brand-500 bg-brand-50' : 'border-gray-200 hover:border-brand-300'}`}>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-brand-100 flex items-center justify-center text-xl">🧑‍⚕️</div>
              <div>
                <div className="font-medium">{doc.user?.first_name} {doc.user?.last_name}</div>
                <div className="text-sm text-gray-500">{doc.specialty_names?.slice(0, 2).join(' · ')}</div>
                {doc.years_experience > 0 && <div className="text-xs text-gray-400 mt-0.5">{doc.years_experience} years experience</div>}
              </div>
              <ChevronRight className="w-4 h-4 text-gray-400 ml-auto" />
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}

function DateTimeStep({ selected, onSelect }) {
  const today = new Date()
  const [activeDate, setActiveDate] = useState(format(addDays(today, 1), 'yyyy-MM-dd'))

  const { data: slotsData, isLoading } = useQuery({
    queryKey: ['slots', selected?.doctor?.id, activeDate],
    queryFn: () => doctorsAPI.availability(selected?.doctor?.id, activeDate),
    enabled: !!selected?.doctor?.id,
  })

  const slots = slotsData?.data?.slots || []
  const dates = Array.from({ length: 14 }, (_, i) => format(addDays(today, i + 1), 'yyyy-MM-dd'))

  return (
    <div>
      <h2 className="font-semibold text-gray-900 mb-4">Choose Date & Time</h2>
      {/* Date selector */}
      <div className="flex gap-2 overflow-x-auto pb-3 mb-6">
        {dates.map(d => {
          const dt = new Date(d + 'T12:00:00')
          return (
            <button key={d} onClick={() => setActiveDate(d)}
              className={`shrink-0 flex flex-col items-center px-3 py-2 rounded-xl border-2 transition-all min-w-14
                ${activeDate === d ? 'border-brand-500 bg-brand-50 text-brand-700' : 'border-gray-200 hover:border-gray-300 text-gray-600'}`}>
              <span className="text-xs">{format(dt, 'EEE')}</span>
              <span className="font-bold">{format(dt, 'd')}</span>
              <span className="text-xs">{format(dt, 'MMM')}</span>
            </button>
          )
        })}
      </div>
      {/* Time slots */}
      {isLoading ? (
        <div className="grid grid-cols-4 gap-2">
          {[...Array(8)].map((_,i) => <div key={i} className="h-10 bg-gray-100 rounded-lg animate-pulse" />)}
        </div>
      ) : slots.length === 0 ? (
        <p className="text-center text-gray-400 py-8">No slots available on this date</p>
      ) : (
        <div className="grid grid-cols-4 gap-2">
          {slots.map(slot => (
            <button key={slot.time}
              onClick={() => slot.available && onSelect(activeDate, slot.time)}
              disabled={!slot.available}
              className={`py-2.5 rounded-lg text-sm font-medium transition-all
                ${!slot.available ? 'bg-gray-100 text-gray-300 cursor-not-allowed' :
                  selected?.time === slot.time ? 'bg-brand-600 text-white' :
                  'bg-brand-50 text-brand-700 hover:bg-brand-100'}`}>
              {slot.time}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

function ConfirmStep({ selected, onReasonChange, onVisitTypeChange, onAddressChange, onConfirm, loading, error }) {
  const clinic = useClinic()
  const isHome = selected.visitType === 'home'
  const fee = isHome ? clinic.rates.home : clinic.rates.clinic
  const missingAddress = isHome && !selected.homeAddress.trim()

  return (
    <div>
      <h2 className="font-semibold text-gray-900 mb-6">Confirm Appointment</h2>

      {/* Where? */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {[['clinic', 'At the clinic', clinic.rates.clinic], ['home', 'Home visit', clinic.rates.home]].map(([value, label, price]) => (
          <button key={value} type="button" onClick={() => onVisitTypeChange(value)}
            className={`text-left p-3 rounded-xl border-2 transition-all
              ${selected.visitType === value ? 'border-brand-500 bg-brand-50' : 'border-gray-200 hover:border-brand-300'}`}>
            <div className="font-medium text-sm">{label}</div>
            <div className="text-xs text-gray-500">{formatKES(price)} per session</div>
          </button>
        ))}
      </div>
      {isHome && (
        <div className="mb-4">
          <label className="label">Home address</label>
          <textarea className="input resize-none" rows={2} value={selected.homeAddress}
            placeholder="Building, street, area and any directions"
            onChange={e => onAddressChange(e.target.value)} />
        </div>
      )}

      <div className="bg-gray-50 rounded-xl p-4 space-y-3 mb-6">
        <Row icon="🏥" label="Service" value={selected.service?.name} />
        <Row icon="🧑‍⚕️" label="Therapist" value={`${selected.doctor?.user?.first_name ?? ''} ${selected.doctor?.user?.last_name ?? ''}`.trim()} />
        <Row icon={<Calendar className="w-4 h-4" />} label="Date" value={selected.date && format(new Date(selected.date + 'T12:00'), 'MMMM d, yyyy')} />
        <Row icon={<Clock className="w-4 h-4" />} label="Time" value={selected.time} />
        <Row icon="📍" label="Where" value={isHome ? 'Home visit' : (clinic.address || 'At the clinic')} />
        <Row icon="💰" label="Fee" value={formatKES(fee)} />
      </div>
      <div className="mb-6">
        <label className="label">Reason for visit (optional)</label>
        <textarea
          className="input resize-none"
          rows={3}
          placeholder="Describe your symptoms or reason for the appointment..."
          onChange={e => onReasonChange(e.target.value)}
        />
      </div>
      {error && <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 mb-4 text-sm">{error}</div>}
      <button onClick={onConfirm} className="btn-primary w-full py-3 text-base" disabled={loading || missingAddress}>
        {loading ? 'Booking...' : 'Confirm Booking'}
      </button>
      {missingAddress && <p className="text-xs text-red-500 text-center mt-2">Please enter your home address to book a home visit.</p>}
      <p className="text-xs text-gray-400 text-center mt-3">
        You'll receive a confirmation email. Please cancel at least {clinic.cancellation_notice_hours} hours before your appointment.
      </p>
    </div>
  )
}

function Row({ icon, label, value }) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-gray-400 text-lg w-6 text-center">{icon}</span>
      <span className="text-gray-500 text-sm w-20">{label}</span>
      <span className="font-medium text-gray-900 text-sm">{value}</span>
    </div>
  )
}
