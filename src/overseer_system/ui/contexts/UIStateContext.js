import React, { createContext, useContext, useState } from 'react';

// Create UI state context
const UIStateContext = createContext();

/**
 * UI State provider component that manages global UI state
 * such as sidebar open/closed, current view, selected role,
 * and other UI-specific state.
 * 
 * This supports the Role-First, Context-Aware design principle by
 * managing role-based views and UI state across the application.
 */
export const UIStateProvider = ({ children }) => {
  // Sidebar state
  const [sidebarOpen, setSidebarOpen] = useState(true);
  
  // Current view state (Master, Domain, Process, Agent)
  const [currentView, setCurrentView] = useState('Master');
  
  // Current role state
  const [selectedRole, setSelectedRole] = useState('Administrator');
  
  // Theme mode state
  const [darkMode, setDarkMode] = useState(false);
  
  // Notification state
  const [notifications, setNotifications] = useState([]);
  
  // Modal state
  const [activeModal, setActiveModal] = useState(null);
  
  // Toggle sidebar
  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);
  
  // Change view
  const changeView = (view) => setCurrentView(view);
  
  // Change role
  const changeRole = (role) => setSelectedRole(role);
  
  // Toggle dark mode
  const toggleDarkMode = () => setDarkMode(!darkMode);
  
  // Add notification
  const addNotification = (notification) => {
    const id = Date.now().toString();
    const newNotification = {
      id,
      timestamp: new Date().toISOString(),
      read: false,
      ...notification,
    };
    
    setNotifications((prev) => [newNotification, ...prev]);
    return id;
  };
  
  // Mark notification as read
  const markNotificationAsRead = (id) => {
    setNotifications((prev) =>
      prev.map((notification) =>
        notification.id === id ? { ...notification, read: true } : notification
      )
    );
  };
  
  // Remove notification
  const removeNotification = (id) => {
    setNotifications((prev) => prev.filter((notification) => notification.id !== id));
  };
  
  // Open modal
  const openModal = (modalId, modalProps = {}) => {
    setActiveModal({ id: modalId, props: modalProps });
  };
  
  // Close modal
  const closeModal = () => {
    setActiveModal(null);
  };
  
  // Context value
  const value = {
    sidebarOpen,
    toggleSidebar,
    currentView,
    changeView,
    selectedRole,
    changeRole,
    darkMode,
    toggleDarkMode,
    notifications,
    addNotification,
    markNotificationAsRead,
    removeNotification,
    activeModal,
    openModal,
    closeModal,
  };
  
  return <UIStateContext.Provider value={value}>{children}</UIStateContext.Provider>;
};

// Custom hook for using UI state context
export const useUIState = () => {
  const context = useContext(UIStateContext);
  if (!context) {
    throw new Error('useUIState must be used within a UIStateProvider');
  }
  return context;
};

export default UIStateContext;
