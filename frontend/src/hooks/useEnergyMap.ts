import { useQuery } from "@tanstack/react-query";
import axios from "axios";

interface EnergyMapData {
    node_count: number;
    total_energy: number;
    status: string;
}

export function useEnergyMap() {
    return useQuery({
        queryKey: ["energyMap"],
        queryFn: async (): Promise<EnergyMapData> => {
            // In a real scenario, fetch from /api/v1/thermodynamic/map
            // For now, return mock data or try to fetch if endpoint exists
            try {
                const response = await axios.get("/v1/shield/state");
                return {
                    node_count: response.data.metrics.node_count,
                    total_energy: response.data.metrics.total_power_watts,
                    status: response.data.status
                };
            } catch (e) {
                // Fallback mock
                return {
                    node_count: 27,
                    total_energy: 4500,
                    status: "stable"
                };
            }
        },
        refetchInterval: 5000
    });
}
