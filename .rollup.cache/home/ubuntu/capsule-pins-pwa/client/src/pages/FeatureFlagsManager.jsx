/**
 * Feature Flags Manager Page
 * Week 8: White-Label Platform - Phase 4
 *
 * UI for managing feature flags across white-label deployments.
 */
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useFeatureFlags, featureFlags } from '@/services/FeatureFlags';
import { toast } from 'sonner';
export default function FeatureFlagsManager() {
    var flags = useFeatureFlags();
    var _a = useState('core'), activeCategory = _a[0], setActiveCategory = _a[1];
    var categories = ['core', 'widget', 'ami', 'integration', 'experimental'];
    var handleToggle = function (flagKey) {
        featureFlags.toggle(flagKey);
        toast.success('Feature flag updated');
    };
    var handleExport = function () {
        var config = featureFlags.exportConfig();
        var json = JSON.stringify(config, null, 2);
        var blob = new Blob([json], { type: 'application/json' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = "feature-flags-".concat(config.tenantId, ".json");
        a.click();
        toast.success('Configuration exported');
    };
    var handleReset = function () {
        if (confirm('Reset all flags to defaults?')) {
            featureFlags.resetToDefaults();
            toast.success('Flags reset to defaults');
        }
    };
    var categoryFlags = flags.filter(function (flag) { return flag.category === activeCategory; });
    var enabledCount = categoryFlags.filter(function (f) { return f.enabled; }).length;
    return (<div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground">Feature Flags</h1>
              <p className="text-sm text-muted-foreground">Per-tenant feature management</p>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="outline" onClick={handleExport}>
                Export Config
              </Button>
              <Button variant="outline" onClick={handleReset}>
                Reset to Defaults
              </Button>
              <Button variant="outline" onClick={function () { return window.location.href = '/admin'; }}>
                Back to Admin
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Tabs value={activeCategory} onValueChange={function (v) { return setActiveCategory(v); }}>
          <TabsList className="grid w-full grid-cols-5">
            {categories.map(function (cat) { return (<TabsTrigger key={cat} value={cat} className="capitalize">
                {cat}
              </TabsTrigger>); })}
          </TabsList>

          {categories.map(function (category) { return (<TabsContent key={category} value={category} className="space-y-6">
              <Card className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-xl font-semibold capitalize">{category} Features</h2>
                    <p className="text-sm text-muted-foreground mt-1">
                      {enabledCount} of {categoryFlags.length} enabled
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={function () {
                var updates = {};
                categoryFlags.forEach(function (flag) {
                    updates[flag.key] = true;
                });
                featureFlags.updateFlags(updates);
                toast.success('All flags enabled');
            }}>
                      Enable All
                    </Button>
                    <Button variant="outline" size="sm" onClick={function () {
                var updates = {};
                categoryFlags.forEach(function (flag) {
                    updates[flag.key] = false;
                });
                featureFlags.updateFlags(updates);
                toast.success('All flags disabled');
            }}>
                      Disable All
                    </Button>
                  </div>
                </div>

                <div className="space-y-4">
                  {categoryFlags.map(function (flag) { return (<Card key={flag.key} className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3">
                            <h3 className="text-lg font-medium">{flag.name}</h3>
                            <span className={"text-xs px-2 py-1 rounded ".concat(flag.enabled
                    ? 'bg-status-success/20 text-status-success'
                    : 'bg-muted text-muted-foreground')}>
                              {flag.enabled ? 'Enabled' : 'Disabled'}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground mt-2">{flag.description}</p>
                          <div className="text-xs text-muted-foreground mt-2 font-mono">
                            {flag.key}
                          </div>
                        </div>
                        <Button variant={flag.enabled ? 'default' : 'outline'} size="sm" onClick={function () { return handleToggle(flag.key); }}>
                          {flag.enabled ? 'Disable' : 'Enable'}
                        </Button>
                      </div>
                    </Card>); })}
                </div>
              </Card>
            </TabsContent>); })}
        </Tabs>

        {/* Summary Card */}
        <Card className="p-6 mt-6">
          <h2 className="text-xl font-semibold mb-4">Configuration Summary</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {categories.map(function (category) {
            var catFlags = flags.filter(function (f) { return f.category === category; });
            var enabled = catFlags.filter(function (f) { return f.enabled; }).length;
            return (<div key={category} className="text-center">
                  <div className="text-2xl font-bold text-brand-primary">
                    {enabled}/{catFlags.length}
                  </div>
                  <div className="text-sm text-muted-foreground capitalize mt-1">
                    {category}
                  </div>
                </div>);
        })}
          </div>
        </Card>
      </main>
    </div>);
}
//# sourceMappingURL=FeatureFlagsManager.jsx.map