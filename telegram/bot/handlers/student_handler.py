from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .base_handler import BaseHandler
from ..config import STUDENT_ROLE
from ..utils.logger import logger
from datetime import datetime


class StudentHandler(BaseHandler):
    async def student_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "student_help")
        
        if not await self.require_authentication(update):
            return
        
        if not await self.require_role(update, STUDENT_ROLE):
            return
        
        help_message = (
            "📚 <b>Student Commands:</b>\n\n"
            "📚 <b>My Events</b> - View your registered events\n"
            "🔍 <b>Find Events</b> - Search for events\n"
            "📅 <b>Available Events</b> - View all available events\n"
            "❓ <b>Student Help</b> - Show this help message\n\n"
            "<b>Text Commands:</b>\n"
            "/register_event &lt;event_id&gt; - Register for an event\n"
            "/unregister_event &lt;event_id&gt; - Unregister from an event\n\n"
            "<b>Tips:</b>\n"
            "• Use the buttons above for quick access\n"
            "• Event IDs can be found in the Available Events list\n"
            "• You can register/unregister directly from event lists"
        )
        await update.message.reply_text(help_message, parse_mode='HTML')
    
    async def my_events(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "my_events")
        
        if not await self.require_authentication(update):
            return
        
        if not await self.require_role(update, STUDENT_ROLE):
            return
        
        user_id = update.effective_user.id
        events = self.api_service.get_student_events(user_id)
        
        if events is None:
            await update.message.reply_text(
                "❌ Failed to fetch your events. Please try again later."
            )
            return
        
        if not events:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔍 Find Events", callback_data="find_events")]
            ])
            await update.message.reply_text(
                "📅 You haven't registered for any events yet.\n"
                "Click the button below to find events you can join!",
                reply_markup=keyboard
            )
            return
        
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
                upcoming_events.append(event)
        
        events_text = "📚 <b>Your Events</b>\n\n"
        keyboard = []
        
        if upcoming_events:
            events_text += "🔜 <b>Upcoming Events:</b>\n\n"
            
            for event in upcoming_events:
                date_str = self._format_event_date(event.get('date', ''))
                event_id = event.get('id', '')
                
                events_text += (
                    f"🎯 <b>{event.get('name', 'N/A')}</b>\n"
                    f"📅 {date_str}\n"
                    f"📍 {event.get('location', 'N/A')}\n"
                    f"📝 {event.get('description', 'No description')[:100]}{'...' if len(event.get('description', '')) > 100 else ''}\n"
                    f"👥 {len(event.get('registrations', []))} participants\n"
                    f"🆔 <code>{event_id}</code>\n\n"
                )
                
                keyboard.append([
                    InlineKeyboardButton("❌ Unregister", callback_data=f"unregister_{event_id}")
                ])
        
        if past_events:
            events_text += "📚 <b>Past Events:</b>\n\n"
            
            for event in past_events[:5]:
                date_str = self._format_event_date(event.get('date', ''))
                
                events_text += (
                    f"🎯 <b>{event.get('name', 'N/A')}</b>\n"
                    f"📅 {date_str}\n"
                    f"📍 {event.get('location', 'N/A')}\n"
                    f"✅ Attended\n\n"
                )
        
        keyboard.append([InlineKeyboardButton("🔍 Find More Events", callback_data="find_events")])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        await update.message.reply_text(events_text, parse_mode='HTML', reply_markup=reply_markup)

    async def available_events(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "available_events")
        
        if not await self.require_authentication(update):
            return
        
        if not await self.require_role(update, STUDENT_ROLE):
            return
        
        user_id = update.effective_user.id
        all_events = self.api_service.get_all_events(user_id)
        student_events = self.api_service.get_student_events(user_id) or []
        
        if all_events is None:
            await update.message.reply_text(
                "❌ Failed to fetch events. Please try again later."
            )
            return
        
        if not all_events:
            await update.message.reply_text(
                "📅 No events are currently available."
            )
            return
        
        registered_event_ids = {event.get('id') for event in student_events}
        
        now = datetime.now()
        upcoming_events = []
        past_events = []
        
        for event in all_events:
            try:
                event_date = datetime.fromisoformat(event.get('date', '').replace('Z', '+00:00'))
                if event_date > now:
                    upcoming_events.append(event)
                else:
                    past_events.append(event)
            except:
                upcoming_events.append(event)
        
        upcoming_events.sort(key=lambda x: x.get('date', ''))
        past_events.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        events_text = "📅 <b>All Events</b>\n\n"
        keyboard = []
        
        if upcoming_events:
            events_text += "🔜 <b>Upcoming Events:</b>\n\n"
            
            for event in upcoming_events[:8]:
                date_str = self._format_event_date(event.get('date', ''))
                event_id = event.get('id', '')
                is_registered = event_id in registered_event_ids
                
                status = "✅ Registered" if is_registered else "📝 Available"
                participant_count = len(event.get('registrations', []))
                
                events_text += (
                    f"🎯 <b>{event.get('name', 'N/A')}</b>\n"
                    f"📅 {date_str}\n"
                    f"📍 {event.get('location', 'N/A')}\n"
                    f"👥 {participant_count} participants\n"
                    f"📝 {event.get('description', 'No description')[:100]}{'...' if len(event.get('description', '')) > 100 else ''}\n"
                    f"📊 Status: {status}\n"
                    f"🆔 <code>{event_id}</code>\n\n"
                )
                
                if is_registered:
                    keyboard.append([
                        InlineKeyboardButton("❌ Unregister", callback_data=f"unregister_{event_id}")
                    ])
                else:
                    keyboard.append([
                        InlineKeyboardButton("✅ Register", callback_data=f"register_{event_id}")
                    ])
        
        if past_events:
            events_text += "\n📚 <b>Past Events:</b>\n\n"
            
            for event in past_events[:5]:
                date_str = self._format_event_date(event.get('date', ''))
                event_id = event.get('id', '')
                is_registered = event_id in registered_event_ids
                participant_count = len(event.get('registrations', []))
                
                status = "✅ Attended" if is_registered else "❌ Not attended"
                
                events_text += (
                    f"🎯 <b>{event.get('name', 'N/A')}</b>\n"
                    f"📅 {date_str}\n"
                    f"📍 {event.get('location', 'N/A')}\n"
                    f"👥 {participant_count} participants\n"
                    f"📊 {status}\n\n"
                )
        
        keyboard.append([InlineKeyboardButton("🔄 Refresh Events", callback_data="refresh_events")])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        if len(events_text) > 4000:
            upcoming_text = events_text.split("📚 <b>Past Events:</b>")[0]
            await update.message.reply_text(upcoming_text, parse_mode='HTML', reply_markup=reply_markup)
            
            if "📚 <b>Past Events:</b>" in events_text:
                past_text = "📚 <b>Past Events:</b>" + events_text.split("📚 <b>Past Events:</b>")[1]
                await update.message.reply_text(past_text, parse_mode='HTML')
        else:
            await update.message.reply_text(events_text, parse_mode='HTML', reply_markup=reply_markup)

    def _format_event_date(self, date_str: str) -> str:
        if not date_str or date_str == 'N/A':
            return 'N/A'
        
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.strftime('%d/%m/%Y %H:%M')
        except:
            return date_str

    async def find_events(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.available_events(update, context)

    async def register_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "register_event")
        
        if not await self.require_authentication(update):
            return
        
        if not await self.require_role(update, STUDENT_ROLE):
            return
        
        command_parts = update.message.text.split()
        if len(command_parts) < 2:
            await update.message.reply_text(
                "❌ Please provide an event ID.\n"
                "Usage: <code>/register_event &lt;event_id&gt;</code>\n\n"
                "You can find event IDs in the Available Events list.",
                parse_mode='HTML'
            )
            return
        
        event_id = command_parts[1]
        user_id = update.effective_user.id
        
        success, message = self.api_service.register_for_event(user_id, event_id)
        
        if success:
            await update.message.reply_text(
                f"✅ <b>Registration Successful!</b>\n\n"
                f"You have been registered for the event.\n"
                f"Event ID: <code>{event_id}</code>\n\n"
                f"Use /my_events to see all your registered events.",
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                f"❌ <b>Registration Failed:</b>\n{message}\n\n"
                f"Please check the event ID and try again.",
                parse_mode='HTML'
            )

    async def unregister_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "unregister_event")
        
        if not await self.require_authentication(update):
            return
        
        if not await self.require_role(update, STUDENT_ROLE):
            return
        
        command_parts = update.message.text.split()
        if len(command_parts) < 2:
            await update.message.reply_text(
                "❌ Please provide an event ID.\n"
                "Usage: <code>/unregister_event &lt;event_id&gt;</code>\n\n"
                "You can find event IDs in your registered events list.",
                parse_mode='HTML'
            )
            return
        
        event_id = command_parts[1]
        user_id = update.effective_user.id
        
        success, message = self.api_service.unregister_from_event(user_id, event_id)
        
        if success:
            await update.message.reply_text(
                f"✅ <b>Unregistration Successful!</b>\n\n"
                f"You have been unregistered from the event.\n"
                f"Event ID: <code>{event_id}</code>\n\n"
                f"Use /my_events to see your remaining registered events.",
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                f"❌ <b>Unregistration Failed:</b>\n{message}\n\n"
                f"Please check the event ID and try again.",
                parse_mode='HTML'
            )

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        if not await self.require_role(update, STUDENT_ROLE):
            await query.edit_message_text("❌ This feature is only available for students.")
            return
        
        if query.data == "find_events" or query.data == "refresh_events":
            await self._send_available_events(query, user_id)
            
        elif query.data.startswith("register_"):
            event_id = query.data.split("_", 1)[1]
            await self._handle_event_registration(query, event_id, user_id)
            
        elif query.data.startswith("unregister_"):
            event_id = query.data.split("_", 1)[1]
            await self._handle_event_unregistration(query, event_id, user_id)

    async def _send_available_events(self, query, user_id):
        all_events = self.api_service.get_all_events(user_id)
        student_events = self.api_service.get_student_events(user_id) or []
        
        if all_events is None:
            await query.edit_message_text("❌ Failed to fetch events. Please try again later.")
            return
        
        if not all_events:
            await query.edit_message_text("📅 No events are currently available.")
            return
        
        registered_event_ids = {event.get('id') for event in student_events}
        
        now = datetime.now()
        upcoming_events = []
        
        for event in all_events:
            try:
                event_date = datetime.fromisoformat(event.get('date', '').replace('Z', '+00:00'))
                if event_date > now:
                    upcoming_events.append(event)
            except:
                upcoming_events.append(event)
        
        if not upcoming_events:
            await query.edit_message_text("📅 No upcoming events available for registration.")
            return
        
        upcoming_events.sort(key=lambda x: x.get('date', ''))
        
        events_text = "🔜 <b>Upcoming Events:</b>\n\n"
        keyboard = []
        
        for event in upcoming_events[:6]:  # Limit to 6 for inline
            date_str = self._format_event_date(event.get('date', ''))
            event_id = event.get('id', '')
            is_registered = event_id in registered_event_ids
            
            status = "✅ Registered" if is_registered else "📝 Available"
            participant_count = len(event.get('registrations', []))
            
            events_text += (
                f"🎯 <b>{event.get('name', 'N/A')}</b>\n"
                f"📅 {date_str}\n"
                f"📍 {event.get('location', 'N/A')}\n"
                f"👥 {participant_count} participants\n"
                f"📊 {status}\n\n"
            )

            if is_registered:
                keyboard.append([
                    InlineKeyboardButton("❌ Unregister", callback_data=f"unregister_{event_id}")
                ])
            else:
                keyboard.append([
                    InlineKeyboardButton("✅ Register", callback_data=f"register_{event_id}")
                ])
        
        keyboard.append([InlineKeyboardButton("🔄 Refresh", callback_data="refresh_events")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(events_text, parse_mode='HTML', reply_markup=reply_markup)

    async def _handle_event_registration(self, query, event_id, user_id):
        success, message = self.api_service.register_for_event(user_id, event_id)
        
        if success:
            await query.edit_message_text(
                f"✅ <b>Registration Successful!</b>\n\n"
                f"You have been registered for the event.\n\n"
                f"Use the buttons below to manage your events:",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📚 My Events", callback_data="find_events")],
                    [InlineKeyboardButton("🔍 Find More Events", callback_data="refresh_events")]
                ])
            )
        else:
            await query.edit_message_text(
                f"❌ <b>Registration Failed:</b>\n{message}",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Try Again", callback_data="refresh_events")]
                ])
            )

    async def _handle_event_unregistration(self, query, event_id, user_id):
        success, message = self.api_service.unregister_from_event(user_id, event_id)
        
        if success:
            await query.edit_message_text(
                f"✅ <b>Unregistration Successful!</b>\n\n"
                f"You have been unregistered from the event.\n\n"
                f"Use the buttons below to manage your events:",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📚 My Events", callback_data="find_events")],
                    [InlineKeyboardButton("🔍 Find More Events", callback_data="refresh_events")]
                ])
            )
        else:
            await query.edit_message_text(
                f"❌ <b>Unregistration Failed:</b>\n{message}",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Try Again", callback_data="refresh_events")]
                ])
            )
