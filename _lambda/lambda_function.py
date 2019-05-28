# -*- coding: utf-8 -*-

import logging
import json
import random
import math
import re

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name, viewport
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective, ExecuteCommandsDirective, SpeakItemCommand,
    AutoPageCommand, HighlightMode)

from typing import Dict, Any


SKILL_NAME = "Mi Peso"
WELCOME_MESSAGE = ("<speak>Bienvenido a la Skill de "+SKILL_NAME+", aquí podré calcular tu <sub alias=\"I M C\">IMC</sub>, solo dime tu peso y estatura. <break time=\"500ms\"/> Si necesitas ayuda, solo dí: 'Ayuda'. Recuerda que este diagnostico es únicamente con fines informativos y educativos, y no es un sustituto del asesoramiento, tratamiento o diagnóstico médico profesional. Llame a su médico para recibir asesoramiento médico. ¿Qué deseas realizar? </speak>")
HELP_MESSAGE = ('''<speak> 
    <p>Si deseas tu <sub alias=\"I M C\">IMC</sub>, puedes pedirme: <s>"Alexa, abre '''+SKILL_NAME+''' y dime cómo estoy"<break time=\"500ms\"/> </s> </p> 
    <p>También, puedes decirme: <s>"Calcula mi <sub alias=\"I M C\">IMC</sub>"<break time=\"500ms\"/> </s> </p> 
    <p>Si deseas saber que es el <sub alias=\"I M C\">IMC</sub>, puedes decirme: <s>"Quiero saber qué es <sub alias=\"I M C\">IMC</sub>"<break time=\"500ms\"/> </s> </p> 
    ¿Qué deseas realizar?
    </speak>''')
HELP_REPROMPT = (HELP_MESSAGE)
STOP_MESSAGE = "Gracias por usar esta skill. ¡Adiós! "
EXCEPTION_MESSAGE = "No entendí muy bien, ¿Qué deseas realizar?"

sb = SkillBuilder()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def apl_img_title_text(title, text):
    return {
    "json" :"apl_img_title_text.json",
                    "datasources" : {
                    "bodyTemplate1Data": {
                        "type": "object",
                        "objectId": "bt1Sample",
                        "backgroundImage": {
                            "contentDescription": None,
                            "smallSourceUrl": None,
                            "largeSourceUrl": None,
                            "sources": [
                                {
                                    "url": "https://www.comoquedarembarazada10.com/wp-content/uploads/2017/12/Cuanto-debo-pesar-para-quedar-embarazada-2.jpg",
                                    "size": "small",
                                    "widthPixels": 0,
                                    "heightPixels": 0
                                },
                                {
                                    "url": "https://www.comoquedarembarazada10.com/wp-content/uploads/2017/12/Cuanto-debo-pesar-para-quedar-embarazada-2.jpg",
                                    "size": "large",
                                    "widthPixels": 0,
                                    "heightPixels": 0
                                }
                            ]
                        },
                        "title": title,
                        "textContent": {
                            "primaryText": {
                                "type": "PlainText",
                                "text": text
                            }
                        },
                        "logoUrl": "https://es.calcuworld.com/wp-content/uploads/sites/2/2013/02/imc.png"
                    }
                }
            }

def _load_apl_document(file_path):
    # type: (str) -> Dict[str, Any]
    """Load the apl json document at the path into a dict object."""
    with open(file_path) as f:
        return json.load(f)
        
