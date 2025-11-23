import { Toaster } from "@/components/ui/sonner";
import NotFound from "@/pages/NotFound";
import { Switch, Route } from "wouter";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./lib/queryClient";
import Portal from "@/pages/Portal";
import Dashboard from "@/pages/AmIVisualizationDashboard"; // Using existing dashboard for now
import Lab from "@/pages/Lab";
import DNA from "@/pages/DNA";
import { ThemeProvider } from "@/components/theme-provider";
import { TooltipProvider } from "@/components/ui/tooltip";
import ErrorBoundary from "./ErrorBoundary"; // Assuming ErrorBoundary is in the root or needs to be imported

function Router() {
  return (
    <Switch>
      <Route path="/" component={Portal} />
      <Route path="/dashboard" component={Dashboard} />
      <Route path="/lab" component={Lab} />
      <Route path="/dna" component={DNA} />
      {/* Add other routes as they are built */}
      <Route component={NotFound} />
    </Switch>
  );
}

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
