import type { WorkflowStep } from "../../hooks/useWorkflow";
import { CheckCircle2, Circle, Loader2, XCircle } from "lucide-react";
import { cn } from "../../lib/utils";

interface WorkflowStatusProps {
    steps: WorkflowStep[];
    activeStepId: string | null;
}

export function WorkflowStatus({ steps, activeStepId }: WorkflowStatusProps) {
    return (
        <div className="space-y-6">
            {steps.map((step, index) => {
                const isActive = activeStepId === step.id;
                return (
                    <div key={step.id} className="relative pl-8">
                        {/* Connector Line */}
                        {index !== steps.length - 1 && (
                            <div className="absolute left-3 top-8 bottom-0 w-px bg-slate-800" />
                        )}

                        {/* Icon */}
                        <div className={cn(
                            "absolute left-0 top-1 p-1 rounded-full border border-slate-800 bg-slate-900",
                            {
                                'text-slate-500': step.status === 'pending',
                                'text-indigo-500': step.status === 'running',
                                'text-green-500': step.status === 'completed',
                                'text-red-500': step.status === 'failed',
                            }
                        )}>
                            {step.status === 'pending' && <Circle className="w-4 h-4" />}
                            {step.status === 'running' && <Loader2 className="w-4 h-4 animate-spin" />}
                            {step.status === 'completed' && <CheckCircle2 className="w-4 h-4" />}
                            {step.status === 'failed' && <XCircle className="w-4 h-4" />}
                        </div>

                        {/* Content */}
                        <div className={cn("space-y-1 transition-opacity", {
                            'opacity-50': step.status === 'pending' && !isActive
                        })}>
                            <h3 className="text-sm font-medium text-slate-200">{step.name}</h3>
                            <p className={cn("text-xs", {
                                'text-slate-500': step.status === 'pending',
                                'text-indigo-400': step.status === 'running',
                                'text-green-400': step.status === 'completed',
                            })}>
                                {step.status.charAt(0).toUpperCase() + step.status.slice(1)}
                            </p>
                            {step.logs.length > 0 && isActive && (
                                <div className="mt-2 text-xs font-mono text-slate-400 bg-slate-950/50 p-2 rounded">
                                    <p>{step.logs[step.logs.length - 1]}</p>
                                </div>
                            )}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
