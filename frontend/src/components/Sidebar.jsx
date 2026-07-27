import { LayoutDashboard, UserSearch, Radar, History } from 'lucide-react'

export default function Sidebar({ activeView, setActiveView }) {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'predict', label: 'Predict Customer', icon: UserSearch },
    { id: 'history', label: 'History', icon: History },
  ]

  return (
    <aside className="w-full md:w-64 md:h-screen glass-panel rounded-none border-l-0 border-t-0 border-b-0 flex flex-row md:flex-col p-4 md:p-6 items-center md:items-stretch">
      <div className="flex items-center gap-3 md:mb-12 mr-4 md:mr-0">
        <div className="icon-chip bg-indigo-500/20 text-indigo-400 shrink-0">
          <Radar size={18} />
        </div>
        <div className="hidden md:block">
          <h1 className="text-base font-bold tracking-tight leading-none">Churn Predictor</h1>
          <p className="eyebrow mt-1.5">Obsidian Predictive</p>
        </div>
      </div>

      <nav className="flex flex-row md:flex-col gap-1 overflow-x-auto md:overflow-visible flex-1">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = activeView === item.id
          return (
            <button
              key={item.id}
              onClick={() => setActiveView(item.id)}
              className={`relative flex items-center gap-2 md:gap-3 px-3 md:px-4 py-2 md:py-3 rounded-xl text-sm font-medium transition-all duration-200 whitespace-nowrap shrink-0
                ${isActive
                  ? 'bg-indigo-500/10 text-indigo-300'
                  : 'text-slate-400 hover:bg-white/5 hover:text-white'
                }`}
            >
              {isActive && (
                <span className="hidden md:block absolute left-0 top-1/2 -translate-y-1/2 h-5 w-[3px] rounded-full bg-indigo-400 glow-indigo" />
              )}
              <Icon size={17} />
              <span className="md:inline">{item.label}</span>
            </button>
          )
        })}
      </nav>

      <div className="hidden md:block mt-auto pt-6 border-t border-white/5">
        <p className="eyebrow">System</p>
        <div className="flex items-center gap-2 mt-2">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
          <p className="text-xs text-slate-400">Model online</p>
        </div>
      </div>
    </aside>
  )
}
