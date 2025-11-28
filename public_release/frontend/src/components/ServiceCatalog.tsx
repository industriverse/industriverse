import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, Package, Server, Shield, Zap, Loader2 } from 'lucide-react';

interface ServicePackage {
    id: string;
    name: string;
    description: string;
    category: string;
    version: string;
    required_resources: Record<string, string>;
    capabilities: string[];
    monthly_cost_est: number;
}

interface ServiceCatalogProps {
    onSelect: (pkg: ServicePackage) => void;
}

export default function ServiceCatalog({ onSelect }: ServiceCatalogProps) {
    const [packages, setPackages] = useState<ServicePackage[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchPackages = async () => {
            try {
                const res = await axios.get('/api/v1/orchestrator/packages');
                setPackages(res.data);
            } catch (e) {
                console.error("Failed to fetch catalog", e);
                setError("Failed to load service catalog.");
            } finally {
                setLoading(false);
            }
        };
        fetchPackages();
    }, []);

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-dyson-plasma" />
            </div>
        );
    }

    if (error) {
        return <div className="text-red-500 text-center p-8">{error}</div>;
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {packages.map((pkg) => (
                <Card
                    key={pkg.id}
                    className="p-6 bg-black/40 border-white/10 hover:border-dyson-plasma/50 transition-all duration-300 group cursor-pointer backdrop-blur-sm"
                    onClick={() => onSelect(pkg)}
                >
                    <div className="flex justify-between items-start mb-4">
                        <div className="p-3 rounded-lg bg-white/5 group-hover:bg-dyson-plasma/20 transition-colors">
                            <Package className="w-6 h-6 text-dyson-plasma" />
                        </div>
                        <Badge variant="outline" className="border-white/20 text-xs font-mono">
                            {pkg.version}
                        </Badge>
                    </div>

                    <h3 className="text-lg font-bold text-white mb-2 group-hover:text-dyson-plasma transition-colors">
                        {pkg.name}
                    </h3>
                    <p className="text-sm text-gray-400 mb-4 h-12 line-clamp-2">
                        {pkg.description}
                    </p>

                    <div className="space-y-3 mb-6">
                        <div className="flex items-center gap-2 text-xs text-gray-500">
                            <Server className="w-3 h-3" />
                            <span>{pkg.required_resources.cpu} vCPU / {pkg.required_resources.memory} RAM</span>
                        </div>
                        <div className="flex flex-wrap gap-1">
                            {pkg.capabilities.slice(0, 3).map(cap => (
                                <span key={cap} className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-gray-300 border border-white/5">
                                    {cap}
                                </span>
                            ))}
                            {pkg.capabilities.length > 3 && (
                                <span className="text-[10px] px-1.5 py-0.5 text-gray-500">+{pkg.capabilities.length - 3}</span>
                            )}
                        </div>
                    </div>

                    <div className="flex items-center justify-between pt-4 border-t border-white/5">
                        <div className="text-sm font-mono text-dyson-gold">
                            ${pkg.monthly_cost_est}<span className="text-gray-600 text-xs">/mo</span>
                        </div>
                        <Button size="sm" variant="ghost" className="text-dyson-plasma hover:text-white hover:bg-dyson-plasma/20">
                            Select
                        </Button>
                    </div>
                </Card>
            ))}
        </div>
    );
}
