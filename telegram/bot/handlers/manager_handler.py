from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from .base_handler import BaseHandler
from ..config import MANAGER_ROLE, CREATE_EVENT_NAME, CREATE_EVENT_DESC, CREATE_EVENT_DATE, CREATE_EVENT_LOCATION
from ..utils.logger import logger
from datetime import datetime, timedelta
import re


class ManagerHandler(BaseHandler):
    
    def __init__(self):
        super().__init__()
        self.event_creation_data = {}
        self.event_editing_data = {}
    
    async def manager_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "manager_help")
        
        if not await self.require_role(update, MANAGER_ROLE):
            return
        
        help_message = (
            "👔 <b>Manager Commands:</b>\n\n"
            "🏢 <b>Company Events</b> - View your company's events\n"
            "➕ <b>Create Event</b> - Create a new event\n"
            "📊 <b>Event Stats</b> - View event statistics\n"
            "❓ <b>Manager Help</b> - Show this help message\n\n"
            "<b>Text Commands:</b>\n"
            "/edit_event - Edit an existing event\n"
            "/delete_event &lt;event_id&gt; - Delete an event\n"
            "/event_participants &lt;event_id&gt; - View event participants\n\n"
            "<b>Tips:</b>\n"
            "• Use the buttons above for quick access\n"
            "• Event IDs can be found in the Company Events list\n"
            "• All dates should be in DD/MM/YYYY HH:MM format"
        )
        await update.message.reply_text(help_message, parse_mode='HTML')
    
    async def my_company_events(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "my_company_events")
        
        if not await self.require_role(update, MANAGER_ROLE):
            return
        
        user_id = update.effective_user.id
        events = self.api_service.get_company_events(user_id)
        
        if events is None:
            await update.message.reply_text(
                "❌ Failed to fetch company events. Please try again later."
            )
            return
        
        if not events:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Create First Event", callback_data="create_event")]
            ])
            await update.message.reply_text(
                "📅 Your company has no events yet.\n"
                "Click the button below to create your first event!",
                reply_markup=keyboard
            )
            return
        
        events_text = "📅 <b>Your Company's Events:</b>\n\n"
        keyboard = []
        
        for event in events[:10]:
            date_str = event.get('date', 'N/A')
            if date_str != 'N/A':
                try:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    date_str = date_obj.strftime('%d/%m/%Y %H:%M')
                except:
                    pass
            
            events_text += (
                f"🎯 <b>{event.get('name', 'N/A')}</b>\n"
                f"📅 {date_str}\n"
                f"📍 {event.get('location', 'N/A')}\n"
                f"� Participants: {len(event.get('registrations', []))}\n"
                f"🆔 <code>{event.get('id', 'N/A')}</code>\n\n"
            )

            keyboard.append([
                InlineKeyboardButton("👥 Participants", callback_data=f"participants_{event.get('id')}"),
                InlineKeyboardButton("✏️ Edit", callback_data=f"edit_event_{event.get('id')}"),
                InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_event_{event.get('id')}")
            ])
        
        keyboard.append([InlineKeyboardButton("➕ Create New Event", callback_data="create_event")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(events_text, parse_mode='HTML', reply_markup=reply_markup)
    
    async def create_event_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "create_event")
        
        if not await self.require_role(update, MANAGER_ROLE):
            return ConversationHandler.END
        
        user_id = update.effective_user.id
        
        if not hasattr(self, 'event_creation_data'):
            self.event_creation_data = {}
        self.event_creation_data[user_id] = {}
        
        logger.info(f"Starting event creation for user {user_id}")
        
        await update.message.reply_text(
            "➕ <b>Create New Event</b>\n\n"
            "Let's create a new event for your company!\n\n"
            "Please enter the <b>event name</b>:",
            parse_mode='HTML'
        )
        return CREATE_EVENT_NAME
    
    async def get_event_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        event_name = update.message.text.strip()
        
        logger.info(f"Received event name from user {user_id}: {event_name}")
        
        if len(event_name) > 255:
            await update.message.reply_text(
                "❌ Event name is too long (maximum 255 characters).\n"
                "Please enter a shorter event name:"
            )
            return CREATE_EVENT_NAME
        
        if not hasattr(self, 'event_creation_data') or user_id not in self.event_creation_data:
            await update.message.reply_text(
                "❌ Session expired. Please start over with /create_event"
            )
            return ConversationHandler.END
        
        self.event_creation_data[user_id]['name'] = event_name
        
        await update.message.reply_text(
            f"✅ Event name: <b>{event_name}</b>\n\n"
            "Now please enter the <b>event description</b> (or send 'skip' if no description needed):",
            parse_mode='HTML'
        )
        return CREATE_EVENT_DESC
    
    async def get_event_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        description = update.message.text.strip()
        
        logger.info(f"Received event description from user {user_id}: {description[:50]}...")
        
        if not hasattr(self, 'event_creation_data') or user_id not in self.event_creation_data:
            await update.message.reply_text(
                "❌ Session expired. Please start over with /create_event"
            )
            return ConversationHandler.END
        
        if description.lower() == 'skip':
            self.event_creation_data[user_id]['description'] = None
        else:
            if len(description) > 3000:
                await update.message.reply_text(
                    "❌ Description is too long (maximum 3000 characters).\n"
                    "Please enter a shorter description or send 'skip':"
                )
                return CREATE_EVENT_DESC
            self.event_creation_data[user_id]['description'] = description
        
        await update.message.reply_text(
            "📅 Please enter the <b>event date and time</b> in the format:\n"
            "<code>DD/MM/YYYY HH:MM</code>\n\n"
            "Example: <code>25/12/2024 14:30</code>",
            parse_mode='HTML'
        )
        return CREATE_EVENT_DATE
    
    async def get_event_date(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        date_str = update.message.text.strip()
        
        date_pattern = r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}$'
        if not re.match(date_pattern, date_str):
            await update.message.reply_text(
                "❌ Invalid date format. Please use: <code>DD/MM/YYYY HH:MM</code>\n"
                "Example: <code>25/12/2024 14:30</code>",
                parse_mode='HTML'
            )
            return CREATE_EVENT_DATE
        
        try:
            event_date = datetime.strptime(date_str, '%d/%m/%Y %H:%M')

            if event_date <= datetime.now():
                await update.message.reply_text(
                    "❌ Event date must be in the future.\n"
                    "Please enter a future date and time:"
                )
                return CREATE_EVENT_DATE
            
            self.event_creation_data[user_id]['date'] = event_date.isoformat()
            
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid date. Please enter a valid date in format: <code>DD/MM/YYYY HH:MM</code>",
                parse_mode='HTML'
            )
            return CREATE_EVENT_DATE
        
        await update.message.reply_text(
            f"✅ Event date: <b>{date_str}</b>\n\n"
            "Finally, please enter the <b>event location</b>:",
            parse_mode='HTML'
        )
        return CREATE_EVENT_LOCATION
    
    async def get_event_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        location = update.message.text.strip()
        
        if not location:
            await update.message.reply_text(
                "❌ Location cannot be empty. Please enter the event location:"
            )
            return CREATE_EVENT_LOCATION
        
        self.event_creation_data[user_id]['location'] = location
        
        event_data = self.event_creation_data[user_id]
        
        summary_text = (
            f"📋 <b>Event Summary:</b>\n\n"
            f"🎯 <b>Name:</b> {event_data['name']}\n"
            f"📝 <b>Description:</b> {event_data.get('description', 'None')}\n"
            f"📅 <b>Date:</b> {datetime.fromisoformat(event_data['date']).strftime('%d/%m/%Y %H:%M')}\n"
            f"📍 <b>Location:</b> {event_data['location']}\n\n"
            "Creating event..."
        )
        
        await update.message.reply_text(summary_text, parse_mode='HTML')
        
        success, message = self.api_service.create_event(user_id, event_data)
        
        if success:
            await update.message.reply_text(
                f"✅ <b>Event created successfully!</b>\n\n"
                f"Your event '{event_data['name']}' has been created and is now available for student registration.",
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                f"❌ <b>Failed to create event:</b>\n{message}\n\n"
                "Please try again with /create_event or use the Create Event button.",
                parse_mode='HTML'
            )
        
        if user_id in self.event_creation_data:
            del self.event_creation_data[user_id]
        
        return ConversationHandler.END
    
    async def cancel_event_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id in self.event_creation_data:
            del self.event_creation_data[user_id]
        
        await update.message.reply_text(
            "❌ Event creation cancelled.\n"
            "Use the ➕ Create Event button or /create_event to start over."
        )
        return ConversationHandler.END
    
    async def event_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "event_stats")
        
        if not await self.require_role(update, MANAGER_ROLE):
            return
        
        user_id = update.effective_user.id
        events = self.api_service.get_company_events(user_id)
        
        if events is None:
            await update.message.reply_text(
                "❌ Failed to fetch event statistics. Please try again later."
            )
            return
        
        if not events:
            await update.message.reply_text(
                "📊 No events to show statistics for.\n"
                "Create your first event to see stats!"
            )
            return
        
        total_events = len(events)
        total_participants = sum(len(event.get('registrations', [])) for event in events)

        most_popular = max(events, key=lambda e: len(e.get('registrations', [])), default=None)
        
        now = datetime.now()
        upcoming_events = []
        past_events = []
        
        for event in events:
            try:
                event_date = datetime.fromisoformat(event.get('date', '').replace('Z', '+00:00'))
                if event_date > now:
                    upcoming_events.append(event)
                else:
                    past_events.append(event)
            except:
                pass
        
        stats_text = (
            f"📊 <b>Event Statistics</b>\n\n"
            f"📈 <b>Overview:</b>\n"
            f"• Total Events: {total_events}\n"
            f"• Total Participants: {total_participants}\n"
            f"• Upcoming Events: {len(upcoming_events)}\n"
            f"• Past Events: {len(past_events)}\n\n"
        )
        
        if most_popular:
            participant_count = len(most_popular.get('registrations', []))
            stats_text += (
                f"🏆 <b>Most Popular Event:</b>\n"
                f"'{most_popular.get('name', 'N/A')}' with {participant_count} participants\n\n"
            )
        
        if upcoming_events:
            stats_text += f"📅 <b>Upcoming Events ({len(upcoming_events)}):</b>\n"
            for event in upcoming_events[:5]:
                try:
                    date_obj = datetime.fromisoformat(event.get('date', '').replace('Z', '+00:00'))
                    date_str = date_obj.strftime('%d/%m/%Y %H:%M')
                except:
                    date_str = 'Unknown date'
                
                stats_text += f"• {event.get('name', 'N/A')} - {date_str}\n"
        
        await update.message.reply_text(stats_text, parse_mode='HTML')
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        if not await self.require_role(update, MANAGER_ROLE):
            await query.edit_message_text("❌ This feature is only available for managers.")
            return
        
        if query.data == "create_event":
            await query.edit_message_text(
                "➕ <b>Create New Event</b>\n\n"
                "Starting event creation process...\n"
                "Please enter the event name:",
                parse_mode='HTML'
            )
            return
        
        elif query.data.startswith("participants_"):
            event_id = query.data.split("_", 1)[1]
            await self._show_event_participants_inline(query, event_id, user_id)
            
        elif query.data.startswith("edit_event_"):
            event_id = query.data.split("_", 2)[2]
            await self._show_event_edit_options(query, event_id, user_id)
            
        elif query.data.startswith("delete_event_"):
            event_id = query.data.split("_", 2)[2]
            await self._confirm_event_deletion(query, event_id, user_id)
            
        elif query.data.startswith("confirm_delete_"):
            event_id = query.data.split("_", 2)[2]
            await self._delete_event_confirmed(query, event_id, user_id)
            
        elif query.data == "cancel_delete":
            await query.edit_message_text(
                "❌ <b>Deletion Cancelled</b>\n\n"
                "The event was not deleted.",
                parse_mode='HTML'
            )
            
    async def _show_event_participants_inline(self, query, event_id, user_id):
        participants = self.api_service.get_event_participants(user_id, event_id)
        
        if participants is None:
            await query.edit_message_text(
                "❌ Failed to fetch event participants. Event may not exist or you may not have permission."
            )
            return
        
        if not participants:
            await query.edit_message_text("👥 No participants registered for this event yet.")
            return
        
        participants_text = f"👥 <b>Event Participants ({len(participants)}):</b>\n\n"
        for i, participant in enumerate(participants[:20], 1):
            participants_text += (
                f"{i}. <b>{participant.get('fullName', 'N/A')}</b>\n"
                f"📧 {participant.get('email', 'N/A')}\n"
                f"👤 {participant.get('role', 'N/A')}"
            )
            
            if participant.get('group'):
                participants_text += f" - Group: {participant['group']}\n"
            elif participant.get('company'):
                participants_text += f" - Company: {participant['company']}\n"
            else:
                participants_text += "\n"
            participants_text += "\n"
        
        if len(participants) > 20:
            participants_text += f"... and {len(participants) - 20} more participants"
        
        await query.edit_message_text(participants_text, parse_mode='HTML')
    
    async def _show_event_edit_options(self, query, event_id, user_id):
        await query.edit_message_text(
            f"✏️ <b>Edit Event</b>\n\n"
            f"Event ID: <code>{event_id}</code>\n\n"
            "Event editing via buttons is not implemented yet.\n"
            "Please use the command: <code>/edit_event</code>",
            parse_mode='HTML'
        )
    
    async def _confirm_event_deletion(self, query, event_id, user_id):
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes, Delete", callback_data=f"confirm_delete_{event_id}"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_delete")
            ]
        ])
        
        await query.edit_message_text(
            f"🗑️ <b>Delete Event</b>\n\n"
            f"Are you sure you want to delete this event?\n"
            f"Event ID: <code>{event_id}</code>\n\n"
            f"⚠️ <b>This action cannot be undone!</b>\n"
            f"All participant registrations will be lost.",
            parse_mode='HTML',
            reply_markup=keyboard
        )
    
    async def _delete_event_confirmed(self, query, event_id, user_id):
        success, message = self.api_service.delete_event(user_id, event_id)
        
        if success:
            await query.edit_message_text(
                f"✅ <b>Event Deleted</b>\n\n"
                f"The event has been successfully deleted.\n"
                f"{message}",
                parse_mode='HTML'
            )
        else:
            await query.edit_message_text(
                f"❌ <b>Deletion Failed</b>\n\n"
                f"Failed to delete the event:\n{message}",
                parse_mode='HTML'
            )
    
    async def edit_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "edit_event")
        
        if not await self.require_role(update, MANAGER_ROLE):
            return
        
        # TODO: Implement event editing conversation
        await update.message.reply_text("🚧 Event editing feature will be implemented soon!")
    
    async def delete_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "delete_event")
        
        if not await self.require_role(update, MANAGER_ROLE):
            return
        
        command_parts = update.message.text.split()
        if len(command_parts) < 2:
            await update.message.reply_text(
                "❌ Please provide an event ID.\n"
                "Usage: <code>/delete_event &lt;event_id&gt;</code>\n\n"
                "Use /my_company_events to see your events and their IDs.",
                parse_mode='HTML'
            )
            return
        
        event_id = command_parts[1]
        user_id = update.effective_user.id
        
        success, message = self.api_service.delete_event(user_id, event_id)
        
        if success:
            await update.message.reply_text(f"✅ {message}")
        else:
            await update.message.reply_text(f"❌ {message}")
    
    async def event_participants(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "event_participants")
        
        if not await self.require_role(update, MANAGER_ROLE):
            return
        
        command_parts = update.message.text.split()
        if len(command_parts) < 2:
            await update.message.reply_text(
                "❌ Please provide an event ID.\n"
                "Usage: <code>/event_participants &lt;event_id&gt;</code>\n\n"
                "Use /my_company_events to see your events and their IDs.",
                parse_mode='HTML'
            )
            return
        
        event_id = command_parts[1]
        user_id = update.effective_user.id
        
        participants = self.api_service.get_event_participants(user_id, event_id)
        
        if participants is None:
            await update.message.reply_text(
                "❌ Failed to fetch event participants. Please check the event ID and try again."
            )
            return
        
        if not participants:
            await update.message.reply_text(
                "� No participants registered for this event yet."
            )
            return
        
        participants_text = f"👥 <b>Event Participants ({len(participants)}):</b>\n\n"
        for i, participant in enumerate(participants, 1):
            participants_text += (
                f"{i}. <b>{participant.get('fullName', 'N/A')}</b>\n"
                f"📧 Email: {participant.get('email', 'N/A')}\n"
                f"👤 Role: {participant.get('role', 'N/A')}\n"
                f"🏫 Group/Company: {participant.get('group') or participant.get('company', 'N/A')}\n\n"
            )
        
        await update.message.reply_text(participants_text, parse_mode='HTML')

    async def cancel_event_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        logger.info(f"User {update.effective_user.id} cancelled event creation")
        
        if 'event_data' in context.user_data:
            del context.user_data['event_data']
        
        await update.message.reply_text(
            "Event creation cancelled. You can start again with /create_event whenever you're ready.",
            reply_markup=self.general_handler.get_role_keyboard(update.effective_user)
        )
        return ConversationHandler.END
