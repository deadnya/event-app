import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Header from '../../components/Header/Header';
import EventList from './EventList/EventList';
import MyEvents from './MyEvents/MyEvents';
import EventDetails from './EventDetails/EventDetails';
import Navigation from './Navigation/Navigation';
import styles from './StudentDashboard.module.css';

const StudentDashboard: React.FC = () => {
    return (
        <div className={styles.dashboard}>
            <Header title="Student Portal" />
            <div className={styles.container}>
                <Navigation />
                <main className={styles.main}>
                    <Routes>
                        <Route path="/" element={<Navigate to="/student/events" replace />} />
                        <Route path="/events" element={<EventList />} />
                        <Route path="/my-events" element={<MyEvents />} />
                        <Route path="/event/:id" element={<EventDetails />} />
                    </Routes>
                </main>
            </div>
        </div>
    );
};

export default StudentDashboard;
