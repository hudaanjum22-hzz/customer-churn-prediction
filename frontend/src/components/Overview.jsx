import { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { Users, TrendingDown, Smile, Grid3x3, BarChart3, Flame, LineChart } from 'lucide-react'

const COLORS = ['#6366F1', '#06B6D4', '#F59E0B']

export default function Overview() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('http://localhost:8000/api/analytics')
      .then((res) => res.json())
      .then(setData)
      .catch((err) => setError(err.message))
  }, [])

  if (error) return <div className="text-rose-400">Failed to load analytics: {error}</div>
  if (!data) return <div className="text-slate-400">Loading analytics...</div>

  const pieData = [
    { name: 'Churned', value: data.churn_distribution.churned },
    { name: 'Retained', value: data.churn_distribution.retained },
  ]

  const barData = Object.entries(data.churn_by_subscription).map(([type, rate]) => ({
    type,
    rate,
  }))

  const histData = data.monthly_charges_histogram.counts.map((count, i) => ({
    bin: `$${Math.round(data.monthly_charges_histogram.bin_edges[i])}`,
    count,
  }))

  const corrCols = Object.keys(data.correlation_matrix)

  return (
    <div>
      <div className="text-center mb-10 mt-2">
        <h2 className="text-3xl font-bold tracking-tight">Your customer base, at a glance</h2>
        <p className="text-slate-400 text-sm mt-2">Live metrics pulled straight from your churn model and dataset.</p>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-8">
        <KPIWidget label="Total Customers" value={data.kpis.total_customers.toLocaleString()} color="indigo" icon={Users} />
        <KPIWidget label="Average Churn Rate" value={`${data.kpis.churn_rate}%`} color="rose" icon={TrendingDown} />
        <KPIWidget label="Avg Customer Satisfaction" value={`${data.kpis.avg_satisfaction}/10`} color="cyan" icon={Smile} />
      </div>

      <div className="grid grid-cols-2 gap-6">
        <ChartCard title="Churn Distribution" icon={Grid3x3} color="indigo">
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={60} outerRadius={90} paddingAngle={2}>
                {pieData.map((_, i) => <Cell key={i} fill={COLORS[i]} stroke="none" />)}
              </Pie>
              <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 10 }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex gap-4 justify-center mt-2">
            <Legend color={COLORS[0]} label="Churned" />
            <Legend color={COLORS[1]} label="Retained" />
          </div>
        </ChartCard>

        <ChartCard title="Churn Rate by Subscription Type" icon={BarChart3} color="cyan">
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
              <XAxis dataKey="type" stroke="#64748B" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke="#64748B" fontSize={12} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 10 }} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
              <Bar dataKey="rate" fill="#06B6D4" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Correlation Heatmap" icon={Flame} color="amber">
          <div className="grid gap-1.5" style={{ gridTemplateColumns: `repeat(${corrCols.length}, minmax(0, 1fr))` }}>
            {corrCols.map((rowKey) =>
              corrCols.map((colKey) => {
                const val = data.correlation_matrix[rowKey][colKey]
                const intensity = Math.abs(val)
                const bg = val >= 0
                  ? `rgba(99, 102, 241, ${intensity})`
                  : `rgba(245, 158, 11, ${intensity})`
                return (
                  <div
                    key={`${rowKey}-${colKey}`}
                    className="aspect-square flex items-center justify-center text-[9px] rounded-md font-mono-data"
                    style={{ background: bg }}
                    title={`${rowKey} vs ${colKey}: ${val}`}
                  >
                    {val}
                  </div>
                )
              })
            )}
          </div>
        </ChartCard>

        <ChartCard title="Monthly Charges Distribution" icon={LineChart} color="indigo">
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={histData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
              <XAxis dataKey="bin" stroke="#64748B" fontSize={10} tickLine={false} axisLine={false} />
              <YAxis stroke="#64748B" fontSize={12} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 10 }} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
              <Bar dataKey="count" fill="#6366F1" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  )
}

function ChartCard({ title, icon: Icon, color, children }) {
  const colorMap = {
    indigo: { bg: 'bg-indigo-500/15', text: 'text-indigo-400' },
    cyan: { bg: 'bg-cyan-500/15', text: 'text-cyan-400' },
    amber: { bg: 'bg-amber-500/15', text: 'text-amber-400' },
  }
  const c = colorMap[color]
  return (
    <div className="glass-panel p-6">
      <div className="flex items-center gap-2.5 mb-5">
        <div className={`icon-chip ${c.bg} ${c.text}`} style={{ width: '1.9rem', height: '1.9rem' }}>
          <Icon size={14} />
        </div>
        <h3 className="text-sm font-semibold text-slate-200">{title}</h3>
      </div>
      {children}
    </div>
  )
}

function Legend({ color, label }) {
  return (
    <div className="flex items-center gap-1.5">
      <span className="h-2 w-2 rounded-full" style={{ background: color }} />
      <span className="text-xs text-slate-400">{label}</span>
    </div>
  )
}

function KPIWidget({ label, value, color, icon: Icon }) {
  const colorMap = {
    indigo: { text: 'text-indigo-400', bg: 'bg-indigo-500/15' },
    rose: { text: 'text-rose-400', bg: 'bg-rose-500/15' },
    cyan: { text: 'text-cyan-400', bg: 'bg-cyan-500/15' },
  }
  const c = colorMap[color]
  return (
    <div className="glass-panel p-6">
      <div className="flex items-center justify-between mb-4">
        <p className="eyebrow">{label}</p>
        {Icon && (
          <div className={`icon-chip ${c.bg} ${c.text}`}>
            <Icon size={16} />
          </div>
        )}
      </div>
      <p className={`text-3xl font-mono-data font-bold ${c.text}`}>{value}</p>
    </div>
  )
}
