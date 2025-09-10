from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .base_handler import BaseHandler
from ..config import STUDENT_ROLE
from ..utils.logger import logger
from datetime import datetime


class StudentHandler(BaseHandler):
    async def student_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "student_help")
        
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
                "Click the button below to find events you can register for!",
                reply_markup=keyboard
            )
            return
        
        events_text = "📅 <b>Your Registered Events:</b>\n\n"
        keyboard = []
        
        for event in events:
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
                f"🆔 <code>{event.get('id', 'N/A')}</code>\n\n"
            )
            
            keyboard.append([
                InlineKeyboardButton(
                    f"❌ Leave '{event.get('name', 'Event')[:20]}...'", 
                    callback_data=f"unregister_{event.get('id')}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("🔍 Find More Events", callback_data="find_events")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(events_text, parse_mode='HTML', reply_markup=reply_markup)
    
    async def available_events(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "available_events")
        
        if not await self.require_role(update, STUDENT_ROLE):
            return
        
        user_id = update.effective_user.id
        events = self.api_service.get_available_events(user_id)
        
        if events is None:
            await update.message.reply_text(
                "❌ Failed to fetch available events. Please try again later."
            )
            return
        
        if not events:
            await update.message.reply_text(
                "📅 No events available for registration at the moment."
            )
            return
        
        events_text = "📅 <b>Available Events for Registration:</b>\n\n"
        keyboard = []
        
        for event in events[:10]:
            date_str = event.get('date', 'N/A')
            if date_str != 'N/A':
                try:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    date_str = date_obj.strftime('%d/%m/%Y %H:%M')
                    
                    if date_obj < datetime.now():
                        status = "🔒 Past"
                    else:
                        status = "✅ Available"
                except:
                    status = "❓ Unknown"
            else:
                status = "❓ Unknown"
            
            events_text += (
                f"🎯 <b>{event.get('name', 'N/A')}</b>\n"
                f"📅 {date_str} ({status})\n"
                f"📍 {event.get('location', 'N/A')}\n"
                f"� {event.get('description', 'N/A')[:100]}{'...' if len(event.get('description', '')) > 100 else ''}\n"
                f"� Registrations: {len(event.get('registrations', []))}\n"
                f"🆔 <code>{event.get('id', 'N/A')}</code>\n\n"
            )
            
            if status != "� Past":
                keyboard.append([
                    InlineKeyboardButton(
                        f"✅ Join '{event.get('name', 'Event')[:20]}...'", 
                        callback_data=f"register_{event.get('id')}"
                    )
                ])
        
        if len(events) > 10:
            events_text += f"... and {len(events) - 10} more events available"
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        await update.message.reply_text(events_text, parse_mode='HTML', reply_markup=reply_markup)
    
    async def find_events(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Find events with search functionality"""
        await self.log_command_usage(update, "find_events")
        
        if not await self.require_role(update, STUDENT_ROLE):
            return
        
        await self.available_events(update, context)
    
    async def register_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Register for an event"""
        await self.log_command_usage(update, "register_event")
        
        if not await self.require_role(update, STUDENT_ROLE):
            return
        
        command_parts = update.message.text.split()
        if len(command_parts) < 2:
            await update.message.reply_text(
                "❌ Please provide an event ID.\n"
                "Usage: <code>/register_event &lt;event_id&gt;</code>\n\n"
                "Use /available_events to see available events and their IDs.",
                parse_mode='HTML'
            )
            return
        
        event_id = command_parts[1]
        user_id = update.effective_user.id
        
        success, message = self.api_service.register_for_event(user_id, event_id)
        
        if success:
            await update.message.reply_text(f"✅ {message}")
        else:
            await update.message.reply_text(f"❌ {message}")
    
    async def unregister_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "unregister_event")
        
        if not await self.require_role(update, STUDENT_ROLE):
            return
        
        command_parts = update.message.text.split()
        if len(command_parts) < 2:
            await update.message.reply_text(
                "❌ Please provide an event ID.\n"
                "Usage: <code>/unregister_event &lt;event_id&gt;</code>\n\n"
                "Use /my_events to see your registered events and their IDs.",
                parse_mode='HTML'
            )
            return
        
        event_id = command_parts[1]
        user_id = update.effective_user.id
        
        success, message = self.api_service.unregister_from_event(user_id, event_id)
        
        if success:
            await update.message.reply_text(f"✅ {message}")
        else:
            await update.message.reply_text(f"❌ {message}")
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        if not await self.require_role(update, STUDENT_ROLE):
            await query.edit_message_text("❌ This feature is only available for students.")
            return
        
        if query.data == "find_events":
            await query.edit_message_text(
                "🔍 <b>Finding Events...</b>\n\n"
                "Loading available events for you...",
                parse_mode='HTML'
            )
            await self.available_events(update, context)
            return
        
        elif query.data.startswith("register_"):
            event_id = query.data.split("_", 1)[1]
            await self._register_event_inline(query, event_id, user_id)
            
        elif query.data.startswith("unregister_"):
            event_id = query.data.split("_", 1)[1]
            await self._unregister_event_inline(query, event_id, user_id)
    
    async def _register_event_inline(self, query, event_id, user_id):
        success, message = self.api_service.register_for_event(user_id, event_id)
        
        if success:
            await query.edit_message_text(
                f"✅ <b>Successfully Registered!</b>\n\n"
                f"You have been registered for the event.\n"
                f"Event ID: <code>{event_id}</code>\n\n"
                f"Use the 📚 My Events button to see all your registered events.",
                parse_mode='HTML'
            )
        else:
            await query.edit_message_text(
                f"❌ <b>Registration Failed</b>\n\n"
                f"Failed to register for the event:\n{message}\n\n"
                f"Event ID: <code>{event_id}</code>",
                parse_mode='HTML'
            )
    
    async def _unregister_event_inline(self, query, event_id, user_id):
        success, message = self.api_service.unregister_from_event(user_id, event_id)
        
        if success:
            await query.edit_message_text(
                f"✅ <b>Successfully Unregistered</b>\n\n"
                f"You have been unregistered from the event.\n"
                f"Event ID: <code>{event_id}</code>\n\n"
                f"Use the 📚 My Events button to see your remaining events.",
                parse_mode='HTML'
            )
        else:
            await query.edit_message_text(
                f"❌ <b>Unregistration Failed</b>\n\n"
                f"Failed to unregister from the event:\n{message}\n\n"
                f"Event ID: <code>{event_id}</code>",
                parse_mode='HTML'
            )
