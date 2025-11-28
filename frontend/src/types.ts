export interface Capsule {
    capsule_id: string;
    name: string;
    category?: string;
    status: 'active' | 'idle' | 'optimizing' | 'standby' | 'error';
    entropy: number;
    prin_score: number;
    utid: string;
    version: string;
    description?: string;
    area_code?: number;
}

export interface PulseMetrics {
    globalEntropy: number;
    activeCapsules: number;
    credits: number;
    creditFlow: number;
}
