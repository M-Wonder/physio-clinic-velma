import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { patientAPI, notificationsAPI } from '../api/endpoints'
import { useAuthStore } from '../store/authStore'
import { User, Bell, Shield, Download } from 'lucide-react'

export default function ProfilePage() {
  const { user, updateUser } = useAuthStore()
  const qc = useQueryClient()
  const [saved, setSaved] = useState(false)

  const { data: profileData } = useQuery({
    queryKey: ['patient-profile'],
    queryFn: () => patientAPI.getProfile(),
  })

  const { data: prefsData } = useQuery({
    queryKey: ['notification-prefs'],
    queryFn: () => notificationsAPI.getPreferences(),
  })

  const updatePrefsMutation = useMutation({
    mutationFn: (data) => notificationsAPI.updatePreferences(data),
    onSuccess: () => { setSaved(true); setTimeout(() => setSaved(false), 2000) }
  })

  const prefs = prefsData?.data || {}
  const profile = profileData?.data || {}

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
      <h1 className="text-2xl font-bold">My Profile</h1>

      {/* Personal Info */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <User className="w-5 h-5 text-emerald-600" />
          <h2 className="font-semibold">Personal Information</h2>
        </div>
        <div className="grid sm:grid-cols-2 gap-4 text-sm">
          <div><span className="text-gray-500">Name:</span> <span className="font-medium ml-2">{user?.name}</span></div>
          <div><span className="text-gray-500">Email:</span> <span className="font-medium ml-2">{user?.email}</span></div>
          <div><span className="text-gray-500">Role:</span> <span className="font-medium ml-2 capitalize">{user?.role}</span></div>
          {profile.age && <div><span className="text-gray-500">Age:</span> <span className="font-medium ml-2">{profile.age} years</span></div>}
          {profile.blood_type && <div><span className="text-gray-500">Blood Type:</span> <span className="font-medium ml-2">{profile.blood_type}</span></div>}
          {profile.primary_doctor_name && <div><span className="text-gray-500">Primary Doctor:</span> <span className="font-medium ml-2">{profile.primary_doctor_name}</span></div>}
        </div>
      </div>

      {/* Notifications */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Bell className="w-5 h-5 text-emerald-600" />
          <h2 className="font-semibold">Notification Preferences</h2>
        </div>
        <div className="space-y-3">
          <label className="flex items-center justify-between cursor-pointer">
            <div>
              <div className="font-medium text-sm">Email Notifications</div>
              <div className="text-xs text-gray-500">Confirmations, reminders, and updates</div>
            </div>
            <input type="checkbox" className="w-4 h-4"
              checked={prefs.email_notifications ?? true}
              onChange={e => updatePrefsMutation.mutate({ email_notifications: e.target.checked })}
            />
          </label>
          <label className="flex items-center justify-between cursor-pointer">
            <div>
              <div className="font-medium text-sm">SMS Notifications</div>
              <div className="text-xs text-gray-500">Text message reminders (requires phone number)</div>
            </div>
            <input type="checkbox" className="w-4 h-4"
              checked={prefs.sms_notifications ?? false}
              onChange={e => updatePrefsMutation.mutate({ sms_notifications: e.target.checked })}
            />
          </label>
          {saved && <p className="text-xs text-emerald-600">Preferences saved ✓</p>}
        </div>
      </div>

      {/* GDPR */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Shield className="w-5 h-5 text-emerald-600" />
          <h2 className="font-semibold">Privacy & Data</h2>
        </div>
        <div className="space-y-3">
          <button onClick={() => patientAPI.exportData().then(r => {
            const blob = new Blob([JSON.stringify(r.data, null, 2)], { type: 'application/json' })
            const a = document.createElement('a'); a.href = URL.createObjectURL(blob)
            a.download = 'my-health-data.json'; a.click()
          })} className="btn-outline text-sm flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export My Data
          </button>
          <p className="text-xs text-gray-400">Under GDPR, you have the right to access and export your personal data.</p>
        </div>
      </div>
    </div>
  )
}
