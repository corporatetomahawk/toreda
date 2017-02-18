# Django
from django.shortcuts import render
from django.contrib.auth import logout
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Django REST Framework
from rest_framework import viewsets, mixins

# Scripts
from scripts.github import *
from scripts.quandl import *
from scripts.linkedin import LinkedinOauthClient
from scripts.facebook import *
from scripts.googlePlus import *

# Python
import oauth2 as oauth
import simplejson as json
import requests

# Models
from hackathon.models import *
from hackathon.serializers import SnippetSerializer
from hackathon.forms import UserForm


profile_track = None
getTumblr = TumblrOauthClient(settings.TUMBLR_CONSUMER_KEY, settings.TUMBLR_CONSUMER_SECRET)
getInstagram = InstagramOauthClient(settings.INSTAGRAM_CLIENT_ID, settings.INSTAGRAM_CLIENT_SECRET)
getTwitter = TwitterOauthClient(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET, settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_TOKEN_SECRET)
getGithub = GithubOauthClient('2a11ce63ea7952d21f02', '7e20f82a34698fb33fc837186e96b12aaca2618d')
getLinkedIn = LinkedinOauthClient(settings.LINKEDIN_CLIENT_ID, settings.LINKEDIN_CLIENT_SECRET)
getFacebook = FacebookOauthClient(settings.FACEBOOK_APP_ID, settings.FACEBOOK_APP_SECRET)
getGoogle = GooglePlus(settings.GOOGLE_PLUS_APP_ID, settings.GOOGLE_PLUS_APP_SECRET)
getDropbox = DropboxOauthClient(settings.DROPBOX_APP_ID, settings.DROPBOX_APP_SECRET)
getFoursquare = FoursquareOauthClient(settings.FOURSQUARE_APP_ID, settings.FOURSQUARE_APP_SECRET)

