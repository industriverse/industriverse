/**
 * Global TypeScript declarations
 * Week 8: White-Label Platform
 */

declare namespace JSX {
  interface IntrinsicElements {
    'iv-wallet-orb': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement> & {
      balance?: string;
      currency?: string;
      'ws-url'?: string;
      'user-id'?: string;
      'auto-connect'?: string;
    };
    
    'iv-proof-ticker': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement> & {
      'ws-url'?: string;
      'max-items'?: string;
      'scroll-speed'?: 'slow' | 'normal' | 'fast';
      'auto-connect'?: string;
    };
    
    'iv-capsule-card': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement> & {
      'capsule-id'?: string;
      title?: string;
      status?: 'active' | 'warning' | 'critical' | 'resolved';
      priority?: string;
      source?: string;
      description?: string;
      'api-url'?: string;
    };
  }
}
