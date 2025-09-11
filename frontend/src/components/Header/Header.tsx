import React, { useState } from 'react';
import { observer } from 'mobx-react-lite';
import { useStore } from '../../store/StoreContext';
import EditProfile from '../EditProfile/EditProfile';
import styles from './Header.module.css';

interface HeaderProps {
    title?: string;
}

const Header: React.FC<HeaderProps> = observer(({ title }) => {
    const store = useStore();
    const [isEditProfileOpen, setIsEditProfileOpen] = useState(false);

    const handleLogout = async () => {
        await store.logout();
    };

    const handleEditProfile = () => {
        setIsEditProfileOpen(true);
    };

    const handleCloseEditProfile = async () => {
        setIsEditProfileOpen(false);
        if (store.isAuth) {
            try {
                await store.fetchUserProfile();
            } catch (error) {
                console.error('Failed to refresh user profile:', error);
            }
        }
    };

    const getUserDisplayName = () => {
        if (store.user?.name) {
            return `${store.user.name.name} ${store.user.name.surname}`;
        }
        return store.user?.email || 'User';
    };

    return (
        <header className={styles.header}>
            <div className={styles.container}>
                <div className={styles.left}>
                    <h1 className={styles.title}>{title || 'Event Management'}</h1>
                </div>
                
                <div className={styles.right}>
                    <div className={styles.userInfo}>
                        <button 
                            onClick={handleEditProfile}
                            className={styles.userNameButton}
                            title="Click to edit profile"
                        >
                            <span className={styles.userName}>{getUserDisplayName()}</span>
                        </button>
                        <span className={styles.userRole}>({store.userRole})</span>
                    </div>
                    
                    <button 
                        onClick={handleLogout}
                        className={styles.logoutButton}
                    >
                        Logout
                    </button>
                </div>
            </div>
            
            <EditProfile 
                isOpen={isEditProfileOpen}
                onClose={handleCloseEditProfile}
            />
        </header>
    );
});

export default Header;
