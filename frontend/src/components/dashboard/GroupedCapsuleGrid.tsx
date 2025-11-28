
import React from 'react';
import CapsuleCard from '../CapsuleCard';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Capsule } from '../../types/capsule';

interface GroupedCapsuleGridProps {
    capsules: Capsule[];
    onLaunch: (id: string) => void;
}

const CATEGORIES = {
    'Sourcing & Processing': [1, 2, 3, 4, 13, 23],
    'Manufacturing & Assembly': [5, 6, 7, 8, 9, 10, 12, 14, 20],
    'Systems & Control': [11, 15, 16, 17],
    'Quality & Compliance': [18, 19, 24, 26],
    'Logistics & Service': [21, 22, 25, 27]
};

export const GroupedCapsuleGrid: React.FC<GroupedCapsuleGridProps> = ({ capsules, onLaunch }) => {

    const getCategory = (areaCode?: number) => {
        if (!areaCode) return 'Uncategorized';
        for (const [cat, codes] of Object.entries(CATEGORIES)) {
            if (codes.includes(areaCode)) return cat;
        }
        return 'Other';
    };

    const groupedCapsules = capsules.reduce((acc, cap) => {
        const cat = getCategory(cap.area_code);
        if (!acc[cat]) acc[cat] = [];
        acc[cat].push(cap);
        return acc;
    }, {} as Record<string, Capsule[]>);

    return (
        <Accordion type="multiple" defaultValue={Object.keys(CATEGORIES)} className="w-full space-y-4">
            {Object.entries(groupedCapsules).map(([category, caps]) => (
                <AccordionItem key={category} value={category} className="border border-slate-800 rounded-lg bg-slate-900/50 px-4">
                    <AccordionTrigger className="text-lg font-semibold text-slate-200 hover:text-cyan-400">
                        {category} <span className="ml-2 text-xs text-slate-500">({caps.length})</span>
                    </AccordionTrigger>
                    <AccordionContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 pt-4 pb-2">
                            {caps.map((capsule) => (
                                <CapsuleCard
                                    key={capsule.capsule_id}
                                    capsule={capsule}
                                    onIgnite={() => { }} // Placeholder or pass from props
                                    onLaunch={() => onLaunch(capsule.capsule_id)}
                                />
                            ))}
                        </div>
                    </AccordionContent>
                </AccordionItem>
            ))}
        </Accordion>
    );
};
