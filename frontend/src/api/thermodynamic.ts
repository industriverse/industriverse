import { useQuery, useMutation } from "@tanstack/react-query";

const API_BASE_URL = "/api/v1/thermodynamic";

export interface HardwareNode {
    node_id: string;
    node_type: string;
    electrical: {
        capacitance_gate: number;
        capacitance_wire: number;
        voltage_min: number;
        voltage_max: number;
        leakage_current_base: number;
        thermal_resistance: number;
        total_capacitance: number;
    };
    location: Record<string, number>;
    metadata: Record<string, string>;
}

export interface EnergyMap {
    timestamp: string;
    node_count: number;
    nodes: Record<string, HardwareNode>;
}

export interface TelemetryVector {
    timestamp?: string;
    node_id: string;
    voltage: number;
    current: number;
    temperature_c: number;
    utilization: number;
    error_rate: number;
}

export interface PredictionResult {
    timestamp: string;
    predicted_vector: TelemetryVector;
    confidence_interval: number[];
    failure_probability: number;
}

export interface OptimizationRequest {
    map_name: string;
    steps: number;
    initial_state?: number[];
}

export interface OptimizationResponse {
    final_energy: number;
    energy_delta: number;
    entropy: number;
    converged: boolean;
    final_state_sample: number[];
}

// Fetch Energy Map
export const fetchEnergyMap = async (): Promise<EnergyMap> => {
    try {
        const response = await fetch(`${API_BASE_URL}/energy-map`);
        if (!response.ok) throw new Error("Failed to fetch energy map");
        return await response.json();
    } catch (error) {
        console.warn("API fetch failed, using mock data:", error);
        return {
            timestamp: new Date().toISOString(),
            node_count: 2,
            nodes: {
                "mock_gpu_01": {
                    node_id: "mock_gpu_01",
                    node_type: "gpu",
                    electrical: {
                        capacitance_gate: 1.5e-9,
                        capacitance_wire: 2.0e-9,
                        voltage_min: 0.7,
                        voltage_max: 1.2,
                        leakage_current_base: 0.05,
                        thermal_resistance: 0.15,
                        total_capacitance: 4.0e-9
                    },
                    location: { x: 0, y: 0, z: 0 },
                    metadata: { vendor: "NVIDIA", model: "H100" }
                },
                "mock_tpu_01": {
                    node_id: "mock_tpu_01",
                    node_type: "tpu",
                    electrical: {
                        capacitance_gate: 1.2e-9,
                        capacitance_wire: 1.8e-9,
                        voltage_min: 0.6,
                        voltage_max: 1.1,
                        leakage_current_base: 0.04,
                        thermal_resistance: 0.18,
                        total_capacitance: 3.4e-9
                    },
                    location: { x: 10, y: 0, z: 0 },
                    metadata: { vendor: "Google", model: "TPUv5" }
                }
            }
        };
    }
};

// React Query Hooks
export const useEnergyMap = () => {
    return useQuery({
        queryKey: ["energyMap"],
        queryFn: fetchEnergyMap,
        refetchInterval: 5000, // Poll every 5 seconds
    });
};

export const usePredictVector = () => {
    return useMutation({
        mutationFn: async (vector: TelemetryVector) => {
            const response = await fetch(`${API_BASE_URL}/predict-vector`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(vector),
            });
            if (!response.ok) throw new Error("Prediction failed");
            return (await response.json()) as PredictionResult;
        },
    });
};

export const useOptimizeConfiguration = () => {
    return useMutation({
        mutationFn: async (req: OptimizationRequest) => {
            const response = await fetch(`/api/v1/idf/diffuse/optimize`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(req),
            });
            if (!response.ok) throw new Error("Optimization failed");
            return (await response.json()) as OptimizationResponse;
        },
    });
};
