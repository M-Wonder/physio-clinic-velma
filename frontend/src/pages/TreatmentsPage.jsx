import { useQuery } from '@tanstack/react-query'
import { treatmentsAPI } from '../api/endpoints'
import { FileText, Calendar, Activity } from 'lucide-react'
import { format } from 'date-fns'

export default function TreatmentsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['treatments'],
    queryFn: () => treatmentsAPI.list({ ordering: '-visit_date' }),
  })
  const records = data?.data?.results || []

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Treatment Records</h1>
      {isLoading ? (
        <div className="space-y-4">{[1,2,3].map(i => <div key={i} className="card h-28 animate-pulse bg-gray-100" />)}</div>
      ) : records.length === 0 ? (
        <div className="card text-center py-12 text-gray-400">
          <FileText className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>No treatment records yet</p>
        </div>
      ) : (
        <div className="space-y-4">
          {records.map(rec => (
            <div key={rec.id} className="card hover:shadow-md transition-all">
              <div className="flex justify-between items-start">
                <div>
                  <div className="font-medium text-gray-900">{rec.diagnosis}</div>
                  <div className="text-sm text-gray-500 mt-1">{rec.doctor_name}</div>
                  <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                    <span className="flex items-center gap-1"><Calendar className="w-3 h-3" />{format(new Date(rec.visit_date), 'MMM d, yyyy')}</span>
                    {rec.pain_level_before !== null && (
                      <span className="flex items-center gap-1"><Activity className="w-3 h-3" />Pain: {rec.pain_level_before}/10 → {rec.pain_level_after}/10</span>
                    )}
                  </div>
                </div>
                <span className={rec.status === 'finalized' ? 'badge-green' : 'badge-yellow'}>{rec.status}</span>
              </div>
              {rec.treatment_given && (
                <p className="text-sm text-gray-500 mt-3 pt-3 border-t border-gray-100 line-clamp-2">{rec.treatment_given}</p>
              )}
              {rec.files?.length > 0 && (
                <div className="flex gap-2 mt-3">
                  {rec.files.map(f => (
                    <a key={f.id} href={f.file_url} target="_blank" rel="noopener noreferrer" className="badge-gray text-xs">
                      📎 {f.original_filename}
                    </a>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
