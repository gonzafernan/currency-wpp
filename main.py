"""
Launch ngrok (app in localhost port 5000): $ngrok http 5000
See https://www.twilio.com/console in order to configure host url: https://ngrok-forward.ngrok.io/bot
"""

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests

from msg_processing import process_msg
from exchangerate import pair_conversion

app = Flask(__name__)


@app.route('/bot', methods=['POST'])
def bot():
    """
    Webhook
    The application defines a /bot endpoint that listens to POST requests.
    Each time an incoming message from a user is received by Twilio, they will in turn invoke this endpoint.
    The body of the function bot() is going to analyze the message sent by the user and provide the appropriate response
    """

    # add webhook logic here and return a response
    # The message comes in the payload of the POST request with a key of ’Body’.
    # We can access it through Flask’s request object.
    incoming_msg = request.values.get('Body', '').lower()

    # The response that Twilio expects from the webhook needs to be given in TwiML or Twilio Markup Language,
    # which is an XML-based language. Create a response that includes text and media components.
    resp = MessagingResponse()
    msg = resp.message()

    # Process incoming message
    lang, amount, base_unit, target_unit = process_msg(incoming_msg)

    # Begin reply crafting
    responded = False

    # More than one value identified
    if amount < 0:
        if lang == '__label__es':
            error_msg = "Por favor, brindeme un único monto a convertir."
        elif lang == '__label__fr':
            error_msg = "Veuillez me donner un seul montant à convertir."
        else:
            error_msg = "Please give me a single amount to convert."

        msg.body(error_msg)
        return str(resp)

    # More or less than two currencies to convert
    if not base_unit or not target_unit:
        if lang == '__label__es':
            error_msg = "Por favor, proporcioname dos monedas a convertir."
        elif lang == '__label__fr':
            error_msg = "Veuillez me fournir deux devises à convertir."
        else:
            error_msg = "Please provide me with two currencies to convert."

        msg.body(error_msg)
        return str(resp)

    # API call for conversion
    conversion_result = pair_conversion(base_unit, target_unit, amount)

    # Check for API call success
    if conversion_result == 0:
        if lang == '__label__es':
            error_msg = "No puedo realizar la conversión en este momento."
        elif lang == '__label__fr':
            error_msg = "Je ne peux pas realiser la conversion maintenant."
        else:
            error_msg = "I can't make the conversion in this moment."

        msg.body(error_msg)
        return str(resp)

    # Simple currency price
    if amount == 0:
        if lang == '__label__es':
            reply_msg = "El precio del " + str(base_unit) + " es de " + \
                        str(conversion_result) + " " + str(target_unit) + "."
        elif lang == '__label__fr':
            reply_msg = "Le prix du " + str(base_unit) + " est de " + str(conversion_result) + \
                        " " + str(target_unit) + "."
        else:
            reply_msg = "The price of the " + str(base_unit) + " is " + str(conversion_result) + \
                        " " + str(target_unit) + "."

        msg.body(reply_msg)
        return str(resp)

    if amount > 0:
        if lang == '__label__es':
            reply_msg = str(amount) + str(base_unit) + " corresponde a " + \
                        str(conversion_result) + " " + str(target_unit) + "."
        elif lang == '__label__fr':
            reply_msg = str(amount) + str(base_unit) + " est " + \
                        str(conversion_result) + " " + str(target_unit) + "."
        else:
            reply_msg = str(amount) + str(base_unit) + " are " + \
                        str(conversion_result) + " " + str(target_unit) + "."

        msg.body(reply_msg)
        return str(resp)

    """
    responded = False
    if 'quote' in incoming_msg:
        # return a quote
        r = requests.get('https://api.quotable.io/random')
        if r.status_code == 200:
            data = r.json()
            quote = f'{data["content"]} ({data["author"]})'
        else:
            quote = 'I could not retrieve a quote at this time, sorry.'
        msg.body(quote)
        responded = True
    if 'cat' in incoming_msg:
        # return a cat pic
        msg.media('https://cataas.com/cat')
        responded = True
    if not responded:
        msg.body('I only know about famous quotes and cats, sorry!')
    """


if __name__ == '__main__':
    print("Hello world!")
    app.run()

