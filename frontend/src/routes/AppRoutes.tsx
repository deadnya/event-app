import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { observer } from 'mobx-react-lite';
import { useStore } from '../store/StoreContext';

import LoginPage from '../pages/LoginPage/LoginPage';
import AdminDashboard from '../pages/AdminDashboard/AdminDashboard';
import StudentDashboard from '../pages/StudentDashboard/StudentDashboard';
import ErrorPage from '../pages/ErrorPage/ErrorPage';
import LoadingSpinner from '../components/LoadingSpinner/LoadingSpinner';

const AppRoutes: React.FC = observer(() => {
    const store = useStore();

    if (store.isAdminLoading) {
        return <LoadingSpinner />;
    }

    if (!store.isAuth) {
        return (
            <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
        );
    }

    switch (store.userRole) {
        case 'ADMIN':
        return (
            <Routes>
                <Route path="/admin/*" element={<AdminDashboard />} />
                <Route path="*" element={<Navigate to="/admin" replace />} />
            </Routes>
        );

        case 'STUDENT':
        return (
            <Routes>
                <Route path="/student/*" element={<StudentDashboard />} />
                <Route path="*" element={<Navigate to="/student" replace />} />
            </Routes>
        );

        case 'MANAGER':
        return (
            <Routes>
                <Route path="/error" element={<ErrorPage message="Manager access is not available on web platform." />} />
                <Route path="*" element={<Navigate to="/error" replace />} />
            </Routes>
        );

        default:
        return (
            <Routes>
                <Route path="/error" element={<ErrorPage message="Unknown user role. Please contact administrator." />} />
                <Route path="*" element={<Navigate to="/error" replace />} />
            </Routes>
        );
    }
});

export default AppRoutes;
