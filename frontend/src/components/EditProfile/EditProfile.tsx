import React, { useState } from 'react';
import { observer } from 'mobx-react-lite';
import { useStore } from '../../store/StoreContext';
import type { FullName } from '../../models/User';
import styles from './EditProfile.module.css';

interface EditProfileProps {
    isOpen: boolean;
    onClose: () => void;
}

const EditProfile: React.FC<EditProfileProps> = observer(({ isOpen, onClose }) => {
    const store = useStore();
    const [formData, setFormData] = useState<FullName>({
        surname: store.user?.name?.surname || '',
        name: store.user?.name?.name || '',
        patronymic: store.user?.name?.patronymic || ''
    });
    const [isLoading, setIsLoading] = useState(false);
    const [errors, setErrors] = useState<{ [key: string]: string }>({});

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }));
        }
    };

    const validateForm = (): boolean => {
        const newErrors: { [key: string]: string } = {};

        if (!formData.surname.trim()) {
            newErrors.surname = 'Surname is required';
        }

        if (!formData.name.trim()) {
            newErrors.name = 'Name is required';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        setIsLoading(true);
        try {
            await store.updateUser({ 
                    name: {
                    surname: formData.surname.trim(),
                    name: formData.name.trim(),
                    patronymic: formData.patronymic?.trim() || undefined
                }
            });

            onClose();
        } catch (error) {
            console.error('Failed to update profile:', error);
            setErrors({ submit: 'Failed to update profile. Please try again.' });
        } finally {
            setIsLoading(false);
        }
    };

    const handleClose = () => {
        if (!isLoading) {
            setFormData({
                surname: store.user?.name?.surname || '',
                name: store.user?.name?.name || '',
                patronymic: store.user?.name?.patronymic || ''
            });

            setErrors({});
            onClose();
        }
    };

    const handleOverlayClick = (e: React.MouseEvent) => {
        if (e.target === e.currentTarget) {
            handleClose();
        }
    };

    if (!isOpen) return null;

    return (
        <div className={styles.modal} onClick={handleOverlayClick}>
            <div className={styles.modalContent}>
                <div className={styles.modalHeader}>
                    <h2 className={styles.modalTitle}>Edit Profile</h2>
                    <button 
                        className={styles.closeButton} 
                        onClick={handleClose}
                        disabled={isLoading}
                    >
                        ×
                    </button>
                </div>

                <form className={styles.form} onSubmit={handleSubmit}>
                    <div className={styles.formGroup}>
                        <label className={styles.label}>
                            Surname <span className={styles.required}>*</span>
                        </label>
                        <input
                            type="text"
                            name="surname"
                            value={formData.surname}
                            onChange={handleChange}
                            className={styles.input}
                            disabled={isLoading}
                            maxLength={50}
                        />

                        {errors.surname && <div className={styles.error}>{errors.surname}</div>}
                    </div>

                    <div className={styles.formGroup}>
                        <label className={styles.label}>
                            Name <span className={styles.required}>*</span>
                        </label>
                        <input
                            type="text"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            className={styles.input}
                            disabled={isLoading}
                            maxLength={50}
                        />

                        {errors.name && <div className={styles.error}>{errors.name}</div>}
                    </div>

                    <div className={styles.formGroup}>
                        <label className={styles.label}>Patronymic</label>
                        <input
                            type="text"
                            name="patronymic"
                            value={formData.patronymic}
                            onChange={handleChange}
                            className={styles.input}
                            disabled={isLoading}
                            maxLength={50}
                        />
                    </div>

                    {errors.submit && <div className={styles.error}>{errors.submit}</div>}

                    <div className={styles.buttonGroup}>
                        <button
                            type="button"
                            className={`${styles.button} ${styles.cancelButton}`}
                            onClick={handleClose}
                            disabled={isLoading}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className={`${styles.button} ${styles.saveButton}`}
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <div className={styles.loading}>
                                    <div className={styles.spinner}></div>
                                    Saving...
                                </div>
                            ) : (
                                'Save Changes'
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
});

export default EditProfile;
