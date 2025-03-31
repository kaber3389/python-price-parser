from django.http import HttpResponse

def api_productmy_id(request, id):
    return HttpResponse(f"My product ID: {id}")

def api_productmy(request):
    return HttpResponse("All my products")