def _imc(peso, estatura):
    
    IMC=peso/(estatura/100)**2
    
    provoca = ""
    tipo = "" 
    mensaje = ""
    recomendacion = ""
    diagnostico = ""
    
    if IMC < 5:
        tipo = "Delgadez 3"
        diagnostico = "Delgadez de nivel 3, tienes un peso demasiado bajo"
        provoca = "te puede causar: Postración, Atenia, Adinamia, Enfermedades Degenerativas y Peligro de Muerte."
    elif IMC >= 5 and IMC < 10:
        tipo = "Delgadez 2"
        diagnostico = "Delgadez de nivel 2, tienes un peso muy bajo"
        provoca = "te puede causar: Anorexia, Bulimia, Osteoporosis y Autoconsumo de Masa Muscular."
    elif IMC >= 10 and IMC < 18.5:
        tipo = "Delgadez 1"
        diagnostico = "Delgadez de nivel 1, tienes un peso bajo"
        provoca = "te puede causar: Trastornos Digestivos, Debilidad, Fatiga Crónica, Estrés, Ansiedad y Delifusión Hormonal."
    elif IMC >= 18.5 and IMC < 25:
        tipo = "Peso Normal"
        diagnostico = "Tu peso es normal, felicidades"
        provoca = "tienes un Estado Normal, Buen Nivel de Energía, Vitalidad y Buena Condición Física."
    elif IMC >= 25 and IMC < 30:
        tipo = "Sobrepeso"
        diagnostico = "Tienes sobrepeso, vigila tu dieta"
        provoca = "te puede causar: Fatiga, Enfermedades Digestivas, Problemas Cardíacos, Mala Circulación en piernas y Várices."
    elif IMC >= 30 and IMC < 35:
        tipo = "Obesidad 1"
        diagnostico = "Obesidad nivel 1, consulta a tu médico"
        provoca = "te puede causar: Diabetes, Hipertensión, Enfermedades Cardiovasculares, Problemas Articulares, Rodilla y Columna, Cálculos Biliares."
    elif IMC >= 35 and IMC < 40:
        tipo = "Obesidad 2"
        diagnostico = "Obesidad nivel 2, consulta a tu médico"
        provoca = "te puede causar: Diabetes, Cáncer, Angina de Pecho, Infartos, Tromboflebitis, Arterosclerosis, Embolias, Alteraciones de Menstruación."
    elif IMC>=40:
        tipo = "Obesidad 3"
        diagnostico = "Obesidad grave de nivel 3, consulta a tu médico"
        provoca = "te puede causar: Falta de Aire, Somnolencia, Trombosis Pulmonar, Úlceras Varicosas, Cáncer de Próstata, Reflujo Esofágico."
    
    peso_ideal = estatura -100 - ( (estatura - 150) / 4 )
    recomendacion = ""
    if IMC <18.5 or IMC >=25:
        recomendacion = "Tu peso ideal es de aproximadamente {:.0f} kg te recomiendo {} de {:.0f} a {:.0f} kg.".format(peso_ideal, 'bajar' if (peso-peso_ideal) >= 0  else 'subir', abs(peso-peso_ideal) - 4 ,abs(peso-peso_ideal))
    
    recomendacion = recomendacion +" Recuerda que este diagnostico es únicamente con fines informativos y educativos, y no es un sustituto del asesoramiento, tratamiento o diagnóstico médico profesional. Llame a su médico para recibir asesoramiento médico."
    
    return ("{}, {} {} ".format(diagnostico, provoca, recomendacion))

# Built-in Intent Handlers
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LaunchRequest")


        speech = WELCOME_MESSAGE

        apl = apl_img_title_text("Bienvenido", re.sub('<[^<]+>', "",WELCOME_MESSAGE))
        
        if viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_LARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_MEDIUM or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_ROUND_SMALL or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.TV_LANDSCAPE_XLARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.MOBILE_LANDSCAPE_SMALL:
            handler_input.response_builder.speak(speech).add_directive(
                RenderDocumentDirective(document=_load_apl_document(apl["json"]),datasources=apl["datasources"])
            ).set_should_end_session(False)
        else:
            handler_input.response_builder.speak(speech).ask(HELP_REPROMPT).set_card(SimpleCard(SKILL_NAME, re.sub('<[^<]+>', "",speech))).set_should_end_session(False)
        #handler_input.response_builder.speak(speech).ask(speech).set_card(
        #    SimpleCard(SKILL_NAME, speech))
        return handler_input.response_builder.response




