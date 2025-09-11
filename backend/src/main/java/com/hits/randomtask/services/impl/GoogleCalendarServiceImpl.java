package com.hits.randomtask.services.impl;

import com.google.api.client.auth.oauth2.AuthorizationCodeFlow;
import com.google.api.client.auth.oauth2.AuthorizationCodeRequestUrl;
import com.google.api.client.auth.oauth2.BearerToken;
import com.google.api.client.auth.oauth2.ClientParametersAuthentication;
import com.google.api.client.auth.oauth2.TokenResponse;
import com.google.api.client.googleapis.javanet.GoogleNetHttpTransport;
import com.google.api.client.http.GenericUrl;
import com.google.api.client.http.HttpTransport;
import com.google.api.client.json.JsonFactory;
import com.google.api.client.json.gson.GsonFactory;
import com.google.api.client.util.DateTime;
import com.google.api.services.calendar.Calendar;
import com.google.api.services.calendar.CalendarScopes;
import com.google.api.services.calendar.model.Event.Creator;
import com.google.api.services.calendar.model.Event.Organizer;
import com.google.api.services.calendar.model.EventDateTime;
import com.google.auth.http.HttpCredentialsAdapter;
import com.google.auth.oauth2.AccessToken;
import com.google.auth.oauth2.GoogleCredentials;
import com.hits.randomtask.config.GoogleCalendarConfig;
import com.hits.randomtask.entities.Event;
import com.hits.randomtask.entities.User;
import com.hits.randomtask.repositories.UserRepository;
import com.hits.randomtask.services.GoogleCalendarService;
import com.hits.randomtask.shared.exceptions.custom.BadRequestException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.security.GeneralSecurityException;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.Collections;
import java.util.Date;

@Service
@RequiredArgsConstructor
@Slf4j
public class GoogleCalendarServiceImpl implements GoogleCalendarService {

    private final GoogleCalendarConfig config;
    private final UserRepository userRepository;
    
    private static final JsonFactory JSON_FACTORY = GsonFactory.getDefaultInstance();
    private static final GenericUrl TOKEN_SERVER_URL = new GenericUrl("https://oauth2.googleapis.com/token");
    private static final String AUTHORIZATION_SERVER_URL = "https://accounts.google.com/o/oauth2/auth";

    @Override
    public String getAuthorizationUrl(User user) {

        if (config.getClientId() == null || config.getClientId().trim().isEmpty()) {
            throw new BadRequestException("Google Calendar client ID is not configured");
        }
        if (config.getClientSecret() == null || config.getClientSecret().trim().isEmpty()) {
            throw new BadRequestException("Google Calendar client secret is not configured");
        }
        if (config.getRedirectUri() == null || config.getRedirectUri().trim().isEmpty()) {
            throw new BadRequestException("Google Calendar redirect URI is not configured");
        }

        try {
            HttpTransport httpTransport = GoogleNetHttpTransport.newTrustedTransport();
            
            AuthorizationCodeFlow flow = new AuthorizationCodeFlow.Builder(
                    BearerToken.authorizationHeaderAccessMethod(),
                    httpTransport,
                    JSON_FACTORY,
                    TOKEN_SERVER_URL,
                    new ClientParametersAuthentication(config.getClientId(), config.getClientSecret()),
                    config.getClientId(),
                    AUTHORIZATION_SERVER_URL)
                    .setScopes(Collections.singletonList(CalendarScopes.CALENDAR))
                    .build();

            AuthorizationCodeRequestUrl authorizationUrl = flow.newAuthorizationUrl()
                    .setRedirectUri(config.getRedirectUri())
                    .setState(user.getId());

            return authorizationUrl.build();
        } catch (Exception e) {
            log.error("Error creating Google authorization URL", e);
            throw new BadRequestException("Failed to create Google authorization URL");
        }
    }

