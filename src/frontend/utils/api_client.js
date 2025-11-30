// Simple API Client for Empeiria Haus Bridge
const API_URL = "http://localhost:8000";

export const getStatus = async () => {
    try {
        const response = await fetch(`${API_URL}/status`);
        return await response.json();
    } catch (error) {
        console.error("API Error:", error);
        return { status: "OFFLINE" };
    }
};

export const getMetrics = async () => {
    try {
        const response = await fetch(`${API_URL}/metrics`);
        return await response.json();
    } catch (error) {
        return { entropy: 1.0, safety: 1.0, mastery_stage: "DISCONNECTED" };
    }
};

export const getVaultItems = async () => {
    try {
        const response = await fetch(`${API_URL}/vault`);
        return await response.json();
    } catch (error) {
        return { items: [] };
    }
};
