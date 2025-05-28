import React, { createContext, useContext, useState, useEffect } from 'react';
import io from 'socket.io-client';

// Create event bus context
const EventBusContext = createContext();

/**
 * Event Bus provider component that manages real-time event communication
 * between the UI and backend services.
 * 
 * This supports the Live, Linked Visuals design principle by enabling
 * real-time updates across all UI components.
 */
export const EventBusProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const [events, setEvents] = useState([]);
  const [subscriptions, setSubscriptions] = useState({});

  // Initialize socket connection
  useEffect(() => {
    // Connect to event bus
    const socketInstance = io(process.env.NEXT_PUBLIC_EVENT_BUS_URL || 'http://localhost:8085', {
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: 10,
      reconnectionDelay: 1000,
    });

    // Set up event handlers
    socketInstance.on('connect', () => {
      console.log('Connected to event bus');
      setConnected(true);
    });

    socketInstance.on('disconnect', () => {
      console.log('Disconnected from event bus');
      setConnected(false);
    });

    socketInstance.on('error', (error) => {
      console.error('Event bus error:', error);
    });

    // Handle incoming events
    socketInstance.on('event', (event) => {
      console.log('Received event:', event);
      setEvents((prevEvents) => [...prevEvents, event]);

      // Notify subscribers
      if (event.type && subscriptions[event.type]) {
        subscriptions[event.type].forEach((callback) => {
          try {
            callback(event);
          } catch (error) {
            console.error(`Error in event handler for ${event.type}:`, error);
          }
        });
      }
    });

    setSocket(socketInstance);

    // Cleanup on unmount
    return () => {
      if (socketInstance) {
        socketInstance.disconnect();
      }
    };
  }, []);

  // Subscribe to event type
  const subscribe = (eventType, callback) => {
    if (!eventType || typeof callback !== 'function') {
      console.error('Invalid subscription parameters');
      return () => {}; // Return empty unsubscribe function
    }

    setSubscriptions((prev) => {
      const eventSubscribers = prev[eventType] || [];
      return {
        ...prev,
        [eventType]: [...eventSubscribers, callback],
      };
    });

    // Return unsubscribe function
    return () => {
      setSubscriptions((prev) => {
        const eventSubscribers = prev[eventType] || [];
        return {
          ...prev,
          [eventType]: eventSubscribers.filter((cb) => cb !== callback),
        };
      });
    };
  };

  // Publish event to event bus
  const publish = (eventType, payload) => {
    if (!socket || !connected) {
      console.error('Cannot publish event: not connected to event bus');
      return false;
    }

    const event = {
      type: eventType,
      payload,
      timestamp: new Date().toISOString(),
    };

    socket.emit('event', event);
    return true;
  };

  // Context value
  const value = {
    connected,
    events,
    subscribe,
    publish,
  };

  return <EventBusContext.Provider value={value}>{children}</EventBusContext.Provider>;
};

// Custom hook for using event bus context
export const useEventBus = () => {
  const context = useContext(EventBusContext);
  if (!context) {
    throw new Error('useEventBus must be used within an EventBusProvider');
  }
  return context;
};

export default EventBusContext;