    @Override
    public void handleCallback(String code, User user) {
        try {
            HttpTransport httpTransport = GoogleNetHttpTransport.newTrustedTransport();
            
            AuthorizationCodeFlow flow = new AuthorizationCodeFlow.Builder(
                    BearerToken.authorizationHeaderAccessMethod(),
                    httpTransport,
                    JSON_FACTORY,
                    TOKEN_SERVER_URL,
                    new ClientParametersAuthentication(config.getClientId(), config.getClientSecret()),
                    config.getClientId(),
                    AUTHORIZATION_SERVER_URL)
                    .setScopes(Collections.singletonList(CalendarScopes.CALENDAR))
                    .build();

            TokenResponse response = flow.newTokenRequest(code)
                    .setRedirectUri(config.getRedirectUri())
                    .execute();

            user.setGoogleAccessToken(response.getAccessToken());
            user.setGoogleRefreshToken(response.getRefreshToken());
            
            if (response.getExpiresInSeconds() != null) {
                Instant expiryTime = Instant.now().plusSeconds(response.getExpiresInSeconds());
                user.setGoogleTokenExpiry(LocalDateTime.ofInstant(expiryTime, ZoneId.systemDefault()));
            }
            
            user.setGoogleCalendarEnabled(true);
            userRepository.save(user);
            
            log.info("Successfully connected Google Calendar for user: {}", user.getEmail());
        } catch (Exception e) {
            log.error("Error handling Google Calendar callback", e);
            throw new BadRequestException("Failed to connect Google Calendar");
        }
    }

    @Override
    public void disconnectGoogleCalendar(User user) {
        user.setGoogleAccessToken(null);
        user.setGoogleRefreshToken(null);
        user.setGoogleTokenExpiry(null);
        user.setGoogleCalendarEnabled(false);
        userRepository.save(user);
        
        log.info("Disconnected Google Calendar for user: {}", user.getEmail());
    }

    @Override
    public String createCalendarEvent(Event event, User user) {
        if (!isGoogleCalendarConnected(user)) {
            return null;
        }

        try {
            Calendar calendarService = getCalendarService(user);
            
            com.google.api.services.calendar.model.Event googleEvent = new com.google.api.services.calendar.model.Event()
                    .setSummary(event.getName())
                    .setDescription(event.getDescription())
                    .setLocation(event.getLocation());

            DateTime startDateTime = new DateTime(Date.from(event.getDate().atZone(ZoneId.systemDefault()).toInstant()));
            EventDateTime start = new EventDateTime()
                    .setDateTime(startDateTime)
                    .setTimeZone(ZoneId.systemDefault().getId());
            googleEvent.setStart(start);

            DateTime endDateTime = new DateTime(Date.from(event.getDate().plusHours(1).atZone(ZoneId.systemDefault()).toInstant()));
            EventDateTime end = new EventDateTime()
                    .setDateTime(endDateTime)
                    .setTimeZone(ZoneId.systemDefault().getId());
            googleEvent.setEnd(end);

            String extendedDescription = event.getDescription() != null ? event.getDescription() : "";
            extendedDescription += "\n\nRegistration deadline: " + 
                event.getRegistrationDeadline().format(DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm"));
            googleEvent.setDescription(extendedDescription);

            googleEvent = calendarService.events().insert("primary", googleEvent).execute();
            
            log.info("Created Google Calendar event: {} for user: {}", googleEvent.getId(), user.getEmail());
            return googleEvent.getId();
            
        } catch (Exception e) {
            log.error("Error creating Google Calendar event", e);
            return null;
        }
    }

    @Override
    public void deleteCalendarEvent(String googleEventId, User user) {
        if (!isGoogleCalendarConnected(user) || googleEventId == null) {
            return;
        }

        try {
            Calendar calendarService = getCalendarService(user);
            calendarService.events().delete("primary", googleEventId).execute();
            
            log.info("Deleted Google Calendar event: {} for user: {}", googleEventId, user.getEmail());
        } catch (Exception e) {
            log.error("Error deleting Google Calendar event: {}", googleEventId, e);
        }
    }

    @Override
    public boolean isGoogleCalendarConnected(User user) {
        return user.getGoogleCalendarEnabled() && 
               user.getGoogleAccessToken() != null && 
               (user.getGoogleTokenExpiry() == null || 
                user.getGoogleTokenExpiry().isAfter(LocalDateTime.now()));
    }

    private Calendar getCalendarService(User user) throws IOException, GeneralSecurityException {
        HttpTransport httpTransport = GoogleNetHttpTransport.newTrustedTransport();
        
        AccessToken accessToken = new AccessToken(user.getGoogleAccessToken(), 
            user.getGoogleTokenExpiry() != null ? 
                Date.from(user.getGoogleTokenExpiry().atZone(ZoneId.systemDefault()).toInstant()) : null);
        
        GoogleCredentials credentials = GoogleCredentials.create(accessToken);
        
        return new Calendar.Builder(httpTransport, JSON_FACTORY, new HttpCredentialsAdapter(credentials))
                .setApplicationName("Event Management System")
                .build();
    }
}
