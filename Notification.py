from ampalibe import Model
from datetime import datetime

class NotificationModel(Model):
    def __init__ (self, cycle_id, notification_date, zone_type, sent):
        super().__init__()
        self.cycle_id = cycle_id
        self.notification_date = notification_date
        self.zone_type = zone_type
        self.sent = sent
        self.created_at = datetime.now()

