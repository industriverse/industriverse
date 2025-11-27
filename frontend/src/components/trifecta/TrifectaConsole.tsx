import { useState, useRef, useEffect } from 'react';
import { Mic, Send, Activity, Terminal, User, Cpu, Zap, Server } from 'lucide-react';
import { toast } from 'sonner';

interface LogEntry {
    step: string;
    output: string;
}

export const TrifectaConsole = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [goal, setGoal] = useState("");
    const [persona, setPersona] = useState("Operator");
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [isProcessing, setIsProcessing] = useState(false);
    const [finalScore, setFinalScore] = useState<number | null>(null);

    const personas = ["Operator", "Physicist", "Logistics Manager", "Auditor", "VC"];

    const runLoop = async () => {
        if (!goal) return;

        setIsProcessing(true);
        setLogs([]);
        setFinalScore(null);

        try {
            const res = await fetch('/api/v1/idf/trifecta/loop', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ goal, persona })
            });

            if (!res.ok) throw new Error("Loop failed");

            const data = await res.json();

            // Simulate streaming logs for effect
            for (const log of data.log) {
                setLogs(prev => [...prev, log]);
                await new Promise(r => setTimeout(r, 500)); // Delay for visual pacing
            }

            if (data.status === 'completed') {
                setFinalScore(data.final_score);
                toast.success("Trifecta Loop Completed", { description: `Score: ${data.final_score.toFixed(2)}` });
            } else {
                toast.error("Trifecta Loop Rejected/Failed");
            }

        } catch (err) {
            console.error(err);
            toast.error("Execution Failed");
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <>
            {/* Toggle Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="fixed bottom-8 left-8 w-12 h-12 rounded-full bg-dyson-void/80 border border-dyson-teal/30 flex items-center justify-center hover:bg-dyson-teal/10 transition-all z-50"
                title="Open Trifecta Console"
            >
                <Terminal className="w-5 h-5 text-dyson-teal" />
            </button>

            {/* Console Overlay */}
            {isOpen && (
                <div className="fixed inset-x-0 bottom-0 h-[50vh] bg-black/90 backdrop-blur-xl border-t border-dyson-teal/30 z-40 flex flex-col shadow-2xl animate-in slide-in-from-bottom duration-300">
                    {/* Header */}
                    <div className="flex items-center justify-between p-4 border-b border-white/10">
                        <div className="flex items-center gap-2">
                            <Activity className="w-5 h-5 text-dyson-teal animate-pulse" />
                            <span className="font-mono text-dyson-teal tracking-widest uppercase">Trifecta Orchestration</span>
                        </div>
                        <button onClick={() => setIsOpen(false)} className="text-white/50 hover:text-white">Close</button>
                    </div>

                    {/* Content */}
                    <div className="flex-1 flex overflow-hidden">
                        {/* Controls */}
                        <div className="w-1/3 p-6 border-r border-white/10 flex flex-col gap-6">
                            <div>
                                <label className="block text-xs font-mono text-dyson-glass mb-2 uppercase">Persona</label>
                                <select
                                    value={persona}
                                    onChange={(e) => setPersona(e.target.value)}
                                    className="w-full bg-white/5 border border-white/10 rounded p-2 text-white font-mono focus:border-dyson-teal outline-none"
                                >
                                    {personas.map(p => <option key={p} value={p}>{p}</option>)}
                                </select>
                            </div>

                            <div>
                                <label className="block text-xs font-mono text-dyson-glass mb-2 uppercase">Operational Goal</label>
                                <textarea
                                    value={goal}
                                    onChange={(e) => setGoal(e.target.value)}
                                    placeholder="e.g., Optimize Fusion Stability..."
                                    className="w-full h-32 bg-white/5 border border-white/10 rounded p-2 text-white font-mono focus:border-dyson-teal outline-none resize-none"
                                />
                            </div>

                            <button
                                onClick={runLoop}
                                disabled={isProcessing || !goal}
                                className={`w-full py-3 rounded font-mono uppercase tracking-widest transition-all flex items-center justify-center gap-2
                                    ${isProcessing
                                        ? 'bg-dyson-teal/20 text-dyson-teal cursor-wait'
                                        : 'bg-dyson-teal hover:bg-dyson-teal/80 text-black'}`}
                            >
                                {isProcessing ? <Activity className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                                {isProcessing ? 'Orchestrating...' : 'Execute Loop'}
                            </button>
                        </div>

                        {/* Logs */}
                        <div className="flex-1 p-6 overflow-y-auto bg-black/50 font-mono text-sm">
                            {logs.length === 0 && !isProcessing && (
                                <div className="h-full flex items-center justify-center text-white/20">
                                    System Ready. Awaiting Intent.
                                </div>
                            )}

                            <div className="space-y-4">
                                {logs.map((log, i) => (
                                    <div key={i} className="animate-in fade-in slide-in-from-left duration-300">
                                        <div className="flex items-center gap-2 mb-1">
                                            {log.step === 'ACE' && <Cpu className="w-3 h-3 text-purple-400" />}
                                            {log.step === 'UserLM' && <User className="w-3 h-3 text-blue-400" />}
                                            {log.step.includes('RND1') && <Activity className="w-3 h-3 text-yellow-400" />}
                                            {log.step === 'BitNet' && <Server className="w-3 h-3 text-green-400" />}
                                            <span className="text-xs uppercase opacity-50">[{log.step}]</span>
                                        </div>
                                        <div className="pl-5 text-white/90 border-l border-white/10">
                                            {log.output}
                                        </div>
                                    </div>
                                ))}
                                {finalScore !== null && (
                                    <div className="mt-8 p-4 border border-dyson-teal/50 bg-dyson-teal/10 rounded text-center animate-in zoom-in">
                                        <div className="text-xs uppercase text-dyson-teal mb-1">Optimization Score</div>
                                        <div className="text-3xl font-bold text-white">{finalScore.toFixed(4)}</div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};
