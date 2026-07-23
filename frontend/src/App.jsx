import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Overview from './components/Overview'
import Predictor from './components/Predictor'
import History from './components/History'

export default function App() {
  const [activeView, setActiveView] = useState('overview')

  return (
    <div className="relative flex min-h-screen bg-slate-950">
      <div className="bg-mesh" />
      <div className="relative z-10 flex w-full">
        <Sidebar activeView={activeView} setActiveView={setActiveView} />
        <main className="flex-1 p-8 overflow-y-auto">
          {activeView === 'overview' && <Overview />}
          {activeView === 'predict' && <Predictor />}
          {activeView === 'history' && <History />}
        </main>
      </div>
    </div>
  )
}
