import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { observer } from 'mobx-react-lite';
import type { EventDTO } from '../../../models/Event';
import ApiRequests from '../../../api/apiRequests';
import LoadingSpinner from '../../../components/LoadingSpinner/LoadingSpinner';
import styles from './EventManagement.module.css';

const EventManagement: React.FC = observer(() => {
    const [events, setEvents] = useState<EventDTO[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        loadEvents();
    }, []);

    const loadEvents = async () => {
        try {
            setLoading(true);
            const response = await ApiRequests.getAdminEvents();
            setEvents(response.data);
        } catch (err: any) {
            console.error('Failed to load events:', err);
            setError('Failed to load events. Please try again.');
        } finally {
            setLoading(false);
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
                <h2 className={styles.title}>Event Management</h2>
                <button onClick={loadEvents} className={styles.refreshButton}>
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
                    <p>No events found.</p>
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
                                    <span className={styles.pastBadge}>Past</span>
                                ) : (
                                    <span className={styles.upcomingBadge}>Upcoming</span>
                                )}
                                </div>
                            </div>

                            <div className={styles.eventDetails}>
                                <p className={styles.eventDate}>
                                    <span className={styles.icon}>📅</span>
                                    {formatDate(event.date)}
                                </p>
                                <p className={styles.eventDate}>
                                    <span className={styles.icon}>⏰</span>
                                    Registration deadline: {formatDate(event.registrationDeadline)}
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
                                    to={`/admin/event/${event.id}`}
                                    className={styles.viewButton}
                                >
                                    View Details
                                </Link>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
});

export default EventManagement;
