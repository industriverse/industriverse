/**
 * Deployment Wizard
 * Week 8: White-Label Platform - Phase 4 Final
 * 
 * Step-by-step onboarding flow for white-label deployments:
 * 1. Welcome & Tenant Info
 * 2. Theme Selection
 * 3. Widget Configuration
 * 4. Domain Setup
 * 5. Feature Flags
 * 6. Review & Deploy
 */

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ThemeSwitcher } from '@/components/ThemeSwitcher';
import { themePresets } from '@/themes/presets';
import { featureFlags, DEFAULT_FEATURE_FLAGS } from '@/services/FeatureFlags';
import type { Theme } from '@/types/theme';
import type { FeatureFlag } from '@/services/FeatureFlags';
import { toast } from 'sonner';

interface WizardStep {
  id: number;
  title: string;
  description: string;
}

interface DeploymentConfig {
  tenantName: string;
  tenantId: string;
  contactEmail: string;
  industry: string;
  theme: Theme;
  widgets: {
    walletOrb: boolean;
    proofTicker: boolean;
    capsuleCard: boolean;
    energyGauge: boolean;
    utidBadge: boolean;
    amiPulse: boolean;
    shadowTwin: boolean;
  };
  domain: string;
  sslEnabled: boolean;
  featureFlags: Record<string, boolean>;
}

const WIZARD_STEPS: WizardStep[] = [
  {
    id: 1,
    title: 'Welcome',
    description: 'Basic tenant information',
  },
  {
    id: 2,
    title: 'Theme',
    description: 'Select your visual theme',
  },
  {
    id: 3,
    title: 'Widgets',
    description: 'Configure embeddable widgets',
  },
  {
    id: 4,
    title: 'Domain',
    description: 'Set up custom domain',
  },
  {
    id: 5,
    title: 'Features',
    description: 'Customize feature flags',
  },
  {
    id: 6,
    title: 'Review',
    description: 'Review and deploy',
  },
];

