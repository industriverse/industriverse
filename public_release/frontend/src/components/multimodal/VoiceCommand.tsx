import { useState, useRef } from 'react';
import { Mic, MicOff, Activity } from 'lucide-react';
import { toast } from 'sonner';

export const VoiceCommand = () => {
    const [isListening, setIsListening] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const mediaRecorder = useRef<MediaRecorder | null>(null);
    const chunks = useRef<Blob[]>([]);

    const startListening = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder.current = new MediaRecorder(stream);
            chunks.current = [];

            mediaRecorder.current.ondataavailable = (e) => {
                chunks.current.push(e.data);
            };

            mediaRecorder.current.onstop = async () => {
                const blob = new Blob(chunks.current, { type: 'audio/wav' });
                await processAudio(blob);
            };

            mediaRecorder.current.start();
            setIsListening(true);
            toast.info("Listening...", { description: "Speak your command (e.g., 'Optimize Fusion')" });
        } catch (err) {
            console.error("Mic Error:", err);
            toast.error("Microphone Access Denied");
        }
    };

    const stopListening = () => {
        if (mediaRecorder.current && isListening) {
            mediaRecorder.current.stop();
            setIsListening(false);
            setIsProcessing(true);
        }
    };

    const processAudio = async (blob: Blob) => {
        const formData = new FormData();
        formData.append('file', blob, 'command.wav');

        try {
            const res = await fetch('/api/v1/idf/interact/voice', {
                method: 'POST',
                body: formData
            });

            if (!res.ok) throw new Error("Voice processing failed");

            const data = await res.json();
            const intent = data.intent;

            toast.success("Command Recognized", {
                description: `"${data.transcript}" -> ${intent.action.toUpperCase()} ${intent.params.domain || ''}`
            });

            if (intent.action === 'optimize' && intent.params.domain) {
                // Trigger optimization via event or callback
                // For now, we just notify. In real app, we'd call the hook or dispatch event.
                window.dispatchEvent(new CustomEvent('value-strike', { detail: intent.params.domain }));
            }

        } catch (err) {
            console.error(err);
            toast.error("Voice Command Failed");
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <button
            onMouseDown={startListening}
            onMouseUp={stopListening}
            onTouchStart={startListening}
            onTouchEnd={stopListening}
            className={`
                fixed bottom-8 right-8 w-16 h-16 rounded-full 
                flex items-center justify-center 
                backdrop-blur-md border border-dyson-glass/30
                transition-all duration-300 z-50
                ${isListening
                    ? 'bg-dyson-plasma/20 border-dyson-plasma scale-110 animate-pulse'
                    : 'bg-dyson-void/80 hover:bg-dyson-glass/10'}
            `}
        >
            {isProcessing ? (
                <Activity className="w-6 h-6 text-dyson-gold animate-spin" />
            ) : isListening ? (
                <Mic className="w-6 h-6 text-dyson-plasma" />
            ) : (
                <MicOff className="w-6 h-6 text-dyson-glass/50" />
            )}
        </button>
    );
};
