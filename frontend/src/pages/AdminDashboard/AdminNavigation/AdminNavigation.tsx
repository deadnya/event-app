import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import styles from './AdminNavigation.module.css';

const AdminNavigation: React.FC = () => {
    const location = useLocation();

    const navItems = [
        { path: '/admin/companies', label: 'Company Management' },
        { path: '/admin/users', label: 'User Management' },
        { path: '/admin/events', label: 'Event Management' },
    ];

    return (
        <nav className={styles.navigation}>
            <h3 className={styles.title}>Admin Panel</h3>
            <ul className={styles.navList}>
                {navItems.map((item) => (
                    <li key={item.path}>
                        <Link
                            to={item.path}
                            className={`${styles.navLink} ${
                                location.pathname === item.path ? styles.active : ''
                            }`}
                        >
                            {item.label}
                        </Link>
                    </li>
                ))}
            </ul>
        </nav>
    );
};

export default AdminNavigation;
