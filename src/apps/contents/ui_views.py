from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def content_create_page(request):
    return render(request, "contents/new_content.html")
