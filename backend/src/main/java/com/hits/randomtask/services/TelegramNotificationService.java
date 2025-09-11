package com.hits.randomtask.services;

import com.hits.randomtask.entities.User;

public interface TelegramNotificationService {
    void sendApprovalNotification(User user);
    void sendDeclineNotification(User user, String reason);
}
