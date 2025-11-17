import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import Home from "./pages/Home";
import TenantManagement from "./pages/TenantManagement";
import WidgetDemo from "./pages/WidgetDemo";
import CapsuleCatalog from "./pages/CapsuleCatalog";
import Settings from "./pages/Settings";
import AdminPortal from "./pages/AdminPortal";
import FeatureFlagsManager from "./pages/FeatureFlagsManager";
import DeploymentWizard from "./pages/DeploymentWizard";
import AmIVisualizationDashboard from "./pages/AmIVisualizationDashboard";

function Router() {
  // make sure to consider if you need authentication for certain routes
  return (
    <Switch>
      <Route path={"/"} component={Home} />
      <Route path={"/admin/tenants"} component={TenantManagement} />
      <Route path={"/widgets"} component={WidgetDemo} />
      <Route path={"/catalog"} component={CapsuleCatalog} />
        <Route path="/settings" component={Settings} />
        <Route path="/admin" component={AdminPortal} />
        <Route path="/admin/feature-flags" component={FeatureFlagsManager} />
        <Route path="/admin/deploy" component={DeploymentWizard} />
        <Route path="/admin/ami-dashboard" component={AmIVisualizationDashboard} />
      <Route path={"/404"} component={NotFound} />
      {/* Final fallback route */}
      <Route component={NotFound} />
    </Switch>
  );
}

// NOTE: About Theme
// - First choose a default theme according to your design style (dark or light bg), than change color palette in index.css
//   to keep consistent foreground/background color across components
// - If you want to make theme switchable, pass `switchable` ThemeProvider and use `useTheme` hook

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider
        defaultTheme="dark"
        // switchable
      >
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
