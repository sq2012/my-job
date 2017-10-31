from django.test import TestCase
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
# Create your tests here.

def index(request):
        return render_to_response('visitors/321.html',
							 {
							},RequestContext(request, {}))


def picturesave(request):
        print 'wwwwwwwwww'