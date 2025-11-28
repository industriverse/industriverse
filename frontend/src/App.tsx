import { Switch, Route } from "wouter";
import Portal from './pages/Portal';
import Dashboard from './pages/Dashboard';

import LandingIndustriverse from "./pages/LandingIndustriverse";
import LandingThermodynasty from "./pages/LandingThermodynasty";
import PhysicsPortal from "./portals/PhysicsPortal";
import HardwarePortal from "./portals/HardwarePortal";
import BioPortal from "./portals/BioPortal";
import SpacePortal from "./portals/SpacePortal";
import EconomyPortal from "./portals/EconomyPortal";
import ALifePortal from "./portals/ALifePortal";


function App() {
  return (
    <Switch>
      <Route path="/" component={LandingIndustriverse} />
      <Route path="/thermodynasty" component={LandingThermodynasty} />
      <Route path="/dashboard" component={Dashboard} />
      <Route path="/portal" component={Portal} />

      {/* Dyson Sphere Portals */}
      <Route path="/physics" component={PhysicsPortal} />
      <Route path="/hardware" component={HardwarePortal} />
      <Route path="/bio" component={BioPortal} />
      <Route path="/space" component={SpacePortal} />
      <Route path="/economy" component={EconomyPortal} />
      <Route path="/alife" component={ALifePortal} />

      <Route>404: Not Found</Route>
    </Switch>
  );
}

export default App;
