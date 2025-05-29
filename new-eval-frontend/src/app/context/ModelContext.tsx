'use client';
 
/**
* ModelContext.tsx
*
* Manages global state for selected LLM models using React Context.
* Explicitly persists selections across sessions via localStorage.
*
* Core Functionalities:
* - Global state management for selected models.
* - Persistent storage in localStorage with robust error handling.
* - Clear debug logs for easy troubleshooting and transparency.
* - Comprehensive inline documentation and comments for maintainability.
*/
 
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
 
// Explicit shape of the context state
interface ModelContextType {
  selectedModelIds: string[];
  setSelectedModelIds: (models: string[]) => void;
}
 
// Default models if none selected
const defaultModels = ['gpt4', 'claude3', 'gemini', 'o1mini'];
 
// Create context explicitly with default values
const ModelContext = createContext<ModelContextType>({
  selectedModelIds: defaultModels,
  setSelectedModelIds: () => {},
});
 
/**
* ModelProvider Component
* Wraps the application explicitly providing selected models' state and setter method.
*/
export const ModelProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [selectedModelIds, setSelectedModelIdsState] = useState<string[]>(defaultModels);
 
  /**
   * Initializes selected models from localStorage explicitly on initial render.
   */
  useEffect(() => {
    try {
      const storedModels = localStorage.getItem('selectedModelIds');
      if (storedModels) {
        const parsedModels = JSON.parse(storedModels);
        if (Array.isArray(parsedModels) && parsedModels.length > 0) {
          console.info('[ModelContext] Loaded selected models from localStorage:', parsedModels);
          setSelectedModelIdsState(parsedModels);
        } else {
          console.warn('[ModelContext] localStorage contained invalid data:', parsedModels);
        }
      } else {
        console.info('[ModelContext] No stored models found, using defaults:', defaultModels);
      }
    } catch (error) {
      console.error('[ModelContext] Error loading models from localStorage:', error);
    }
  }, []);
 
  /**
   * Updates selected models in state and explicitly persists to localStorage.
   * Includes robust error handling and clear debug logging.
   */
  const setSelectedModelIds = (models: string[]) => {
    console.debug('[ModelContext] Updating selected models to:', models);
    setSelectedModelIdsState(models);
    try {
      localStorage.setItem('selectedModelIds', JSON.stringify(models));
      console.info('[ModelContext] Saved selected models to localStorage:', models);
    } catch (error) {
      console.error('[ModelContext] Error saving selected models to localStorage:', error);
    }
  };
 
  return (
<ModelContext.Provider value={{ selectedModelIds, setSelectedModelIds }}>
      {children}
</ModelContext.Provider>
  );
};
 
/**
* useModelContext Hook
* Provides explicit and convenient access to model context throughout the app.
*/
export const useModelContext = () => {
  const context = useContext(ModelContext);
  if (!context) {
    console.error('[ModelContext] useModelContext called outside of ModelProvider.');
    throw new Error('useModelContext must be used within a ModelProvider');
  }
  return context;
};