import React, { useState } from 'react';
import axios from 'axios';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Loader2, CheckCircle, Rocket } from 'lucide-react';
import ServiceCatalog from '../components/ServiceCatalog';

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

export default function DeploymentWizard() {
  const [open, setOpen] = useState(false);
  const [selectedPkg, setSelectedPkg] = useState<ServicePackage | null>(null);
  const [deploying, setDeploying] = useState(false);
  const [result, setResult] = useState<any | null>(null);

  const handleDeploy = async () => {
    if (!selectedPkg) return;
    setDeploying(true);
    try {
      const res = await axios.post('/api/v1/orchestrator/deploy', {
        package_id: selectedPkg.id,
        tenant_id: "tenant-default", // In real app, get from auth context
        parameters: {}
      });
      setResult(res.data);
    } catch (e) {
      console.error("Deployment failed", e);
    } finally {
      setDeploying(false);
    }
  };

  const reset = () => {
    setSelectedPkg(null);
    setResult(null);
    setDeploying(false);
  };

  return (
    <Dialog open={open} onOpenChange={(val) => { setOpen(val); if (!val) reset(); }}>
      <DialogTrigger asChild>
        <Button className="bg-dyson-plasma hover:bg-dyson-plasma/80 text-black font-bold">
          <Rocket className="w-4 h-4 mr-2" />
          Deploy Service
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-4xl bg-gray-900 border-white/10 text-white max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-dyson-plasma to-dyson-gold">
            Service Orchestrator
          </DialogTitle>
        </DialogHeader>

        {!selectedPkg ? (
          <div className="mt-4">
            <p className="text-gray-400 mb-6">Select a Value Package to rehydrate from Cold Storage.</p>
            <ServiceCatalog onSelect={setSelectedPkg} />
          </div>
        ) : !result ? (
          <div className="mt-4 space-y-6">
            <div className="p-6 rounded-lg bg-white/5 border border-white/10">
              <h3 className="text-xl font-bold mb-2">{selectedPkg.name}</h3>
              <p className="text-gray-400 mb-4">{selectedPkg.description}</p>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500 block">Version</span>
                  <span className="font-mono">{selectedPkg.version}</span>
                </div>
                <div>
                  <span className="text-gray-500 block">Est. Cost</span>
                  <span className="font-mono text-dyson-gold">${selectedPkg.monthly_cost_est}/mo</span>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3">
              <Button variant="ghost" onClick={() => setSelectedPkg(null)}>Back</Button>
              <Button
                onClick={handleDeploy}
                disabled={deploying}
                className="bg-dyson-plasma text-black hover:bg-dyson-plasma/80"
              >
                {deploying ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Rehydrating...
                  </>
                ) : (
                  <>
                    <Rocket className="w-4 h-4 mr-2" />
                    Confirm Deployment
                  </>
                )}
              </Button>
            </div>
          </div>
        ) : (
          <div className="mt-4 text-center py-12">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-500/20 mb-6">
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-2">Deployment Initiated</h3>
            <p className="text-gray-400 mb-6 max-w-md mx-auto">
              {result.message}
            </p>
            <div className="bg-black/40 p-4 rounded border border-white/10 font-mono text-xs text-left max-w-md mx-auto mb-8">
              <div className="flex justify-between mb-1">
                <span className="text-gray-500">ID:</span>
                <span className="text-dyson-plasma">{result.deployment_id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">ETA:</span>
                <span className="text-white">{result.estimated_completion}</span>
              </div>
            </div>
            <Button onClick={() => setOpen(false)} variant="outline" className="border-white/20">
              Close & Monitor
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
