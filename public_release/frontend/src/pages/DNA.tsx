import { GlassPanel } from '@/components/ui/GlassPanel';
import { Button } from '@/components/ui/button';
import { Link } from 'wouter';
import { ArrowLeft, Database } from 'lucide-react';

export default function DNA() {
    return (
        <div className="min-h-screen bg-void-blue text-supernova-white p-8">
            <div className="container mx-auto">
                <div className="flex items-center gap-4 mb-8">
                    <Link href="/">
                        <Button variant="outline" size="icon">
                            <ArrowLeft className="h-4 w-4" />
                        </Button>
                    </Link>
                    <h1 className="text-3xl font-bold flex items-center gap-2">
                        <Database className="h-8 w-8 text-entropy-orange" />
                        Ontology DNA
                    </h1>
                </div>

                <GlassPanel className="h-[700px] flex items-center justify-center bg-black/40">
                    <p className="text-muted-foreground">Force-Directed Graph Placeholder (D3/Canvas)</p>
                </GlassPanel>
            </div>
        </div>
    );
}
