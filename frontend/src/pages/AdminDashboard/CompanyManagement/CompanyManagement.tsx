import React, { useState, useEffect } from 'react';
import { observer } from 'mobx-react-lite';
import type { CompanyShortDTO, CreateCompanyDTO, EditCompanyDTO } from '../../../models/Company';
import ApiRequests from '../../../api/apiRequests';
import LoadingSpinner from '../../../components/LoadingSpinner/LoadingSpinner';
import styles from './CompanyManagement.module.css';

const CompanyManagement: React.FC = observer(() => {
    const [companies, setCompanies] = useState<CompanyShortDTO[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);
    const [editingCompany, setEditingCompany] = useState<CompanyShortDTO | null>(null);
    const [actionLoading, setActionLoading] = useState(false);

    const [newCompanyName, setNewCompanyName] = useState('');
    const [editCompanyName, setEditCompanyName] = useState('');

    useEffect(() => {
        loadCompanies();
    }, []);

    const loadCompanies = async () => {
        try {
            setLoading(true);
            const response = await ApiRequests.getAllCompanies();
            setCompanies(response.data);
        } catch (err: any) {
            console.error('Failed to load companies:', err);
            setError('Failed to load companies. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleCreateCompany = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newCompanyName.trim()) return;

        try {
            setActionLoading(true);
            const createData: CreateCompanyDTO = { name: newCompanyName.trim() };
            await ApiRequests.createCompany(createData);
            setNewCompanyName('');
            setShowCreateModal(false);
            await loadCompanies();
        } catch (err: any) {
            console.error('Failed to create company:', err);
            alert('Failed to create company. Please try again.');
        } finally {
            setActionLoading(false);
        }
    };

    const handleEditCompany = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!editingCompany || !editCompanyName.trim()) return;

        try {
            setActionLoading(true);
            const editData: EditCompanyDTO = {
                id: editingCompany.id,
                name: editCompanyName.trim()
            };
            await ApiRequests.editCompany(editData);
            setShowEditModal(false);
            setEditingCompany(null);
            setEditCompanyName('');
            await loadCompanies();
        } catch (err: any) {
            console.error('Failed to edit company:', err);
            alert('Failed to edit company. Please try again.');
        } finally {
            setActionLoading(false);
        }
    };

    const openEditModal = (company: CompanyShortDTO) => {
        setEditingCompany(company);
        setEditCompanyName(company.name);
        setShowEditModal(true);
    };

    const closeModals = () => {
        setShowCreateModal(false);
        setShowEditModal(false);
        setEditingCompany(null);
        setNewCompanyName('');
        setEditCompanyName('');
    };

    if (loading) {
        return <LoadingSpinner />;
    }

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h2 className={styles.title}>Company Management</h2>
                <button
                onClick={() => setShowCreateModal(true)}
                className={styles.createButton}
                >
                Create Company
                </button>
            </div>

            {error && (
                <div className={styles.error}>
                {error}
                </div>
            )}

            <div className={styles.companiesGrid}>
                {companies.length === 0 ? (
                    <div className={styles.emptyState}>
                        <p>No companies found.</p>
                    </div>
                ) : (
                    companies.map((company) => (
                        <div key={company.id} className={styles.companyCard}>
                            <div className={styles.companyInfo}>
                                <h3 className={styles.companyName}>{company.name}</h3>
                            </div>
                            <div className={styles.companyActions}>
                                <button
                                    onClick={() => openEditModal(company)}
                                    className={styles.editButton}
                                >
                                    Edit
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {showCreateModal && (
                <div className={styles.modal}>
                    <div className={styles.modalContent}>
                        <div className={styles.modalHeader}>
                            <h3>Create New Company</h3>
                            <button onClick={closeModals} className={styles.closeButton}>×</button>
                        </div>
                            
                        <form onSubmit={handleCreateCompany} className={styles.form}>
                            <div className={styles.inputGroup}>
                                <label htmlFor="companyName" className={styles.label}>
                                    Company Name
                                </label>
                                <input
                                    type="text"
                                    id="companyName"
                                    value={newCompanyName}
                                    onChange={(e) => setNewCompanyName(e.target.value)}
                                    className={styles.input}
                                    placeholder="Enter company name"
                                    required
                                    disabled={actionLoading}
                                />
                            </div>

                            <div className={styles.modalActions}>
                                <button
                                    type="button"
                                    onClick={closeModals}
                                    className={styles.cancelButton}
                                    disabled={actionLoading}
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className={styles.submitButton}
                                    disabled={actionLoading || !newCompanyName.trim()}
                                >
                                    {actionLoading ? 'Creating...' : 'Create Company'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {showEditModal && editingCompany && (
                <div className={styles.modal}>
                    <div className={styles.modalContent}>
                        <div className={styles.modalHeader}>
                            <h3>Edit Company</h3>
                            <button onClick={closeModals} className={styles.closeButton}>×</button>
                        </div>
                        
                        <form onSubmit={handleEditCompany} className={styles.form}>
                            <div className={styles.inputGroup}>
                                <label htmlFor="editCompanyName" className={styles.label}>
                                    Company Name
                                </label>
                                <input
                                    type="text"
                                    id="editCompanyName"
                                    value={editCompanyName}
                                    onChange={(e) => setEditCompanyName(e.target.value)}
                                    className={styles.input}
                                    placeholder="Enter company name"
                                    required
                                    disabled={actionLoading}
                                />
                            </div>

                            <div className={styles.modalActions}>
                                <button
                                    type="button"
                                    onClick={closeModals}
                                    className={styles.cancelButton}
                                    disabled={actionLoading}
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className={styles.submitButton}
                                    disabled={actionLoading || !editCompanyName.trim()}
                                >
                                    {actionLoading ? 'Saving...' : 'Save Changes'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
});

export default CompanyManagement;
