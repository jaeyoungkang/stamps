from django.contrib.auth import login, authenticate
from django.http import HttpResponse

from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from datetime import datetime, timedelta
import operator

from .models import Stamp, CLog, Board, User
from .forms import UserCreationForm, LoginForm

def my_boards(user):
    return Board.objects.filter(user=user).all()

def my_stamps(user):
    return Stamp.objects.filter(user=user).all()

def get_stamp_all(user, board_name):
    if board_name == "all":
        return my_stamps(user).exclude(board__name='trash').order_by('-updated_at').all()
    else:
        return my_stamps(user).filter(board__name=board_name).order_by('-updated_at').all()

def get_clog_list(user, length, keyword):
    log_list = CLog.objects.filter(user=user).exclude(stamp__board__name="trash").order_by('-stamped_at').all()

    if keyword != "":
        log_list = log_list.filter(stamp__name__contains=keyword)

    count = log_list.count()
    if count < length:
        length = count

    return log_list[:length]

class MainView(generic.ListView):
    template_name = 'stamps/index.html'
    context_object_name = 'stamp_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board_count = my_boards(self.request.user).count()
        if board_count == 0 :
            make_basic_board(self.request.user)

        context['board_list'] = get_ordered_board_names(self.request.user)
        context['board_name'] = self.kwargs['board_name']
        return context

    def get_queryset(self):
        board_name = self.kwargs['board_name']
        return get_stamp_all(self.request.user, board_name)

def make_basic_board(user):
    b = Board(name="all")
    b.user = user
    b.save()
    b = Board(name="trash")
    b.user = user
    b.save()

def get_ordered_board_names(user):
    all = my_boards(user).get(name="all")
    trash = my_boards(user).get(name="trash")
    board_list = my_boards(user).exclude(name="all").exclude(name="trash").all()
    board_names = []
    for board in board_list:
        board_names.append(board.name)
    board_names.insert(0, all.name)
    board_names.insert(0, trash.name)
    return board_names

class EditView(generic.ListView):
    template_name = 'stamps/edit.html'
    context_object_name = 'stamp_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['board_list'] = get_ordered_board_names(self.request.user)
        context['board_name'] = self.kwargs['board_name']
        return context

    def get_queryset(self):
        board_name = self.kwargs['board_name']
        return get_stamp_all(self.request.user, board_name)


class HistoryView(generic.ListView):
    template_name = 'stamps/history.html'
    context_object_name = 'clog_list'

    def get_queryset(self):
        return get_clog_list(self.request.user, 100, "")

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

        logs = CLog.objects.filter(user=self.request.user).filter(stamped_at__range=range).filter(is_active=True).all()
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
    log = s.clog_set.create(user=request.user)
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

    if board_name == "all":
        return redirect('stamps:main', board_name)
    if board_name == "trash":
        return redirect('stamps:main', board_name)

    b = my_boards(request.user).get(name=board_name)
    if b :
        trash = my_boards(request.user).get(name="trash")
        for s in b.stamp_set.all():
            s.board = trash
            s.save()
        b.delete()
        return redirect('stamps:main', "trash")

    return redirect('stamps:main', board_name)

def make_board(request):
    board_name = request.GET['query']

    if my_boards(request.user).filter(name=board_name).exists():
        return redirect('stamps:main', 1)

    b = Board(name=board_name)
    b.user = request.user
    b.save()
    return redirect('stamps:main', board_name)

def add_counter(request):
    stamp_name = request.GET['query']
    board_name = request.GET['board_name']
    if my_stamps(request.user).filter(name=stamp_name).exists():
        return redirect('stamps:main', board_name)
    s = Stamp(name=stamp_name)
    s.board = my_boards(request.user).get(name=board_name)
    s.user = request.user
    s.save()
    return redirect('stamps:main', board_name)


def remove(request, stamp_id):
    my_stamps(request.user).filter(id=stamp_id).delete()
    return redirect('stamps:main', "trash")

def search(request):
    keyword = request.GET['query']
    stamps = my_stamps(request.user).exclude(board__name='trash').filter(name__contains=keyword).all()
    return render(request, "stamps/search.html", {"stamp_list":stamps, "board_list":get_ordered_board_names(request.user), "board_name":""})

def filter(request):
    keyword = request.GET['query']
    logs = get_clog_list(100, keyword)
    return render(request, "stamps/history.html", {"clog_list":logs})

def move(request):
    stamp_id = request.GET['stamp_id']
    board_name = request.GET['board_name']
    s = my_stamps(request.user).get(id=stamp_id)
    b = Board.objects.get(name=board_name)
    if s and b:
        s.board = b
        s.save()
    return redirect('stamps:edit', "1")

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            return redirect('stamps:main', 'all')
    else:
        form = UserCreationForm()
        return render(request, 'stamps/join.html', {'form': form})

def signin(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('stamps:main', 'all')
        else:
            return HttpResponse('로그인 실패. 다시 시도 해보세요.')
    else:
        form = LoginForm()
        return render(request, 'stamps/login.html', {'form': form})

def load_board():
    u = User.objects.get(email="jaeyoung2010@gmail.com")
    f = open("baord.txt", "r")
    result = f.read()
    f.close()
    datas = result.split("\n")
    for i in datas:
        if i == '':
            continue
        b = Board(name=i)
        b.user = u
        b.save()
    return datas

def get_string_to_datetime(date_str):
    date = None
    if date_str != ' ':
        date = datetime.strptime(date_str, '%Y-%m-%d_%H:%M:%S')
    return date

def get_board(board_name):
    u = User.objects.get(email="jaeyoung2010@gmail.com")
    if board_name != '':
        if Board.objects.filter(user=u).filter(name=board_name).exists() == False:
            b = Board(name=board_name)
            b.user = u
            b.save()
            return b
        else:
            return Board.objects.filter(user=u).get(name=board_name)
    else:
        return None

def get_stamp(stamp_name):
    u = User.objects.get(email="jaeyoung2010@gmail.com")
    if Stamp.objects.filter(user=u).filter(name=stamp_name).exists():
        return Stamp.objects.filter(user=u).get(name=stamp_name)

    return None



def load_stamp():
    u = User.objects.get(email="jaeyoung2010@gmail.com")
    f = open("stamp.txt", "r")
    result = f.read()
    f.close()
    datas = result.split("\n")
    for i in datas:
        row = i.split(", ")
        if len(row) < 5:
            break
        s = Stamp(name=row[0])
        b = get_board(row[1])
        s.board = b
        s.created_at = get_string_to_datetime(row[2])
        s.updated_at = get_string_to_datetime(row[3])
        s.count = int(row[4])
        s.user = u
        s.save()
    return datas

def load_log():
    u = User.objects.get(email="jaeyoung2010@gmail.com")
    f = open("log.txt", "r")
    result = f.read()
    f.close()
    datas = result.split("\n")
    for i in datas:
        row = i.split(", ")
        if len(row) < 3:
            break
        if get_stamp(row[0]) is None:
            break

        l = CLog()
        l.user = u
        l.stamp = get_stamp(row[0])
        l.stamped_at = get_string_to_datetime(row[1])
        l.is_active = row[2] == 'True' and True or False
        l.save()
    return datas

def load_datas(reuqest):
    load_board()
    load_stamp()
    load_log()
    return HttpResponse("Load complete!")



