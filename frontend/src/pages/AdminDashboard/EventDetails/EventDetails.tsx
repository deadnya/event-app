import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { observer } from 'mobx-react-lite';
import type { EventDTO } from '../../../models/Event';
import ApiRequests from '../../../api/apiRequests';
import LoadingSpinner from '../../../components/LoadingSpinner/LoadingSpinner';
import styles from './EventDetails.module.css';

const EventDetails: React.FC = observer(() => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [event, setEvent] = useState<EventDTO | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (id) {
      loadEvent();
    } else {
      navigate('/admin/events');
    }
  }, [id, navigate]);

  const loadEvent = async () => {
    if (!id) return;

    try {
      setLoading(true);
      const response = await ApiRequests.getAdminEventById(id);
      setEvent(response.data);
    } catch (err: any) {
      console.error('Failed to load event:', err);
      setError('Failed to load event details. Please try again.');
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

  if (error || !event) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          {error || 'Event not found'}
        </div>
        <Link to="/admin/events" className={styles.backButton}>
          Back to Events
        </Link>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <Link to="/admin/events" className={styles.backButton}>
          ← Back to Events
        </Link>
        <div className={styles.eventStatus}>
          {isEventPast(event.date) ? (
            <span className={styles.pastBadge}>Past Event</span>
          ) : (
            <span className={styles.upcomingBadge}>Upcoming</span>
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
                    <div className={styles.participantName}>
                      <strong>
                        {registration.user.name.name} {registration.user.name.surname}
                      </strong>
                      {registration.user.name.patronymic && (
                        <span className={styles.patronymic}>
                          {registration.user.name.patronymic}
                        </span>
                      )}
                    </div>
                    
                    <div className={styles.participantDetails}>
                      {registration.user.email && (
                        <span className={styles.participantEmail}>
                          📧 {registration.user.email}
                        </span>
                      )}
                      {registration.user.group && (
                        <span className={styles.participantGroup}>
                          🎓 {registration.user.group}
                        </span>
                      )}
                      <span className={styles.participantRole}>
                        👤 {registration.user.role}
                      </span>
                    </div>
                  </div>
                  
                  <div className={styles.registrationMeta}>
                    <div className={styles.registrationDate}>
                      Registered: {new Date(registration.registeredAt).toLocaleDateString()}
                    </div>
                    {registration.googleEventId && (
                      <div className={styles.googleEventId}>
                        📅 Google Calendar: {registration.googleEventId}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
});

export default EventDetails;
