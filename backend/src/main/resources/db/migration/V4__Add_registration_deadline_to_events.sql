ALTER TABLE events 
ADD COLUMN registration_deadline TIMESTAMP;

UPDATE events 
SET registration_deadline = date - INTERVAL '1 day' 
WHERE registration_deadline IS NULL;

ALTER TABLE events 
ALTER COLUMN registration_deadline SET NOT NULL;

CREATE INDEX idx_events_registration_deadline ON events(registration_deadline);
