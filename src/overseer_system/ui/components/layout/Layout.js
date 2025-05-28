import React from 'react';
import { Box, Drawer, AppBar, Toolbar, Typography, Divider, List, IconButton, useMediaQuery } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import { useUIState } from '../../contexts/UIStateContext';
import MainNavigation from './MainNavigation';
import RoleSelector from './RoleSelector';
import NotificationsPanel from './NotificationsPanel';
import UserMenu from './UserMenu';

// Drawer width for desktop view
const drawerWidth = 280;

/**
 * Main layout component that provides the application shell with
 * responsive sidebar, header, and content area.
 * 
 * This implements the Role-First, Context-Aware design principle by
 * adapting the layout based on the user's role and device.
 */
export default function Layout({ children }) {
  const theme = useTheme();
  const { sidebarOpen, toggleSidebar } = useUIState();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Determine if drawer should be temporary (mobile) or persistent (desktop)
  const isTemporaryDrawer = isMobile;

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          zIndex: theme.zIndex.drawer + 1,
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          ...(sidebarOpen && !isTemporaryDrawer && {
            marginLeft: drawerWidth,
            width: `calc(100% - ${drawerWidth}px)`,
            transition: theme.transitions.create(['width', 'margin'], {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
          }),
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="toggle sidebar"
            edge="start"
            onClick={toggleSidebar}
            sx={{ mr: 2 }}
          >
            {sidebarOpen ? <ChevronLeftIcon /> : <MenuIcon />}
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Overseer System
          </Typography>
          <RoleSelector />
          <NotificationsPanel />
          <UserMenu />
        </Toolbar>
      </AppBar>

      {/* Sidebar Drawer */}
      <Drawer
        variant={isTemporaryDrawer ? 'temporary' : 'persistent'}
        open={sidebarOpen}
        onClose={isTemporaryDrawer ? toggleSidebar : undefined}
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
          },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto', height: '100%', display: 'flex', flexDirection: 'column' }}>
          <List component="nav" sx={{ p: 2 }}>
            <MainNavigation />
          </List>
          <Divider />
          <Box sx={{ flexGrow: 1 }} />
          <Divider />
          <Box sx={{ p: 2 }}>
            <Typography variant="caption" color="textSecondary">
              Overseer System v1.0.0
            </Typography>
          </Box>
        </Box>
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: '100%',
          height: '100vh',
          overflow: 'auto',
          pt: { xs: 8, sm: 9 }, // Toolbar offset
          backgroundColor: theme.palette.background.default,
        }}
      >
        {children}
      </Box>
    </Box>
  );
}
