package com.hits.randomtask.services.impl;

import com.hits.randomtask.entities.User;
import com.hits.randomtask.services.TelegramNotificationService;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class TelegramNotificationServiceImpl implements TelegramNotificationService {

    private static final Logger logger = LoggerFactory.getLogger(TelegramNotificationServiceImpl.class);

    @Value("${telegram.bot.token}")
    private String telegramBotToken;

    private final RestTemplate restTemplate = new RestTemplate();

    @Override
    public void sendApprovalNotification(User user) {
        if (user.getTelegramChatId() == null) {
            logger.warn("Cannot send approval notification to user {}: no Telegram chat ID", user.getId());
            return;
        }

        String message = String.format(
            "*Congratulations!*\n\n" +
            "Your account has been *approved* by the administrator.\n" +
            "You can now access all features of the Event Management System.\n\n" +
            "Welcome aboard, %s!",
            user.getName().getName()
        );

        sendTelegramMessage(user.getTelegramChatId(), message);
    }

    @Override
    public void sendDeclineNotification(User user, String reason) {
        if (user.getTelegramChatId() == null) {
            logger.warn("Cannot send decline notification to user {}: no Telegram chat ID", user.getId());
            return;
        }

        String message = String.format(
            "❌ *Account Application Update*\n\n" +
            "Unfortunately, your account application has been *declined* by the administrator.\n\n" +
            "%s" +
            "\nIf you believe this is an error or have any questions, please contact the administrator.",
            reason != null && !reason.trim().isEmpty() 
                ? "**Reason:** " + reason + "\n\n"
                : ""
        );

        sendTelegramMessage(user.getTelegramChatId(), message);
    }

    private void sendTelegramMessage(Long chatId, String text) {
        try {
            String url = String.format("https://api.telegram.org/bot%s/sendMessage", telegramBotToken);
            
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("chat_id", chatId);
            requestBody.put("text", text);
            requestBody.put("parse_mode", "Markdown");
            requestBody.put("disable_web_page_preview", true);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);

            ResponseEntity<String> response = restTemplate.postForEntity(url, request, String.class);

            if (response.getStatusCode().is2xxSuccessful()) {
                logger.info("Successfully sent Telegram notification to chat ID: {}", chatId);
            } else {
                logger.error("Failed to send Telegram notification. Status: {}, Response: {}", 
                           response.getStatusCode(), response.getBody());
            }

        } catch (Exception e) {
            logger.error("Error sending Telegram notification to chat ID {}: {}", chatId, e.getMessage(), e);
        }
    }
}
