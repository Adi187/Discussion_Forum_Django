from  django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from .models import Room,Subject,Message
from .forms import RoomForm

'''rooms=[
    {'id':1,'name':'Python crash course'},
    {'id':2,'name':'js crash course'},
    {'id':3,'name':'DSA crash course'}

]'''


def loginPage(request):
    page='login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method=='POST':
        username=request.POST.get('username').lower()
        password=request.POST.get('password')
        try:
            user=User.objects.get(username=username)
        except:
            messages.error(request,'user does not exist')
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
             messages.error(request,'username or password mismatch')



    context={'page':page}
    return render(request, 'base/login.html',context)
def logoutUser(request):
    logout(request)
    return redirect('home')

def registerUser(request):
    form=UserCreationForm()
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'an Error has occured')
    return render(request, 'base/login.html',{'form':form})

def home(request):
    q=request.GET.get('q') if request.GET.get('q')!=None else ''
    rooms=Room.objects.filter(
    Q(subject__name__icontains=q) |
    Q(name__icontains=q) |
    Q(description__icontains=q)
    )
    subjects=Subject.objects.all()
    room_count=rooms.count()
    room_messages = Message.objects.all()


    context={'rooms':rooms,'subjects':subjects,'room_count':room_count,'room_messages':room_messages}
    return render(request, 'base/home.html',context)
  

def room(request,id_):
    room=Room.objects.get(id=id_)
    room_messages=room.message_set.all().order_by('-created')
    participants=room.participants.all()
    if request.method == 'POST':
        message=Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',id_=room.id)
    context={'room':room,'room_messages':room_messages,'participants':participants}
    return render(request, 'base/Room.html',context)

@login_required(login_url='login')


def userProfile(request,pk):
    user=User.objects.get(id=pk)
    rooms=user.room_set.all()
    context={'user':user,'rooms':rooms}
    return render(request, 'base/profile.html',context)

def createRoom(request):
    form=RoomForm()
    if request.method == "POST":
        form=RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context={'form':form}
    return render(request,'base/r_form.html',context)

@login_required(login_url='login')

def UpdateRoom(request,pk):
    room=Room.objects.get(id=pk)
    form=RoomForm(instance=room)
    if request.user !=room.Chat_host:
        return HttpResponse('you are not authorised to perform the following action')

    if request.method=='POST':
        form=RoomForm(request.POST,instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context={'form':form}
    return render(request,'base/r_form.html',context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room=Room.objects.get(id=pk)
    if request.user !=room.Chat_host:
        return HttpResponse('you are not authorised to perform the following action')
    if request.method=='POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room})

@login_required(login_url='login')
def deleteMessage(request,pk):
    message=Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('you are not authorised to perform the following action')
    if request.method=='POST':
        message.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':message})

