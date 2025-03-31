from django.http import HttpResponse

def api_productcompetitor_id(request, id):
    return HttpResponse(f"Competitor product ID: {id}")

def api_productcompetitor(request):
    return HttpResponse("All competitor products")