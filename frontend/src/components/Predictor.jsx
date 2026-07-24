import { useState } from 'react'
import { supabase } from '../lib/supabaseClient'
import { Sparkles, ShieldCheck, Zap, Crown, Building2 } from 'lucide-react'

const initialForm = {
  age: '',
  subscription_type: 'Basic',
  monthly_charges: '',
  tenure_months: '',
  satisfaction_score: '',
  support_tickets: '',
  usage_hours_per_week: '',
}

const subscriptionOptions = [
  { value: 'Basic', label: 'Basic', subtitle: 'Entry-level plan', icon: Zap, color: 'slate' },
  { value: 'Premium', label: 'Premium', subtitle: 'Most popular tier', icon: Crown, color: 'indigo' },
  { value: 'Enterprise', label: 'Enterprise', subtitle: 'Full feature access', icon: Building2, color: 'cyan' },
]

const colorStyles = {
  slate: { bg: 'bg-slate-500/15', text: 'text-slate-300', ring: 'ring-slate-400/40' },
  indigo: { bg: 'bg-indigo-500/15', text: 'text-indigo-300', ring: 'ring-indigo-400/50' },
  cyan: { bg: 'bg-cyan-500/15', text: 'text-cyan-300', ring: 'ring-cyan-400/50' },
}

