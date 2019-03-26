from django.shortcuts import render, get_object_or_404
from django.views import generic

from .models import Stamp, CLog

def get_stamp_all():
    return Stamp.objects.order_by('-created_at').all()

def get_clog_all():
    return CLog.objects.order_by('-stamped_at').all()


class IndexView(generic.ListView):
    template_name = 'stamps/index.html'
    context_object_name = 'stamp_list'

    def get_queryset(self):
        return get_stamp_all()

class HistoryView(generic.ListView):
    template_name = 'stamps/history.html'
    context_object_name = 'clog_list'

    def get_queryset(self):
        return get_clog_all()

def update_count(stamp):
    stamp.count = stamp.clog_set.filter(is_active=True).count();
    stamp.save()


def count(request, stamp_name):
    s = get_object_or_404(Stamp, name=stamp_name)
    s.clog_set.create()
    update_count(s)
    return render(request, 'stamps/index.html', {'stamp_list': get_stamp_all()} )

def on_clog(request, clog_id):
    clog = get_object_or_404(CLog, id=clog_id)
    clog.is_active = True;
    clog.save()
    update_count(clog.stamp)
    return render(request, 'stamps/history.html', {'clog_list':get_clog_all()} )

def off_clog(request, clog_id):
    clog = get_object_or_404(CLog, id=clog_id)
    clog.is_active = False;
    clog.save()
    update_count(clog.stamp)
    return render(request, 'stamps/history.html', {'clog_list':get_clog_all()} )


def add_button(request):
    stamp_name = request.GET['query']
    if Stamp.objects.filter(name=stamp_name).exists():
        return render(request, 'stamps/index.html', {'stamp_list': get_stamp_all()} )
    s = Stamp(name=stamp_name)
    s.save()
    return render(request, 'stamps/index.html', {'stamp_list': get_stamp_all()} )