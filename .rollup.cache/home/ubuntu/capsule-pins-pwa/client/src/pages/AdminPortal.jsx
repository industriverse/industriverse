/**
 * Admin Portal
 * Week 8: White-Label Platform - Phase 4
 *
 * Control center for white-label management:
 * - Theme Editor with live preview
 * - Widget Configurator
 * - Multi-tenant management
 * - Domain setup
 * - Feature flags
 * - Analytics dashboard
 */
import { __assign } from "tslib";
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ThemeSwitcher } from '@/components/ThemeSwitcher';
import { themePresets } from '@/themes/presets';
export default function AdminPortal() {
    var _a = useState('theme'), activeTab = _a[0], setActiveTab = _a[1];
    var _b = useState(themePresets[0].theme), currentTheme = _b[0], setCurrentTheme = _b[1];
    var _c = useState({
        walletOrb: { enabled: true, position: 'top-right' },
        proofTicker: { enabled: true, maxItems: 10 },
        capsuleCard: { enabled: true, compact: false },
        energyGauge: { enabled: true, showStats: true },
        utidBadge: { enabled: true, showQR: true },
        amiPulse: { enabled: true, showDetails: false },
        shadowTwin: { enabled: true, autoSync: true },
    }), widgetConfig = _c[0], setWidgetConfig = _c[1];
    var handleThemeChange = function (theme) {
        setCurrentTheme(theme);
    };
    var handleExportTheme = function () {
        var json = JSON.stringify(currentTheme, null, 2);
        var blob = new Blob([json], { type: 'application/json' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = "theme-".concat(currentTheme.name.toLowerCase().replace(/\s+/g, '-'), ".json");
        a.click();
    };
    var generateWidgetEmbedCode = function (widgetName) {
        var config = widgetConfig[widgetName];
        var attrs = Object.entries(config)
            .filter(function (_a) {
            var key = _a[0];
            return key !== 'enabled';
        })
            .map(function (_a) {
            var key = _a[0], value = _a[1];
            return "".concat(key, "=\"").concat(value, "\"");
        })
            .join(' ');
        return "<".concat(widgetName, " ").concat(attrs, " ws-url=\"wss://your-domain.com/ws\"></").concat(widgetName, ">");
    };
    return (<div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground">Admin Portal</h1>
              <p className="text-sm text-muted-foreground">White-Label Management</p>
            </div>
            <div className="flex items-center gap-4">
              <Button variant="outline" onClick={function () { return window.location.href = '/'; }}>
                Back to App
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="theme">Theme Editor</TabsTrigger>
            <TabsTrigger value="widgets">Widgets</TabsTrigger>
            <TabsTrigger value="tenants">Tenants</TabsTrigger>
            <TabsTrigger value="domains">Domains</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          {/* Theme Editor Tab */}
          <TabsContent value="theme" className="space-y-6">
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Theme Customization</h2>
              <p className="text-sm text-muted-foreground mb-6">
                Customize your white-label theme with live preview. All changes are applied in real-time.
              </p>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Theme Selector */}
                <div>
                  <h3 className="text-lg font-medium mb-4">Select Base Theme</h3>
                  <ThemeSwitcher onThemeChange={handleThemeChange}/>

                  <div className="mt-6">
                    <h3 className="text-lg font-medium mb-4">Theme Actions</h3>
                    <div className="flex gap-3">
                      <Button onClick={handleExportTheme}>
                        Export Theme
                      </Button>
                      <Button variant="outline">
                        Import Theme
                      </Button>
                      <Button variant="outline">
                        Reset to Default
                      </Button>
                    </div>
                  </div>

                  <div className="mt-6">
                    <h3 className="text-lg font-medium mb-4">Color Customization</h3>
                    <div className="space-y-4">
                      {Object.entries(currentTheme.colors.brand).map(function (_a) {
            var key = _a[0], value = _a[1];
            return (<div key={key} className="flex items-center justify-between">
                          <label className="text-sm capitalize">{key}</label>
                          <input type="color" value={value} onChange={function (e) {
                    var _a;
                    var newTheme = __assign(__assign({}, currentTheme), { colors: __assign(__assign({}, currentTheme.colors), { brand: __assign(__assign({}, currentTheme.colors.brand), (_a = {}, _a[key] = e.target.value, _a)) }) });
                    setCurrentTheme(newTheme);
                }} className="w-12 h-12 rounded cursor-pointer"/>
                        </div>);
        })}
                    </div>
                  </div>
                </div>

                {/* Live Preview */}
                <div>
                  <h3 className="text-lg font-medium mb-4">Live Preview</h3>
                  <Card className="p-6 bg-background">
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <h4 className="text-lg font-semibold">Sample Component</h4>
                        <Button size="sm">Action</Button>
                      </div>
                      <p className="text-muted-foreground">
                        This is how your theme will look in the application.
                      </p>
                      <div className="grid grid-cols-2 gap-4">
                        <Card className="p-4">
                          <div className="text-sm font-medium">Status: Active</div>
                          <div className="text-2xl font-bold text-status-success">✓</div>
                        </Card>
                        <Card className="p-4">
                          <div className="text-sm font-medium">Status: Warning</div>
                          <div className="text-2xl font-bold text-status-warning">⚠</div>
                        </Card>
                      </div>
                    </div>
                  </Card>
                </div>
              </div>
            </Card>
          </TabsContent>

          {/* Widgets Tab */}
          <TabsContent value="widgets" className="space-y-6">
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Widget Configuration</h2>
              <p className="text-sm text-muted-foreground mb-6">
                Configure and generate embed codes for all 7 white-label widgets.
              </p>

              <div className="space-y-6">
                {Object.entries(widgetConfig).map(function (_a) {
            var name = _a[0], config = _a[1];
            return (<Card key={name} className="p-4">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-medium capitalize">
                          {name.replace(/([A-Z])/g, ' $1').trim()}
                        </h3>
                        <p className="text-sm text-muted-foreground">
                          {getWidgetDescription(name)}
                        </p>
                      </div>
                      <Button variant={config.enabled ? 'default' : 'outline'} size="sm" onClick={function () {
                    var _a;
                    setWidgetConfig(__assign(__assign({}, widgetConfig), (_a = {}, _a[name] = __assign(__assign({}, config), { enabled: !config.enabled }), _a)));
                }}>
                        {config.enabled ? 'Enabled' : 'Disabled'}
                      </Button>
                    </div>

                    {config.enabled && (<div className="mt-4">
                        <h4 className="text-sm font-medium mb-2">Embed Code:</h4>
                        <pre className="bg-muted p-3 rounded text-xs overflow-x-auto">
                          <code>{generateWidgetEmbedCode(name)}</code>
                        </pre>
                        <Button variant="outline" size="sm" className="mt-2" onClick={function () {
                        navigator.clipboard.writeText(generateWidgetEmbedCode(name));
                    }}>
                          Copy Code
                        </Button>
                      </div>)}
                  </Card>);
        })}
              </div>
            </Card>
          </TabsContent>

          {/* Tenants Tab */}
          <TabsContent value="tenants" className="space-y-6">
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Multi-Tenant Management</h2>
              <p className="text-sm text-muted-foreground mb-6">
                Manage white-label deployments for multiple clients.
              </p>

              <div className="space-y-4">
                {[
            { name: 'TSMC Fab 18', status: 'active', users: 1250, capsules: 3400 },
            { name: 'Intel Oregon', status: 'active', users: 890, capsules: 2100 },
            { name: 'Samsung Austin', status: 'active', users: 650, capsules: 1800 },
        ].map(function (tenant) { return (<Card key={tenant.name} className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium">{tenant.name}</h3>
                        <div className="flex gap-4 mt-2 text-sm text-muted-foreground">
                          <span>{tenant.users} users</span>
                          <span>{tenant.capsules} capsules</span>
                          <span className="text-status-success capitalize">{tenant.status}</span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm">Configure</Button>
                        <Button variant="outline" size="sm">Analytics</Button>
                      </div>
                    </div>
                  </Card>); })}

                <Button className="w-full" onClick={function () { return window.location.href = '/admin/feature-flags'; }}>
                  Manage Feature Flags
                </Button>
                <Button className="w-full" variant="outline" onClick={function () { return window.location.href = '/admin/ami-dashboard'; }}>
                  View AmI Visualization Dashboard
                </Button>
              </div>
            </Card>
          </TabsContent>

          {/* Domains Tab */}
          <TabsContent value="domains" className="space-y-6">
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Domain Configuration</h2>
              <p className="text-sm text-muted-foreground mb-6">
                Configure custom domains for white-label deployments.
              </p>

              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Domain Name</label>
                    <input type="text" placeholder="capsules.your-company.com" className="w-full mt-2 px-3 py-2 bg-background border border-border rounded"/>
                  </div>
                  <div>
                    <label className="text-sm font-medium">SSL Certificate</label>
                    <Button variant="outline" className="w-full mt-2">
                      Upload Certificate
                    </Button>
                  </div>
                </div>

                <Button>Add Domain</Button>

                <div className="mt-6">
                  <h3 className="text-lg font-medium mb-4">Active Domains</h3>
                  <div className="space-y-2">
                    {[
            { domain: 'tsmc-capsules.industriverse.io', status: 'active', ssl: true },
            { domain: 'intel-ops.industriverse.io', status: 'active', ssl: true },
        ].map(function (domain) { return (<Card key={domain.domain} className="p-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="font-medium">{domain.domain}</div>
                            <div className="text-sm text-muted-foreground">
                              {domain.ssl && '🔒 SSL Enabled'} • {domain.status}
                            </div>
                          </div>
                          <Button variant="outline" size="sm">Configure</Button>
                        </div>
                      </Card>); })}
                  </div>
                </div>
              </div>
            </Card>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Platform Analytics</h2>
              <p className="text-sm text-muted-foreground mb-6">
                Monitor usage across all white-label deployments.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <Card className="p-4">
                  <div className="text-sm text-muted-foreground">Total Deployments</div>
                  <div className="text-3xl font-bold mt-2">12</div>
                  <div className="text-sm text-status-success mt-1">+2 this month</div>
                </Card>
                <Card className="p-4">
                  <div className="text-sm text-muted-foreground">Active Users</div>
                  <div className="text-3xl font-bold mt-2">3,450</div>
                  <div className="text-sm text-status-success mt-1">+15% growth</div>
                </Card>
                <Card className="p-4">
                  <div className="text-sm text-muted-foreground">Total Capsules</div>
                  <div className="text-3xl font-bold mt-2">8,200</div>
                  <div className="text-sm text-muted-foreground mt-1">Across all tenants</div>
                </Card>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-medium">AmI Network Intelligence</h3>
                <Card className="p-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <div className="text-sm text-muted-foreground">Context Awareness</div>
                      <div className="text-2xl font-bold text-brand-primary">87%</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Proactivity</div>
                      <div className="text-2xl font-bold text-brand-secondary">72%</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Seamlessness</div>
                      <div className="text-2xl font-bold text-brand-accent">94%</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Adaptivity</div>
                      <div className="text-2xl font-bold text-status-success">81%</div>
                    </div>
                  </div>
                </Card>

                <Card className="p-4 mt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-medium">Feature Flags</h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        Manage per-tenant feature availability
                      </p>
                    </div>
                    <Button variant="outline" onClick={function () { return window.location.href = '/admin/feature-flags'; }}>
                      Manage Flags
                    </Button>
                  </div>
                </Card>
              </div>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>);
}
function getWidgetDescription(name) {
    var descriptions = {
        walletOrb: 'Visual representation of wallet balance with AmI glow effects',
        proofTicker: 'Real-time proof generation feed with scrolling animation',
        capsuleCard: 'Compact capsule display with status indicators',
        energyGauge: 'Circular energy gauge with color-coded zones',
        utidBadge: 'UTID display with QR code and blockchain verification',
        amiPulse: 'Ambient intelligence activity indicator',
        shadowTwin: 'Digital twin synchronization status',
    };
    return descriptions[name] || 'Widget description';
}
//# sourceMappingURL=AdminPortal.jsx.map