def index(request):
    print "index: " + str(request.user)

    if not request.user.is_active:
        if request.GET.items():
            if profile_track == 'github':
                code = request.GET['code']
                getGithub.get_access_token(code)
                getGithub.getUserInfo()
                print getGithub.access_token
                try:
                    user = User.objects.get(username = getGithub.username + '_github')
                except User.DoesNotExist:
                    username = getGithub.username + '_github'
                    new_user = User.objects.create_user(username, username+'@madewithgithub.com', 'password')
                    new_user.save()
                    try:
                        profile = GithubProfile.objects.get(user = new_user.id)
                        profile.access_token = getGithub.access_token
                    except GithubProfile.DoesNotExist:
                        profile = GithubProfile(user=new_user, access_token=getGithub.access_token, scopes=getGithub.scopes ,github_user=getGithub.username)
                    profile.save()
                user = authenticate(username=getGithub.username+'_github', password='password')
                login(request, user)
            elif profile_track == 'twitter':
                oauth_verifier = request.GET['oauth_verifier']
                getTwitter.get_access_token_url(oauth_verifier)

                try:
                    user = User.objects.get(username = getTwitter.username + '_twitter')#(username=getTwitter.username)
                except User.DoesNotExist:
                    username = getTwitter.username + '_twitter'
                    new_user = User.objects.create_user(username, username+'@madewithtwitter.com', 'password')
                    new_user.save()
                    profile = TwitterProfile(user = new_user,oauth_token = getTwitter.oauth_token, oauth_token_secret= getTwitter.oauth_token_secret, twitter_user=getTwitter.username)
                    profile.save()
                user = authenticate(username=getTwitter.username+'_twitter', password='password')
                login(request, user)
            elif profile_track == 'instagram':
                code = request.GET['code']
                getInstagram.get_access_token(code)

                try:
                    user = User.objects.get(username=getInstagram.user_data['username']+'_instagram')
                except User.DoesNotExist:
                    username = getInstagram.user_data['username']+'_instagram'
                    new_user = User.objects.create_user(username, username+'@madewithinstagram.com', 'password')
                    new_user.save()
                    profile = InstagramProfile(user = new_user, access_token = getInstagram.access_token, instagram_user=getInstagram.user_data['username'])
                    profile.save()
                user = authenticate(username=getInstagram.user_data['username']+'_instagram' , password='password')
                login(request, user)
            elif profile_track == 'linkedin':
                code = request.GET['code']
                getLinkedIn.get_access_token(code)
                getLinkedIn.getUserInfo()

                try:
                    user = User.objects.get(username=getLinkedIn.user_id+'_linkedin')
                except User.DoesNotExist:
                    username = getLinkedIn.user_id+'_linkedin'
                    new_user = User.objects.create_user(username, username+'@madwithlinkedin.com', 'password')
                    new_user.save()
                    try:
                        profile =LinkedinProfile.objects.get(user = new_user.id)
                        profile.access_token = LinkedinProfile.access_token
                    except LinkedinProfile.DoesNotExist:
                        profile = LinkedinProfile(user=new_user, access_token=getLinkedIn.access_token, linkedin_user=getLinkedIn.user_id)
                    profile.save()
                user = authenticate(username=getLinkedIn.user_id+'_linkedin', password='password')
                login(request, user)

            elif profile_track == 'facebook':
                code = request.GET['code']
                getFacebook.get_access_token(code)
                userInfo = getFacebook.get_user_info()
                username = userInfo['first_name'] + userInfo['last_name']

                try:
                    user = User.objects.get(username=username+'_facebook')
                except User.DoesNotExist:
                    new_user = User.objects.create_user(username+'_facebook', username+'@madewithfacbook', 'password')
                    new_user.save()

                    try:
                        profile = FacebookProfile.objects.get(user=new_user.id)
                        profile.access_token = getFacebook.access_token
                    except:
                        profile = FacebookProfile()
                        profile.user = new_user
                        profile.fb_user_id = userInfo['id']
                        profile.profile_url = userInfo['link']
                        profile.access_token = getFacebook.access_token
                    profile.save()
                user = authenticate(username=username+'_facebook', password='password')
                login(request, user)
            elif profile_track == 'tumblr':
                if not getTumblr.is_authorized:
                    oauth_verifier = request.GET['oauth_verifier']
                    getTumblr.access_token_url(oauth_verifier)
                    getTumblr.getUserInfo()
                    try:
                        user = User.objects.get(username = getTumblr.username + '_tumblr')
                    except User.DoesNotExist:
                        username = getTumblr.username + '_tumblr'
                        new_user = User.objects.create_user(username, username+'@madewithtumblr.com', 'password')
                        new_user.save()
                        try:
                            profile =TumblrProfile.objects.get(user = new_user.id)
                            profile.access_token = getTumblr.access_token['oauth_token']
                            profile.access_token_secret = getTumblr.access_token['oauth_token_secret']
                        except TumblrProfile.DoesNotExist:
                            profile = TumblrProfile(user=new_user, access_token=getTumblr.access_token['oauth_token'], access_token_secret= getTumblr.access_token['oauth_token_secret'], tumblr_user=getTumblr.username)
                        profile.save()
                user = authenticate(username=getTumblr.username+'_tumblr', password='password')
                login(request, user)


            elif profile_track == 'google':
                code = request.GET['code']
                state = request.GET['state']
                getGoogle.get_access_token(code, state)
                userInfo = getGoogle.get_user_info()
                username = userInfo['given_name'] + userInfo['family_name']

                try:
                    user = User.objects.get(username=username+'_google')
                except User.DoesNotExist:
                    new_user = User.objects.create_user(username+'_google', username+'@madewithgoogleplus', 'password')
                    new_user.save()

                    try:
                        profle = GoogleProfile.objects.get(user = new_user.id)
                        profile.access_token = getGoogle.access_token
                    except:
                        profile = GoogleProfile()
                        profile.user = new_user
                        profile.google_user_id = userInfo['id']
                        profile.access_token = getGoogle.access_token
                        profile.profile_url = userInfo['link']
                    profile.save()
                user = authenticate(username=username+'_google', password='password')
                login(request, user)

            elif profile_track == 'dropbox':
                code = request.GET['code']
                state = request.GET['state']
                getDropbox.get_access_token(code, state)
                userInfo = getDropbox.get_user_info()
                username = userInfo['name_details']['given_name'] + userInfo['name_details']['surname']

                try:
                    user = User.objects.get(username=username+'_dropbox')
                except User.DoesNotExist:
                    new_user = User.objects.create_user(username+'_dropbox', username+'@madewithdropbox', 'password')
                    new_user.save()

                    try:
                        profile = DropboxProfile.objects.get(user=new_user.id)
                        profile.access_token = getDropbox.access_token
                    except:
                        profile = DropboxProfile()
                        profile.user = new_user
                        profile.access_token = getDropbox.access_token
                        profile.dropbox_user_id = userInfo['uid']
                    profile.save()
                user = authenticate(username=username+'_dropbox', password='password')
                login(request, user)

            elif profile_track == 'foursquare':
                code = request.GET['code']
                getFoursquare.get_access_token(code)
                userInfo = getFoursquare.get_user_info()
                username = userInfo['firstName'] + userInfo['lastName']

                try:
                    user = User.objects.get(username=username+'_foursquare')
                except User.DoesNotExist:
                    new_user = User.objects.create_user(username+'_foursquare', username+'@madewithfoursquare', 'password')
                    new_user.save()

                    try:
                        profile = FoursquareProfile.object.get(user=new_user.id)
                        profile.access_token = getFoursquare.access_token

                    except:
                        profile = FoursquareProfile()
                        profile.user = new_user
                        profile.foursquare_id = userInfo['id']
                        profile.access_token = getFoursquare.access_token
                    profile.save()

                user = authenticate(username=username+'_foursquare', password='password')
                login(request, user)





    else:
        if request.GET.items():
            user = User.objects.get(username = request.user.username)
            if profile_track == 'github':
                code = request.GET['code']
                getGithub.get_access_token(code)
                getGithub.getUserInfo()

                try:
                    githubUser = GithubProfile.objects.get(user=user.id)
                except GithubProfile.DoesNotExist:
                    profile = GithubProfile(user=new_user, access_token=getGithub.access_token, scopes=getGithub.scopes ,github_user=getGithub.username)
                    profile.save()
            elif profile_track == 'twitter':
                oauth_verifier = request.GET['oauth_verifier']
                getTwitter.get_access_token_url(oauth_verifier)

                try:
                    twitterUser = TwitterProfile.objects.get(user = user.id)
                except TwitterProfile.DoesNotExist:
                    profile = TwitterProfile(user = user, oauth_token = getTwitter.oauth_token, oauth_token_secret= getTwitter.oauth_token_secret, twitter_user=getTwitter.username)
                    profile.save()
            elif profile_track == 'instagram':
                code = request.GET['code']
                getInstagram.get_access_token(code)

                try:
                    instagramUser = InstagramProfile.objects.get(user= user.id)
                except InstagramProfile.DoesNotExist:
                    profile = InstagramProfile(user = user, access_token = getInstagram.access_token, instagram_user=getInstagram.user_data['username'])
                    profile.save()
            elif profile_track == 'linkedin':
                code = request.GET['code']
                getLinkedIn.get_access_token(code)
                getLinkedIn.getUserInfo()

                try:
                    linkedinUser = LinkedinProfile.objects.get(user=user.id)
                except LinkedinProfile.DoesNotExist:
                    profile = LinkedinProfile(user = user, access_token = getLinkedIn.access_token, linkedin_user=getLinkedIn.user_id)
                    profile.save()
            elif profile_track == 'tumblr':
                if not getTumblr.is_authorized:
                    oauth_verifier = request.GET['oauth_verifier']
                    getTumblr.access_token_url(oauth_verifier)
                    getTumblr.getUserInfo()

                    try:
                        tumblrUser = TumblrProfile.objects.get(user=user.id)
                    except TumblrProfile.DoesNotExist:
                        profile = TumblrProfile(user=user, access_token=getTumblr.access_token['oauth_token'], access_token_secret= getTumblr.access_token['oauth_token_secret'], tumblr_user=getTumblr.username)
                        profile.save()


    context = {'hello': 'world'}
    return render(request, 'hackathon/index.html', context)


