# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls import include, url
from django.contrib import admin

from .views import HomePage, AboutPage
from accounts import urls as accounts_urls
from profiles import urls as profiles_urls

urlpatterns = [
    url(r'^$', HomePage.as_view(), name='home'),
    url(r'^about/$', AboutPage.as_view(), name='about'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/', include(profiles_urls, namespace='profiles')),
    url(r'^', include(accounts_urls, namespace='accounts')),

]
