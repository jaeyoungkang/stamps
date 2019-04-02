from django.urls import path, include
from rest_framework import routers
from . import api
from . import views

router = routers.DefaultRouter()
router.register('stamps', api.StampViewSet)

app_name = 'stamps'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('history', views.HistoryView.as_view(), name='history'),
    path('<clog_id>/onlog', views.on_clog, name='onlog'),
    path('<clog_id>/offlog', views.off_clog, name='offlog'),
    path('add', views.add_button, name='add'),
    path('api/', include(router.urls)),
    path('<stamp_name>/count', views.count, name='count'),
    path('edit', views.edit, name='edit'),
    path('discard/<stamp_name>', views.discard, name='discard'),
    path('empty', views.empty_trash, name='empty'),
    path('restore/<stamp_name>', views.restore, name='restore'),
    path('trash', views.TrashView.as_view(), name='trash'),

]