##################
#  API Examples  #
##################

def api_examples(request):
    context = {'title': 'API Examples Page'}
    return render(request, 'hackathon/api_examples.html', context)

#################
#  FACEBOOK API #
#################

def facebook(request):
    '''
    This is an example of getting basic user info and display it
    '''
    userInfo = getFacebook.get_user_info()
    return render(request, 'hackathon/facebookAPIExample.html', { 'userInfo' : userInfo})

#################
#  GOOGLE API   #
#################
def googlePlus(request):

    userInfo = getGoogle.get_user_info()
    return render(request, 'hackathon/googlePlus.html', {'userInfo' : userInfo})

#################
#   QUANDL API  #
#################

def quandlDowJones(request):
    '''Returns JSON response about the latest dowjones index.'''
    dowjonesdata = fetchData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/BCB/UDJIAD1.json?')
    print dowjonesdata
    return JsonResponse({'data': dowjonesdata})

def quandlSnp500(request):
    '''Returns JSON response about the latest SNP 500 index.'''
    snpdata = fetchData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/YAHOO/INDEX_GSPC.json?')
    return JsonResponse({'data': snpdata})

def quandlNasdaq(request):
    '''Returns JSON response about the latest nasdaq index.'''
    nasdaqdata = fetchData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/NASDAQOMX/COMP.json?')
    return JsonResponse({'data': nasdaqdata})

def quandlapple(request):
    '''Returns JSON response about the latest apple stock.'''
    appledata = fetchstockData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/GOOG/NASDAQ_AAPL.json')
    return JsonResponse({'data': appledata})

def quandlNasdaqdiff(request):
    '''Returns JSON response about the latest nasdaq index.'''
    nasdaqdata = rdiffData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/NASDAQOMX/COMP.json?')
    return JsonResponse({'data': nasdaqdata})

def quandlSnp500diff(request):
    '''Returns JSON response about the latest SNP 500 index.'''
    snpdata = rdiffData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/YAHOO/INDEX_GSPC.json?')
    return JsonResponse({'data': snpdata})

def quandlDowJonesdiff(request):
    '''Returns JSON response about the latest dowjones index.'''
    dowjonesdata = rdiffData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/BCB/UDJIAD1.json?')
    return JsonResponse({'data': dowjonesdata})

