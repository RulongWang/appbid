# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response,render
from django.shortcuts import render_to_response,HttpResponse,  RequestContext, HttpResponseRedirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import reverse
import urllib
import json
# from PIL import Image
from appbid import models

#register app entry
def register_app(request):
    return render(request, "seller/register_content.html",{"test":"test"})


def hello(request):
    return HttpResponse(" This is the home page")


def getIcon(request):
    pass

def list_latest(request):
    list_apps = []
    return render_to_response('query/listing_base.html', {"list_latest":list_apps}, context_instance=RequestContext(request))


def getDetail(request, *args, **kwargs):
    """Get app detail info."""
    if kwargs['pk']:
        app = get_object_or_404(models.App, pk=kwargs['pk'], publisher=request.user)
        initParam = {'app': app}
        initParam['appInfo'] = app.appinfo
        initParam['attachments'] = app.attachment_set.all()
        return render_to_response('query/listing_detail.html', initParam, context_instance=RequestContext(request))
    raise Http404

#     description_detail = """<div class="details description">
# 			<h2>
# 				Description
# 							</h2>
# 			<p>You are bidding on an extremely unique and easy to expand iOS photography app that includes a PR2 website getting thousands of users monthly.</p>
# <p>Over 25,000 people have downloaded Frampix from the App Store in the last year and has over 75,000 logged uses in Google Analytics (we track app usage and website traffic with Google Analytics).&nbsp;</p>
# <p>&nbsp;</p>
# <p><strong>Here is how the app works.</strong></p>
# <p>1. User chooses from our frame catalog<br>2. User takes a photo with the frame or pulls an image from their library<br>3. Framed image is saved with the option to post to facebook and twitter.</p>
# <p>If the user uploads the image to a social network, a short url is created which feeds back to the image page on FramPix.com (run by WordPress)</p>
# <p>So every time a user uploads a photo, traffic is generated to the website.</p>
# <p>&nbsp;</p>
# <p><strong>This app has an almost perfect 5 star rating.<br></strong>We have been reviewed on several blogs including&nbsp;<a href="http://www.killerstartups.com/rising-startup-stars/frampix-frames-for-pix/" rel="nofollow external" target="_blank">KillerStartups.com</a></p>
# <p>&nbsp;</p>
# <p><strong>This app is EASY to expand<br></strong>If you want to add more frames, just create as many square PDF files with transparency as you like and add them to the app.</p>
# <p>The more frames you add, the more search results you will show up under in the app store.</p>
# <p>&nbsp;</p>
# <p><strong>This app is EASY to duplicate<br></strong>Once you have the code, you could use the same technology to make semi transparent photo filter apps, watermarking apps, tourist specific photo apps for small businesses and more.</p>
# <p><br><strong>This app is FUTURE PROOF<br></strong>Because we use vector PDF graphics for our frames they will work the same on any resolution of current or future iOS devices.&nbsp;When Apple released the new retina screen iPads our frames looked awesome. They can scale to any resolution perfectly.</p>
# <p>&nbsp;</p>
# <p><strong>This app is EASY to monetize</strong></p>
# <ul>
# <li>Serve ads next to the hosted photos</li>
# <li>Selling new frames or frame packs in app</li>
# <li>Offering companies the ability to sponsor a frame</li>
# <li>Co branding the app with movie posters etc.</li>
# <li>Start serving ads in app</li>
# </ul><p>&nbsp;</p>
# <p><strong>Why am I selling this?<br></strong>This app is one of several projects I finished but never properly focused on. I have incubated it for a year and now it's time for someone to take it to a new level. I am not that person mainly because my <a href="http://vectortoons.com/" rel="nofollow external" target="_blank">graphics</a> business and <a href="http://nohy.pe/mml13" rel="nofollow external" target="_blank">speaking at events</a> is where my focus goes.&nbsp;</p>
# <p>I just had to renew my Apple Developer membership while they were down for 3 weeks and the app was removed from the app store. They have since put it back after their developer center came online August 10th. After renewing the annual membership I decided to list it here so someone could scale this to the level it demands.</p>
# <p>My goal for this was millions of users. This is still more than possible if properly promoted.</p>
# <p>&nbsp;</p>
# <p><strong>About Me<br></strong>My name is Brad Gosse. I have been an online entrepreneur for over 15 years and have written a best selling book called&nbsp;<a href="http://amzn.com/1470158647" rel="nofollow external" target="_blank">Chronic Marketer</a>. Google me. I have been around a long time and have a good reputation online. I have also quickly gained a good reputation here on Flippa for truthful listings, quick turnarounds and smooth transitions. Ask any of my previous buyers.</p>
# <p>&nbsp;</p>
# <p><strong>Access to my mentorship is priceless<br></strong>Buying a website from me is more than a simple business deal. This opens the door to me and my network of affiliates. You will get access to a community, and to help from me 1-1. I currently charge&nbsp;<a href="http://nohy.pe/bookbrad" rel="nofollow external" target="_blank">$2000 for a single hour of my time</a>&nbsp;because I am so busy with other projects. Buying a business from me is sometimes the best way to get direct access.</p>
# <p>Again feel free to Google me to see why this is so valuable.</p>
# <p>&nbsp;</p>
# <p><strong>What you get</strong></p>
# <ul>
# <li>The native iOS iphone/iPad app Frampix and all source code.</li>
# <li>The 2 domains FramPix.com and fmpx.me</li>
# <li>The URL Shortner database and software</li>
# <li>The Wordpress Database and images</li>
# <li>Thousands of email and twitter WP user profiles</li>
# <li>A giant library of exclusively designed vector photo frames.</li>
# </ul><p>&nbsp;</p>
# <p><strong>Payment<br></strong>I will accept PayPal payments from a verified account with an on file address. I will ship all contracts/licenses and bill of sale to this address via Fedex. I will also accept Visa, Mastercard, Amex and Wire transfer.</p>
# <p>I even accept Bitcoin :)</p>
# <p>&nbsp;</p>
# <p><strong>I look forward to working with you.<br></strong>As a successful bidder you will get access to me and my team to make this the easiest business purchase possible. I will also spend time with you over Skype to discuss how you might scale this business. Thanks for your bids! :)</p>		</div>"""
#
#     search_url = 'http://itunes.apple.com/lookup?id=639384326'
#     raw = urllib.urlopen(search_url)
#     js = raw.read()
#     js_object = json.loads(js)
#     results = js_object["results"][0]
#     icon = results['artworkUrl60']
#     return render_to_response('query/listing_detail.html',
#                               {"json_objects": js_object["resultCount"],
#                                "icon": icon, "detail_content":description_detail},
#                               context_instance=RequestContext(request))
