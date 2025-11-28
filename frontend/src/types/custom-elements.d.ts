import React from 'react';

declare global {
    namespace JSX {
        interface IntrinsicElements {
            'iv-capsule-card': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement> & {
                'capsule-id'?: string;
                'name'?: string;
                'status'?: string;
                'prin-score'?: string;
                'energy-usage'?: string;
                'description'?: string;
            };
            'iv-proof-ticker': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
            'iv-wallet-orb': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
        }
    }
}