export default function Predictor() {
  const [form, setForm] = useState(initialForm)
  const [errors, setErrors] = useState({})
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [apiError, setApiError] = useState(null)

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const selectSubscription = (value) => {
    setForm({ ...form, subscription_type: value })
  }

  const validate = () => {
    const newErrors = {}
    const age = Number(form.age)
    const tenure = Number(form.tenure_months)
    const satisfaction = Number(form.satisfaction_score)
    const tickets = Number(form.support_tickets)
    const usage = Number(form.usage_hours_per_week)
    const charges = Number(form.monthly_charges)

    if (!form.age || age < 18 || age > 100) newErrors.age = 'Age must be 18-100'
    if (!form.monthly_charges || charges < 0) newErrors.monthly_charges = 'Must be 0 or more'
    if (!form.tenure_months || tenure < 0 || tenure > 120) newErrors.tenure_months = 'Must be 0-120'
    if (!form.satisfaction_score || satisfaction < 1 || satisfaction > 10) newErrors.satisfaction_score = 'Must be 1-10'
    if (!form.support_tickets || tickets < 0 || tickets > 20) newErrors.support_tickets = 'Must be 0-20'
    if (!form.usage_hours_per_week || usage < 0 || usage > 168) newErrors.usage_hours_per_week = 'Must be 0-168'

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setApiError(null)
    setResult(null)

    if (!validate()) return

    setLoading(true)

    const payload = {
      age: Number(form.age),
      subscription_type: form.subscription_type,
      monthly_charges: Number(form.monthly_charges),
      tenure_months: Number(form.tenure_months),
      satisfaction_score: Number(form.satisfaction_score),
      support_tickets: Number(form.support_tickets),
      usage_hours_per_week: Number(form.usage_hours_per_week),
    }

    try {
      const res = await fetch('https://customer-churn-prediction-sub.onrender.com', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!res.ok) throw new Error('Prediction request failed')
      const data = await res.json()
      setResult(data)

      supabase.from('predictions').insert({
        ...payload,
        prediction: data.prediction,
        churn_probability: data.churn_probability,
      }).then(({ error }) => {
        if (error) console.error('Supabase log failed:', error.message)
      })
    } catch (err) {
      setApiError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getRecommendations = () => {
    if (!result) return []
    const recs = []
    const tickets = Number(form.support_tickets)
    const satisfaction = Number(form.satisfaction_score)
    const tenure = Number(form.tenure_months)

    if (tickets > 3) recs.push('Escalate support priority — high ticket volume detected')
    if (satisfaction < 4) recs.push('Assign a high-touch customer success manager')
    if (tenure < 6) recs.push('Enroll in new-customer onboarding follow-up')
    if (recs.length === 0) recs.push('Customer profile looks healthy — no urgent action needed')
    return recs
  }

  const isChurn = result?.prediction === 'Likely to Churn'
  const probability = result ? Math.round(result.churn_probability * 100) : 0

  return (
    <div>
      <div className="text-center mb-10 mt-4">
        <h2 className="text-3xl font-bold tracking-tight">Will this customer stay?</h2>
        <p className="text-slate-400 text-sm mt-2">Enter their profile and we'll assess the churn risk instantly.</p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <form onSubmit={handleSubmit} className="glass-panel p-7 space-y-5">
          <Field label="Age" name="age" value={form.age} onChange={handleChange} error={errors.age} type="number" />

          <div>
            <label className="eyebrow block mb-2">Subscription Type</label>
            <div className="grid grid-cols-3 gap-2">
              {subscriptionOptions.map((opt) => {
                const Icon = opt.icon
                const isSelected = form.subscription_type === opt.value
                const c = colorStyles[opt.color]
                return (
                  <button
                    type="button"
                    key={opt.value}
                    onClick={() => selectSubscription(opt.value)}
                    className={`p-3 rounded-xl text-left transition-all duration-150 border
                      ${isSelected
                        ? `${c.bg} border-transparent ring-2 ${c.ring}`
                        : 'bg-slate-800/30 border-white/5 hover:bg-slate-800/50'
                      }`}
                  >
                    <div className={`icon-chip ${c.bg} ${c.text} mb-2`} style={{ width: '2rem', height: '2rem' }}>
                      <Icon size={14} />
                    </div>
                    <p className={`text-xs font-semibold ${isSelected ? c.text : 'text-slate-300'}`}>{opt.label}</p>
                    <p className="text-[10px] text-slate-500 mt-0.5 leading-tight">{opt.subtitle}</p>
                  </button>
                )
              })}
            </div>
          </div>

          <Field label="Monthly Charges ($)" name="monthly_charges" value={form.monthly_charges} onChange={handleChange} error={errors.monthly_charges} type="number" step="0.01" />
          <Field label="Tenure (months)" name="tenure_months" value={form.tenure_months} onChange={handleChange} error={errors.tenure_months} type="number" />
          <Field label="Satisfaction Score (1-10)" name="satisfaction_score" value={form.satisfaction_score} onChange={handleChange} error={errors.satisfaction_score} type="number" />
          <Field label="Support Tickets (last month)" name="support_tickets" value={form.support_tickets} onChange={handleChange} error={errors.support_tickets} type="number" />
          <Field label="Usage Hours per Week" name="usage_hours_per_week" value={form.usage_hours_per_week} onChange={handleChange} error={errors.usage_hours_per_week} type="number" step="0.1" />

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full rounded-lg py-3 font-semibold text-sm disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <Sparkles size={16} />
            {loading ? 'Predicting...' : 'Predict Churn'}
          </button>

          {apiError && <p className="text-rose-400 text-sm">{apiError}</p>}
        </form>

        <div className="glass-panel p-7 flex flex-col items-center justify-center min-h-[560px]">
          {!result && !loading && (
            <div className="text-center">
              <div className="icon-chip bg-indigo-500/15 text-indigo-400 mx-auto mb-4" style={{ width: '3rem', height: '3rem' }}>
                <ShieldCheck size={22} />
              </div>
              <p className="text-slate-500 text-sm">Fill out the form and click Predict to see results</p>
            </div>
          )}

          {loading && <p className="text-slate-400 text-sm">Running prediction...</p>}

          {result && (
            <div className="result-enter flex flex-col items-center">
              <p className="eyebrow mb-4">Churn Probability</p>
              <Gauge probability={probability} isChurn={isChurn} />

              <div className={`mt-6 px-4 py-2 rounded-full text-xs font-bold tracking-wider
                ${isChurn ? 'bg-rose-500/15 text-rose-400 pulse-critical' : 'bg-emerald-500/15 text-emerald-400 glow-indigo'}`}
              >
                {isChurn ? 'LIKELY TO CHURN' : 'LIKELY TO STAY'}
              </div>

              <div className="mt-8 w-full">
                <p className="eyebrow mb-3">Retention Playbook</p>
                <ul className="space-y-2.5">
                  {getRecommendations().map((rec, i) => (
                    <li key={i} className="text-sm text-slate-300 flex gap-2.5 items-start">
                      <span className="h-1.5 w-1.5 rounded-full bg-indigo-400 mt-1.5 shrink-0" />
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function Field({ label, name, value, onChange, error, type = 'text', step }) {
  return (
    <div>
      <label className="eyebrow block mb-2">{label}</label>
      <input
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        step={step}
        className={`input-field w-full rounded-lg px-3 py-2.5 text-sm
          ${error ? 'border-rose-500/60' : ''}`}
      />
      {error && <p className="text-rose-400 text-xs mt-1">{error}</p>}
    </div>
  )
}

function Gauge({ probability, isChurn }) {
  const radius = 72
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (probability / 100) * circumference
  const color = isChurn ? '#F43F5E' : '#6366F1'

  return (
    <svg width="190" height="190" viewBox="0 0 190 190">
      <circle cx="95" cy="95" r={radius} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="12" />
      <circle
        cx="95" cy="95" r={radius} fill="none"
        stroke={color} strokeWidth="12" strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        transform="rotate(-90 95 95)"
        style={{ filter: `drop-shadow(0 0 8px ${color}88)` }}
      />
      <text x="95" y="102" textAnchor="middle" fontSize="30" fontWeight="bold" fill="white" fontFamily="'JetBrains Mono', monospace">
        {probability}%
      </text>
    </svg>
  )
}
