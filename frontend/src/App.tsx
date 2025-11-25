import { Switch, Route } from "wouter";
import Portal from './pages/Portal';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <Switch>
      <Route path="/" component={Portal} />
      <Route path="/dashboard" component={Dashboard} />
    </Switch>
  );
}

export default App;
