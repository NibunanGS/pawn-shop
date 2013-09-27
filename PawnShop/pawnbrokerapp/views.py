# Create your views here.
from PawnShop.pawnbrokerapp.models import Pledge, Redemption
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404

def index(request):
    latest_pledges = Pledge.objects.all().order_by('-pledge_no')[:5]
    return render_to_response('pawnbrokerapp/index.html', {'latest_pledges': latest_pledges})

def pledge(request, pledge_id):
    try:
        p = Pledge.objects.get(pk = pledge_id) 
    except Pledge.DoesNotExist:
        raise Http404
    return render_to_response('pawnbrokerapp/pledge.html', {'pledge': p})

def redemption(request, pledge_id):
    r = get_object_or_404(Redemption, pledge__id = pledge_id)
    return render_to_response('pawnbrokerapp/redemption.html', {'redemption': r})
