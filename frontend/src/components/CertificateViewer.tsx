import React from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';

interface ProofCertificate {
    id: string;
    timestamp: string;
    issuer: string;
    claims: Record<string, any>;
    signature: string;
}

interface CertificateViewerProps {
    isOpen: boolean;
    onClose: () => void;
    certificate: ProofCertificate;
}

export const CertificateViewer: React.FC<CertificateViewerProps> = ({ isOpen, onClose, certificate }) => {
    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="bg-slate-950 border-slate-800 text-slate-200 max-w-2xl">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2 text-xl font-mono text-cyan-400">
                        <span className="text-2xl">📜</span> ASAL Proof Certificate
                    </DialogTitle>
                </DialogHeader>

                <div className="space-y-6 py-4">
                    {/* Header Info */}
                    <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <label className="text-slate-500 block mb-1">Proof ID</label>
                            <code className="bg-slate-900 px-2 py-1 rounded text-cyan-200">{certificate.id}</code>
                        </div>
                        <div>
                            <label className="text-slate-500 block mb-1">Timestamp</label>
                            <div className="font-mono">{new Date(certificate.timestamp).toLocaleString()}</div>
                        </div>
                    </div>

                    {/* Claims */}
                    <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-800">
                        <h4 className="text-sm font-semibold text-slate-400 mb-3 uppercase tracking-wider">Verified Claims</h4>
                        <div className="space-y-2">
                            {Object.entries(certificate.claims).map(([key, value]) => (
                                <div key={key} className="flex justify-between items-center border-b border-slate-800 pb-2 last:border-0">
                                    <span className="text-slate-300">{key}</span>
                                    <span className="font-mono text-green-400">{String(value)}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Signature */}
                    <div>
                        <label className="text-slate-500 block mb-1">Cryptographic Signature</label>
                        <ScrollArea className="h-20 w-full rounded border border-slate-800 bg-slate-900 p-2">
                            <code className="text-xs text-slate-500 break-all">
                                {certificate.signature}
                            </code>
                        </ScrollArea>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
};
