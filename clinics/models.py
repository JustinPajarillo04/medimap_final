from django.db import models
from django.utils import timezone


class Clinic(models.Model):
    name = models.CharField(max_length=150)
    address = models.TextField()
    contact = models.CharField(max_length=50, blank=True, null=True)
    hours = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, default="Open Now")
    services = models.TextField(blank=True, null=True)
    rating = models.FloatField(default=5.0)
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    # New time fields for automatic status computation
    open_time = models.TimeField(blank=True, null=True)
    close_time = models.TimeField(blank=True, null=True)
    
    # Weekday availability
    open_monday = models.BooleanField(default=True)
    open_tuesday = models.BooleanField(default=True)
    open_wednesday = models.BooleanField(default=True)
    open_thursday = models.BooleanField(default=True)
    open_friday = models.BooleanField(default=True)
    open_saturday = models.BooleanField(default=True)
    open_sunday = models.BooleanField(default=True)

    @property
    def service_list(self):
        if not self.services:
            return []

        return [
            service.strip()
            for service in self.services.split(",")
            if service.strip()
        ]

    @property
    def computed_status(self):
        """
        Automatically compute clinic status based on current day/time.
        Returns 'Closed' if current day is not available or current time is outside operating hours.
        Otherwise returns 'Open Now' or the manual status.
        """
        now = timezone.localtime()
        current_time = now.time()
        current_weekday = now.weekday()  # 0=Monday, 6=Sunday
        
        # Map weekday to our open_* fields
        weekday_fields = [
            'open_monday',
            'open_tuesday',
            'open_wednesday',
            'open_thursday',
            'open_friday',
            'open_saturday',
            'open_sunday',
        ]
        
        # Check if clinic is open on this weekday
        is_open_today = getattr(self, weekday_fields[current_weekday], False)
        
        if not is_open_today:
            return "Closed"
        
        # If no time is set, use manual status or default to Open Now
        if not self.open_time or not self.close_time:
            return self.status or "Open Now"
        
        # Handle overnight schedules (e.g., 8 PM to 2 AM)
        if self.close_time < self.open_time:
            # Overnight schedule
            if current_time >= self.open_time or current_time < self.close_time:
                return "Open Now"
            else:
                return "Closed"
        else:
            # Same-day schedule
            if self.open_time <= current_time <= self.close_time:
                return "Open Now"
            else:
                return "Closed"

    @property
    def days_display(self):
        """
        Return a clean text showing open days.
        Examples: "Mon, Tue, Wed" or "Daily" or "No open days set"
        """
        days = []
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        open_days = [
            self.open_monday,
            self.open_tuesday,
            self.open_wednesday,
            self.open_thursday,
            self.open_friday,
            self.open_saturday,
            self.open_sunday,
        ]
        
        for i, is_open in enumerate(open_days):
            if is_open:
                days.append(day_names[i])
        
        if len(days) == 0:
            return "No open days set"
        elif len(days) == 7:
            return "Daily"
        else:
            return ", ".join(days)

    class Meta:
        db_table = "clinics"

    def __str__(self):
        return self.name