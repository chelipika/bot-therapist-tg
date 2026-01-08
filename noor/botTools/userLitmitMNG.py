import os
import json
from collections import defaultdict
from datetime import datetime, timedelta


class UserLimitManager:
    def __init__(self, max_daily_limit=5, audio_max_limits=0):
        self.max_daily_limit = max_daily_limit
        self.max_daily_limit_audio = audio_max_limits
        self.user_limits = defaultdict(dict)
        self.filename = "user_limits.json"
        self.load_limits()

    def load_limits(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                for user_id, info in data.items():
                    self.user_limits[user_id] = {
                        'count': info['count'],
                        'last_reset': datetime.fromisoformat(info['last_reset']),
                        'audio_count': info['audio_count']
                    }
        except FileNotFoundError:
            pass

    def save_limits(self):
        data = {
            user_id: {
                'count': info['count'],
                'last_reset': info['last_reset'].isoformat(),
                'audio_count': info['audio_count']
            }
            for user_id, info in self.user_limits.items()
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f)

    def check_and_reset_daily(self, user_id):
        user_id = str(user_id)
        if user_id not in self.user_limits:
            self.user_limits[user_id] = {'count': 0, 'last_reset': datetime.now(), 'audio_count': 0}
        
        last_reset = self.user_limits[user_id]['last_reset']
        if datetime.now() - last_reset > timedelta(hours=1):
            self.user_limits[user_id] = {'count': 0, 'last_reset': datetime.now(), 'audio_count': 0}
    def funded_limites(self, user_id):
        user_id = str(user_id)
        x = int(self.user_limits[user_id]['count'])
        y = self.user_limits[user_id]['last_reset']
        j = int(self.user_limits[user_id]['audio_count'])
        self.user_limits[user_id] = {'count': x-10, 'last_reset': y, 'audio_count': j}
    def funded_limites_auido(self, user_id):
        user_id = str(user_id)
        x = int(self.user_limits[user_id]['count'])
        y = self.user_limits[user_id]['last_reset']
        j = int(self.user_limits[user_id]['audio_count'])
        self.user_limits[user_id] = {'count': x, 'last_reset': y, 'audio_count': j-10}

    async def use_limit(self, user_id):
        user_id = str(user_id)
        self.check_and_reset_daily(user_id)

        if self.user_limits[user_id]['count'] >= self.max_daily_limit:
            reset_time = self.user_limits[user_id]['last_reset'] + timedelta(hours=1)
            return False, 0, reset_time

        self.user_limits[user_id]['count'] += 1
        remaining = self.max_daily_limit - self.user_limits[user_id]['count']
        self.save_limits()
        return True, remaining, None
    async def use_limit_audio(self, user_id):
        user_id = str(user_id)
        self.check_and_reset_daily(user_id)

        if self.user_limits[user_id]['audio_count'] >= self.max_daily_limit_audio:
            return False, 0

        self.user_limits[user_id]['audio_count'] += 1
        remaining = self.max_daily_limit_audio - self.user_limits[user_id]['audio_count']
        self.save_limits()
        return True, remaining