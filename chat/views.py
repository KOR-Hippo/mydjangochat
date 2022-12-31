from django.contrib.auth.decorators import login_required
from django.contrib import messages  # hmm...
from django.shortcuts import render, redirect, get_object_or_404

from chat.forms import RoomForm
from chat.models import Room


# Create your views here.
def index(request):

    # .order_by("-pk")를 지정하지 않으면,
    # Room 모델의 디폴트 정렬 옵션이 적용됩니다.
    room_qs = Room.objects.all()
    return render(request, "chat/index.html", {
        "room_list": room_qs,
    })


@login_required
def room_new(request):
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            created_room = form.save(commit=False)
            created_room.owner = request.user
            created_room.save()
            # room pk 기반으로 채팅방 URL을 만듭니다.
            return redirect("chat:room_chat", created_room.pk)
    else:
        form = RoomForm()

    return render(request, "chat/room_form.html", {
        "form": form,
    })


@login_required
def room_chat(request, room_pk):
    room = get_object_or_404(Room, pk=room_pk)
    return render(request, "chat/room_chat.html", {
        "room": room,
    })


@login_required
def room_delete(request, room_pk):
    room = get_object_or_404(Room, pk=room_pk)

    # 권한을 체크하는 방법은 다양하며, 다양한 철학의 라이브러리가 있습니다.
    # 소유자에게만 삭제버튼을 노출하는 것만으로 충분하지 않습니다. URL을 예상하여 요청이 들어올 수도 있습니다.
    # 프론트 단에서의 체킹과 별개로 백엔드 단에서의 권한 체크는 필수입니다.
    if room.owner != request.user:
        messages.error(request, "채팅방 소유자가 아닙니다.")  # import where?
        return redirect("chat:index")

    if request.method == "POST":
        room.delete() # HARD DELETE : 데이터베이스에서 삭제
        messages.success(request, "채팅방을 삭제했습니다.")
        return redirect("chat:index")

    return render(request, "chat/room_confirm_delete.html", {
        "room": room,
    })
