import { Rocket } from "lucide-react";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { WorkflowStatus } from "../Dashboard/WorkflowStatus";
import type { WorkflowStep } from "../../hooks/useWorkflow";

interface SidebarProps {
    steps: WorkflowStep[];
    activeStepId: string | null;
    isRunning: boolean;
    onStart: () => void;
}

export function Sidebar({ steps, activeStepId, isRunning, onStart }: SidebarProps) {
    return (
        <div className="w-80 flex flex-col gap-6 shrink-0">
            {/* Control Console */}
            <Card className="p-6 space-y-4">
                <h2 className="text-lg font-semibold text-slate-100">控制台</h2>
                <Button
                    className="w-full text-md py-6 font-bold tracking-wide"
                    variant="gradient"
                    onClick={onStart}
                    disabled={isRunning}
                >
                    {isRunning ? (
                        <span className="flex items-center gap-2">
                            <Rocket className="w-5 h-5 animate-pulse" />
                            运行中...
                        </span>
                    ) : (
                        <span className="flex items-center gap-2">
                            <Rocket className="w-5 h-5" />
                            启动工作流
                        </span>
                    )}
                </Button>
            </Card>

            {/* Workflow Status */}
            <Card className="flex-1 p-6">
                <h2 className="text-lg font-semibold text-slate-100 mb-6">工作流状态</h2>
                <WorkflowStatus steps={steps} activeStepId={activeStepId} />
            </Card>
        </div>
    );
}
