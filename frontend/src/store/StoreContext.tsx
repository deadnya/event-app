import React, { createContext, useContext } from 'react';
import Store from './store';

interface StoreContextType {
    store: Store;
}

const StoreContext = createContext<StoreContextType | undefined>(undefined);

export const store = new Store();

export const StoreProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    return (
        <StoreContext.Provider value={{ store }}>
            {children}
        </StoreContext.Provider>
    );
};

export const useStore = (): Store => {
    const context = useContext(StoreContext);
    if (!context) {
        throw new Error('useStore must be used within a StoreProvider');
    }
    return context.store;
};
