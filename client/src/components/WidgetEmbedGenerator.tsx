/**
 * Widget Embed Generator
 * Week 8: White-Label Platform - Phase 4
 * 
 * Generate copy-paste embed codes for all 7 widgets with configuration options.
 */

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { toast } from 'sonner';

interface WidgetConfig {
  name: string;
  tag: string;
  description: string;
  attributes: {
    name: string;
    type: 'text' | 'number' | 'boolean' | 'select';
    default: string | number | boolean;
    options?: string[];
    description: string;
  }[];
}

const WIDGET_CONFIGS: WidgetConfig[] = [
  {
    name: 'Wallet Orb',
    tag: 'iv-wallet-orb',
    description: 'Visual representation of wallet balance with AmI glow effects',
    attributes: [
      {
        name: 'ws-url',
        type: 'text',
        default: 'wss://api.industriverse.io/ws',
        description: 'WebSocket server URL',
      },
      {
        name: 'theme',
        type: 'select',
        default: 'cosmic-industrial',
        options: ['cosmic-industrial', 'industrial-chrome', 'light-portal'],
        description: 'Visual theme',
      },
      {
        name: 'show-balance',
        type: 'boolean',
        default: true,
        description: 'Show numeric balance',
      },
      {
        name: 'glow-intensity',
        type: 'number',
        default: 0.8,
        description: 'AmI glow effect intensity (0-1)',
      },
    ],
  },
  {
    name: 'Proof Ticker',
    tag: 'iv-proof-ticker',
    description: 'Real-time proof generation feed with scrolling animation',
    attributes: [
      {
        name: 'ws-url',
        type: 'text',
        default: 'wss://api.industriverse.io/ws',
        description: 'WebSocket server URL',
      },
      {
        name: 'max-items',
        type: 'number',
        default: 10,
        description: 'Maximum items to display',
      },
      {
        name: 'scroll-speed',
        type: 'number',
        default: 50,
        description: 'Scroll speed in pixels/second',
      },
      {
        name: 'show-timestamps',
        type: 'boolean',
        default: true,
        description: 'Show proof timestamps',
      },
    ],
  },
  {
    name: 'Capsule Card',
    tag: 'iv-capsule-card',
    description: 'Compact capsule display with status indicators',
    attributes: [
      {
        name: 'capsule-id',
        type: 'text',
        default: '',
        description: 'Capsule ID to display',
      },
      {
        name: 'compact',
        type: 'boolean',
        default: false,
        description: 'Use compact layout',
      },
      {
        name: 'show-actions',
        type: 'boolean',
        default: true,
        description: 'Show action buttons',
      },
    ],
  },
  {
    name: 'Energy Gauge',
    tag: 'iv-energy-gauge',
    description: 'Circular energy gauge with color-coded zones',
    attributes: [
      {
        name: 'ws-url',
        type: 'text',
        default: 'wss://api.industriverse.io/ws',
        description: 'WebSocket server URL',
      },
      {
        name: 'show-stats',
        type: 'boolean',
        default: true,
        description: 'Show energy statistics',
      },
      {
        name: 'size',
        type: 'select',
        default: 'medium',
        options: ['small', 'medium', 'large'],
        description: 'Gauge size',
      },
    ],
  },
  {
    name: 'UTID Badge',
    tag: 'iv-utid-badge',
    description: 'UTID display with QR code and blockchain verification',
    attributes: [
      {
        name: 'utid',
        type: 'text',
        default: '',
        description: 'Universal Traceability ID',
      },
      {
        name: 'show-qr',
        type: 'boolean',
        default: true,
        description: 'Show QR code',
      },
      {
        name: 'verify-blockchain',
        type: 'boolean',
        default: true,
        description: 'Verify on blockchain',
      },
    ],
  },
  {
    name: 'AmI Pulse',
    tag: 'iv-ami-pulse',
    description: 'Ambient intelligence activity indicator',
    attributes: [
      {
        name: 'ws-url',
        type: 'text',
        default: 'wss://api.industriverse.io/ws',
        description: 'WebSocket server URL',
      },
      {
        name: 'show-details',
        type: 'boolean',
        default: false,
        description: 'Show detailed AmI metrics',
      },
      {
        name: 'pulse-speed',
        type: 'number',
        default: 1,
        description: 'Animation speed multiplier',
      },
    ],
  },
  {
    name: 'Shadow Twin',
    tag: 'iv-shadow-twin',
    description: 'Digital twin synchronization status',
    attributes: [
      {
        name: 'twin-id',
        type: 'text',
        default: '',
        description: 'Digital twin ID',
      },
      {
        name: 'auto-sync',
        type: 'boolean',
        default: true,
        description: 'Enable automatic synchronization',
      },
      {
        name: 'sync-interval',
        type: 'number',
        default: 5000,
        description: 'Sync interval in milliseconds',
      },
    ],
  },
];

