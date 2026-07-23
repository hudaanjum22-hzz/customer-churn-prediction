import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabaseClient'
import { History as HistoryIcon, TrendingDown, TrendingUp } from 'lucide-react'

export default function History() {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    setLoading(true)
    const { data, error } = await supabase
      .from('predictions')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(50)

    if (error) setError(error.message)
    else setRecords(data)
    setLoading(false)
  }

  return (
    <div>
      <div className="text-center mb-10 mt-2">
        <h2 className="text-3xl font-bold tracking-tight">Prediction History</h2>
        <p className="text-slate-400 text-sm mt-2">The last 50 churn predictions run on this dashboard.</p>
      </div>

      <div className="glass-panel p-6">
        {loading && <p className="text-slate-400 text-sm text-center py-8">Loading history...</p>}
        {error && <p className="text-rose-400 text-sm text-center py-8">Failed to load: {error}</p>}

        {!loading && !error && records.length === 0 && (
          <div className="text-center py-12">
            <div className="icon-chip bg-indigo-500/15 text-indigo-400 mx-auto mb-4" style={{ width: '3rem', height: '3rem' }}>
              <HistoryIcon size={20} />
            </div>
            <p className="text-slate-500 text-sm">No predictions yet — run one on the Predict Customer page.</p>
          </div>
        )}

        {!loading && !error && records.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left border-b border-white/5">
                  <th className="eyebrow pb-3 pr-4">Date</th>
                  <th className="eyebrow pb-3 pr-4">Age</th>
                  <th className="eyebrow pb-3 pr-4">Plan</th>
                  <th className="eyebrow pb-3 pr-4">Charges</th>
                  <th className="eyebrow pb-3 pr-4">Tenure</th>
                  <th className="eyebrow pb-3 pr-4">Satisfaction</th>
                  <th className="eyebrow pb-3 pr-4">Result</th>
                  <th className="eyebrow pb-3">Probability</th>
                </tr>
              </thead>
              <tbody>
                {records.map((r) => {
                  const isChurn = r.prediction === 'Likely to Churn'
                  return (
                    <tr key={r.id} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                      <td className="py-3 pr-4 text-slate-400 font-mono-data text-xs">
                        {new Date(r.created_at).toLocaleString()}
                      </td>
                      <td className="py-3 pr-4">{r.age}</td>
                      <td className="py-3 pr-4">{r.subscription_type}</td>
                      <td className="py-3 pr-4 font-mono-data">${r.monthly_charges}</td>
                      <td className="py-3 pr-4">{r.tenure_months}mo</td>
                      <td className="py-3 pr-4">{r.satisfaction_score}/10</td>
                      <td className="py-3 pr-4">
                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold
                          ${isChurn ? 'bg-rose-500/15 text-rose-400' : 'bg-emerald-500/15 text-emerald-400'}`}>
                          {isChurn ? <TrendingDown size={11} /> : <TrendingUp size={11} />}
                          {isChurn ? 'Churn' : 'Stay'}
                        </span>
                      </td>
                      <td className="py-3 font-mono-data">{Math.round(r.churn_probability * 100)}%</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
