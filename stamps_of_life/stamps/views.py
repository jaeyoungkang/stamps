from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from datetime import datetime, timedelta
import operator

from .models import Stamp, CLog

MAX_COUNT = 12

def get_stamp_page(index, stamps):
    start_index = MAX_COUNT * (index-1)
    end_index = start_index  + MAX_COUNT
    if stamps.count() <= end_index:
        return stamps[start_index:]
    else:
        return stamps[start_index:end_index]

def get_stamp_all():
    return Stamp.objects.exclude(tag="trash").order_by('-created_at').all()

def get_trash_all():
    return Stamp.objects.filter(tag="trash").order_by('-created_at').all()

def get_clog_all():
    return CLog.objects.exclude(stamp__tag="trash").order_by('-stamped_at').all()

def make_page_index(stamps):
    total_count = stamps.count()

    if total_count <= MAX_COUNT:
        page_count = 2
    else:
        page_count = int(total_count / MAX_COUNT) + 1
        if total_count % MAX_COUNT > 0:
            page_count += 1
    return page_count

class TrashView(generic.ListView):
    template_name = 'stamps/trash.html'
    context_object_name = 'stamp_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_count'] = range(1, make_page_index(get_trash_all()))
        context['page_number'] = int(self.kwargs['page_index'])
        return context

    def get_queryset(self):
        page_number = int(self.kwargs['page_index'])
        return get_stamp_page(page_number, get_trash_all())

class MainView(generic.ListView):
    template_name = 'stamps/index.html'
    context_object_name = 'stamp_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_count'] = range(1, make_page_index(get_stamp_all()))
        context['page_number'] = int(self.kwargs['page_index'])
        return context

    def get_queryset(self):
        page_number = int(self.kwargs['page_index'])
        return get_stamp_page(page_number, get_stamp_all())


class HistoryView(generic.ListView):
    template_name = 'stamps/history.html'
    context_object_name = 'clog_list'

    def get_queryset(self):
        return get_clog_all()

def make_range(period):
    today = datetime.now() + timedelta(days=1)
    startday = today - timedelta(days=period)

    start = startday.strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")
    return [start, end]


class StatView(generic.ListView):
    template_name = 'stamps/stat.html'
    context_object_name = 'stats'

    def get_context_data(self, **kwargs):
        period = int(self.kwargs['period'])
        range = make_range(period)

        context = super().get_context_data(**kwargs)
        context['start_day'] = range[0]
        context['end_day'] = range[1]
        return context

    def get_queryset(self):
        period = int(self.kwargs['period'])
        range = make_range(period)

        logs = CLog.objects.filter(stamped_at__range=range).filter(is_active=True).all()
        names = logs.values("stamp__name").distinct()
        total_count = logs.count()
        result = []
        for name in names:
            n = name['stamp__name']
            c = logs.filter(stamp__name=n).count()
            r = round(c/total_count * 100, 1)
            result.append({"name": n, "count": c, "rate":r})

        result.sort(key=operator.itemgetter('count'), reverse=True)
        return result

def update_count(stamp):
    stamp.count = stamp.clog_set.filter(is_active=True).count();
    stamp.updated_at = datetime.now()
    stamp.save()

def count(request, page_number, stamp_id):
    s = get_object_or_404(Stamp, id=stamp_id)
    s.clog_set.create()
    update_count(s)
    return redirect('stamps:main', page_number)

def on_clog(request, clog_id):
    clog = get_object_or_404(CLog, id=clog_id)
    clog.is_active = True;
    clog.save()
    update_count(clog.stamp)
    return redirect('stamps:history')

def off_clog(request, clog_id):
    clog = get_object_or_404(CLog, id=clog_id)
    clog.is_active = False;
    clog.save()
    update_count(clog.stamp)
    return redirect('stamps:history')


def add_button(request):
    stamp_name = request.GET['query']
    page_number = request.GET['page_number']
    if Stamp.objects.filter(name=stamp_name).exists():
        return redirect('stamps:main', page_number)
    s = Stamp(name=stamp_name)
    s.save()
    return redirect('stamps:main', page_number)

class EditView(generic.ListView):
    template_name = 'stamps/edit.html'
    context_object_name = 'stamp_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_count'] = range(1, make_page_index(get_stamp_all()))
        context['page_number'] = int(self.kwargs['page_index'])
        return context

    def get_queryset(self):
        page_number = int(self.kwargs['page_index'])
        return get_stamp_page(page_number, get_stamp_all())


def discard(request, page_number, stamp_id):
    s = Stamp.objects.filter(id=stamp_id).get()
    if s:
        s.tag = "trash"
        s.save()
    return redirect('stamps:edit', page_number)

def empty_trash(request):
    Stamp.objects.filter(tag="trash").delete()
    return redirect('stamps:trash', 1)

def restore(request, page_number, stamp_id):
    s = Stamp.objects.get(id=stamp_id)
    s.tag = 'normal'
    s.save()
    return redirect('stamps:trash', page_number)

def search(request):
    keyword = request.GET['query']
    stamps = Stamp.objects.exclude(tag='trash').filter(name__contains=keyword).all()
    return render(request, "stamps/search.html", {"stamp_list":stamps})