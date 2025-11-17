/**
 * Settings Page
 *
 * Configuration for Capsule Pins PWA:
 * - WebSocket connection settings
 * - Notification preferences
 * - Theme toggle
 * - App information
 */
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { ArrowLeft, Save, RefreshCw } from 'lucide-react';
import { Link } from 'wouter';
import { toast } from 'sonner';
import { useTheme } from '@/contexts/ThemeContext';
export default function Settings() {
    var _a = useTheme(), theme = _a.theme, toggleTheme = _a.toggleTheme;
    // WebSocket settings
    var _b = useState(import.meta.env.VITE_CAPSULE_GATEWAY_WS || 'wss://capsule-gateway.industriverse.io/ws'), wsUrl = _b[0], setWsUrl = _b[1];
    var _c = useState(import.meta.env.VITE_AUTH_TOKEN || ''), authToken = _c[0], setAuthToken = _c[1];
    var _d = useState(import.meta.env.VITE_ENABLE_WEBSOCKET === 'true'), enableWebSocket = _d[0], setEnableWebSocket = _d[1];
    // Notification settings
    var _e = useState(true), enableNotifications = _e[0], setEnableNotifications = _e[1];
    var _f = useState(true), notifyOnCritical = _f[0], setNotifyOnCritical = _f[1];
    var _g = useState(true), notifyOnWarning = _g[0], setNotifyOnWarning = _g[1];
    var _h = useState(false), notifyOnResolved = _h[0], setNotifyOnResolved = _h[1];
    // App settings
    var _j = useState(import.meta.env.VITE_USE_MOCK_DATA !== 'false'), useMockData = _j[0], setUseMockData = _j[1];
    var handleSave = function () {
        // In a real app, these would be saved to localStorage or backend
        localStorage.setItem('capsule_pins_settings', JSON.stringify({
            wsUrl: wsUrl,
            authToken: authToken,
            enableWebSocket: enableWebSocket,
            enableNotifications: enableNotifications,
            notifyOnCritical: notifyOnCritical,
            notifyOnWarning: notifyOnWarning,
            notifyOnResolved: notifyOnResolved,
            useMockData: useMockData
        }));
        toast.success('Settings Saved', {
            description: 'Your preferences have been saved. Reload the page to apply changes.'
        });
    };
    var handleReset = function () {
        setWsUrl('wss://capsule-gateway.industriverse.io/ws');
        setAuthToken('');
        setEnableWebSocket(false);
        setEnableNotifications(true);
        setNotifyOnCritical(true);
        setNotifyOnWarning(true);
        setNotifyOnResolved(false);
        setUseMockData(true);
        localStorage.removeItem('capsule_pins_settings');
        toast.info('Settings Reset', {
            description: 'All settings have been reset to defaults'
        });
    };
    return (<div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2"/>
                  Back
                </Button>
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-foreground">Settings</h1>
                <p className="text-sm text-muted-foreground">Configure Capsule Pins PWA</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="outline" size="sm" onClick={handleReset}>
                <RefreshCw className="h-4 w-4 mr-2"/>
                Reset
              </Button>
              <Button variant="default" size="sm" onClick={handleSave}>
                <Save className="h-4 w-4 mr-2"/>
                Save
              </Button>
            </div>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="container py-8">
        <div className="max-w-2xl mx-auto space-y-8">
          
          {/* WebSocket Configuration */}
          <section className="space-y-4">
            <div>
              <h2 className="text-lg font-semibold text-foreground">WebSocket Configuration</h2>
              <p className="text-sm text-muted-foreground">Configure real-time connection to Capsule Gateway</p>
            </div>
            
            <div className="space-y-4 bg-card border border-border rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="enable-ws">Enable WebSocket</Label>
                  <p className="text-sm text-muted-foreground">
                    Auto-connect to WebSocket server on app start
                  </p>
                </div>
                <Switch id="enable-ws" checked={enableWebSocket} onCheckedChange={setEnableWebSocket}/>
              </div>
              
              <Separator />
              
              <div className="space-y-2">
                <Label htmlFor="ws-url">WebSocket URL</Label>
                <Input id="ws-url" type="text" value={wsUrl} onChange={function (e) { return setWsUrl(e.target.value); }} placeholder="wss://capsule-gateway.industriverse.io/ws"/>
                <p className="text-xs text-muted-foreground">
                  WebSocket endpoint for real-time updates
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="auth-token">Authentication Token</Label>
                <Input id="auth-token" type="password" value={authToken} onChange={function (e) { return setAuthToken(e.target.value); }} placeholder="JWT token from Industriverse platform"/>
                <p className="text-xs text-muted-foreground">
                  JWT token for authentication (obtain from platform dashboard)
                </p>
              </div>
            </div>
          </section>
          
          {/* Notification Preferences */}
          <section className="space-y-4">
            <div>
              <h2 className="text-lg font-semibold text-foreground">Notification Preferences</h2>
              <p className="text-sm text-muted-foreground">Choose which events trigger notifications</p>
            </div>
            
            <div className="space-y-4 bg-card border border-border rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="enable-notif">Enable Notifications</Label>
                  <p className="text-sm text-muted-foreground">
                    Show browser notifications for capsule events
                  </p>
                </div>
                <Switch id="enable-notif" checked={enableNotifications} onCheckedChange={setEnableNotifications}/>
              </div>
              
              <Separator />
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="notif-critical">Critical Capsules</Label>
                  <p className="text-sm text-muted-foreground">
                    Notify when critical capsules appear
                  </p>
                </div>
                <Switch id="notif-critical" checked={notifyOnCritical} onCheckedChange={setNotifyOnCritical} disabled={!enableNotifications}/>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="notif-warning">Warning Capsules</Label>
                  <p className="text-sm text-muted-foreground">
                    Notify when warning capsules appear
                  </p>
                </div>
                <Switch id="notif-warning" checked={notifyOnWarning} onCheckedChange={setNotifyOnWarning} disabled={!enableNotifications}/>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="notif-resolved">Resolved Capsules</Label>
                  <p className="text-sm text-muted-foreground">
                    Notify when capsules are resolved
                  </p>
                </div>
                <Switch id="notif-resolved" checked={notifyOnResolved} onCheckedChange={setNotifyOnResolved} disabled={!enableNotifications}/>
              </div>
            </div>
          </section>
          
          {/* Appearance */}
          <section className="space-y-4">
            <div>
              <h2 className="text-lg font-semibold text-foreground">Appearance</h2>
              <p className="text-sm text-muted-foreground">Customize the look and feel</p>
            </div>
            
            <div className="space-y-4 bg-card border border-border rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="theme">Dark Mode</Label>
                  <p className="text-sm text-muted-foreground">
                    Use dark theme (currently {theme})
                  </p>
                </div>
                <Switch id="theme" checked={theme === 'dark'} onCheckedChange={toggleTheme}/>
              </div>
            </div>
          </section>
          
          {/* Development Options */}
          <section className="space-y-4">
            <div>
              <h2 className="text-lg font-semibold text-foreground">Development Options</h2>
              <p className="text-sm text-muted-foreground">Options for testing and development</p>
            </div>
            
            <div className="space-y-4 bg-card border border-border rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="mock-data">Use Mock Data</Label>
                  <p className="text-sm text-muted-foreground">
                    Use mock capsules instead of API (requires reload)
                  </p>
                </div>
                <Switch id="mock-data" checked={useMockData} onCheckedChange={setUseMockData}/>
              </div>
            </div>
          </section>
          
          {/* About */}
          <section className="space-y-4">
            <div>
              <h2 className="text-lg font-semibold text-foreground">About</h2>
              <p className="text-sm text-muted-foreground">Application information</p>
            </div>
            
            <div className="space-y-4 bg-card border border-border rounded-lg p-6">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Version</span>
                  <span className="text-sm text-muted-foreground">1.0.0 (Week 7)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Build</span>
                  <span className="text-sm text-muted-foreground">Progressive Web App</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Platform</span>
                  <span className="text-sm text-muted-foreground">Industriverse</span>
                </div>
              </div>
              
              <Separator />
              
              <div className="text-xs text-muted-foreground">
                <p>Powered by the complete vertical stack:</p>
                <p className="mt-1">Remix Lab → A2A → MCP → Thermodynamic Computing → DAC Factory</p>
              </div>
            </div>
          </section>
          
        </div>
      </main>
    </div>);
}
//# sourceMappingURL=Settings.jsx.map