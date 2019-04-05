from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from datetime import datetime, timedelta
import operator

from .models import Stamp, CLog, Board

def get_stamp_all(board_name):
    return Stamp.objects.filter(board__name=board_name).order_by('-created_at').all()

def get_trash_all():
    if Board.objects.filter(name="trash").exists() != True:
        trash = Board(name="trash")
        trash.save()
    else:
        trash = Board.objects.filter(name="trash").get()
    return trash.stamp_set.all() # remove order

def get_clog_all(length):
    count = CLog.objects.exclude(stamp__board__name="trash").order_by('-stamped_at').count()
    if count < length:
        length = count
    return CLog.objects.exclude(stamp__board__name="trash").order_by('-stamped_at').all()[:length]

class MainView(generic.ListView):
    template_name = 'stamps/index.html'
    context_object_name = 'stamp_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board_count =  Board.objects.count()
        if board_count == 0 :
            b = Board(name="1")
            b.save()

        context['board_list'] = Board.objects.all()
        context['board_name'] = self.kwargs['board_name']
        return context

    def get_queryset(self):
        board_name = self.kwargs['board_name']
        return get_stamp_all(board_name)


class EditView(generic.ListView):
    template_name = 'stamps/edit.html'
    context_object_name = 'stamp_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['board_list'] = Board.objects.all()
        context['board_name'] = self.kwargs['board_name']
        return context

    def get_queryset(self):
        board_name = self.kwargs['board_name']
        return get_stamp_all(board_name)


class HistoryView(generic.ListView):
    template_name = 'stamps/history.html'
    context_object_name = 'clog_list'

    def get_queryset(self):
        return get_clog_all(100)

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
        period = int(self.request.GET['period'])
        type = self.request.GET['type']
        range = make_range(period)

        context = super().get_context_data(**kwargs)
        context['start_day'] = range[0]
        context['end_day'] = range[1]
        context['period'] = period
        context['type'] = type
        return context

    def get_queryset(self):
        period = int(self.request.GET['period'])
        range = make_range(period)

        logs = CLog.objects.filter(stamped_at__range=range).filter(is_active=True).all()
        total_count = logs.count()
        result = []

        type = self.request.GET['type']
        if  type == "group":
            board_names = logs.values("stamp__board__name").distinct()
            for name in board_names:
                n = name['stamp__board__name']
                c = logs.filter(stamp__board__name=n).count()
                r = round(c/total_count * 100, 1)
                result.append({"name": n, "count": c, "rate":r})
        else:
            names = logs.values("stamp__name").distinct()
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

def count(request, stamp_id, board_name):
    s = get_object_or_404(Stamp, id=stamp_id)
    s.clog_set.create()
    update_count(s)
    return redirect('stamps:main', board_name)

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

def remove_board(request):
    board_name = request.GET['query']

    if board_name == "1":
        return redirect('stamps:main', board_name)
    if board_name == "trash":
        return redirect('stamps:main', board_name)

    b = Board.objects.get(name=board_name)
    if b :
        trash = Board.objects.get(name="trash")
        for s in b.stamp_set.all():
            s.board = trash
            s.save()
        b.delete()
        return redirect('stamps:main', "trash")

    return redirect('stamps:main', board_name)

def make_board(request):
    board_name = request.GET['query']

    if Board.objects.filter(name=board_name).exists():
        return redirect('stamps:main', 1)

    b = Board(name=board_name)
    b.save()
    return redirect('stamps:main', board_name)

def add_counter(request):
    stamp_name = request.GET['query']
    board_name = request.GET['board_name']
    if Stamp.objects.filter(name=stamp_name).exists():
        return redirect('stamps:main', board_name)
    s = Stamp(name=stamp_name)
    s.board = Board.objects.get(name=board_name)
    s.save()
    return redirect('stamps:main', board_name)

def get_trash_board():
    return Board.objects.filter(name="trash").get()

def remove(request, stamp_id):
    Stamp.objects.filter(id=stamp_id).delete()
    return redirect('stamps:main', "trash")

def search(request):
    keyword = request.GET['query']
    stamps = Stamp.objects.exclude(board__name='trash').filter(name__contains=keyword).all()
    return render(request, "stamps/search.html", {"stamp_list":stamps, "board_list":Board.objects.all(), "board_name":""})

def filter(request):
    keyword = request.GET['query']
    logs = CLog.objects.filter(stamp__name__contains=keyword).order_by('-stamped_at').all()
    return render(request, "stamps/history.html", {"clog_list":logs})

def move(request):
    stamp_id = request.GET['stamp_id']
    board_name = request.GET['board_name']
    s = Stamp.objects.get(id=stamp_id)
    b = Board.objects.get(name=board_name)
    if s and b:
        s.board = b
        s.save()
    return redirect('stamps:edit', "1")
