import React, { useEffect } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { observer } from 'mobx-react-lite';
import { StoreProvider, useStore } from './store/StoreContext';
import AppRoutes from './routes/AppRoutes';
import './App.css'

const AppContent: React.FC = observer(() => {
    const store = useStore();

    useEffect(() => {
        store.checkAuth();
    }, [store]);

    return <AppRoutes />;
});

function App() {
    return (
        <StoreProvider>
            <BrowserRouter>
                <AppContent />
            </BrowserRouter>
        </StoreProvider>
    )
}

export default App
