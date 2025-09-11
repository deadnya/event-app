import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import styles from './Navigation.module.css';

const Navigation: React.FC = () => {
    const location = useLocation();

    const navItems = [
        { path: '/student/events', label: 'All Events', icon: '📅' },
        { path: '/student/my-events', label: 'My Events', icon: '⭐' },
    ];

    return (
        <nav className={styles.navigation}>
            <h3 className={styles.title}>Navigation</h3>
            <ul className={styles.navList}>
                {navItems.map((item) => (
                    <li key={item.path}>
                        <Link
                            to={item.path}
                            className={`${styles.navLink} ${
                                location.pathname === item.path ? styles.active : ''
                            }`}
                        >
                            <span className={styles.icon}>{item.icon}</span>
                            {item.label}
                        </Link>
                    </li>
                ))}
            </ul>
        </nav>
    );
};

export default Navigation;
