from django.urls import path, include
from rest_framework import routers
from . import api
from . import views

router = routers.DefaultRouter()
router.register('stamps', api.StampViewSet)

app_name = 'stamps'
urlpatterns = [
    path('main/<page_index>', views.MainView.as_view(), name='main'),
    path('edit/<page_index>', views.EditView.as_view(), name='edit'),
    path('trash/<page_index>', views.TrashView.as_view(), name='trash'),
    path('history', views.HistoryView.as_view(), name='history'),
    path('stat/<period>', views.StatView.as_view(), name='stat'),

    path('<clog_id>/onlog', views.on_clog, name='onlog'),
    path('<clog_id>/offlog', views.off_clog, name='offlog'),
    path('add', views.add_button, name='add'),
    path('api/', include(router.urls)),

    path('count/<page_number>/<stamp_id>', views.count, name='count'),
    path('discard/<page_number>/<stamp_id>', views.discard, name='discard'),
    path('restore/<page_number>/<stamp_id>', views.restore, name='restore'),

    path('empty', views.empty_trash, name='empty'),

    path('search', views.search, name='search'),

    path('filter', views.filter, name='filter'),
]