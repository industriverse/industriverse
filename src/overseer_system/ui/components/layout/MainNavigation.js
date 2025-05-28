import React from 'react';
import { List, ListItem, ListItemIcon, ListItemText, Collapse, Box, Typography } from '@mui/material';
import { useRouter } from 'next/router';
import DashboardIcon from '@mui/icons-material/Dashboard';
import BarChartIcon from '@mui/icons-material/BarChart';
import PeopleIcon from '@mui/icons-material/People';
import SettingsIcon from '@mui/icons-material/Settings';
import BuildIcon from '@mui/icons-material/Build';
import TimelineIcon from '@mui/icons-material/Timeline';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import FactoryIcon from '@mui/icons-material/Factory';
import StorageIcon from '@mui/icons-material/Storage';
import { useUIState } from '../../contexts/UIStateContext';
import { useAuth } from '../../contexts/AuthContext';

/**
 * Main navigation component that provides the primary navigation
 * for the application based on the user's role and current view.
 * 
 * This implements the Role-First, Context-Aware design principle by
 * adapting the navigation options based on the user's role and selected view.
 */
export default function MainNavigation() {
  const router = useRouter();
  const { currentView, changeView } = useUIState();
  const { hasRole } = useAuth();
  const [openMenus, setOpenMenus] = React.useState({
    agents: false,
    processes: false,
    analytics: false,
  });

  // Toggle submenu open/closed state
  const handleToggleMenu = (menu) => {
    setOpenMenus((prev) => ({
      ...prev,
      [menu]: !prev[menu],
    }));
  };

  // Navigation items based on current view
  const getNavigationItems = () => {
    // Base navigation items available in all views
    const baseItems = [
      {
        text: 'Dashboard',
        icon: <DashboardIcon />,
        path: '/',
        roles: ['Administrator', 'Operator', 'Analyst', 'Manager'],
      },
      {
        text: 'Agents',
        icon: <SmartToyIcon />,
        submenu: true,
        key: 'agents',
        roles: ['Administrator', 'Operator', 'Manager'],
        items: [
          {
            text: 'Agent Management',
            path: '/agents',
            roles: ['Administrator', 'Operator', 'Manager'],
          },
          {
            text: 'Capsule Evolution',
            path: '/agents/evolution',
            roles: ['Administrator', 'Manager'],
          },
          {
            text: 'Trust Management',
            path: '/agents/trust',
            roles: ['Administrator', 'Manager'],
          },
        ],
      },
      {
        text: 'Processes',
        icon: <FactoryIcon />,
        submenu: true,
        key: 'processes',
        roles: ['Administrator', 'Operator', 'Manager'],
        items: [
          {
            text: 'Process Management',
            path: '/processes',
            roles: ['Administrator', 'Operator', 'Manager'],
          },
          {
            text: 'Workflow Automation',
            path: '/processes/workflows',
            roles: ['Administrator', 'Manager'],
          },
          {
            text: 'Strategic Simulation',
            path: '/processes/simulation',
            roles: ['Administrator', 'Manager', 'Analyst'],
          },
        ],
      },
      {
        text: 'Analytics',
        icon: <BarChartIcon />,
        submenu: true,
        key: 'analytics',
        roles: ['Administrator', 'Analyst', 'Manager'],
        items: [
          {
            text: 'Monitoring',
            path: '/analytics/monitoring',
            roles: ['Administrator', 'Operator', 'Analyst', 'Manager'],
          },
          {
            text: 'Anomaly Detection',
            path: '/analytics/anomalies',
            roles: ['Administrator', 'Analyst', 'Manager'],
          },
          {
            text: 'Optimization',
            path: '/analytics/optimization',
            roles: ['Administrator', 'Analyst', 'Manager'],
          },
          {
            text: 'Maintenance',
            path: '/analytics/maintenance',
            roles: ['Administrator', 'Operator', 'Manager'],
          },
        ],
      },
    ];

    // Additional items based on view and role
    const viewSpecificItems = [];

    // Master view specific items
    if (currentView === 'Master' && hasRole('Administrator')) {
      viewSpecificItems.push(
        {
          text: 'System Configuration',
          icon: <SettingsIcon />,
          path: '/settings',
          roles: ['Administrator'],
        },
        {
          text: 'Integration',
          icon: <StorageIcon />,
          path: '/integration',
          roles: ['Administrator'],
        }
      );
    }

    // Domain view specific items
    if (currentView === 'Domain' && (hasRole('Administrator') || hasRole('Manager'))) {
      viewSpecificItems.push({
        text: 'Domain Configuration',
        icon: <BuildIcon />,
        path: '/domain/settings',
        roles: ['Administrator', 'Manager'],
      });
    }

    // Process view specific items
    if (currentView === 'Process' && (hasRole('Administrator') || hasRole('Operator'))) {
      viewSpecificItems.push({
        text: 'Process Metrics',
        icon: <TimelineIcon />,
        path: '/process/metrics',
        roles: ['Administrator', 'Operator', 'Analyst'],
      });
    }

    // Agent view specific items
    if (currentView === 'Agent' && (hasRole('Administrator') || hasRole('Operator'))) {
      viewSpecificItems.push({
        text: 'Agent Metrics',
        icon: <TimelineIcon />,
        path: '/agent/metrics',
        roles: ['Administrator', 'Operator', 'Analyst'],
      });
    }

    // Filter items based on user roles
    const filteredBaseItems = baseItems.filter((item) => {
      if (!item.roles) return true;
      return item.roles.some((role) => hasRole(role));
    });

    const filteredViewSpecificItems = viewSpecificItems.filter((item) => {
      if (!item.roles) return true;
      return item.roles.some((role) => hasRole(role));
    });

    return [...filteredBaseItems, ...filteredViewSpecificItems];
  };

  // Render navigation items
  const renderNavigationItems = () => {
    const items = getNavigationItems();

    return items.map((item) => {
      // If item has submenu, render collapsible menu
      if (item.submenu) {
        const submenuItems = item.items.filter((subItem) => {
          if (!subItem.roles) return true;
          return subItem.roles.some((role) => hasRole(role));
        });

        // Skip rendering if no submenu items are available for the user's role
        if (submenuItems.length === 0) return null;

        return (
          <React.Fragment key={item.key}>
            <ListItem button onClick={() => handleToggleMenu(item.key)}>
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
              {openMenus[item.key] ? <ExpandLess /> : <ExpandMore />}
            </ListItem>
            <Collapse in={openMenus[item.key]} timeout="auto" unmountOnExit>
              <List component="div" disablePadding>
                {submenuItems.map((subItem) => (
                  <ListItem
                    button
                    key={subItem.path}
                    sx={{ pl: 4 }}
                    selected={router.pathname === subItem.path}
                    onClick={() => router.push(subItem.path)}
                  >
                    <ListItemText primary={subItem.text} />
                  </ListItem>
                ))}
              </List>
            </Collapse>
          </React.Fragment>
        );
      }

      // Regular menu item
      return (
        <ListItem
          button
          key={item.path}
          selected={router.pathname === item.path}
          onClick={() => router.push(item.path)}
        >
          <ListItemIcon>{item.icon}</ListItemIcon>
          <ListItemText primary={item.text} />
        </ListItem>
      );
    });
  };

  // Render view selector
  const renderViewSelector = () => {
    const views = [
      { id: 'Master', label: 'Master View', roles: ['Administrator', 'Manager'] },
      { id: 'Domain', label: 'Domain View', roles: ['Administrator', 'Manager', 'Analyst'] },
      { id: 'Process', label: 'Process View', roles: ['Administrator', 'Operator', 'Analyst', 'Manager'] },
      { id: 'Agent', label: 'Agent View', roles: ['Administrator', 'Operator', 'Analyst'] },
    ];

    // Filter views based on user roles
    const filteredViews = views.filter((view) => {
      return view.roles.some((role) => hasRole(role));
    });

    return (
      <Box sx={{ mb: 3 }}>
        <Typography variant="overline" sx={{ pl: 2 }}>
          Current View
        </Typography>
        <List component="div">
          {filteredViews.map((view) => (
            <ListItem
              button
              key={view.id}
              selected={currentView === view.id}
              onClick={() => changeView(view.id)}
            >
              <ListItemText primary={view.label} />
            </ListItem>
          ))}
        </List>
      </Box>
    );
  };

  return (
    <>
      {renderViewSelector()}
      <Typography variant="overline" sx={{ pl: 2 }}>
        Navigation
      </Typography>
      {renderNavigationItems()}
    </>
  );
}
