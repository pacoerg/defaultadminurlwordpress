# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         sfp_defaultwordpressadminurl
# Purpose:      Search in a domain if there is the default url for wordpress admin.
#
# Author:      Francisco Simón Molina <pacoerg@gmail.com>
#
# Created:     13/02/2022
# Copyright:   (c) Francisco Simón Molina 2022
# Licence:     GPL
# -------------------------------------------------------------------------------
import requests #import to check URL
import json
from netaddr import IPNetwork
from spiderfoot import SpiderFootEvent, SpiderFootPlugin


class sfp_defaultwordpressadminurl(SpiderFootPlugin):

    meta = {
        'name': "Default Wordpress Admin URL check",
        'summary': "Check if a domain has a Worpress site with default admin form URL",
        'flags': [""],
        'useCases': ["Custom"],
        'categories': ["Passive"]
    }

    # Default options
    opts = {
    }

    # Option descriptions
    optdescs = {
    }

    results = None

    def setup(self, sfc, userOpts=dict()):
        self.sf = sfc
        self.results = self.tempStorage()

        for opt in list(userOpts.keys()):
            self.opts[opt] = userOpts[opt]

    # What events is this module interested in for input
    def watchedEvents(self):
        return ["DOMAIN_NAME"] #Solo poner nombre del dominio, NO SUBDOMMINIOS

    # What events this module produces
    # This is to support the end user in selecting modules based on events
    # produced.
    def producedEvents(self):
        return ["URL_FORM"]

    # Handle events sent to this module
    def handleEvent(self, event):
        eventName = event.eventType
        srcModuleName = event.module
        eventData = event.data

        if eventData in self.results:
            return

        self.results[eventData] = True

        self.sf.debug(f"Received event, {eventName}, from {srcModuleName}")

        try:
            data = None

            self.sf.debug(f"We use the data: {eventData}")
            print(f"We use the data: {eventData}")

            ########################
            # INICIO DE MI CÓDIGO
            #
            # NOTA: Dado el retraso en las prácticas que llevo, no he añadido otras funcionalidades
            # que se podrían añadir, como por ejemplo, que realice la búsqueda en todos
            # los subdominios del dominio principal dado
            #
             
            # Creamos una variable con el dominio y el archivo por defecto del login de administración de Wordpress 
            urlAdminWP = eventData+'/wp-login.php' 
            
            # Probamos a checkear si existe la URL
            try:
                # Probamos primero en caso de tener habilitado HTTPS
                respuesta = requests.get('https://'+urlAdminWP)

                if respuesta.status_code == 200:
                    # Si tiene habilitado habilitado HTTPS Y la URL existe, entonces tenemos un "POSITIVO" y lo enviamos a Spiderfoot
                    # Si no tiene HTTPS habilitado, simplemente dará un error que nos enviará al EXCEPTIO, por lo que no pasará por el ELSE
                    data = 'https://'+urlAdminWP
                else:
                    # Si tiene HTTPS habilitado, pero no existe la URL por defecto de Wordpress, envía a Spiderfoot el siguiente mensaje
                    data = "No default admin Wordpress HTTPS in "+eventData+" domain"

            # El dominio probado, no tiene habilitado HTTPS
            except:
                # Probamos la URL pero con HTTP
                respuesta = requests.get('http://'+urlAdminWP)

                if respuesta.status_code == 200:
                    # Si la encuentra, entonces enviamos a Spiderfoot, la URL encontrada
                    data = 'http://'+urlAdminWP
                else:
                    # Si llega aquí es porque ni en HTTPS ni en HTTP, existe la ruta de admin por defecto de Wordpress, enviamos el siguiente mensaje
                    data = "No default admin Wordpress HTTP in "+eventData+" domain"
            #
            #
            # FIN DE MI CÓDIGO
            ########################
            
            if not data:
                self.sf.error("Unable to perform <ACTION MODULE> on " + eventData)
                return
        except Exception as e:
            self.sf.error("Unable to perform the <ACTION MODULE> on " + eventData + ": " + str(e))
            return
        
        #typ = "DOMAIN_NAME"
        #typ = data
        #data = "newdomaintest.com"
        

        evt = SpiderFootEvent("URL_FORM", data, self.__name__, event)
        self.notifyListeners(evt)

# End of sfp_new_module class
