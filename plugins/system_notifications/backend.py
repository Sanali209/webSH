import logging
import asyncio
from typing import Optional
from core.sdk import PluginBase, PluginContext
from core.events import event_bus
from plugins.system_notifications.config import NotificationSettings

logger = logging.getLogger(__name__)

class NotificationManager(PluginBase):
    def on_load(self, context: PluginContext):
        self.context = context
        self.settings = NotificationSettings()
        logger.info("NotificationManager loaded")

    def on_activate(self):
        logger.info("NotificationManager activated")

    def on_deactivate(self):
        logger.info("NotificationManager deactivated")

    async def send(self, message: str, severity: str = "info"):
        """
        Sends a notification to both desktop (OS) and frontend (Toast).
        """
        if not self.settings.enabled:
            return

        logger.info(f"Notification [{severity}]: {message}")

        # 1. Emit event for Frontend Toast
        await event_bus.publish("notification:new", {
            "message": message,
            "severity": severity,
            "timeout": self.settings.timeout
        })

        # 2. Desktop Notification (OS level)
        try:
            # Import here to avoid hard dependency if not installed
            from desktop_notifier import DesktopNotifier, Urgency, Button

            urgency_map = {
                "info": Urgency.Low,
                "warning": Urgency.Normal,
                "error": Urgency.Critical
            }

            notifier = DesktopNotifier()
            await notifier.send(
                title="PC Center",
                message=message,
                urgency=urgency_map.get(severity, Urgency.Normal)
            )
        except ImportError:
            logger.warning("desktop-notifier not installed. Skipping OS notification.")
        except Exception as e:
            logger.error(f"Failed to send desktop notification: {e}")
