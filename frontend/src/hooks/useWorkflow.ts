import { useState, useCallback, useRef, useEffect } from 'react';

export type StepStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface WorkflowStep {
    id: string;
    name: string;
    status: StepStatus;
    description: string;
    logs: string[];
}

export const INITIAL_STEPS: WorkflowStep[] = [
    {
        id: 'collect',
        name: '热点采集',
        status: 'pending',
        description: '监控 Polymarket 预测市场，识别 Web3 相关热门话题。',
        logs: []
    },
    {
        id: 'plan',
        name: '内容策划',
        status: 'pending',
        description: '分析市场数据，生成吸引人的视频脚本（包含标题、Hook、关键帧）。',
        logs: []
    },
    {
        id: 'distribute',
        name: '社交分发',
        status: 'pending',
        description: '生成的视频将上传至 YouTube 并同步分发至 Twitter/X。',
        logs: []
    },
];

export function useWorkflow() {
    const [steps, setSteps] = useState<WorkflowStep[]>(INITIAL_STEPS);
    const [isRunning, setIsRunning] = useState(false);
    const [activeStepId, setActiveStepId] = useState<string | null>(null);
    const ws = useRef<WebSocket | null>(null);

    const updateStepStatus = (id: string, status: StepStatus) => {
        setSteps(prev => prev.map(s => s.id === id ? { ...s, status } : s));
    };

    const addLog = (id: string, log: string) => {
        setSteps(prev => prev.map(s => s.id === id ? { ...s, logs: [...s.logs, log] } : s));
    };

    // Auto-switch active step based on logs/status
    const determineActiveStep = (log: string) => {
        const lowerLog = log.toLowerCase();
        if (lowerLog.includes('polymarket') || lowerLog.includes('market')) return 'collect';
        if (lowerLog.includes('script') || lowerLog.includes('generate') || lowerLog.includes('llm')) return 'plan';
        if (lowerLog.includes('upload') || lowerLog.includes('youtube') || lowerLog.includes('twitter')) return 'distribute';
        return null; // Keep current
    };

    const startWorkflow = useCallback(() => {
        if (isRunning) return;
        setIsRunning(true);
        setSteps(INITIAL_STEPS.map(s => ({ ...s, status: 'pending', logs: [] })));

        // Initialize WebSocket
        ws.current = new WebSocket('ws://localhost:8000/ws');

        ws.current.onopen = () => {
            console.log('Connected to backend');
            ws.current?.send('start');
            setActiveStepId('collect');
            updateStepStatus('collect', 'running');
        };

        ws.current.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                if (data.type === 'log') {
                    const msg = data.message;
                    const stepId = determineActiveStep(msg) || activeStepId || 'collect';

                    if (stepId !== activeStepId) {
                        // Complete previous step if moving forward
                        const currentIndex = INITIAL_STEPS.findIndex(s => s.id === activeStepId);
                        const nextIndex = INITIAL_STEPS.findIndex(s => s.id === stepId);
                        if (activeStepId && nextIndex > currentIndex) {
                            updateStepStatus(activeStepId, 'completed');
                        }

                        setActiveStepId(stepId);
                        updateStepStatus(stepId, 'running');
                    }

                    addLog(stepId, msg);
                } else if (data.type === 'result') {
                    updateStepStatus(activeStepId || 'distribute', 'completed');
                    setIsRunning(false);
                } else if (data.type === 'error') {
                    addLog(activeStepId || 'collect', `ERROR: ${data.message}`);
                    updateStepStatus(activeStepId || 'collect', 'failed');
                    setIsRunning(false);
                }
            } catch (e) {
                console.error('Failed to parse WebSocket message', e);
            }
        };

        ws.current.onerror = (e) => {
            console.error('WebSocket error', e);
            updateStepStatus(activeStepId || 'collect', 'failed');
            setIsRunning(false);
        };

        ws.current.onclose = () => {
            console.log('Disconnected');
            if (isRunning) setIsRunning(false);
        };

    }, [isRunning, activeStepId]);

    // Cleanup
    useEffect(() => {
        return () => {
            ws.current?.close();
        };
    }, []);

    return {
        steps,
        isRunning,
        startWorkflow,
        activeStepId
    };
}
