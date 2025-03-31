from django.http import HttpResponse

def api_match_id(request, id):
    return HttpResponse(f"Match ID: {id}")

def api_match(request):
    return HttpResponse("All matches")