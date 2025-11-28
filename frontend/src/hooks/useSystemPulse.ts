import { useState, useEffect, useRef } from 'react';

interface SystemMetrics {
    total_power_watts: number;
    avg_temperature_c: number;
    system_entropy: number;
}

interface PulseData {
    type: 'system_heartbeat' | 'shield_state' | 'capsule_update' | 'capsule.credit_flow' | 'capsule.status' | 'capsule.proof';
    timestamp?: string;
    metrics?: SystemMetrics;
    [key: string]: any;
}

export function useSystemPulse() {
    const [metrics, setMetrics] = useState<SystemMetrics>({
        total_power_watts: 0,
        avg_temperature_c: 0,
        system_entropy: 0
    });
    const [isConnected, setIsConnected] = useState(false);
    const ws = useRef<WebSocket | null>(null);

    const [lastEvent, setLastEvent] = useState<PulseData | null>(null);

    useEffect(() => {
        // Determine WS URL based on current window location
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.hostname;
        const port = '8000'; // Default backend port, or use window.location.port if proxied
        // In production, this might need adjustment via env vars
        const wsUrl = `${protocol}//${host}:${port}/ws/pulse`;

        const connect = () => {
            ws.current = new WebSocket(wsUrl);

            ws.current.onopen = () => {
                console.log('Connected to System Pulse');
                setIsConnected(true);
            };

            ws.current.onmessage = (event) => {
                try {
                    const data: PulseData = JSON.parse(event.data);
                    setLastEvent(data);
                    if (data.type === 'system_heartbeat' && data.metrics) {
                        setMetrics(data.metrics);
                    }
                } catch (e) {
                    console.error('Failed to parse pulse data', e);
                }
            };

            ws.current.onclose = () => {
                console.log('Disconnected from System Pulse');
                setIsConnected(false);
                // Reconnect after 5 seconds
                setTimeout(connect, 5000);
            };

            ws.current.onerror = (err) => {
                console.error('System Pulse WebSocket error', err);
                ws.current?.close();
            };
        };

        connect();

        return () => {
            ws.current?.close();
        };
    }, []);

    return { metrics, isConnected, lastEvent };
}
