import { Card } from "../ui/Card";
import type { WorkflowStep } from "../../hooks/useWorkflow";
import { Terminal } from "lucide-react";

interface MainContentProps {
    activeStep: WorkflowStep | undefined;
}

export function MainContent({ activeStep }: MainContentProps) {
    return (
        <div className="flex-1 h-full min-h-[500px]">
            <Card className="h-full p-8 flex flex-col bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                {!activeStep ? (
                    <div className="flex-1 flex flex-col items-center justify-center text-slate-500 gap-4">
                        <h3 className="text-xl font-medium">预览区域</h3>
                        <p>选中的任务详情将在此显示</p>
                    </div>
                ) : (
                    <div className="flex-1 flex flex-col gap-6 animate-in fade-in duration-500">
                        <div className="flex items-center gap-3 border-b border-slate-700 pb-4">
                            <div className="p-2 bg-indigo-500/10 rounded-lg">
                                <Terminal className="w-6 h-6 text-indigo-400" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-white">{activeStep.name}</h2>
                                <p className="text-slate-400">{activeStep.description}</p>
                            </div>
                        </div>

                        <div className="flex-1 bg-slate-950/50 rounded-lg p-6 font-mono text-sm overflow-y-auto custom-scrollbar border border-slate-800">
                            <div className="space-y-2">
                                {activeStep.logs.length === 0 ? (
                                    <span className="text-slate-500 italic">等待输出...</span>
                                ) : (
                                    activeStep.logs.map((log, i) => (
                                        <div key={i} className="flex gap-3 text-slate-300">
                                            <span className="text-slate-600 select-none">{`>`}</span>
                                            <span>{log}</span>
                                        </div>
                                    ))
                                )}
                                {activeStep.status === 'running' && (
                                    <div className="flex gap-3 text-indigo-400 animate-pulse">
                                        <span className="text-slate-600 select-none">{`>`}</span>
                                        <span>_</span>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="flex justify-end pt-2">
                            <span className="text-xs text-slate-600">ID: {activeStep.id}</span>
                        </div>
                    </div>
                )}
            </Card>
        </div>
    );
}
