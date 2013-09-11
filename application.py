# -*- coding: utf-8 -*-

# This file is part of JSB 16+.
#
# Copyright (C) 2013 Hugo Herter
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


'''
    Web app for JSB 16+, handles user profiles, registration to activities
    and login via Mozilla Persona.
    
    This is prototype work. Do not consider close from stable or as using
    good practices.
'''

import os
current_dir = os.path.dirname(os.path.abspath(__file__))
 
import cherrypy
import requests

from cherrypy.lib.static import serve_file

# Local project imports:
import config
from profile import Profile, page as profile_page

cherrypy.config.update({'tools.sessions.on': True,
                        'server.socket_host': '0.0.0.0',
                        'server.socket_port': 1616,
                        })

current_dir = os.path.dirname(os.path.abspath(__file__))
 
def signed_in():
    'Returns True if the user is connected.'
    return 'identifier' in cherrypy.session


class Root(object):
    '''
        Root of the CherryPy web app.
    '''

    @cherrypy.expose
    def index(self):
        # TODO: Use static access to static pages.
        if signed_in():
            value = open('templates/index-member.html').read()
            value = value.replace('IDENTIFIER', str(cherrypy.session['identifier']))
        else:
            value = open('templates/index-guest.html')
        return value

    @cherrypy.expose
    def profil(self, **kwargs):
        '''
            Displays user's profile and allows him to edit it.
        '''
        if signed_in():
            profile = Profile(cherrypy.session['identifier'])

            # Update:
            if cherrypy.request.method == 'POST':
                profile.update(kwargs)
                profile.save()
                return unicode(profile_page(profile, u'Profil mis a jour'))
            # Reading:
            else:
                return unicode(profile_page(profile))
        else:
            raise cherrypy.HTTPError(401, u'Vous devez vous connecter')

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    def inscription(self, event):
        '''
            Allows users to register to a certain event.
        '''
        
        # Only allowing alphanumeric event identifiers:
        if not event.isalnum():
            raise cherrypy.HTTPError(404, u'Mauvais identifiant')
           
        if signed_in():
            path = os.path.join(config.REGISTRATIONS_PATH, event + '.txt')
            if os.path.isfile(path):
                identifier = cherrypy.session['identifier']
                
                # Checking if user already registrered:
                if identifier in (line.strip() for line in open(path).readlines()):
                    return u'Vous etiez deja inscrit a cette activite.'
                else:
                    # TODO: evolve to a more sophisticated system than appending
                    # the user ID to a text file.
                    open(path, 'a').write(identifier + '\n')
                    return u'Votre inscription a {} est dans la poche.'.format(event)
            else:
                raise cherrypy.HTTPError(404, 'Evenement inconnu')
        else:
            raise cherrypy.HTTPError(401, u'Vous devez vous connecter')
            
    
    @cherrypy.expose
    def update(self):
        ''' Pulls and checkouts the 'latest' repository. Used to update static files. '''
        here = os.getcwd()
        os.chdir(config.repository_latest)
        yield u'Telechargement...\n'
        os.system('git pull')
        yield u'Mise en place...\n'
        os.system('git checkout .')
        os.chdir(here)
        yield u'Nouvelle version active.\n'
    

    @cherrypy.expose
    def static(self, filename):
        return serve_file(os.path.join(current_dir, 'static', filename))
                        #content_type='application/xml')


class Persona(object):
    'Mozilla Persona'

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    def signin(self, assertion):
        
        # Validating Mozilla Persona login info:
        assertion_info = {'assertion': assertion,
                          'audience': config.hostname } # window.location.host
        resp = requests.post('https://verifier.login.persona.org/verify',
                             data=assertion_info, verify=True)
        if not resp.ok:
            raise cherrypy.HTTPError(500)

        data = resp.json()

        if data['status'] == 'okay':
            cherrypy.session.update({'identifier': data['email']})
            # Creating a profile for the user if it does not exist.
            profile = Profile(cherrypy.session['identifier'])
            profile.save()
            return resp.content

    @cherrypy.expose
    def signout(self):
        cherrypy.session.pop('identifier', None)
        return u'You are now disconnected'


def application(environ, start_response):
    # WSGI launch:
    root = Root()
    root.persona = Persona()
    cherrypy.tree.mount(root, '/', None)
    return cherrypy.tree(environ, start_response)

if __name__ == '__main__':
    # CherryPy launch:
    root = Root()
    root.persona = Persona()
    cherrypy.quickstart(root)
