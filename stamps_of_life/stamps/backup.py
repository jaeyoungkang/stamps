from django.http import HttpResponse
from .models import Stamp, CLog, Board, User
from datetime import datetime
import os.path


# 경로얻기 관련 참고 링크 https://stackoverflow.com/questions/9271464/what-does-the-file-variable-mean-do/9271617
def get_abs_path(file_name):
    dir = os.path.dirname(os.path.abspath(__file__))
    abs_path = os.path.join(dir, file_name)
    return abs_path

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

def backup():
    stamps = Stamp.objects.all()
    result3 = []
    for s in stamps:
        if s.board is None:
            board_name = ""
        else:
            board_name = s.board.name

        if s.updated_at is None:
            info = s.name + ", " + board_name + ", " + s.created_at.strftime('%Y-%m-%d_%H:%M:%S') + ", " + " " + ", " + str(s.count)
        else :
            info = s.name + ", " + board_name + ", " + s.created_at.strftime('%Y-%m-%d_%H:%M:%S') + ", " + s.updated_at.strftime('%Y-%m-%d_%H:%M:%S') + ", " + str(s.count)
        result3.append(info)

    boards = Board.objects.all()
    result2 = []
    for b in boards:
        info = b.name
        result2.append(info)

    logs = CLog.objects.all()
    result1 = []
    for l in logs:
        info = l.stamp.name + ", " + l.stamped_at.strftime('%Y-%m-%d_%H:%M:%S') + ", " + str(l.is_active)
        result1.append(info)


    f = open("stamp.txt", "w")
    for r in result3:
        f.write(r+"\n")
    f.close()

    f = open("baord.txt", "w")
    for r in result2:
        f.write(r+"\n")
    f.close()

    f = open("log.txt", "w")
    for r in result1:
        f.write(r+"\n")
    f.close()

    return [result1, result2, result3]