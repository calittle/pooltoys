// (C) 2019 C.A. Little 
// MIT License
// This lambda function is used to grab a data feed and parse it, rendering a response
// To Do:
// include authorization with the data source so as to not require hard-coded feeds.
// user settings for what is a cold/ok/great/ok/hot temp.

const Alexa = require('ask-sdk-core');
var https = require('https');
const servicePort = 443;
const serviceHost = 'io.adafruit.com';
const servicePath = '/api/v2/<adafruit user name>/feeds/<feed_name>/data';
// you can also use /data/retain to grab only the last data point.
// that would be faster, especially if you have significant data.
// but keep in mind that the retain only sends the data, not the metadata
// so you won't have the detail about the timestamps for comparison...

const nicePhrases = [
    'perfect time for a dip...',
    'should be a nice swim...',
    'it sounds inviting...',
    'grab some sunscreen and hit the water...',
    'get a Tap, start your playlist and jump in...'
];
const okPhrases = [
    'nice and refreshing...',
    'if the air is hot, the pool should be great...',
    'you might be just fine...',
    'grab some sunscreen and hit the water...',
    'get a Tap, crank some tunes, and hit the water...'
];

const coolPhrases = [
    'a little on the cool side',
    'a bit tepid, maybe turn up the heater or put on the cover...',
    'it\'s probably great if you like swimming in the mountains or glacial pools...',
    'might be a bit chilly, but ok...',
    'it\'s probably quite refreshing...'
];
const hotPhrases = [
    'wow it\'s practically a hot tub...',
    'a bit on the hot side...maybe you should remove the cover or turn down the heater...',
    'if you like it hot, then it\'s definitely ready...',
    'it\'s like a hot tub in here...anyone have a time machine?',
    'you can probably sous vide a protein in the pool right now..',
    'it\'s too warm for kids, senior citizens, or people with heart conditions...'
];

function getQualifierForTemp( theTemp ) {
    var okRand = Math.floor(Math.random()*okPhrases.length);
    var coolRand = Math.floor(Math.random()*coolPhrases.length);
    var hotRand = Math.floor(Math.random()*hotPhrases.length);
    var niceRand = Math.floor(Math.random()*nicePhrases.length);
    var res = 'The pool is ' + theTemp + ' degrees,';
    // These temps are what my wife likes.
    if (theTemp >= 89 & theTemp <= 92) {
        res += nicePhrases[niceRand];
    // at this point it's basically a hot tub. Ugh.	
    }else if(theTemp >= 93){
        res += hotPhrases[hotRand];
    // this is what most people like.
    }else if(theTemp >= 85 & theTemp <= 89){
        res += okPhrases[okRand];
    // only for Canadians.
    }else if(theTemp <85){
        res += coolPhrases[coolRand];
    }else{
	// something wrong happens if you get here. Like, terribly, horribly wrong.
        res = 'I don\'t know what to think about that temperature...';
    }
    return res;
}
function parseResponse ( responseData ){
    var t;
	var o;
	var r = 'Hmm. I\'m not sure what the pool temperature is...';
	
	try{
		// try a number parse
		t = parseInt( responseData, 10 );

		if (!isNaN(t)){			
			r = getQualifierForTemp( t );

		}else{
			// try a JSON parse.
			o = JSON.parse( responseData );
			t = parseInt( o[0].value, 10 );	
			if (!isNaN(t)){
				r = getQualifierForTemp( t );
				
				// check the time to see how old this measurement is...
				// console.log ('Report Time: ' + new Date(o[0].created_at));
				var hours = Math.trunc(Math.abs(new Date() - new Date(o[0].created_at)) / 3600000);
				
				if (hours > 3 ){
					r += ' You should know that the temperature info is ' + hours + ' hours old... perhaps you should check on your thermometer hardware...';
					
				}
				if (hours > 1 & hours <= 3){
					r += ' reported ' + hours + ' ago';
				    
				}else if (hours <= 1){
					r += ' reported recently.';
				}				
			}
		}
	}
	catch( error ){
		console.log (error);
	}	
	finally{
		return r;
	}
}

function doGetPoolTemp( userHost, userPath, userPort ) {
    if (userHost == null) { userHost = serviceHost; }
    if (userPath == null) { userPath = servicePath; }
    if (userPort == null) { userPort = servicePort; }
    return new Promise(((resolve, reject) => {
        var options = {
            host: userHost,
            port: userPort,
            path: userPath,
            method: 'GET',
    };
    
    const request = https.request(options, (response) => {
      response.setEncoding('utf8');
      let returnData = '';

      response.on('data', (chunk) => {
        returnData += chunk;
      });

      response.on('end', () => {
        resolve(parseResponse(returnData));
      });

      response.on('error', (error) => {
        reject(error);
      });
    });
    request.end();
  }));
}

const LaunchRequestHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'LaunchRequest';
    },
    async handle(handlerInput) {
        const response = await doGetPoolTemp();
        console.log(response);
        return handlerInput.responseBuilder
            .speak(response)
            .reprompt('Need any more information about your pool?')
            .getResponse();
    },
};

const PoolIntentHandler = {

    canHandle(handlerInput) {
        return handlerInput.requestEnvelope.request.type === 'IntentRequest'
            && handlerInput.requestEnvelope.request.intent.name === 'PoolIntentHandler';
    },

    async handle(handlerInput) {
        const response = await doGetPoolTemp();
        console.log(response);
        return handlerInput.responseBuilder
            .speak(response)
            .reprompt('Need any more information about your pool?')
            .getResponse();
    },

    
};

const HelpIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.HelpIntent';
    },
    handle(handlerInput) {
        const speakOutput = 'You can say things like ... how is my pool, what is my pool temperature, or, is my pool too hot.';
        return handlerInput.responseBuilder
            .speak(speakOutput)
            .reprompt(speakOutput)
            .getResponse();
    }
};
const CancelAndStopIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && (Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.CancelIntent'
                || Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.StopIntent');
    },
    handle(handlerInput) {
        const speakOutput = 'Sorry I bothered you with my friendship';
        return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
    }
};
const SessionEndedRequestHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'SessionEndedRequest';
    },
    handle(handlerInput) {
        // Any cleanup logic goes here.
        return handlerInput.responseBuilder.getResponse();
    }
};

const IntentReflectorHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest';
    },
    handle(handlerInput) {
        const intentName = Alexa.getIntentName(handlerInput.requestEnvelope);
        const speakOutput = `You just triggered ${intentName}`;

        return handlerInput.responseBuilder
            .speak(speakOutput)
            //.reprompt('add a reprompt if you want to keep the session open for the user to respond')
            .getResponse();
    }
};

const ErrorHandler = {
    canHandle() {
        return true;
    },
    handle(handlerInput, error) {
        console.log(`~~~~ Error handled: ${error.stack}`);
        const speakOutput = `Sorry, I had trouble doing what you asked. Please try again.`;

        return handlerInput.responseBuilder
            .speak(speakOutput)
            .reprompt(speakOutput)
            .getResponse();
    }
};

exports.handler = Alexa.SkillBuilders.custom()
    .addRequestHandlers(
        LaunchRequestHandler,
        PoolIntentHandler,
        HelpIntentHandler,
        CancelAndStopIntentHandler,
        SessionEndedRequestHandler,
        IntentReflectorHandler, 
    )
    .addErrorHandlers(
        ErrorHandler,
    )
    .lambda();
