from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler
from .config import (BOT_TOKEN, SURNAME, NAME, PATRONYMIC, ROLE, GROUP_OR_COMPANY, 
                    CREATE_EVENT_NAME, CREATE_EVENT_DESC, CREATE_EVENT_DATE, CREATE_EVENT_LOCATION,
                    EDIT_EVENT_SELECT, EDIT_EVENT_FIELD, EDIT_EVENT_VALUE)
from .handlers.general_handler import GeneralHandler
from .handlers.registration_handler import RegistrationHandler
from .handlers.student_handler import StudentHandler
from .handlers.manager_handler import ManagerHandler
from .utils.logger import logger


class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        self.general_handler = GeneralHandler()
        self.registration_handler = RegistrationHandler()
        self.student_handler = StudentHandler()
        self.manager_handler = ManagerHandler()
        
        self.setup_handlers()
    
    def setup_handlers(self):
        registration_conversation = ConversationHandler(
            entry_points=[CommandHandler('register', self.registration_handler.start_registration)],
            states={
                SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.registration_handler.get_surname)],
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.registration_handler.get_name)],
                PATRONYMIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.registration_handler.get_patronymic)],
                ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.registration_handler.get_role)],
                GROUP_OR_COMPANY: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.registration_handler.get_group_or_company),
                    CallbackQueryHandler(self.registration_handler.handle_company_selection, pattern=r'^(company_|page_|noop)')
                ],
            },
            fallbacks=[CommandHandler('cancel', self.registration_handler.cancel_registration)],
            per_user=True,
            per_chat=True,
            name="registration"
        )
        
        event_creation_conversation = ConversationHandler(
            entry_points=[CommandHandler('create_event', self.manager_handler.create_event_start)],
            states={
                CREATE_EVENT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.manager_handler.get_event_name)],
                CREATE_EVENT_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.manager_handler.get_event_description)],
                CREATE_EVENT_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.manager_handler.get_event_date)],
                CREATE_EVENT_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.manager_handler.get_event_location)],
            },
            fallbacks=[CommandHandler('cancel', self.manager_handler.cancel_event_creation)],
            per_user=True,
            per_chat=True,
            name="event_creation"
        )

        event_editing_conversation = ConversationHandler(
            entry_points=[CommandHandler('edit_event', self.manager_handler.edit_event)],
            states={
                EDIT_EVENT_SELECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.manager_handler.get_edit_event_selection)],
                EDIT_EVENT_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.manager_handler.get_edit_field)],
                EDIT_EVENT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.manager_handler.get_edit_value)],
            },
            fallbacks=[CommandHandler('cancel', self.manager_handler.cancel_event_editing)],
            per_user=True,
            per_chat=True,
            name="event_editing"
        )
        
        self.application.add_handler(CommandHandler("start", self.general_handler.start_command))
        self.application.add_handler(CommandHandler("help", self.general_handler.help_command))
        self.application.add_handler(CommandHandler("status", self.general_handler.status_command))
        self.application.add_handler(CommandHandler("backend_health", self.general_handler.backend_health_command))
        
        self.application.add_handler(registration_conversation)
        self.application.add_handler(event_creation_conversation)
        self.application.add_handler(event_editing_conversation)
        
        self.application.add_handler(CommandHandler("student_help", self.student_handler.student_help))
        self.application.add_handler(CommandHandler("my_events", self.student_handler.my_events))
        self.application.add_handler(CommandHandler("available_events", self.student_handler.available_events))
        self.application.add_handler(CommandHandler("find_events", self.student_handler.find_events))
        self.application.add_handler(CommandHandler("register_event", self.student_handler.register_event))
        self.application.add_handler(CommandHandler("unregister_event", self.student_handler.unregister_event))

        self.application.add_handler(CommandHandler("manager_help", self.manager_handler.manager_help))
        self.application.add_handler(CommandHandler("my_company_events", self.manager_handler.my_company_events))
        self.application.add_handler(CommandHandler("event_stats", self.manager_handler.event_stats))
        self.application.add_handler(CommandHandler("delete_event", self.manager_handler.delete_event))
        self.application.add_handler(CommandHandler("event_participants", self.manager_handler.event_participants))
        
        self.application.add_handler(CallbackQueryHandler(
            self.manager_handler.handle_callback_query, 
            pattern=r'^(create_event|participants_|edit_event_|delete_event_|confirm_delete_|cancel_delete)'
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.student_handler.handle_callback_query, 
            pattern=r'^(find_events|register_|unregister_|refresh_events)'
        ))
        
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.general_handler.handle_message))

        self.application.add_error_handler(self.error_handler)
    
    async def error_handler(self, update, context):
        logger.error(f"Update {update} caused error {context.error}")
    
    def run(self):
        logger.info("Starting Telegram Bot...")
        self.application.run_polling()
