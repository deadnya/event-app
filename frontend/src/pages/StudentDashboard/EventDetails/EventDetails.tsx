import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { observer } from 'mobx-react-lite';
import { useStore } from '../../../store/StoreContext';
import type { EventDTO } from '../../../models/Event';
import ApiRequests from '../../../api/apiRequests';
import LoadingSpinner from '../../../components/LoadingSpinner/LoadingSpinner';
import styles from './EventDetails.module.css';

const EventDetails: React.FC = observer(() => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const store = useStore();
    const [event, setEvent] = useState<EventDTO | null>(null);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(false);
    const [error, setError] = useState('');
    const [isRegistered, setIsRegistered] = useState(false);

    useEffect(() => {
        if (id) {
        loadEvent();
        } else {
        navigate('/student/events');
        }
    }, [id, navigate]);

    const loadEvent = async () => {
        if (!id) return;

        try {
        setLoading(true);
        const response = await ApiRequests.getEventById(id);
        setEvent(response.data);
        
        // Check if user is registered
        const userRegistration = response.data.registrations.find(
            reg => reg.user.id === store.user.id
        );
        setIsRegistered(!!userRegistration);
        } catch (err: any) {
        console.error('Failed to load event:', err);
        setError('Failed to load event details. Please try again.');
        } finally {
        setLoading(false);
        }
    };

    const handleRegister = async () => {
        if (!id) return;

        try {
        setActionLoading(true);
        await ApiRequests.registerToEvent(id);
        await loadEvent(); // Refresh event data
        } catch (err: any) {
        console.error('Failed to register:', err);
        if (err.response?.status === 409) {
            alert('You are already registered for this event.');
        } else {
            alert('Failed to register for event. Please try again.');
        }
        } finally {
        setActionLoading(false);
        }
    };

    const handleUnregister = async () => {
        if (!id) return;
        
        if (!confirm('Are you sure you want to unregister from this event?')) {
        return;
        }

        try {
        setActionLoading(true);
        await ApiRequests.unregisterFromEvent(id);
        await loadEvent(); // Refresh event data
        } catch (err: any) {
        console.error('Failed to unregister:', err);
        alert('Failed to unregister from event. Please try again.');
        } finally {
        setActionLoading(false);
        }
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        });
    };

    const isEventPast = (dateString: string) => {
        return new Date(dateString) < new Date();
    };

    const isRegistrationClosed = (deadlineString: string) => {
        return new Date(deadlineString) < new Date();
    };

    if (loading) {
        return <LoadingSpinner />;
    }

    if (error || !event) {
        return (
        <div className={styles.container}>
            <div className={styles.error}>
            {error || 'Event not found'}
            </div>
            <Link to="/student/events" className={styles.backButton}>
            Back to Events
            </Link>
        </div>
        );
    }

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <Link to="/student/events" className={styles.backButton}>
                    ← Back to Events
                </Link>
                <div className={styles.eventStatus}>
                    {isEventPast(event.date) ? (
                        <span className={styles.pastBadge}>Past Event</span>
                    ) : isRegistrationClosed(event.registrationDeadline) ? (
                        <span className={styles.closedBadge}>Registration Closed</span>
                    ) : (
                        <span className={styles.upcomingBadge}>Open for Registration</span>
                    )}
                </div>
            </div>

            <div className={styles.eventCard}>
                <div className={styles.eventHeader}>
                    <h1 className={styles.eventTitle}>{event.name}</h1>
                </div>

                <div className={styles.eventMeta}>
                    <div className={styles.metaItem}>
                        <span className={styles.icon}>📅</span>
                        <div>
                            <strong>Date & Time</strong>
                            <p>{formatDate(event.date)}</p>
                        </div>
                    </div>

                    <div className={styles.metaItem}>
                        <span className={styles.icon}>⏰</span>
                        <div>
                            <strong>Registration Deadline</strong>
                            <p>{formatDate(event.registrationDeadline)}</p>
                        </div>
                    </div>

                    <div className={styles.metaItem}>
                        <span className={styles.icon}>📍</span>
                        <div>
                            <strong>Location</strong>
                            <p>{event.location}</p>
                        </div>
                    </div>

                    <div className={styles.metaItem}>
                        <span className={styles.icon}>👥</span>
                        <div>
                            <strong>Registered</strong>
                            <p>{event.registrations.length} participants</p>
                        </div>
                    </div>
                </div>

                {event.description && (
                    <div className={styles.description}>
                        <h3>Description</h3>
                        <p>{event.description}</p>
                    </div>
                )}

                <div className={styles.registrations}>
                    <h3>Registered Participants ({event.registrations.length})</h3>
                    {event.registrations.length === 0 ? (
                        <p className={styles.noRegistrations}>No participants registered yet.</p>
                    ) : (
                        <div className={styles.participantsList}>
                            {event.registrations.map((registration) => (
                                <div key={registration.id} className={styles.participant}>
                                    <div className={styles.participantInfo}>
                                        <strong>
                                            {registration.user.name.name} {registration.user.name.surname}
                                        </strong>
                                        {registration.user.group && (
                                            <span className={styles.participantGroup}>
                                                {registration.user.group}
                                            </span>
                                        )}
                                    </div>
                                    <div className={styles.registrationDate}>
                                        Registered: {new Date(registration.registeredAt).toLocaleDateString()}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {!isEventPast(event.date) && !isRegistrationClosed(event.registrationDeadline) && (
                    <div className={styles.actions}>
                        {isRegistered ? (
                            <button
                                onClick={handleUnregister}
                                className={styles.unregisterButton}
                                disabled={actionLoading}
                            >
                                {actionLoading ? 'Unregistering...' : 'Unregister from Event'}
                            </button>
                        ) : (
                            <button
                                onClick={handleRegister}
                                className={styles.registerButton}
                                disabled={actionLoading}
                            >
                                {actionLoading ? 'Registering...' : 'Register for Event'}
                            </button>
                        )}
                    </div>
                )}

                {!isEventPast(event.date) && isRegistrationClosed(event.registrationDeadline) && (
                    <div className={styles.actions}>
                        <div className={styles.closedMessage}>
                            Registration deadline has passed
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
});

export default EventDetails;
