from django.urls import path, include
from rest_framework import routers
from . import api
from . import views

router = routers.DefaultRouter()
router.register('stamps', api.StampViewSet)

app_name = 'stamps'
urlpatterns = [
    path('main/<board_name>', views.MainView.as_view(), name='main'),
    path('edit/<board_name>', views.EditView.as_view(), name='edit'),
    path('history', views.HistoryView.as_view(), name='history'),
    path('stat', views.StatView.as_view(), name='stat'),

    path('<clog_id>/onlog', views.on_clog, name='onlog'),
    path('<clog_id>/offlog', views.off_clog, name='offlog'),

    path('add', views.add_counter, name='add'),
    path('make_board', views.make_board, name='make_board'),
    path('remove_board', views.remove_board, name='remove_board'),

    path('api/', include(router.urls)),

    path('count/<board_name>/<stamp_id>', views.count, name='count'),
    path('remove/<stamp_id>', views.remove, name='remove'),

    path('search', views.search, name='search'),

    path('filter', views.filter, name='filter'),

    path('move', views.move, name='move'),

    path('join', views.signup, name='join'),
    path('login', views.signin, name='login'),

    path('load', views.load_datas, name='load'),
]