def quandlapplediff(request):
    '''Returns JSON response about the latest apple stock.'''
    appledata = rdiffData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/GOOG/NASDAQ_AAPL.json')
    return JsonResponse({'data': appledata})

def quandlstocks(request):
    everyData = {}
    dowjonesdata = fetchData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/BCB/UDJIAD1.json?')
    everyData['dow'] = dowjonesdata
    everyData['dowdiff'] = rdiffData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/BCB/UDJIAD1.json?')
    snpdata = fetchData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/YAHOO/INDEX_GSPC.json?')
    everyData['snp'] = snpdata
    everyData['snpdiff'] = rdiffData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/YAHOO/INDEX_GSPC.json?')
    nasdaqdata = fetchData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/NASDAQOMX/COMP.json?')
    everyData['nasdaq'] = nasdaqdata
    everyData['nasdaqdiff'] = rdiffData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/NASDAQOMX/COMP.json?')
    everyData['apple'] = fetchstockData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/GOOG/NASDAQ_AAPL.json')
    everyData['applediff'] = rdiffData(settings.QUANDLAPIKEY, 'https://www.quandl.com/api/v1/datasets/GOOG/NASDAQ_AAPL.json')
    return render(request, 'hackathon/quandl.html', { 'everyData': everyData })

#################
#   GITHUB API  #
#################

def githubUser(request):
    '''Returns Github Profile data for a specific user.'''
    parsedData = {}
    if request.method == 'POST':
        user = request.POST.get('user')
        parsedData['userData'] = getUserData(user, settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET)
    return render(request, 'hackathon/github.html', {'data': parsedData})

def githubTopRepositories(request):
    '''Returns Top Commited Repositories for a specific Github User'''

    parsedData = {}
    if request.method == 'POST':
        user = request.POST.get('user')
        repositories = getUserRepositories(user, settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET)
        list = getTopContributedRepositories(user, repositories, settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET)
        filtered = filterCommits(list)
        parsedData['committed'] = filtered
        print parsedData
    return render(request, 'hackathon/githubTopRepositories.html', {'data': parsedData})

def githubResume(request):
    '''A sample application which pulls various Github data to form a Resume of sorts'''

    allData = {}
    userData = getUserData('DrkSephy', settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET)
    repositories = getUserRepositories('DrkSephy', settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET)
    list = getTopContributedRepositories('DrkSephy', repositories, settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET)
    filtered = filterCommits(list)
    stargazers = getStarGazerCount('DrkSephy', settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET)
    filteredStargazers = filterStarGazerCount(stargazers)
    forkedRepos = getForkedRepositories('DrkSephy', settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET)
    allData['userData'] = userData
    allData['filteredData'] = filtered
    allData['filteredStargazers'] = filteredStargazers
    allData['forkedRepos'] = forkedRepos
    return render(request, 'hackathon/githubResume.html', { 'data': allData })


##################
#  LINKEDIN  API #
##################

def linkedin(request):
    if getLinkedIn.is_authorized:
        content = getLinkedIn.getUserInfo()
    else:
        global profile_track
        profile_track = 'linkedin'
        linkedin_url = getLinkedIn.get_authorize_url()
        return HttpResponseRedirect(linkedin_url)

    context = {'title': 'linkedin example', 'content': content}
    return render(request, 'hackathon/linkedin.html', context)


#########################
# Snippet RESTful Model #
#########################

class CRUDBaseView(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    pass

class SnippetView(CRUDBaseView):
    serializer_class = SnippetSerializer
    queryset = Snippet.objects.all()


######################
# Registration Views #
######################

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            registered = True
            return HttpResponseRedirect('/hackathon/login/')
        else:
            print user_form.errors
    else:
        user_form = UserForm()


    return render(request,
            'hackathon/register.html',
            {'user_form': user_form, 'registered': registered} )

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/hackathon/api/')
            else:
                return HttpResponse("Your Django Hackathon account is disabled.")
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    else:
        return render(request, 'hackathon/login.html', {})

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/hackathon/login/')

def github_login(request):
    global profile_track
    profile_track = 'github'
    github_url = getGithub.get_authorize_url()
    return HttpResponseRedirect(github_url)

def linkedin_login(request):
    global profile_track
    profile_track = 'linkedin'
    linkedin_url = getLinkedIn.get_authorize_url()
    return HttpResponseRedirect(linkedin_url)

def facebook_login(request):
    global profile_track
    profile_track = 'facebook'
    facebook_url = getFacebook.get_authorize_url()
    return HttpResponseRedirect(facebook_url)


def google_login(request):
    global profile_track
    profile_track = 'google'
    google_url = getGoogle.get_authorize_url()
    return HttpResponseRedirect(google_url)

