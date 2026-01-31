import { Badge } from './components/ui/Badge';
import { Sidebar } from './components/Layout/Sidebar';
import { MainContent } from './components/Layout/MainContent';
import { useWorkflow } from './hooks/useWorkflow';

function App() {
  const { steps, isRunning, startWorkflow, activeStepId } = useWorkflow();

  const activeStep = steps.find(s => s.id === activeStepId) ||
    steps.find(s => s.status === 'running') ||
    (steps.every(s => s.status === 'completed') ? steps[steps.length - 1] : undefined);


  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500/30">

      {/* Background Gradients */}
      <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-500/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-500/10 rounded-full blur-[120px]" />
      </div>

      <div className="relative z-10 flex flex-col h-screen max-w-[1600px] mx-auto p-6 gap-6">

        {/* Header */}
        <header className="flex items-center justify-between shrink-0">
          <div>
            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400">
              fastKOL Dashboard
            </h1>
            <p className="text-slate-400 text-sm mt-1">Web3 自动化内容生成与分发系统</p>
          </div>
          <Badge variant="success" className="px-3 py-1">
            Connected
          </Badge>
        </header>

        {/* Main Layout */}
        <div className="flex flex-1 gap-6 overflow-hidden">
          <Sidebar
            steps={steps}
            activeStepId={activeStepId}
            isRunning={isRunning}
            onStart={startWorkflow}
          />
          <MainContent activeStep={activeStep} />
        </div>

      </div>
    </div>
  )
}

export default App
