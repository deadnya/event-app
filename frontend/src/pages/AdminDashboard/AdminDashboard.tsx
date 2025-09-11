import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Header from '../../components/Header/Header';
import AdminNavigation from './AdminNavigation/AdminNavigation';
import CompanyManagement from './CompanyManagement/CompanyManagement';
import UserManagement from './UserManagement/UserManagement';
import EventManagement from './EventManagement/EventManagement';
import EventDetails from './EventDetails/EventDetails';
import styles from './AdminDashboard.module.css';

const AdminDashboard: React.FC = () => {
    return (
        <div className={styles.dashboard}>
            <Header title="Admin Portal" />
            <div className={styles.container}>
                <AdminNavigation />
                <main className={styles.main}>
                    <Routes>
                        <Route path="/" element={<Navigate to="/admin/companies" replace />} />
                        <Route path="/companies" element={<CompanyManagement />} />
                        <Route path="/users" element={<UserManagement />} />
                        <Route path="/events" element={<EventManagement />} />
                        <Route path="/event/:id" element={<EventDetails />} />
                    </Routes>
                </main>
            </div>
        </div>
    );
};

export default AdminDashboard;
