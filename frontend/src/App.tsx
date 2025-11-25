import { Switch, Route } from "wouter";
import Portal from './pages/Portal';
import Dashboard from './pages/Dashboard';

import LandingIndustriverse from "./pages/LandingIndustriverse";
import LandingThermodynasty from "./pages/LandingThermodynasty";


function App() {
  return (
    <Switch>
      <Route path="/" component={LandingIndustriverse} />
      <Route path="/thermodynasty" component={LandingThermodynasty} />
      <Route path="/dashboard" component={Dashboard} />
      <Route path="/portal" component={Portal} />
      <Route>404: Not Found</Route>
    </Switch>
  );
}

export default App;
