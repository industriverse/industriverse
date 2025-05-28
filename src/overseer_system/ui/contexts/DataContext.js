import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';

// Create data context
const DataContext = createContext();

/**
 * Data provider component that manages data fetching, caching,
 * and state management for the application.
 * 
 * This supports the Live, Linked Visuals design principle by
 * providing a common data layer for all visualizations.
 */
export const DataProvider = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [loading, setLoading] = useState({});
  const [error, setError] = useState({});
  const [data, setData] = useState({});
  const [cache, setCache] = useState({});
  const [cacheTimestamps, setCacheTimestamps] = useState({});
  
  // Cache expiration time in milliseconds (5 minutes)
  const CACHE_EXPIRATION = 5 * 60 * 1000;
  
  // Clear cache when user logs out
  useEffect(() => {
    if (!isAuthenticated) {
      setCache({});
      setCacheTimestamps({});
      setData({});
    }
  }, [isAuthenticated]);
  
  // Check if cache is valid
  const isCacheValid = (key) => {
    if (!cache[key] || !cacheTimestamps[key]) return false;
    
    const now = Date.now();
    const timestamp = cacheTimestamps[key];
    
    return now - timestamp < CACHE_EXPIRATION;
  };
  
  // Fetch data from API
  const fetchData = async (endpoint, params = {}, options = {}) => {
    const {
      skipCache = false,
      forceRefresh = false,
      cacheKey = endpoint,
    } = options;
    
    // Generate unique key for caching
    const queryString = new URLSearchParams(params).toString();
    const key = queryString ? `${cacheKey}?${queryString}` : cacheKey;
    
    // Set loading state
    setLoading((prev) => ({ ...prev, [key]: true }));
    setError((prev) => ({ ...prev, [key]: null }));
    
    try {
      // Check cache if not skipping or forcing refresh
      if (!skipCache && !forceRefresh && isCacheValid(key)) {
        setData((prev) => ({ ...prev, [key]: cache[key] }));
        setLoading((prev) => ({ ...prev, [key]: false }));
        return cache[key];
      }
      
      // Fetch data from API
      const response = await axios.get(endpoint, { params });
      const responseData = response.data;
      
      // Update state and cache
      setData((prev) => ({ ...prev, [key]: responseData }));
      
      if (!skipCache) {
        setCache((prev) => ({ ...prev, [key]: responseData }));
        setCacheTimestamps((prev) => ({ ...prev, [key]: Date.now() }));
      }
      
      return responseData;
    } catch (err) {
      console.error(`Error fetching data from ${endpoint}:`, err);
      setError((prev) => ({ ...prev, [key]: err.message }));
      throw err;
    } finally {
      setLoading((prev) => ({ ...prev, [key]: false }));
    }
  };
  
  // Mutate data (create, update, delete)
  const mutateData = async (method, endpoint, payload = null, options = {}) => {
    const {
      invalidateCache = [],
      updateCache = true,
      optimisticUpdate = null,
    } = options;
    
    // Apply optimistic update if provided
    if (optimisticUpdate) {
      optimisticUpdate(setData, setCache);
    }
    
    try {
      // Make API request
      const response = await axios({
        method,
        url: endpoint,
        data: payload,
      });
      
      const responseData = response.data;
      
      // Invalidate cache for specified keys
      if (invalidateCache.length > 0) {
        const newCache = { ...cache };
        const newCacheTimestamps = { ...cacheTimestamps };
        
        invalidateCache.forEach((key) => {
          delete newCache[key];
          delete newCacheTimestamps[key];
        });
        
        setCache(newCache);
        setCacheTimestamps(newCacheTimestamps);
      }
      
      // Update cache with new data if specified
      if (updateCache && responseData) {
        const cacheKey = options.cacheKey || endpoint;
        setCache((prev) => ({ ...prev, [cacheKey]: responseData }));
        setCacheTimestamps((prev) => ({ ...prev, [cacheKey]: Date.now() }));
        setData((prev) => ({ ...prev, [cacheKey]: responseData }));
      }
      
      return responseData;
    } catch (err) {
      console.error(`Error mutating data at ${endpoint}:`, err);
      
      // Revert optimistic update if it failed
      if (optimisticUpdate && options.revertOnError) {
        options.revertOnError(setData, setCache);
      }
      
      throw err;
    }
  };
  
  // Helper methods for common operations
  const getData = (key) => data[key];
  const isLoading = (key) => loading[key] || false;
  const getError = (key) => error[key] || null;
  
  // Create helper methods for different HTTP methods
  const createData = (endpoint, payload, options = {}) => 
    mutateData('post', endpoint, payload, options);
    
  const updateData = (endpoint, payload, options = {}) => 
    mutateData('put', endpoint, payload, options);
    
  const patchData = (endpoint, payload, options = {}) => 
    mutateData('patch', endpoint, payload, options);
    
  const deleteData = (endpoint, options = {}) => 
    mutateData('delete', endpoint, null, options);
  
  // Context value
  const value = {
    data,
    loading,
    error,
    fetchData,
    getData,
    isLoading,
    getError,
    createData,
    updateData,
    patchData,
    deleteData,
    clearCache: () => {
      setCache({});
      setCacheTimestamps({});
    },
  };
  
  return <DataContext.Provider value={value}>{children}</DataContext.Provider>;
};

// Custom hook for using data context
export const useData = () => {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error('useData must be used within a DataProvider');
  }
  return context;
};

export default DataContext;