export default function DeploymentWizard() {
  const [currentStep, setCurrentStep] = useState(1);
  const [config, setConfig] = useState<DeploymentConfig>({
    tenantName: '',
    tenantId: '',
    contactEmail: '',
    industry: 'semiconductor',
    theme: themePresets[0].theme,
    widgets: {
      walletOrb: true,
      proofTicker: true,
      capsuleCard: true,
      energyGauge: true,
      utidBadge: true,
      amiPulse: true,
      shadowTwin: true,
    },
    domain: '',
    sslEnabled: true,
    featureFlags: {},
  });

  const [isDraft, setIsDraft] = useState(false);

  // Initialize feature flags
  useState(() => {
    const flags: Record<string, boolean> = {};
    DEFAULT_FEATURE_FLAGS.forEach(flag => {
      flags[flag.key] = flag.enabled;
    });
    setConfig(prev => ({ ...prev, featureFlags: flags }));
  });

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, WIZARD_STEPS.length));
    }
  };

  const handlePrevious = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const handleSaveDraft = () => {
    try {
      localStorage.setItem('deployment_draft', JSON.stringify(config));
      setIsDraft(true);
      toast.success('Draft saved successfully');
    } catch (error) {
      toast.error('Failed to save draft');
    }
  };

  const handleLoadDraft = () => {
    try {
      const draft = localStorage.getItem('deployment_draft');
      if (draft) {
        setConfig(JSON.parse(draft));
        setIsDraft(true);
        toast.success('Draft loaded successfully');
      }
    } catch (error) {
      toast.error('Failed to load draft');
    }
  };

  const validateStep = (step: number): boolean => {
    switch (step) {
      case 1:
        if (!config.tenantName || !config.contactEmail) {
          toast.error('Please fill in all required fields');
          return false;
        }
        if (!config.contactEmail.includes('@')) {
          toast.error('Please enter a valid email address');
          return false;
        }
        return true;
      case 4:
        if (config.domain && !config.domain.includes('.')) {
          toast.error('Please enter a valid domain name');
          return false;
        }
        return true;
      default:
        return true;
    }
  };

  const handleDeploy = () => {
    // Simulate deployment
    toast.success('Deployment initiated! Your white-label instance will be ready in 5-10 minutes.');
    
    // Clear draft
    localStorage.removeItem('deployment_draft');
    
    // Redirect to admin portal after short delay
    setTimeout(() => {
      window.location.href = '/admin';
    }, 2000);
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Welcome to Industriverse White-Label</h2>
              <p className="text-muted-foreground">
                Let's set up your custom deployment. This wizard will guide you through theme selection,
                widget configuration, and deployment settings.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium block mb-2">
                  Tenant Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={config.tenantName}
                  onChange={(e) => setConfig({ ...config, tenantName: e.target.value })}
                  placeholder="e.g., TSMC Fab 18"
                  className="w-full px-3 py-2 bg-background border border-border rounded"
                />
              </div>

              <div>
                <label className="text-sm font-medium block mb-2">
                  Tenant ID <span className="text-muted-foreground">(auto-generated)</span>
                </label>
                <input
                  type="text"
                  value={config.tenantId || config.tenantName.toLowerCase().replace(/\s+/g, '-')}
                  onChange={(e) => setConfig({ ...config, tenantId: e.target.value })}
                  placeholder="tsmc-fab-18"
                  className="w-full px-3 py-2 bg-background border border-border rounded"
                />
              </div>

              <div>
                <label className="text-sm font-medium block mb-2">
                  Contact Email <span className="text-red-500">*</span>
                </label>
                <input
                  type="email"
                  value={config.contactEmail}
                  onChange={(e) => setConfig({ ...config, contactEmail: e.target.value })}
                  placeholder="admin@company.com"
                  className="w-full px-3 py-2 bg-background border border-border rounded"
                />
              </div>

              <div>
                <label className="text-sm font-medium block mb-2">Industry</label>
                <select
                  value={config.industry}
                  onChange={(e) => setConfig({ ...config, industry: e.target.value })}
                  className="w-full px-3 py-2 bg-background border border-border rounded"
                >
                  <option value="semiconductor">Semiconductor Manufacturing</option>
                  <option value="energy">Energy & Sustainability</option>
                  <option value="iot">Edge Computing & IoT</option>
                  <option value="supply-chain">Supply Chain & Logistics</option>
                  <option value="quality">Quality & Compliance</option>
                  <option value="financial">Financial Operations</option>
                </select>
              </div>
            </div>

            {isDraft && (
              <div className="bg-brand-primary/10 border border-brand-primary/30 rounded p-4">
                <p className="text-sm">
                  📝 You have a saved draft. Continue from where you left off.
                </p>
              </div>
            )}
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Choose Your Theme</h2>
              <p className="text-muted-foreground">
                Select a base theme that matches your brand. You can customize colors later in the admin portal.
              </p>
            </div>

            <ThemeSwitcher
              onThemeChange={(theme) => setConfig({ ...config, theme })}
            />

            <div className="mt-6">
              <h3 className="text-lg font-medium mb-4">Live Preview</h3>
              <Card className="p-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="text-lg font-semibold">Sample Component</h4>
                    <Button size="sm">Action</Button>
                  </div>
                  <p className="text-muted-foreground">
                    This is how your deployment will look with the selected theme.
                  </p>
                  <div className="grid grid-cols-3 gap-4">
                    <Card className="p-4 text-center">
                      <div className="text-2xl font-bold text-status-success">✓</div>
                      <div className="text-sm mt-2">Active</div>
                    </Card>
                    <Card className="p-4 text-center">
                      <div className="text-2xl font-bold text-status-warning">⚠</div>
                      <div className="text-sm mt-2">Warning</div>
                    </Card>
                    <Card className="p-4 text-center">
                      <div className="text-2xl font-bold text-status-error">✕</div>
                      <div className="text-sm mt-2">Critical</div>
                    </Card>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Configure Widgets</h2>
              <p className="text-muted-foreground">
                Select which embeddable widgets to enable for your deployment.
              </p>
            </div>

            <div className="space-y-3">
              {Object.entries(config.widgets).map(([key, enabled]) => (
                <Card key={key} className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium capitalize">
                        {key.replace(/([A-Z])/g, ' $1').trim()}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {getWidgetDescription(key)}
                      </p>
                    </div>
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={enabled}
                        onChange={(e) =>
                          setConfig({
                            ...config,
                            widgets: { ...config.widgets, [key]: e.target.checked },
                          })
                        }
                        className="w-4 h-4"
                      />
                      <span className="text-sm">{enabled ? 'Enabled' : 'Disabled'}</span>
                    </label>
                  </div>
                </Card>
              ))}
            </div>

            <div className="bg-brand-accent/10 border border-brand-accent/30 rounded p-4">
              <p className="text-sm">
                💡 You can configure individual widget settings in the admin portal after deployment.
              </p>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Domain Configuration</h2>
              <p className="text-muted-foreground">
                Set up a custom domain for your white-label deployment.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium block mb-2">Custom Domain</label>
                <input
                  type="text"
                  value={config.domain}
                  onChange={(e) => setConfig({ ...config, domain: e.target.value })}
                  placeholder="capsules.your-company.com"
                  className="w-full px-3 py-2 bg-background border border-border rounded"
                />
                <p className="text-xs text-muted-foreground mt-2">
                  Leave empty to use default subdomain: {config.tenantId || 'your-tenant'}.industriverse.io
                </p>
              </div>

              <div>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={config.sslEnabled}
                    onChange={(e) => setConfig({ ...config, sslEnabled: e.target.checked })}
                    className="w-4 h-4"
                  />
                  <span className="text-sm font-medium">Enable SSL/TLS (Recommended)</span>
                </label>
                <p className="text-xs text-muted-foreground mt-2 ml-6">
                  Automatic SSL certificate provisioning via Let's Encrypt
                </p>
              </div>
            </div>

            <Card className="p-4 bg-status-info/10 border-status-info/30">
              <h3 className="font-medium mb-2">DNS Configuration Required</h3>
              <p className="text-sm text-muted-foreground">
                After deployment, you'll need to add a CNAME record pointing to:
                <code className="block mt-2 p-2 bg-background rounded">
                  {config.tenantId || 'your-tenant'}.industriverse.io
                </code>
              </p>
            </Card>
          </div>
        );

      case 5:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Feature Flags</h2>
              <p className="text-muted-foreground">
                Customize which features are enabled for your deployment.
              </p>
            </div>

            <div className="space-y-4">
              {DEFAULT_FEATURE_FLAGS.filter(f => f.category === 'core' || f.category === 'widget').map(
                (flag) => (
                  <Card key={flag.key} className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-medium">{flag.name}</h3>
                        <p className="text-sm text-muted-foreground mt-1">{flag.description}</p>
                      </div>
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={config.featureFlags[flag.key] ?? flag.enabled}
                          onChange={(e) =>
                            setConfig({
                              ...config,
                              featureFlags: {
                                ...config.featureFlags,
                                [flag.key]: e.target.checked,
                              },
                            })
                          }
                          className="w-4 h-4"
                        />
                      </label>
                    </div>
                  </Card>
                )
              )}
            </div>

            <div className="bg-brand-accent/10 border border-brand-accent/30 rounded p-4">
              <p className="text-sm">
                💡 Advanced feature flags (AmI, integrations, experimental) can be configured in the admin portal.
              </p>
            </div>
          </div>
        );

      case 6:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Review & Deploy</h2>
              <p className="text-muted-foreground">
                Review your configuration before deploying your white-label instance.
              </p>
            </div>

            <div className="space-y-4">
              <Card className="p-4">
                <h3 className="font-medium mb-3">Tenant Information</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Name:</span>
                    <span className="font-medium">{config.tenantName}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">ID:</span>
                    <span className="font-medium">{config.tenantId}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Email:</span>
                    <span className="font-medium">{config.contactEmail}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Industry:</span>
                    <span className="font-medium capitalize">{config.industry}</span>
                  </div>
                </div>
              </Card>

              <Card className="p-4">
                <h3 className="font-medium mb-3">Theme & Widgets</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Theme:</span>
                    <span className="font-medium">{config.theme.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Enabled Widgets:</span>
                    <span className="font-medium">
                      {Object.values(config.widgets).filter(Boolean).length} / 7
                    </span>
                  </div>
                </div>
              </Card>

              <Card className="p-4">
                <h3 className="font-medium mb-3">Domain & SSL</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Domain:</span>
                    <span className="font-medium">
                      {config.domain || `${config.tenantId}.industriverse.io`}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">SSL:</span>
                    <span className="font-medium">{config.sslEnabled ? 'Enabled' : 'Disabled'}</span>
                  </div>
                </div>
              </Card>

              <Card className="p-4">
                <h3 className="font-medium mb-3">Feature Flags</h3>
                <div className="text-sm">
                  <span className="text-muted-foreground">
                    {Object.values(config.featureFlags).filter(Boolean).length} features enabled
                  </span>
                </div>
              </Card>
            </div>

            <div className="bg-status-success/10 border border-status-success/30 rounded p-4">
              <h3 className="font-medium mb-2">Ready to Deploy!</h3>
              <p className="text-sm text-muted-foreground">
                Your white-label instance will be provisioned with the above configuration.
                Deployment typically takes 5-10 minutes.
              </p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground">Deployment Wizard</h1>
              <p className="text-sm text-muted-foreground">
                Step {currentStep} of {WIZARD_STEPS.length}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="outline" size="sm" onClick={handleSaveDraft}>
                Save Draft
              </Button>
              {currentStep === 1 && (
                <Button variant="outline" size="sm" onClick={handleLoadDraft}>
                  Load Draft
                </Button>
              )}
              <Button variant="outline" onClick={() => (window.location.href = '/admin')}>
                Exit
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Progress Bar */}
      <div className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {WIZARD_STEPS.map((step, index) => (
              <div key={step.id} className="flex items-center flex-1">
                <div className="flex flex-col items-center flex-1">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center font-medium ${
                      currentStep === step.id
                        ? 'bg-brand-primary text-white'
                        : currentStep > step.id
                        ? 'bg-status-success text-white'
                        : 'bg-muted text-muted-foreground'
                    }`}
                  >
                    {currentStep > step.id ? '✓' : step.id}
                  </div>
                  <div className="text-xs mt-2 text-center">
                    <div className="font-medium">{step.title}</div>
                    <div className="text-muted-foreground">{step.description}</div>
                  </div>
                </div>
                {index < WIZARD_STEPS.length - 1 && (
                  <div
                    className={`h-0.5 flex-1 mx-2 ${
                      currentStep > step.id ? 'bg-status-success' : 'bg-muted'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Card className="p-8 max-w-4xl mx-auto">
          {renderStepContent()}

          {/* Navigation */}
          <div className="flex items-center justify-between mt-8 pt-6 border-t border-border">
            <Button
              variant="outline"
              onClick={handlePrevious}
              disabled={currentStep === 1}
            >
              Previous
            </Button>
            <div className="text-sm text-muted-foreground">
              Step {currentStep} of {WIZARD_STEPS.length}
            </div>
            {currentStep < WIZARD_STEPS.length ? (
              <Button onClick={handleNext}>Next</Button>
            ) : (
              <Button onClick={handleDeploy} className="bg-status-success hover:bg-status-success/90">
                Deploy Now
              </Button>
            )}
          </div>
        </Card>
      </main>
    </div>
  );
}

function getWidgetDescription(key: string): string {
  const descriptions: Record<string, string> = {
    walletOrb: 'Visual representation of wallet balance with AmI glow effects',
    proofTicker: 'Real-time proof generation feed with scrolling animation',
    capsuleCard: 'Compact capsule display with status indicators',
    energyGauge: 'Circular energy gauge with color-coded zones',
    utidBadge: 'UTID display with QR code and blockchain verification',
    amiPulse: 'Ambient intelligence activity indicator',
    shadowTwin: 'Digital twin synchronization status',
  };
  return descriptions[key] || 'Widget description';
}
