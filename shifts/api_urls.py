# shifts/api_urls.py
from django.urls import path
from shifts.views.schedule import schedule_view


from shifts.views.shift_actions import join_shift  # updated import path

urlpatterns = [
    path('join/', join_shift, name='join_shift'),
    path('schedule/', schedule_view, name='view_schedule'),

]
