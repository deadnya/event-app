import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { observer } from 'mobx-react-lite';
import type { EventDTO } from '../../../models/Event';
import ApiRequests from '../../../api/apiRequests';
import LoadingSpinner from '../../../components/LoadingSpinner/LoadingSpinner';
import styles from './MyEvents.module.css';

const MyEvents: React.FC = observer(() => {
    const [events, setEvents] = useState<EventDTO[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [loadingAction, setLoadingAction] = useState<string | null>(null);

    useEffect(() => {
        loadMyEvents();
    }, []);

    const loadMyEvents = async () => {
        try {
        setLoading(true);
        const response = await ApiRequests.getStudentEvents();
        setEvents(response.data);
        } catch (err: any) {
        console.error('Failed to load my events:', err);
        setError('Failed to load your events. Please try again.');
        } finally {
        setLoading(false);
        }
    };

    const handleUnregister = async (eventId: string) => {
        if (!confirm('Are you sure you want to unregister from this event?')) {
        return;
        }

        try {
        setLoadingAction(eventId);
        await ApiRequests.unregisterFromEvent(eventId);
        await loadMyEvents(); // Refresh the list
        } catch (err: any) {
        console.error('Failed to unregister:', err);
        alert('Failed to unregister from event. Please try again.');
        } finally {
        setLoadingAction(null);
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

    if (loading) {
        return <LoadingSpinner />;
    }

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h2 className={styles.title}>My Events</h2>
                <button onClick={loadMyEvents} className={styles.refreshButton}>
                    Refresh
                </button>
            </div>

            {error && (
                <div className={styles.error}>
                    {error}
                </div>
            )}

            {events.length === 0 ? (
                <div className={styles.emptyState}>
                    <p>You haven't registered for any events yet.</p>
                    <Link to="/student/events" className={styles.browseButton}>
                        Browse Events
                    </Link>
                </div>
            ) : (
                <div className={styles.eventGrid}>
                    {events.map((event) => (
                        <div 
                            key={event.id} 
                            className={`${styles.eventCard} ${isEventPast(event.date) ? styles.pastEvent : ''}`}
                        >
                            <div className={styles.eventHeader}>
                                <h3 className={styles.eventName}>{event.name}</h3>
                                <div className={styles.eventStatus}>
                                    {isEventPast(event.date) ? (
                                        <span className={styles.pastBadge}>Completed</span>
                                    ) : (
                                        <span className={styles.registeredBadge}>Registered</span>
                                    )}
                                </div>
                            </div>

                            <div className={styles.eventDetails}>
                                <p className={styles.eventDate}>
                                    <span className={styles.icon}>📅</span>
                                    {formatDate(event.date)}
                                </p>
                                <p className={styles.eventLocation}>
                                    <span className={styles.icon}>📍</span>
                                    {event.location}
                                </p>
                                {event.description && (
                                <p className={styles.eventDescription}>
                                    {event.description.length > 100
                                    ? `${event.description.substring(0, 100)}...`
                                    : event.description
                                    }
                                </p>
                                )}
                                <p className={styles.registrationCount}>
                                    <span className={styles.icon}>👥</span>
                                    {event.registrations.length} registered
                                </p>
                            </div>

                            <div className={styles.eventActions}>
                                <Link 
                                    to={`/student/event/${event.id}`}
                                    className={styles.viewButton}
                                >
                                    View Details
                                </Link>
                                {!isEventPast(event.date) && (
                                    <button
                                        onClick={() => handleUnregister(event.id)}
                                        className={styles.unregisterButton}
                                        disabled={loadingAction === event.id}
                                    >
                                        {loadingAction === event.id ? 'Unregistering...' : 'Unregister'}
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
});

export default MyEvents;