class PesoIntentHandler(AbstractRequestHandler):
    """Handler for Device Information Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("PesoIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("Peso Intent")

        speech = "No entendí muy bien"+ ". ¿Qué más deseas realizar?"
    
        card_title = SKILL_NAME
        card_content = "No entendí muy bien"
        
        
        slots = handler_input.request_envelope.request.intent.slots
        
        try:
            peso = int(slots["kg"].value)
        except:
            peso = -1 # ALEXA no reconoce el 40 -> cuarenta
            
        #attr = handler_input.attributes_manager.persistent_attributes
        session_attr = handler_input.attributes_manager.session_attributes
        
        session_attr['peso'] = peso
        
        try:
            estatura = session_attr['estatura']
        except:
            estatura = -1
        
        
        
        speech =  "Pesas "+str(peso)+" kg. "+ ( "mides "+str(estatura)+" cm " if estatura > -1 else "¿Cuánto mides en centímetros?" )
        session_attr['pregunta_anterior'] = 'estatura'
        
      
        if session_attr['estatura'] > -1 and session_attr['peso'] > -1:
            speech =  "Mides "+str(estatura)+" cm y pesas "+str(peso)+" kg. "
            speech = speech + _imc(peso, estatura) + ". ¿Qué más deseas realizar?"
            
            session_attr['pregunta_anterior'] = ''
            session_attr['estatura'] = -1
            session_attr['peso'] = -1
        
        card_content = speech
            
        apl = apl_img_title_text(card_title, card_content)
        
        if viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_ROUND_SMALL:
            
            apl = apl_img_title_text(card_title, card_content)
            
            handler_input.response_builder.speak(speech).ask(HELP_REPROMPT).add_directive(
            RenderDocumentDirective(document=_load_apl_document(apl["json"]),datasources=apl["datasources"])
            ).set_should_end_session(False)
        elif viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_LARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_MEDIUM or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_ROUND_SMALL or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.TV_LANDSCAPE_XLARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.MOBILE_LANDSCAPE_SMALL:
            handler_input.response_builder.speak(speech).ask(HELP_REPROMPT).add_directive(
            RenderDocumentDirective(document=_load_apl_document(apl["json"]),datasources=apl["datasources"])
            ).set_should_end_session(False)
        else:
            handler_input.response_builder.speak(speech).ask(HELP_REPROMPT).set_card(SimpleCard(SKILL_NAME, re.sub('<[^<]+>', "",speech))).set_should_end_session(False)
            
        

        return handler_input.response_builder.response
        
class EstaturaIntentHandler(AbstractRequestHandler):
    """Handler for Device Information Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("EstaturaIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("Estatura Intent")

        speech = "No entendí muy bien"+ ". ¿Qué más deseas realizar?"
    
        card_title = SKILL_NAME
        card_content = "No entendí muy bien"
        
        
        slots = handler_input.request_envelope.request.intent.slots
        peso = -1
        estatura = -1
        
        try:
            estatura = int(slots["cm"].value)
        except:
            estatura = -1
            
        try:
            estatura_mts = int(slots["mt"].value)
        except:
            estatura_mts = 0
            
        estatura = estatura + estatura_mts
        
        #attr = handler_input.attributes_manager.persistent_attributes
        session_attr = handler_input.attributes_manager.session_attributes
            
        if session_attr['pregunta_anterior'] == 'estatura' or session_attr['pregunta_anterior'] == '' or session_attr['pregunta_anterior'] is None:
            session_attr['estatura'] = estatura
        
            try:
                estatura = session_attr['estatura']
            except:
                estatura = -1
            
            
            card_content = ""
            speech =  ( "Mides "+str(session_attr['estatura'])+" cm " + "¿Cuánto pesas en kilogramos?" )
            session_attr['pregunta_anterior'] = 'peso'
            
        elif session_attr['pregunta_anterior'] == 'peso':
        
            session_attr['peso'] = estatura
            
            try:
                peso = session_attr['peso']
            except:
                peso = -1
            
            speech =  ( "Pesas "+str(peso)+" kg. " + "¿Cuánto mides en centímetros?" )
            session_attr['pregunta_anterior'] = 'estatura'
            
            
            
        
        if session_attr['estatura'] > -1 and session_attr['peso'] > -1:
            speech =  "Mides "+str(session_attr['estatura'])+" cm y pesas "+str(session_attr['peso'])+" kg. "
            speech = speech + _imc(session_attr['peso'], session_attr['estatura']) + ". ¿Qué más deseas realizar?"
            
            session_attr['pregunta_anterior'] = ''
            session_attr['estatura'] = -1
            session_attr['peso'] = -1
            
        card_content = speech      
        
            
        apl = apl_img_title_text(card_title, card_content)
        
        if viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_ROUND_SMALL:
            
            apl = apl_img_title_text(card_title, card_content)
            
            handler_input.response_builder.speak(speech).ask(HELP_REPROMPT).add_directive(
            RenderDocumentDirective(document=_load_apl_document(apl["json"]),datasources=apl["datasources"])
            ).set_should_end_session(False)
        elif viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_LARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_MEDIUM or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_ROUND_SMALL or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.TV_LANDSCAPE_XLARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.MOBILE_LANDSCAPE_SMALL:
            handler_input.response_builder.speak(speech).ask(HELP_REPROMPT).add_directive(
            RenderDocumentDirective(document=_load_apl_document(apl["json"]),datasources=apl["datasources"])
            ).set_should_end_session(False)
        else:
            handler_input.response_builder.speak(speech).ask(HELP_REPROMPT).set_card(SimpleCard(SKILL_NAME, re.sub('<[^<]+>', "",speech))).set_should_end_session(False)
            
        

        return handler_input.response_builder.response
        
        
class CuarentaIntentHandler(AbstractRequestHandler):
    """Handler for Device Information Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("CuarentaIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("Estatura Intent")

        speech = "No entendí muy bien"+ ". ¿Qué más deseas realizar?"
    
        card_title = SKILL_NAME
        card_content = "No entendí muy bien"
        
        
        slots = handler_input.request_envelope.request.intent.slots
        peso = -1
        estatura = -1
        
        
        #attr = handler_input.attributes_manager.persistent_attributes
        session_attr = handler_input.attributes_manager.session_attributes
            
        if session_attr['pregunta_anterior'] == 'estatura' or session_attr['pregunta_anterior'] == '' or session_attr['pregunta_anterior'] is None:
            session_attr['estatura'] = 40
        
            try:
                estatura = session_attr['estatura']
            except:
                estatura = -1
            
            
            card_content = ""
            speech =  ( "Mides "+str(session_attr['estatura'])+" cm " + "¿Cuánto pesas en kilogramos?" )
            session_attr['pregunta_anterior'] = 'peso'
            
        elif session_attr['pregunta_anterior'] == 'peso':
        
            session_attr['peso'] = 40
            
            try:
                peso = session_attr['peso']
            except:
                peso = -1
            
            speech =  ( "Pesas "+str(peso)+" kg. " + "¿Cuánto mides en centímetros?" )
            session_attr['pregunta_anterior'] = 'estatura'
            
            
            
        
        if session_attr['estatura'] > -1 and session_attr['peso'] > -1:
            speech =  "Mides "+str(session_attr['estatura'])+" cm y pesas "+str(session_attr['peso'])+" kg. "
            speech = speech + _imc(session_attr['peso'], session_attr['estatura']) + ". ¿Qué más deseas realizar?"
            
            session_attr['pregunta_anterior'] = ''
            session_attr['estatura'] = -1
            session_attr['peso'] = -1
            
        card_content = speech      
        
            
        apl = apl_img_title_text(card_title, card_content)
        
        if viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_ROUND_SMALL:
            
            apl = apl_img_title_text(card_title, card_content)
            
            handler_input.response_builder.speak(speech).ask(HELP_REPROMPT).add_directive(
            RenderDocumentDirective(document=_load_apl_document(apl["json"]),datasources=apl["datasources"])
            ).set_should_end_session(False)
        elif viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_LARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_MEDIUM or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_ROUND_SMALL or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.TV_LANDSCAPE_XLARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.MOBILE_LANDSCAPE_SMALL:
            handler_input.response_builder.speak(speech).ask(HELP_REPROMPT).add_directive(
            RenderDocumentDirective(document=_load_apl_document(apl["json"]),datasources=apl["datasources"])
            ).set_should_end_session(False)
        else:
            handler_input.response_builder.speak(speech).ask(HELP_REPROMPT).set_card(SimpleCard(SKILL_NAME, re.sub('<[^<]+>', "",speech))).set_should_end_session(False)
            
        

        return handler_input.response_builder.response
   

class PesoEstaturaIntentHandler(AbstractRequestHandler):
    """Handler for Device Information Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("PesoEstaturaIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("PesoEstatura Intent")

        speech = "No entendí muy bien"+ ". ¿Qué más deseas realizar?"
    
        card_title = SKILL_NAME
        card_content = "No entendí muy bien"
        
        
        slots = handler_input.request_envelope.request.intent.slots
        
        try:
            estatura = int(slots["cm"].value)
        except:
            estatura = -1
            
        try:
            estatura_mts = int(slots["mt"].value)
        except:
            estatura_mts = 0
            
        try:
            peso = int(slots["kg"].value)
        except:
            peso = -1
            
        estatura = estatura + estatura_mts
            
        #attr = handler_input.attributes_manager.persistent_attributes
        session_attr = handler_input.attributes_manager.session_attributes
        
        session_attr['estatura'] = estatura
        session_attr['peso'] = peso
        
        
        
        
        if session_attr['estatura'] > -1 and session_attr['peso'] > -1:
            speech =  "Mides "+str(estatura)+" cm y pesas "+str(peso)+" kg. "
            speech = speech + _imc(peso, estatura) + ". ¿Qué más deseas realizar?"
            
            session_attr['pregunta_anterior'] = ''
            session_attr['estatura'] = -1
            session_attr['peso'] = -1
            
        card_content = speech
        
            
        apl = apl_img_title_text(card_title, card_content)
        
        if viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_ROUND_SMALL:
            
            apl = apl_img_title_text(card_title, card_content)
            
            handler_input.response_builder.speak(speech).ask(HELP_REPROMPT).add_directive(
            RenderDocumentDirective(document=_load_apl_document(apl["json"]),datasources=apl["datasources"])
            ).set_should_end_session(False)
        elif viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_LARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_MEDIUM or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_ROUND_SMALL or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.TV_LANDSCAPE_XLARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.MOBILE_LANDSCAPE_SMALL:
            handler_input.response_builder.speak(speech).ask(HELP_REPROMPT).add_directive(
            RenderDocumentDirective(document=_load_apl_document(apl["json"]),datasources=apl["datasources"])
            ).set_should_end_session(False)
        else:
            handler_input.response_builder.speak(speech).ask(HELP_REPROMPT).set_card(SimpleCard(SKILL_NAME, re.sub('<[^<]+>', "",speech))).set_should_end_session(False)
            
        

        return handler_input.response_builder.response
   
   

class CalcularImcIntentHandler(AbstractRequestHandler):
    """Handler for Device Information Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("CalcularImcIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("CalcularImc Intent")

        speech = "No entendí muy bien"+ ". ¿Qué más deseas realizar?"
    
        card_title = SKILL_NAME
        card_content = "No entendí muy bien"
        
        
        
        
        
        session_attr = handler_input.attributes_manager.session_attributes
        
        session_attr['estatura'] = -1
        session_attr['peso'] = -1
        
        
        speech = "Muy bien, ¿Dime cuántos kilos pesas?"
        session_attr['pregunta_anterior'] = 'peso'
        card_content = speech
        
            
        apl = apl_img_title_text(card_title, card_content)
        
        if viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_ROUND_SMALL:
            
            apl = apl_img_title_text(card_title, card_content)
            
            handler_input.response_builder.speak(speech).ask(HELP_REPROMPT).add_directive(
            RenderDocumentDirective(document=_load_apl_document(apl["json"]),datasources=apl["datasources"])
            ).set_should_end_session(False)
        elif viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_LARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_MEDIUM or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_ROUND_SMALL or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.TV_LANDSCAPE_XLARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.MOBILE_LANDSCAPE_SMALL:
            handler_input.response_builder.speak(speech).ask(HELP_REPROMPT).add_directive(
            RenderDocumentDirective(document=_load_apl_document(apl["json"]),datasources=apl["datasources"])
            ).set_should_end_session(False)
        else:
            handler_input.response_builder.speak(speech).ask(HELP_REPROMPT).set_card(SimpleCard(SKILL_NAME, re.sub('<[^<]+>', "",speech))).set_should_end_session(False)
            
        

        return handler_input.response_builder.response  
        
class ImcIntentHandler(AbstractRequestHandler):
    """Handler for Device Information Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("ImcIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("Imc Intent")

        speech = "No entendí muy bien"+ ". ¿Qué más deseas realizar?"
    
        card_title = SKILL_NAME
        card_content = "No entendí muy bien"
        
        
        
        
        
        speech = "El Índice de Masa Corporal (<sub alias=\"I M C\">IMC</sub>) es el resultado de la relación entre tu peso y tu estatura, es uno de los métodos más utilizados y prácticos para identificar el grado de riesgo asociado con la obesidad. Tu salud es una razón de peso, ¡te invitamos a calcular el tuyo!. ¿Qué más deseas realizar?"
        card_content = "El Índice de Masa Corporal IMC es el resultado de la relación entre tu peso y tu estatura, es uno de los métodos más utilizados y prácticos para identificar el grado de riesgo asociado con la obesidad. Tu salud es una razón de peso, ¡te invitamos a calcular el tuyo!. ¿Qué más deseas realizar?"
        
            
        apl = apl_img_title_text(card_title, card_content)
        
        if viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_ROUND_SMALL:
            
            apl = apl_img_title_text(card_title, card_content)
            
            handler_input.response_builder.speak(speech).ask(HELP_REPROMPT).add_directive(
            RenderDocumentDirective(document=_load_apl_document(apl["json"]),datasources=apl["datasources"])
            ).set_should_end_session(False)
        elif viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_LARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_LANDSCAPE_MEDIUM or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.HUB_ROUND_SMALL or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.TV_LANDSCAPE_XLARGE or viewport.get_viewport_profile(handler_input.request_envelope) == viewport.ViewportProfile.MOBILE_LANDSCAPE_SMALL:
            handler_input.response_builder.speak(speech).ask(HELP_REPROMPT).add_directive(
            RenderDocumentDirective(document=_load_apl_document(apl["json"]),datasources=apl["datasources"])
            ).set_should_end_session(False)
        else:
            handler_input.response_builder.speak(speech).ask(HELP_REPROMPT).set_card(SimpleCard(SKILL_NAME, re.sub('<[^<]+>', "",speech))).set_should_end_session(False)
            
        

        return handler_input.response_builder.response        
        
class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ( is_intent_name("AMAZON.HelpIntent")(handler_input) or
                is_intent_name("AyudaIntent")(handler_input) )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")

        handler_input.response_builder.speak(HELP_MESSAGE).ask(
            HELP_REPROMPT).set_card(SimpleCard(
                SKILL_NAME, re.sub('<[^<]+>', "",HELP_MESSAGE)))
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input) or
                is_intent_name("SalirIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CancelOrStopIntentHandler")

        handler_input.response_builder.speak(STOP_MESSAGE).set_should_end_session(True)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedRequestHandler")

        logger.info("Session ended reason: {}".format(
            handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response


# Exception Handler
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.info("In CatchAllExceptionHandler")
        logger.error(exception, exc_info=True)

        handler_input.response_builder.speak(EXCEPTION_MESSAGE).ask(
            HELP_REPROMPT)

        return handler_input.response_builder.response


# Request and Response loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the alexa requests."""
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the alexa responses."""
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.debug("Alexa Response: {}".format(response))


# Register intent handlers
sb.add_request_handler(LaunchRequestHandler())

sb.add_request_handler(PesoEstaturaIntentHandler())
sb.add_request_handler(EstaturaIntentHandler())
sb.add_request_handler(CuarentaIntentHandler())
sb.add_request_handler(PesoIntentHandler())
#sb.add_request_handler(TopicoAleatorioIntentHandler())
#sb.add_request_handler(SalirIntentHandler())



sb.add_request_handler(CalcularImcIntentHandler())
sb.add_request_handler(ImcIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Register exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

# TODO: Uncomment the following lines of code for request, response logs.
# sb.add_global_request_interceptor(RequestLogger())
# sb.add_global_response_interceptor(ResponseLogger())

# Handler name that is used on AWS lambda
lambda_handler = sb.lambda_handler()
