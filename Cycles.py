from ampalibe import Model
from datetime import datetime

class CyclesModel(Model):
    def __init__(self, user_id, start_date, duration, next_ovulation, next_period, fin_regle):
        super().__init__()
        self.user_id = user_id
        self.start_date = start_date
        self.duration = duration
        self.next_ovulation = next_ovulation
        self.next_periode = next_period
        self.fin_regle = fin_regle
        self.created_at = datetime.now()