export default function WidgetEmbedGenerator() {
  const [selectedWidget, setSelectedWidget] = useState<WidgetConfig>(WIDGET_CONFIGS[0]);
  const [config, setConfig] = useState<Record<string, any>>(() => {
    const initial: Record<string, any> = {};
    WIDGET_CONFIGS[0].attributes.forEach(attr => {
      initial[attr.name] = attr.default;
    });
    return initial;
  });

  const handleWidgetChange = (widget: WidgetConfig) => {
    setSelectedWidget(widget);
    const newConfig: Record<string, any> = {};
    widget.attributes.forEach(attr => {
      newConfig[attr.name] = attr.default;
    });
    setConfig(newConfig);
  };

  const generateEmbedCode = (): string => {
    const attrs = Object.entries(config)
      .filter(([_, value]) => value !== '' && value !== false)
      .map(([key, value]) => {
        if (typeof value === 'boolean') {
          return key;
        }
        return `${key}="${value}"`;
      })
      .join(' ');

    return `<${selectedWidget.tag} ${attrs}></${selectedWidget.tag}>`;
  };

  const generateScriptTag = (): string => {
    return `<script src="https://cdn.industriverse.io/widgets/latest/iv-widgets.js"></script>`;
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const copyFullEmbed = () => {
    const fullCode = `${generateScriptTag()}\n${generateEmbedCode()}`;
    copyToClipboard(fullCode);
  };

  return (
    <div className="space-y-6">
      {/* Widget Selector */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Select Widget</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {WIDGET_CONFIGS.map((widget) => (
            <Button
              key={widget.tag}
              variant={selectedWidget.tag === widget.tag ? 'default' : 'outline'}
              onClick={() => handleWidgetChange(widget)}
              className="justify-start"
            >
              {widget.name}
            </Button>
          ))}
        </div>
      </Card>

      {/* Configuration */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-2">{selectedWidget.name}</h3>
        <p className="text-sm text-muted-foreground mb-6">{selectedWidget.description}</p>

        <div className="space-y-4">
          {selectedWidget.attributes.map((attr) => (
            <div key={attr.name}>
              <label className="text-sm font-medium block mb-2">
                {attr.name}
                <span className="text-muted-foreground ml-2">({attr.description})</span>
              </label>

              {attr.type === 'text' && (
                <input
                  type="text"
                  value={config[attr.name] || ''}
                  onChange={(e) => setConfig({ ...config, [attr.name]: e.target.value })}
                  className="w-full px-3 py-2 bg-background border border-border rounded"
                  placeholder={String(attr.default)}
                />
              )}

              {attr.type === 'number' && (
                <input
                  type="number"
                  value={config[attr.name] || 0}
                  onChange={(e) => setConfig({ ...config, [attr.name]: Number(e.target.value) })}
                  className="w-full px-3 py-2 bg-background border border-border rounded"
                  step="0.1"
                />
              )}

              {attr.type === 'boolean' && (
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={config[attr.name] || false}
                    onChange={(e) => setConfig({ ...config, [attr.name]: e.target.checked })}
                    className="w-4 h-4"
                  />
                  <span className="text-sm">Enable</span>
                </label>
              )}

              {attr.type === 'select' && attr.options && (
                <select
                  value={config[attr.name] || attr.default}
                  onChange={(e) => setConfig({ ...config, [attr.name]: e.target.value })}
                  className="w-full px-3 py-2 bg-background border border-border rounded"
                >
                  {attr.options.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* Generated Code */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Embed Code</h3>

        <div className="space-y-4">
          {/* Script Tag */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium">1. Add script to your HTML head:</label>
              <Button
                variant="outline"
                size="sm"
                onClick={() => copyToClipboard(generateScriptTag())}
              >
                Copy
              </Button>
            </div>
            <pre className="bg-muted p-4 rounded text-xs overflow-x-auto">
              <code>{generateScriptTag()}</code>
            </pre>
          </div>

          {/* Widget Tag */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium">2. Add widget to your page:</label>
              <Button
                variant="outline"
                size="sm"
                onClick={() => copyToClipboard(generateEmbedCode())}
              >
                Copy
              </Button>
            </div>
            <pre className="bg-muted p-4 rounded text-xs overflow-x-auto">
              <code>{generateEmbedCode()}</code>
            </pre>
          </div>

          {/* Copy All */}
          <Button onClick={copyFullEmbed} className="w-full">
            Copy Complete Embed Code
          </Button>
        </div>
      </Card>

      {/* Preview */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Live Preview</h3>
        <div className="bg-muted p-8 rounded flex items-center justify-center min-h-[200px]">
          <p className="text-muted-foreground">
            Widget preview will appear here in production build
          </p>
        </div>
      </Card>
    </div>
  );
}
