#!/usr/bin/env python
# python 3.6+

# THIS SCRIPT WAS AUTOGENERATIED FROM SOURCE FILES FOUND AT:
# https://github.com/Pristine-Cat/SymPad

# Copyright (c) 2019 Tomasz Pytel
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

_RUNNING_AS_SINGLE_SCRIPT = True


_FILES = {

	'style.css': # style.css

r"""* {
	box-sizing: border-box;
	margin: 0;
	padding: 0;
}

body {
	margin-top: 1em;
	margin-bottom: 6em;
	cursor: default;
}

#Clipboard {
	position: fixed;
	bottom: 0;
	color: transparent;
	border: 0px;
}

#Background {
	position: fixed;
	z-index: -1;
	left: 0;
	top: 0;
}

#Greeting {
	position: fixed;
	left: 50%;
	top: 50%;
	transform: translate(-50%, -50%);
	color: #0007;
}

.GreetingA {
	display: block;
	color: #0007;
	text-decoration: none;
	margin-bottom: 0.5em;
}

#InputBG {
	position: fixed;
	z-index: 2;
	height: 4em;
	bottom: 0;
	left: 0;
	right: 0;
	background-color: white;
}

#Input {
	position: fixed;
	z-index: 3;
	bottom: 2em;
	left: 4em;
	right: 1em;
	border-color: transparent;
	outline-color: transparent;
	background-color: transparent;
}

#InputOverlay {
	z-index: 4;
}

#OverlayGood {
	-webkit-text-fill-color: transparent;
}

#OverlayError {
	-webkit-text-fill-color: #f44;
}

#OverlayAutocomplete {
	-webkit-text-fill-color: #999;
}

.LogEntry {
	width: 100%;
	margin-bottom: 1.5em;
}

.LogMargin {
	display: inline-block;
	height: 100%;
	width: 4em;
	vertical-align: top;
	text-align: right;
	padding-right: 0.5em;
}

.LogBody {
	display: inline-block;
	margin-right: -9999em;
}

.LogWait {
	vertical-align: top;
}

.LogInput {
	margin-bottom: 0.75em;
	width: fit-content;
	cursor: pointer;
}

.LogEval {
	position: relative;
	margin-bottom: 0.25em;
	cursor: pointer;
}

.LogMsg {
	margin-bottom: 0.25em;
}

.LogError {
	margin-bottom: 0.25em;
	color: red;
}

.LogErrorTriange {
	position: absolute;
	left: -1.25em;
	top: 0.25em;
	font-size: 0.7em;
	color: red;
	font-weight: bold;
}
""".encode ("utf8"),

	'script.js': # script.js

r"""// TODO: Multiple spaces screw up overlay text position.
// TODO: Change how left/right arrows interact with autocomplete.
// TODO: Stupid scrollbars...
// TODO: Warning messages on evaluate when SymPy object not understood?
// TODO: Arrow keys in Edge?

var URL              = '/';
var MJQueue          = null;
var MarginTop        = Infinity;
var PreventFocusOut  = true;

var History          = [];
var HistIdx          = 0;
var LogIdx           = 0;
var UniqueID         = 1;

var Validations      = [undefined];
var Evaluations      = [undefined];
var ErrorIdx         = null;
var Autocomplete     = [];

var LastClickTime    = 0;
var NumClicks        = 0;

var GreetingFadedOut = false;

//...............................................................................................
function generateBG () {
	function writeRandomData (data, x0, y0, width, height) {
		let p, d;

		for (let y = y0; y < height; y ++) {
			p = (width * y + x0) * 4;

			for (let x = x0; x < width; x ++) {
				d            = 244 + Math.floor (Math.random () * 12);
				data [p]     = data [p + 1] = d;
				data [p + 2] = d - 8;
				data [p + 3] = 255;
				p            = p + 4;
			}
		}
	}

	let canv    = document.getElementById ('Background');
	canv.width  = window.innerWidth;
	canv.height = window.innerHeight;
	let ctx     = canv.getContext ('2d');
	let imgd    = ctx.getImageData (0, 0, canv.width, canv.height); // ctx.createImageData (width, height);

	writeRandomData (imgd.data, 0, 0, canv.width, canv.height);
	ctx.putImageData (imgd, 0, 0);

	if (window.location.pathname == '/') {
		canv        = $('#InputBG') [0];
		ctx         = canv.getContext ('2d');
		canv.width  = window.innerWidth;

		ctx.putImageData (imgd, 0, 0);
	}
}

//...............................................................................................
function copyInputStyle () {
	JQInput.css ({left: $('#LogEntry1').position ().left})
	JQInput.width ($('#Log').width ());

	let style   = getComputedStyle (document.getElementById ('Input'));
	let overlay = document.getElementById ('InputOverlay');

  for (let prop of style) {
    overlay.style [prop] = style [prop];
	}

	overlay.style ['backgroundColor'] = 'transparent';
}

//...............................................................................................
function scrollToEnd () {
	window.scrollTo (0, document.body.scrollHeight);
}

//...............................................................................................
function resize () {
	copyInputStyle ();
	scrollToEnd ();
	generateBG ();
}

//...............................................................................................
function logResize () {
	// let atEnd  = !(document.documentElement.offsetHeight - document.documentElement.scrollTop - window.innerHeight);
	let margin = Math.max (BodyMarginTop, Math.floor (window.innerHeight - $('body').height () - BodyMarginBottom + 3)); // +3 is fudge factor

	if (margin < MarginTop) {
		MarginTop = margin
		$('body').css ({'margin-top': margin});
	}

	// if (atEnd) {
	// 	scrollToEnd ();
	// }
}

//...............................................................................................
var LastDocHeight = undefined;
var LastWinHeight = undefined;

function monitorStuff () {
	let curDocHeight = $(document).height ();
	let curWinHeight = $(window).height ();

	if (curDocHeight != LastDocHeight || curWinHeight != LastWinHeight) {
		copyInputStyle ();

		window.LastDocHeight = curDocHeight;
		window.LastWinHeight = curWinHeight;
	}

	if (PreventFocusOut) {
		JQInput.focus ();
	}

	setTimeout (monitorStuff, 50);
}

//...............................................................................................
function readyMathJax () {
	window.MJQueue = MathJax.Hub.queue;

	var TEX        = MathJax.InputJax.TeX;
	var PREFILTER  = TEX.prefilterMath;

	TEX.Augment ({
		prefilterMath: function (tex, displaymode, script) {
			return PREFILTER.call (TEX, '\\displaystyle{' + tex + '}', displaymode, script);
		}
	});
}

//...............................................................................................
function reprioritizeMJQueue () {
	let p = MJQueue.queue.pop ();

	if (p !== undefined) {
		MJQueue.queue.splice (0, 0, p);
	}
}

//...............................................................................................
function addLogEntry () {
	LogIdx += 1;

	$('#Log').append (`
			<div class="LogEntry"><div class="LogMargin">${LogIdx}.</div><div class="LogBody" id="LogEntry${LogIdx}"><div class="LogInput" id="LogInput${LogIdx}">
				<img class="LogWait" id="LogInputWait${LogIdx}" src="https://i.gifer.com/origin/3f/3face8da2a6c3dcd27cb4a1aaa32c926_w200.webp" width="16" style="visibility: hidden">
			</div></div></div>`)

	Validations.push (undefined);
	Evaluations.push (undefined);
}

//...............................................................................................
function writeToClipboard (text) {
	PreventFocusOut = false;

	$('#Clipboard').val (text);
	$('#Clipboard').focus ();
	$('#Clipboard').select ();
	document.execCommand ('copy');

	PreventFocusOut = true;

	JQInput.focus ();
}

//...............................................................................................
function copyToClipboard (e, val_or_eval, idx, subidx = 0) {
	let t = performance.now ();

	if ((t - LastClickTime) > 500) {
		NumClicks = 1;
	} else{
		NumClicks += 1;
	}

	LastClickTime = t;
	let resp      = val_or_eval ? Evaluations [idx].math [subidx] : Validations [idx];

	writeToClipboard (NumClicks == 1 ? resp.simple : NumClicks == 2 ? resp.py : resp.tex);

	e.style.color      = 'transparent';
	e.style.background = 'black';

	setTimeout (function () {
		e.style.color      = 'black';
		e.style.background = 'transparent';
	}, 100);
}

//...............................................................................................
function updateOverlay (text, erridx, autocomplete) {
	ErrorIdx     = erridx;
	Autocomplete = autocomplete;

	if (ErrorIdx === null) {
		$('#OverlayGood').text (text);
		$('#OverlayError').text ('');

	} else {
		$('#OverlayGood').text (text.substr (0, ErrorIdx));
		$('#OverlayError').text (text.substr (ErrorIdx));
	}

	$('#OverlayAutocomplete').text (Autocomplete.join (''));
}

//...............................................................................................
function ajaxResponse (resp) {
	if (resp.mode == 'validate') {
		if (Validations [resp.idx] !== undefined && Validations [resp.idx].subidx >= resp.subidx) {
			return; // ignore out of order responses (which should never happen with single threaded server)
		}

		if (resp.tex !== null) {
			Validations [resp.idx] = resp;

			let eLogInput = document.getElementById ('LogInput' + resp.idx);

			let queue              = [];
			[queue, MJQueue.queue] = [MJQueue.queue, queue];

			MJQueue.queue = queue.filter (function (obj, idx, arr) { // remove previous pending updates to same element
				return obj.data [0].parentElement !== eLogInput;
			})

			let eLogInputWait              = document.getElementById ('LogInputWait' + resp.idx);
			eLogInputWait.style.visibility = '';

			let idMath = 'LogInputMath' + UniqueID ++;
			$(eLogInput).append (`<span id="${idMath}" onclick="copyToClipboard (this, 0, ${resp.idx})" style="visibility: hidden">$${resp.tex}$</span>`);
			let eMath  = document.getElementById (idMath);

			MJQueue.Push (['Typeset', MathJax.Hub, eMath, function () {
				if (eMath === eLogInput.children [eLogInput.children.length - 1]) {
					eLogInput.appendChild (eLogInputWait);

					for (let i = eLogInput.children.length - 3; i >= 0; i --) {
						eLogInput.removeChild (eLogInput.children [i]);
					}

					eLogInputWait.style.visibility = 'hidden';
					eMath.style.visibility         = '';

					logResize ();
					scrollToEnd (); // ???
				}
			}]);

			reprioritizeMJQueue ();
		}

		updateOverlay (JQInput.val (), resp.erridx, resp.autocomplete);

	} else { // resp.mode == 'evaluate'
		Evaluations [resp.idx] = resp;

		let eLogEval = document.getElementById ('LogEval' + resp.idx);

		eLogEval.removeChild (document.getElementById ('LogEvalWait' + resp.idx));

		if (resp.err !== undefined) { // error?
			if (resp.err.length > 1) {
				let idLogErrorHidden = 'LogErrorHidden' + resp.idx;
				$(eLogEval).append (`<div id="${idLogErrorHidden}" style="display: none"></div>`);
				var eLogErrorHidden  = document.getElementById (idLogErrorHidden);

				for (let i = 0; i < resp.err.length - 1; i ++) {
					$(eLogErrorHidden).append (`<div class="LogError">${resp.err [i]}</div>`);
				}
			}

			let idLogErrorTriangle = 'LogErrorTriangle' + resp.idx;
			$(eLogEval).append (`<div class="LogError">${resp.err [resp.err.length - 1]}</div><div class="LogErrorTriange" id="LogErrorTriangle${resp.idx}">\u25b7</div>`);
			var eLogErrorTriangle  = document.getElementById (idLogErrorTriangle);

			$(eLogEval).click (function () {
				if (eLogErrorHidden.style.display === 'none') {
					eLogErrorHidden.style.display = 'block';
					eLogErrorTriangle.innerText   = '\u25bd';
				} else {
					eLogErrorHidden.style.display = 'none';
					eLogErrorTriangle.innerText   = '\u25b7';
				}

				logResize ();
			});

			logResize ();
			scrollToEnd ();

		} else if (resp.msg !== undefined) { // message
			$(eLogEval).append (`<div class="LogMsg">${resp.msg}</div>`);

			logResize ();
			scrollToEnd ();

		} else { // no error
			for (let subidx in resp.math) {
				let idLogEvalDiv  = `LogEvalDiv${resp.idx}_${subidx}`;
				let idLogEvalMath = `LogEvalMath${resp.idx}_${subidx}`;

				$(eLogEval).append (`<div id="${idLogEvalDiv}" class="LogEval"><span id="${idLogEvalMath}" style="visibility: hidden" onclick="copyToClipboard (this, 1, ${resp.idx}, ${subidx})">$${resp.math [subidx].tex}$</span>
						<img id="LogEvalWait${resp.idx}_${subidx}" class="LogWait" src="https://i.gifer.com/origin/3f/3face8da2a6c3dcd27cb4a1aaa32c926_w200.webp" width="16">
						</div>`);

				let eLogEvalDiv   = document.getElementById (idLogEvalDiv);
				let eLogEvalMath  = document.getElementById (idLogEvalMath);

				MJQueue.Push (['Typeset', MathJax.Hub, eLogEvalMath, function () {
					eLogEvalDiv.removeChild (document.getElementById (`LogEvalWait${resp.idx}_${subidx}`));

					eLogEvalMath.style.visibility = '';

					logResize ();
					scrollToEnd ();
				}]);

				reprioritizeMJQueue ();
			}
		}
	}
}

//...............................................................................................
function inputting (text, reset = false) {
	if (reset) {
		ErrorIdx     = null;
		Autocomplete = [];

		JQInput.val (text);
	}

	updateOverlay (text, ErrorIdx, Autocomplete);

	$.ajax ({
		url: URL,
		type: 'POST',
		cache: false,
		dataType: 'json',
		success: ajaxResponse,
		data: {
			mode: 'validate',
			idx: LogIdx,
			subidx: UniqueID ++,
			text: text,
		},
	});
}

//...............................................................................................
function inputted (text) {
	$.ajax ({
		url: URL,
		type: 'POST',
		cache: false,
		dataType: 'json',
		success: ajaxResponse,
		data: {
			mode: 'evaluate',
			idx: LogIdx,
			text: text,
		},
	});

	$('#LogEntry' + LogIdx).append (`
			<div class="LogEval" id="LogEval${LogIdx}">
				<img class="LogWait" id="LogEvalWait${LogIdx}" src="https://i.gifer.com/origin/3f/3face8da2a6c3dcd27cb4a1aaa32c926_w200.webp" width="16">
			</div>`);

	History.push (text);

	HistIdx = History.length;

	addLogEntry ();
	logResize ();
	scrollToEnd ();
}

//...............................................................................................
function inputKeypress (e) {
	if (e.which == 13) {
		s = JQInput.val ().trim ();

		if ((s && ErrorIdx === null) || s === '?') {
			if (!GreetingFadedOut) {
				GreetingFadedOut = true;
				$('#Greeting').fadeOut (3000);
			}

			if (s === 'help' || s === '?') {
				window.open (`${URL}help.html`);
				inputting ('', true);

				return false;
			}

			if (Autocomplete.length > 0) {
				s = s + Autocomplete.join ('');
				inputting (s);
			}

			JQInput.val ('');
			updateOverlay ('', null, []);
			inputted (s);

			return false;
		}

	} else if (e.which == 32) {
		if (!JQInput.val ()) {
			return false;
		}
	}

	return true;
}

//...............................................................................................
function inputKeydown (e) {
	if (e.code == 'Escape') {
		e.preventDefault ();

		if (JQInput.val ()) {
			HistIdx = History.length;
			inputting ('', true);

			return false;
		}

	} else if (e.code == 'Tab') {
		e.preventDefault ();
		$(this).focus ();

		return false;

	} else if (e.code == 'ArrowUp') {
		e.preventDefault ();

		if (HistIdx) {
			inputting (History [-- HistIdx], true);

			return false;
		}

	} else if (e.code == 'ArrowDown') {
		e.preventDefault ();

		if (HistIdx < History.length - 1) {
			inputting (History [++ HistIdx], true);

			return false;

		} else if (HistIdx != History.length) {
			HistIdx = History.length;
			inputting ('', true);

			return false;
		}

	} else if (e.code == 'ArrowRight') {
		if (JQInput.get (0).selectionStart === JQInput.val ().length && Autocomplete.length) {
			let text = JQInput.val ();

			if (Autocomplete [0] === ' \\right') {
				text         = text + Autocomplete.slice (0, 2).join ('');
				Autocomplete = Autocomplete.slice (2);

			} else {
				text         = text + Autocomplete [0];
				Autocomplete = Autocomplete.slice (1);
			}

			JQInput.val (text);
			inputting (text);
			// updateOverlay (text, ErrorIdx, Autocomplete);
		}
	}
}

//...............................................................................................
// function inputFocusout (e) {
// 	if (PreventFocusOut) {
// 		e.preventDefault ();
// 		$(this).focus ();

// 		return false;
// 	}
// }

//...............................................................................................
$(function () {
	window.JQInput = $('#Input');

	if (window.location.pathname != '/') {
		generateBG ();
		return;
	}

	let margin       = $('body').css ('margin-top');
	BodyMarginTop    = Number (margin.slice (0, margin.length - 2));
	margin           = $('body').css ('margin-bottom');
	BodyMarginBottom = Number (margin.slice (0, margin.length - 2));

	$('#Clipboard').prop ('readonly', true);
	$('#InputBG') [0].height = $('#InputBG').height ();

	JQInput.keypress (inputKeypress);
	JQInput.keydown (inputKeydown);
	// JQInput.focusout (inputFocusout);
	// JQInput.blur (inputFocusout);

	addLogEntry ();
	logResize ();
	resize ();
	monitorStuff ();
});


// $('#txtSearch').blur(function (event) {
// 	setTimeout(function () { $("#txtSearch").focus(); }, 20);
// });

// document.getElementById('txtSearch').addEventListener('blur', e => {
//   e.target.focus();
// });

// cursor_test = function (element) {
// 	if (!element.children.length && element.innerText == '∥') {
// 		console.log (element, element.classList);
// 		element.innerText = '|';
// 		element.classList.add ('blinking');
// 	}

// 	for (let e of element.children) {
// 		cursor_test (e);
// 	}
// }

// cursor_test (eLogInput.children [0]);
""".encode ("utf8"),

	'index.html': # index.html

r"""<!DOCTYPE html>
<html>
<head>

<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<link rel="icon" href="https://www.sympy.org/static/SymPy-Favicon.ico">
<title>SymPad</title>
<link rel="stylesheet" type="text/css" href="style.css">

<script type="text/javascript" src="https://code.jquery.com/jquery-3.4.1.js" integrity="sha256-WpOohJOqMqqyKL9FccASB9O0KwACQJpFTUBLTYOVvVU=" crossorigin="anonymous"></script>
<script type="text/javascript" src="script.js"></script>
<script type="text/x-mathjax-config">
	MathJax.Hub.Config ({
		messageStyle: "none",
		tex2jax: {inlineMath: [["$","$"], ["\\(","\\)"]]}
	});

	MathJax.Hub.Register.StartupHook ("End", readyMathJax);
</script>
<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-AMS_CHTML-full"></script>

</head>

<body onresize="resize ()">

<input id="Clipboard">
<canvas id="Background"></canvas>

<div id="Greeting">
	<div align="center">
		<h2>SymPad</h2>
		<h5>v0.3.7</h5>
		<br><br>
		Type '<b>help</b>' or '<b>?</b>' at any time for more information.
		<br>
		- or -
		<br>
		Type or click any of the following to get started:
	</div>
	<br><br>
	<a class="GreetingA" href="javascript:inputting ('sin (3\\pi / 2)', true)">sin (3\pi / 2)</a>
	<a class="GreetingA" href="javascript:inputting ('cos**-1 x', true)">cos**-1 x</a>
	<a class="GreetingA" href="javascript:inputting ('\\log_2{8}', true)">\log_2{8}</a>
	<a class="GreetingA" href="javascript:inputting ('\\lim_{x \\to \\infty} 1/x', true)">\lim_{x \to \infty} 1/x</a>
	<a class="GreetingA" href="javascript:inputting ('Limit (\\frac1x, x, 0, dir=\'-\')', true)">Limit (\frac1x, x, 0, dir='-')</a>
	<a class="GreetingA" href="javascript:inputting ('\\sum_{n=0}^oo x^n / n!', true)">\sum_{n=0}^oo x^n / n!</a>
	<a class="GreetingA" href="javascript:inputting ('\\sum_{n=1}**10 Sum (\\sum_{l=1}^m l, (m, 1, n))', true)">\sum_{n=1}**10 Sum (\sum_{l=1}^m l, (m, 1, n))</a>
	<a class="GreetingA" href="javascript:inputting ('d/dx x**2', true)">d/dx x**2</a>
	<a class="GreetingA" href="javascript:inputting ('Derivative (\\int dx, x)', true)">Derivative (\int dx, x)</a>
	<a class="GreetingA" href="javascript:inputting ('d**6 / dxdy**2dz**3 x^3 y^3 z^3', true)">d**6 / dxdy**2dz**3 x^3 y^3 z^3</a>
	<a class="GreetingA" href="javascript:inputting ('Integral (e^{-x^2}, (x, 0, \\infty))', true)">Integral (e^{-x^2}, (x, 0, \infty))</a>
	<a class="GreetingA" href="javascript:inputting ('\\int_0^1 \\int_0^x \\int_0^y 1 dz dy dx', true)">\int_0^1 \int_0^x \int_0^y 1 dz dy dx</a>
	<a class="GreetingA" href="javascript:inputting ('\\int_0^\\infty e^{-st} dt', true)">\int_0^\infty e^{-st} dt</a>
	<a class="GreetingA" href="javascript:inputting ('{{1, 2}, {3, 4}}**-1', true)">{{1, 2}, {3, 4}}**-1</a>
	<a class="GreetingA" href="javascript:inputting ('det({{sin x, -cos x},{cos x, sin x}})', true)">det({{sin x, -cos x},{cos x, sin x}})</a>
	<a class="GreetingA" href="javascript:inputting ('\\begin{matrix} A & B \\\\ C & D \\end{matrix} * {x, y}', true)">\<span></span>begin{matrix} A & B \\ C & D \end{matrix} * {x, y}</a>
	<a class="GreetingA" href="javascript:inputting ('{{1,2,3},{4,5,6}}.transpose ()', true)">{{1,2,3},{4,5,6}}.transpose ()</a>
	<a class="GreetingA" href="javascript:inputting ('expand {x+1}**2', true)">expand {x+1}**2</a>
	<a class="GreetingA" href="javascript:inputting ('factor (x^3 + 3x^2 + 3x + 1)', true)">factor (x^3 + 3x^2 + 3x + 1)</a>
	<a class="GreetingA" href="javascript:inputting ('series (e^x, x, 1, 9)', true)">series (e^x, x, 1, 9)</a>
	<!-- <a class="GreetingA" href="javascript:inputting ('', true)"></a> -->

	<br><br>
	<div align="center">
	Copyright (c) 2019 Tomasz Pytel. <a href="https://github.com/Pristine-Cat/SymPad" target="_blank" style="color: #0007">SymPad on GitHub</a>
	</div>
</div>

<div id="Log"></div>

<canvas id="InputBG"></canvas>
<input id="Input" oninput="inputting (this.value)" autofocus>
<div id="InputOverlay"><span id="OverlayGood"></span><span id="OverlayError"></span><span id="OverlayAutocomplete"></span></div>

</body>
</html>""".encode ("utf8"),

	'help.html': # help.html

r"""<!DOCTYPE html>
<html>
<head>

<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<link rel="icon" href="https://www.sympy.org/static/SymPy-Favicon.ico">
<title>SymPad Help</title>
<link rel="stylesheet" type="text/css" href="style.css">

<style>
	body { margin: 3em 4em; }
	h2 { margin: 2em 0 1em 0; }
	h4 { margin: 1.5em 0 0.5em 0; }
	p { margin: 0 0 1.2em 1em; line-height: 150%; }
	i { color: red; }
</style>

<script type="text/javascript" src="https://code.jquery.com/jquery-3.4.1.js" integrity="sha256-WpOohJOqMqqyKL9FccASB9O0KwACQJpFTUBLTYOVvVU=" crossorigin="anonymous"></script>
<script type="text/javascript" src="script.js"></script>
<script type="text/x-mathjax-config">
	MathJax.Hub.Config ({
		messageStyle: "none",
		tex2jax: {inlineMath: [["$","$"], ["\\(","\\)"]]}
	});
</script>
<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-AMS_CHTML-full"></script>

</head>

<body onresize="generateBG ()">

<canvas id="Background"></canvas>

<h1 align="center" style="margin: 0">SymPad</h1>
<h4 align="center" style="margin: 0">v0.3.7</h4>


<h2>Introduction</h2>

<p>
Sympad is a simple symbolic calculator / scratch pad. It is a labor of love and grew out of a desire for an easy way to calculate a quick integral while
studying some math without having to start a shell every time and import a package or fire up a browser and navigate to a site (technincally
that last bit is exactly what happens but the response time is better :) This desire for simplicity led to the single script option "sympad.py"
which I could plop down on my desktop and execute when needed.
</p><p>
As said, SymPad is a symbolic calculator using SymPy for the math and MathJax for the display in a web browser. It runs as a private http server
on your machine and executes the system default browser pointing to itself on startup. User input is intended to be quick, easy and intuitive and
is displayed in symbolic form as it is being entered. Sympad will accept LaTeX math formatting as well as Python expressions (or a mix) and
evaluate the result symbolically or numerically. The best way to see what it can do is to try a few things...
</p>

<h4>Quick Start</h4>

<p>
Try entering any of the following into SymPad:
</p><p>
sin (3\pi / 2)<br>
cos**-1 x<br>
\log_2{8}<br>
\lim_{x \to \infty} 1/x<br>
Limit (\frac1x, x, 0, dir='-')<br>
\sum_{n=0}^oo x^n / n!<br>
\sum_{n=1}**10 Sum (\sum_{l=1}^m l, (m, 1, n))<br>
d/dx x**2<br>
Derivative (\int dx, x)<br>
d**6 / dxdy**2dz**3 x^3 y^3 z^3<br>
Integral (e^{-x^2}, (x, 0, \infty))<br>
\int_0^1 \int_0^x \int_0^y 1 dz dy dx<br>
\int_0^\infty e^{-st} dt<br>
{{1,2},{3,4}}**-1<br>
det({{sin x, -cos x}, {cos x, sin x}})<br>
\<span></span>begin{matrix} A & B \\ C & D \end{matrix} * {x, y}<br>
{{1,2,3},{4,5,6}}.transpose ()<br>
expand {x+1}**2<br>
factor (x^3 + 3x^2 + 3x + 1)<br>
series (e^x, x, 1, 9)<br>
a, b, c, d = {{1,2},{3,4}}<br>
</p>

<h4>Usage</h4>

<p>
You enter expresstions and they get evaluated. The expressions may be in normal Pythonic style like "<b>a * (b + sin (x)**2 + 3/4) / 2</b>",
LaTeX such as "<b>a\frac{b+\sin^2{x}+\frac34}{2}</b>" or a mix "<b>a * (b + \sin**x{2} + \frac34) / 2</b>". The input is displayed symbolically as
you type. Input history is supported with the up and down arrows.
</p><p>
The symbolic expressions can be copied to the clipboard in various formats.
Single-click for a simple native format meant to be pasted back into the input field.
A double click-copies the expression in Python format suitable for pasting into a Python shell or source file.
Finally, a triple-click will copy the expression in LaTeX format.
The single-click native format will always be pasteable back into SymPad whereas the Python and LaTeX formats may or may not be depending on what elements are present.
</p>

<h2>Types</h2>

<h4>Numbers</h4>

<p>
Numbers take the standard integer or floating point form or exponential form such as 123, -2.567, 1e+100, 3E-45 or -1.521e22.
The precision for all SymPy Floats used in evaluation is set to the highest precision number present in the equation, so if you ask for the cosine of a number with 50 decimal digits your answer will have at least 50 decimal digits.
</p><p>
Keep in mind that "<b>e</b>" or "<b>E</b>" is the Euler"s number constant $e$ and if you are trying to enter 2 times $e$ plus 22 then do not write it all together as "<b>2e+22</b>" as this will be interpreted to be "<b>2 * 10^22</b>".
Instead, use spaces and/or explicit multiplication: "<b>2 * e + 22</b>".
Imaginary numbers are entered using the imaginary unit "<b>i</b>" or "<b>I</b>" depending on preference, no Pythonic "<b>j</b>" option at the moment but it can be hacked by setting "<b>j = i</b>" in SymPad.
</p>

<h4>Variables</h4>

<p>
Variable names mostly follow LaTeX convention, they are single Latin letters "<b>x</b>", "<b>y</b>", "<b>z</b>", "<b>A</b>", "<b>B</b>", etc... or
single Greek letters preceded by a slash such as "<b>\alpha</b>" ($\alpha$), "<b>\epsilon</b>" ($\epsilon$) or "<b>\Psi</b>" ($\Psi$). The
variable names "<b>i</b>", "<b>e</b>" and "<b>\pi</b>" represent their respective mathematical constants $i$, $e$ and $\pi$. The whole top-level
namespace of the SymPy package is made available as functions or variables. This means that "<b>pi</b>" and "<b>oo</b>" are also available for $\pi$
and $\infty$, as well as any other variables present at the top level. Python's "<b>None</b>", "<b>True</b>" and "<b>False</b>" are also present.
</p><p>
By default lower case "<b>e</b>" and "<b>i</b>" are used to represent Euler's number and the imaginary unit instead of the default SymPy upper case "<b>E</b>" and "<b>I</b>".
This is objectively prettier, but can be changed via the "<b>$sympyEI (True)</b>" and "<b>$sympyEI (False)</b>" function.
The SymPy constant usage can also be activated via the command line switch "<b>--sympyEI</b>".
</p><p>
Variable names may be followed by various primes ' such as "<b> a' </b>" ($a'$) or "<b> \omega'' </b>" ($\omega''$).
Variables may be subscripted with other variables or numbers "<b>x_1</b>" ($x_1$), "<b>y_z</b>" ($y_z$), "<b>\alpha_\omega</b>" ($\alpha_\omega$).
This can be extended to silly levels "<b> \gamma_{x_{y_0'}''}''' </b>" ($\gamma_{x_{y_0'}''}'''$).
</p><p>
Differentials are entered as "<b>dx</b>", "<b>\partialx</b>" or "<b>\partial x</b>" and are treated as a single variable. If you want to enter "<b>d</b>"
* "<b>x</b>" multiplied implicitly then put a space between them or two spaces between the "<b>\partial</b>" and the "<b>x</b>".
</p><p>
Variables may be assigned values, references to other variables or even entire expressions which will subsequently be substituted for those variables in any future expression evaluation.
</p>

<h4>Vectors and Matrices</h4>

<p>
These are specified using curly braces with commas. Vectors are passed as a single level of curlys such as "<b>{1, 2}</b>" or "<b>{x, y, z}</b>".
Matrices are passed as nested rows of curlys. A 2x3 matrix would be specified as  "<b>{{1, 2, 3}, {4, 5, 6}}</b>", a 1x3 would be "<b>{{1, 2, 3},}</b>"
and a 3x1 would be "<b>{{1,},{2,},{3,}}</b>". Note the trailing commas which are needed for the same reason as in Python for tuples of one element
(otherwise the curlys would be treated as parenteses instead of vectors / matrices).
</p><p>
Currently I haven't figured out the best way to interface with the SymPy vector module so SymPad coerces vectors to single column matrices. This at
least allows computation with them until I figure out how best to use the vector module.
</p>

<h4>Strings</h4>

<p>
These exist for the sole purpose of passing string arguments to SymPy functions. They work as expected being enclosed by single or double quotes and
supporting escape sequences. For example "<b>Limit (1/x, x, 0, '-')</b>".
</p>

<h4>Lists</h4>

<p>
Standard Python bracket enclosed potentially nested lists which like strings exist for the purpose of passing parameters to functions like
"<b>Matrix ([[1,2],[3,4]])</b>"
</p>

<h4>Tuples</h4>

<p>
Same...
</p>

<h2>Operations</h2>

<h4>Addition and Multiplication</h4>

<p>
Addition is addition and subtraction is subtraction: "<b>a + b</b>", "<b>a - b</b>". Multiplication is explicit with a "<b>*</b>" operator or implicit
simply by writing two symbols next to each other so that "<b>a * b</b>" is the same as "<b>ab</b>". There is however a difference between the two in that
the implicit version has a higher precedence than the explicit, which means that explicit multiplication will end a limit, sum, derivative or division
"<b>/</b>" expression whereas implicit multiplication will not, e.g. "<b>1/xy</b>" = $\frac{1}{xy}$ whereas "<b>1/x*y</b>" = $\frac{1}{x} \cdot y$.
</p><p>
Division also has two operators, the normal "<b>/</b>" which has a fairly low precedence and the LaTeX "<b>\frac</b>" version which has a very high
precedence, even higher than exponentiation. So high in fact that parentheses are not needed if using "<b>\frac</b>" as an exponent as in
"<b>x^\frac{1}{2}</b>" = $x^\frac{1}{2}$. The "<b>\frac</b>" operation also does not need parentheses if using single digit operands or single letter
variables (Latin or Greek) such as "<b>\frac12</b>" = $\frac12$, "<b>\frac\alpha\beta</b>" = $\frac\alpha\beta$ or "<b>\fracxy</b>" = $\frac xy$ (although
this last version without a space before the x is not legal in LaTeX but convenient for quick typing here).
</p>

<h4>Exponentiation</h4>

<p>
There are two power opearators "<b>^</b>" and "<b>**</b>". They have the same precedence and can be used interchangeably but follow slightly different
parsing rules. The "<b>^</b>" operator follows LaTeX rules which only allow a single positive digit or letter variable (Lating or Greek) without the use
of curly braces whereas the "<b>**</b>" follows Python rules which allow negative values or variables or functions. To illustrate the diffference:
"<b>x**-2</b>" = $x^{-2}$ whereas "<b>x^-2</b>" = $x^-2$ (which makes no sense). Also, "<b>e**log(x)</b>" will work as expected $e^{\log(x)}$ whereas
"<b>e^log(x)</b>" = $e^log(x)$.
</p>

<h4>Logarithms</h4>

<p>
The natural logarithm of x is specified by "<b>lnx</b>", "<b>\ln x</b>", "<b>log x</b>", "<b>\log{x}</b>". A logarithm in a specific base is specified
by "<b>\log_b x</b>" = $\log_b x$, "<b>log_{10}(1000)</b>" = $\log_{10} {1000}$ = 3, etc...
</p>

<h4>Roots</h4>

<p>
The square root of x ($\sqrt{x}$) may be entered in any of these forms "<b>sqrtx</b>", "<b>\sqrt x</b>", "<b>sqrt (x)</b>", "<b>\sqrt{x}</b>", with or without the slash.
The cube (or any other) root is similar, $\sqrt[3]x$ = "<b>sqrt[3]x</b>", "<b>sqrt[3] (x)</b>" or "<b>\sqrt[3] {x}</b>".
</p>

<h4>Factorial</h4>

<p>
"<b>4!</b>" = "<b>24</b>", "<b>x!</b>" = "<b>factorial(x)</b>", "<b>(-0.5)!</b>" = "<b>1.77245385090552</b>" and "<b>simplify(x!/x)</b>" = "<b>gamma(x)</b>".
</p>

<h4>Limits</h4>

<p>
To take the limit of an expression "<b>z</b>" as variable "<b>x</b>" approaches "<b>y</b>" enter "<b>\lim_{x \to y} (z)</b>" = $\lim_{x\to y} (z)$.
This will only give the limit if it exists and is the same when approaching from both directions, unlike SymPy which defaults to approaching from the
positive direction. To specify a direction add "<b>^+</b>" or "<b>^-</b>" to the equation as such: "<b>\lim_{x \to 0^+} 1/x</b>" = $\lim_{x\to 0^+}
\frac1x$ = $\infty$ and "<b>\lim_{x \to 0^-} 1/x</b>" = $\lim_{x\to 0^-} \frac1x$ = $-\infty$. Addition and explicit multiplication terminate a limit
expression. Limits may also be entered using the standard SymPy syntax "<b>Limit (expression, variable, to)</b>", this defaults to limit from positive
direction like SymPy, or you may specify a direction "<b>Limit (expression, variable, to, dir='+-')</b>".
</p>

<h4>Sums</h4>

<p>
The summation (finite or infinite) of expression "<b>z</b>" as variable "<b>n</b>" ranges from "<b>a</b>" to "<b>b</b>" is written as "<b>\sum_{n=a}^b
(z)</b>" = $\sum_{n=a}^b (z)$. Iterated sums work as expected, "<b>\sum_{n=1}^3 \sum_{m=1}^n m</b>" = $\sum_{n=1}^3 \sum_{m=1}^n m$ = 10. Addition and
explicit multiplication terminate a sum expression.
Sums may also be entered using the standard SymPy syntax "<b>Sum (expression, (variable, from, to))</b>".
</p>

<h4>Differentiation</h4>

<p>
The derivative of expression "<b>z</b>" with respect to "<b>x</b>" is entered as "<b>d/dx z</b>" or "<b>\frac{d}{dx} z</b>" = $\frac{d}{dx} z$. The
second derivative is "<b>d^2/dx^2 (z)</b>" or "<b>\frac{d^2}{dx^2} (z)</b>" = $\frac{d^2}{dx^2} (z)$. Using "<b>\partial</b>" ($\partial$) is allowed but
must be consistent within the expression. Mixed derivatives are entered as "<b>d^2/dxdy (z)</b>" or "<b>\partial^2 / \partial x\partial y (z)</b>" =
$\frac{\partial^2}{\partial x\partial y} (z)$. Derivatives may also be entered using the standard SymPy syntax "<b>Derivative (expression, var1, var2,
power2, ...)</b>".
</p>

<h4>Integration</h4>

<p>
The anti-derivative of expression "<b>z</b>" with respect to x is written as "<b>\int z dx</b>" = $\int z\ dx$. The definite integral from "<b>a</b>" to
"<b>b</b>" is "<b>\int_a^b z dx</b>" = $\int_a^b z\ dx$. "<b>\int dx/x</b>" = $\int \frac1x\ dx$. Iterated and improper integrals also work. Integrals
may also be entered using the standard SymPy syntax "<b>Integral (expression, (variable, from, to))</b>".
</p>

<h4>(In)equalities</h4>

<p>
Are parsed from the standard Python "<b>=, ==, !=, &lt;, &lt;=, &gt;, &gt;=</b>" or LaTeX "<b>\ne, \neq, \lt, \le, \gt, \ge</b>" symbols.
Currently only a single comparison is allowed so an expression like "<b>0 &lt;= x &lt;= 2</b>" is not valid.
Note that the "<b>=</b>" and "<b>==</b>" operators are equivalent for SymPy and mapped to the same "<b>Eq</b>" object in expressions but the single "<b>=</b>" operator has a higher precedence than the others and is used by SymPad for variable assignment whereas the double "<b>==</b>" only ever implies comparison.
</p>

<h4>Parentheses</h4>

<p>
Explicit "<b>( )</b>" or implicit curly "<b>{ }</b>" parentheses allow prioritization of lower precedence operations over higher ones as usual and also
delineate an expression as an input to a function. They may be used interchangeably for single expressions, the only difference being that the implicit
version is not drawn if it does not need to be. The case where explicit "<b>( )</b>" parentheses are needed ... explicitly ... is when calling functions
in general and always when calling functions which take multiple parameters like "<b>max(1,2,3)</b>". The curly braces are used as shorthand for vectors
and matrices if commas are present, but that is a different syntactic usage, curlys with no commas are essentially invisible parentheses.
</p>

<h4>Member Access</h4>

<p>
You can access member data or functions of an expression just like in Python with the "<b>.</b>" operator.
If the attribute name following the dot is followed by a parenthesized expression then it will be treated as a function call, otherwise it is a data member.
For example, two ways to get the transpose of a matrix are "<b>{{1,2,3},{4,5,6}}.T</b>" and "<b>{{1,2,3},{4,5,6}}.transpose ()</b>".
</p>

<h4>Variable Assignment</h4>

<p>
Using the syntax "<b>var = expression</b>" you can assign some value to be substituted for that variable in all expressions.
For example, doing "<b>x = pi</b>" and then evaluating "<b>cos x</b>" will give you "<b>-1</b>".
Anything can be assigned to any valid variable, valid mathematical expressions, Python objects like strings or lists or even references to other variables.
To delete an assignment use the "<b>del var</b>" function, to delete all assignments do "<b>delall</b>" and to see what variables are currently assigned to, use the "<b>vars</b>" function.
</p><p>
Tuple assignment is supported and as in Python the source can be another tuple or a single iterable object.
An impractical example of this would be setting "<b> a, b, c = 'str' </b>" which would give you "<b> a = 's' </b>", "<b> b = 't' </b>" and "<b> c = 'r' </b>".
</p><p>
There are two distinct types of assignment that can occur and you should be aware of the difference between them.
Copy assignment is the standard type of assignment used by default in most computer languages where if you start with "<b>x = 1</b>" and you then enter "<b>y = x</b>" then the value "<b>1</b>" will be copied to the "<b>y</b>" variable.
The value of "<b>y</b>" will be independent of whatever else happens to the variable "<b>x</b>" after this.
The other kind of assignment is a reference assignment which will map the source variable instead of copying its value to the target.
This means that if you have a reference set like "<b>y = x</b>" and the value of "<b>x</b>" changes then the value of "<b>y</b>" will reflect this new value.
The reference assignment happens if you try to assign variables which do not exist, so setting "<b>y = x</b>" before "<b>x</b>" has been created will result in a reference.
Otherwise you can force a reference by using the "<b>@()</b>" meta-function.
Doing "<b>y = @x</b>" will create a reference to "<b>x</b>" itself instead of copying the value.
</p>

<h2>Functions</h2>

<p>
Almost all SymPy functions are available directly just by typing their name, the exceptions being single letter functions like "<b>N</b>" or "<b>S</b>".
These can be executed using the escape character "<b>$</b>" before the name.
To numerically evaluate the value of "<b>sin (2)</b>" type in "<b>$N (sin (2))</b>".
Functions may take multiple comma-separated arguments with optional keyword arguments as well. The keyword argument identifier
implementation is hacked into the grammar so if a keyword name can not be entered correctly (due to underscores) then try entering the identifier name as an explicit string such as "<b> 'this_identifier_has_too__many___underscores' = value </b>".
</p><p>
The standard trigonometric and hyperbolic functions and their inverses can be entered as usual, the forward functions with or without a leading slash: "<b>sin</b>", "<b>\coth</b>".
The inverses are entered as Pythonic functions without a slash like "<b>atan</b>" or "<b>acscsh</b>" and the LaTeX versions take a slash and and are spelled out "<b>\arctan</b>".
The inverses may also be specified using the common mathematical syntax: "<b>\tan^{-1}x</b>" or "<b>cos**-1 x</b>".
</p><p>
This last form of exponentiating a function is extended as an input shortcut to all functions so that typing "<b>ln**2x</b>" is a quick way to enter "<b>(ln(x))**2</b>".
Keep in mind that the "<b>-1</b>" exponent in this context is just a -1 and does not specify the inverse function as it does for the forward trigonometric and hyperbolic functions.
</p><p>
Functions don't technically require explicit parentheses in order to allow quick entry like "<b>sqrt2</b>" but for any parameter more complicated than another function or variable to a power they will be needed.
Functions which take more than one parameter always require explicit parentheses.
</p><p>
Most functions which have an explicit mathematical display syntax are translated on the fly for correct rendering.
These include the functions "<b>abs/Abs (x)</b>" which are translated to the standard bar syntax for absolute value "<b>|x|</b>", the "<b>factorial (x)</b>" function is identical to writing "<b>x!</b>" and "<b>exp (x)</b>" is the same as writing "<b>e^x</b>".
Other functions which are translated are "<b>Derivative</b>", "<b>diff</b>", "<b>Integral</b>", "<b>integrate</b>", "<b>Limit</b>", "<b>limit</b>", "<b>Matrix</b>", "<b>pow</b>", "<b>Pow</b>" and "<b>Sum</b>".
</p><p>
The "<b>$</b>" escape character allows you to execute arbitrary functions which are not normally accepted by the grammar. Function names specifically recognized by the grammar are only those specified in the SymPy module and a few builtins.
When functions are entered using the "<b>$</b>" character then many more __builtin__ functions may be accessed, for whatever reason, whether useful or not.
Try entering "<b>$print ('Hello World...')</b>" and have a look at the server output.
Note that only the non-dangerous __builtin__ functions are specifically included in this list, functions like "<b>eval</b>", "<b>exec</b>" and many more have been left out and are not accessible.
</p>

<h2>Notes</h2>

<p>
<b>WARNING!</b> This http server implementation is nowhere near secure, this as well as the posibility of execution of arbitrary Python functions means you should never leave this server open to the internet by serving on an IP address visible to the external world.
</p><p>
Due to mixing operators from Python and LaTeX the grammar may be a little wonky in places so if something doesn't seem to work as it should try wrapping it in parentheses or putting a space between the problematic elements.
</p><p>
There is a special use for the "<b>_</b>" underscore character aside from variable subscripting which is the same as in the Python interactive shell in that it represents the last expression successfully evaluated.
To see this in action type in "<b>1</b>" and hit Enter, then type in "<b>expand ((x+1)*_)</b>" and hit Enter.
Repeat this several times using the up arrow.
</p><p>
If you are getting results which are just plain wrong, check to see if you have any variables mapped which would be changing the evaluation.
</p><p>
There are many SymPy objects which SymPad does not understand natively yet. In any case where such an object is the result of an evalutation then the SymPy LaTeX representation will be used for the displayed answer and the SymPy str version of the object will be used as the Python copy string.
This may or may not allow you to paste the Python string back into SymPad to continue working with the result.
A single-click copy of the result will have the element(s) which was/were not understood replaced with "<b>nan</b>".
</p>

<h4>Future</h4>

<p>
Time and interest permitting: Proper implementation of vectors with "<b>\vec{x}</b>" and "<b>\hat{i}</b>" variables, sympy function/variable module prefix, importing modules to allow custom code execution, assumptions/hints, systems of equations, ODEs, piecewise expressions, long Python variable names, graphical plots (using matplotlib?)... Too much to list...
</p>


<div align="center">
Copyright (c) 2019 Tomasz Pytel, All rights reserved.

SymPad on GitHub: <a target="_blank" href="https://github.com/Pristine-Cat/SymPad">https://github.com/Pristine-Cat/SymPad</a>
</div>

</body>
</html>""".encode ("utf8"),
}

import re
import types

#...............................................................................................
class Incomplete (Exception):
	def __init__ (self, red):
		self.red = red

class Token (str):
	def __new__ (cls, str_, text = None, pos = None, grps = None):
		self      = str.__new__ (cls, str_)
		self.text = text or ''
		self.pos  = pos
		self.grp  = () if not grps else grps

		return self

class State (tuple): # easier on the eyes
	def __new__ (cls, *args):
		return tuple.__new__ (cls, args)

	def __init__ (self, *args): # idx = state index, sym = symbol (TOKEN or 'expression'), red = reduction (if present)
		if len (self) == 2:
			self.idx, self.sym = self
		else: # must be 3
			self.idx, self.sym, self.red = self

class Parser:
	_PARSER_TABLES = '' # placeholders so pylint doesn't have a fit
	_PARSER_TOP    = ''
	TOKENS         = {}

	_rec_SYMBOL_NUMTAIL = re.compile (r'(.*[^_\d])(_?\d+)?') # symbol names in code have extra digits at end for uniqueness which are discarded

	def __init__ (self):
		if isinstance (self._PARSER_TABLES, bytes):
			import ast, base64, zlib
			symbols, rules, strules, terms, nterms = ast.literal_eval (zlib.decompress (base64.b64decode (self._PARSER_TABLES)).decode ('utf8'))
		else:
			symbols, rules, strules, terms, nterms = self._PARSER_TABLES

		self.tokgrps = {} # {'token': (groups pos start, groups pos end), ...}
		tokpats      = list (self.TOKENS.items ())
		pos          = 0

		for tok, pat in tokpats:
			l                   = re.compile (pat).groups + 1
			self.tokgrps [tok]  = (pos, pos + l)
			pos                += l

		self.tokre   = '|'.join (f'(?P<{tok}>{pat})' for tok, pat in tokpats)
		self.tokrec  = re.compile (self.tokre)
		self.rules   = [(0, (symbols [-1]))] + [(symbols [r [0]], tuple (symbols [s] for s in (r [1] if isinstance (r [1], tuple) else (r [1],)))) for r in rules]
		self.strules = [[t if isinstance (t, tuple) else (t, 0) for t in (sr if isinstance (sr, list) else [sr])] for sr in strules]
		states       = max (max (max (t [1]) for t in terms), max (max (t [1]) for t in nterms)) + 1
		self.terms   = [{} for _ in range (states)] # [{'symbol': [+shift or -reduce, conflict +shift or -reduce or None], ...}] - index by state num then terminal
		self.nterms  = [{} for _ in range (states)] # [{'symbol': +shift or -reduce, ...}] - index by state num then non-terminal
		self.rfuncs  = [None] # first rule is always None

		for t in terms:
			sym, sts, acts, confs = t if len (t) == 4 else t + (None,)
			sym                   = symbols [sym]

			for st, act in zip (sts, acts):
				self.terms [st] [sym] = (act, None)

			if confs:
				for st, act in confs.items ():
					self.terms [st] [sym] = (self.terms [st] [sym] [0], act)

		for sym, sts, acts in nterms:
			for st, act in zip (sts, acts):
				self.nterms [st] [symbols [sym]] = act

		prods = {} # {('production', ('symbol', ...)): func, ...}

		for name in dir (self):
			obj = getattr (self, name)

			if name [0] != '_' and type (obj) is types.MethodType and obj.__code__.co_argcount >= 1: # 2: allow empty productions
				m = Parser._rec_SYMBOL_NUMTAIL.match (name)

				if m:
					parms = tuple (p if p in self.TOKENS else Parser._rec_SYMBOL_NUMTAIL.match (p).group (1) \
							for p in obj.__code__.co_varnames [1 : obj.__code__.co_argcount])
					prods [(m.group (1), parms)] = obj

		for irule in range (1, len (self.rules)):
			func = prods.get (self.rules [irule] [:2])

			if not func:
				raise NameError (f"no method for rule '{self.rules [irule] [0]} -> {''' '''.join (self.rules [irule] [1])}'")

			self.rfuncs.append (func)

	def tokenize (self, text):
		tokens = []
		end    = len (text)
		pos    = 0

		while pos < end:
			m = self.tokrec.match (text, pos)

			if m is None:
				tokens.append (Token ('$err', text [pos], pos))

				break

			else:
				if m.lastgroup != 'ignore':
					tok  = m.lastgroup
					s, e = self.tokgrps [tok]
					grps = m.groups () [s : e]

					tokens.append (Token (tok, grps [0], pos, grps [1:]))

				pos += len (m.group (0))

		tokens.append (Token ('$end', '', pos))

		return tokens

	#...............................................................................................
	def parse_getextrastate (self):
		return None

	def parse_setextrastate (self, state):
		pass

	def parse_error (self):
		return False # True if state fixed to continue parsing, False to fail

	def parse_success (self, red):
		'NO PARSE_SUCCESS'
		return None # True to contunue checking conflict backtracks, False to stop and return

	def parse (self, src):
		has_parse_success = (self.parse_success.__doc__ != 'NO PARSE_SUCCESS')

		rules, terms, nterms, rfuncs = self.rules, self.terms, self.nterms, self.rfuncs

		tokens = self.tokenize (src)
		tokidx = 0
		cstack = [] # [(action, tokidx, stack, stidx, extra state), ...] # conflict backtrack stack
		stack  = [State (0, None, None)] # [(stidx, symbol, reduction) or (stidx, token), ...]
		stidx  = 0
		rederr = None # reduction function raised exception (SyntaxError or Incomplete)

		while 1:
			if not rederr:
				tok       = tokens [tokidx]
				act, conf = terms [stidx].get (tok, (None, None))

			if rederr or act is None:
				self.tokens, self.tokidx, self.cstack, self.stack, self.stidx, self.tok, self.rederr = \
						tokens, tokidx, cstack, stack, stidx, tok, rederr

				rederr = None

				if tok == '$end' and stidx == 1 and len (stack) == 2 and stack [1] [1] == rules [0] [1]:
					if not has_parse_success:
						return stack [1].red

					if not self.parse_success (stack [1].red) or not cstack:
						return None

				elif self.parse_error ():
					tokidx, stidx = self.tokidx, self.stidx

					continue

				elif not cstack:
					if has_parse_success: # do not raise SyntaxError if parser relies on parse_success
						return None

					# if self.rederr is not None: # THIS IS COMMENTED OUT BECAUSE IS NOT USED HERE AND PYLINT DOESN'T LIKE IT!
					# 	raise self.rederr # re-raise exception from last reduction function if present

					raise SyntaxError ( \
						'unexpected end of input' if tok == '$end' else \
						f'invalid token {tok.text!r}' if tok == '$err' else \
						f'invalid syntax {src [tok.pos : tok.pos + 16]!r}')

			# if act is None:
				act, tokens, tokidx, stack, stidx, estate = cstack.pop ()
				tok                                       = tokens [tokidx]

				self.parse_setextrastate (estate)

			elif conf is not None:
				cstack.append ((conf, tokens [:], tokidx, stack [:], stidx, self.parse_getextrastate ()))

			if act > 0:
				tokidx += 1
				stidx   = act

				stack.append (State (stidx, tok))

			else:
				rule  = rules [-act]
				rnlen = -len (rule [1])
				prod  = rule [0]

				try:
					red = rfuncs [-act] (*((t [-1] for t in stack [rnlen:]) if rnlen else ()))

				except SyntaxError as e:
					rederr = e or True # why did I do this?

					continue

				except Incomplete as e:
					rederr = e
					red    = e.red

				if rnlen:
					del stack [rnlen:]

				stidx = nterms [stack [-1].idx] [prod]

				stack.append (State (stidx, prod, red))

class lalr1: # for single script
	Incomplete = Incomplete
	Token      = Token
	State      = State
	Parser     = Parser
# TODO: Add known zero parameter funcs.

# Base classes for abstract math syntax tree, tuple based.
#
# ('=', 'rel', lhs, rhs)        - equality of type 'rel' relating Left-Hand-Side and Right-Hand-Side
# ('#', 'num')                  - real numbers represented as strings to pass on maximum precision to sympy
# ('@', 'var')                  - variable name, can take forms: 'x', "x'", 'dx', '\partial x', 'x_2', '\partial x_{y_2}', "d\alpha_{x_{\beta''}'}'''"
# ('.', expr, 'name')           - data member reference
# ('.', expr, 'name', arg)      - method member call
# ('"', 'str')                  - string (for function parameters like '+' or '-')
# (',', (expr1, expr2, ...))    - comma expression (tuple)
# ('(', expr)                   - explicit parentheses
# ('|', expr)                   - absolute value
# ('-', expr)                   - negative of expression, negative numbers are represented with this at least initially
# ('!', expr)                   - factorial
# ('+', (expr1, expr2, ...))    - addition
# ('*', (expr1, expr2, ...))    - multiplication
# ('/', numer, denom)           - fraction numer(ator) / denom(inator)
# ('^', base, exp)              - power base ^ exp(onent)
# ('log', expr)                 - natural logarithm of expr
# ('log', expr, base)           - logarithm of expr in base
# ('sqrt', expr)                - square root of expr
# ('sqrt', expr, n)             - nth root of expr
# ('func', 'func', expr)        - sympy or regular python function 'func', will be called with sympy expression (',' expr gives multiple arguments)
# ('lim', expr, var, to)        - limit of expr when variable var approaches to from both positive and negative directions
# ('lim', expr, var, to, 'dir') - limit of expr when variable var approaches to from specified direction dir which may be '+' or '-'
# ('sum', expr, var, from, to)  - summation of expr over variable var from from to to
# ('diff', expr, (var1, ...))   - differentiation of expr with respect to var1 and optional other vars
# ('intg', expr, var)           - anti-derivative of expr (or 1 if expr is None) with respect to differential var ('dx', 'dy', etc ...)
# ('intg', expr, var, from, to) - definite integral of expr (or 1 if expr is None) with respect to differential var ('dx', 'dy', etc ...)
#
# ('vec', (expr1, expr2, ...))                                 - vector
# ('mat', ((expr11, expr12, ...), (expr21, expr22, ...), ...)) - matrix
#
# ('ten', (?((expr111?, ...), ...), ...)?)                     - FUTURE arbitrary order higher than 2 tensor?

import re
import types

import sympy as sp

_SYMPY_OBJECTS = dict ((name, obj) for name, obj in \
		filter (lambda no: no [0] [0] != '_' and len (no [0]) >= 2 and not isinstance (no [1], types.ModuleType), sp.__dict__.items ()))

#...............................................................................................
class AST (tuple):
	op = None

	_rec_identifier = re.compile (r'^[a-zA-Z_]\w*$')

	def __new__ (cls, *args):
		op       = _AST_CLS2OP.get (cls)
		cls_args = tuple (AST (*arg) if arg.__class__ is tuple else arg for arg in args)

		if op:
			args = (op,) + cls_args

		elif args:
			args = cls_args
			cls2 = _AST_OP2CLS.get (args [0])

			if cls2:
				cls      = cls2
				cls_args = cls_args [1:]

		self = tuple.__new__ (cls, args)

		if self.op:
			self._init (*cls_args)

		return self

	def __getattr__ (self, name): # calculate value for nonexistent self.name by calling self._name () and store
		func                 = getattr (self, f'_{name}') if name [0] != '_' else None
		val                  = func and func ()
		self.__dict__ [name] = val

		return val

	def _is_single_unit (self): # is single positive digit, fraction or single non-differential non-subscripted non-primed variable?
		if self.op == '/':
			return True
		elif self.op == '#':
			return len (self.num) == 1
		else:
			return self.is_single_var

	def neg (self, stack = False): # stack means stack negatives ('-', ('-', ('#', '-1')))
		if stack:
			return \
					AST ('-', self)            if not self.is_pos_num else \
					AST ('#', f'-{self.num}')
		else:
			return \
					self.minus                 if self.is_minus else \
					AST ('-', self)            if not self.is_num else \
					AST ('#', self.num [1:])   if self.num [0] == '-' else \
					AST ('#', f'-{self.num}')

	def strip_paren (self, count = None):
		count = 999999999 if count is None else count

		while self.op == '(' and count:
			self   = self.paren
			count -= 1

		return self

	def strip_minus (self, count = None):
		count = 999999999 if count is None else count

		while self.op == '-' and count:
			self   = self.minus
			count -= 1

		return self

	def as_identifier (self, top = True):
		if self.op in {'#', '@', '"'}:
			name = self [1]
		elif not self.is_mul:
			return None

		else:
			try:
				name = ''.join (m.as_identifier () for m in self.muls)
			except TypeError:
				return None

		return name if AST._rec_identifier.match (name) else None

	@staticmethod
	def is_int_text (text): # >= 0
		return AST_Num._rec_int.match (text)

	@staticmethod
	def flatcat (op, ast0, ast1): # ,,,/O.o\,,,~~
		if ast0.op == op:
			if ast1.op == op:
				return AST (op, ast0 [-1] + ast1 [-1])
			return AST (op, ast0 [-1] + (ast1,))
		elif ast1.op == op:
			return AST (op, (ast0,) + ast1 [-1])
		return AST (op, (ast0, ast1))

#...............................................................................................
class AST_Eq (AST):
	op, is_eq  = '=', True

	SHORT2LONG = {'!=': '\\ne', '<=': '\\le', '>=': '\\ge'} # , '<': '\\lt', '>': '\\gt'}
	LONG2SHORT = {'\\ne': '!=', '\\le': '<=', '\\ge': '>=', '\\lt': '<', '\\gt': '>', '\\neq': '!='}

	def _init (self, rel, lhs, rhs):
		self.rel, self.lhs, self.rhs = rel, lhs, rhs # should be short form

	def _is_eq_eq (self):
		return self.rel in {'=', '=='}

	def _is_ass (self):
		return self.rel == '='

class AST_Num (AST):
	op, is_num = '#', True

	_rec_int          = re.compile (r'^-?\d+$')
	_rec_pos_int      = re.compile (r'^\d+$')
	_rec_mant_and_exp = re.compile (r'^(-?\d*\.?\d*)[eE](?:(-\d+)|\+?(\d+))$')

	def _init (self, num):
		self.num = num

	def _is_pos_num (self):
		return self.num [0] != '-'

	def _is_neg_num (self):
		return self.num [0] == '-'

	def _is_pos_int (self):
		return AST_Num._rec_pos_int.match (self.num)

	def mant_and_exp (self):
		m = AST_Num._rec_mant_and_exp.match (self.num)

		return (self.num, None) if not m else (m.group (1) , m.group (2) or m.group (3))

class AST_Var (AST):
	op, is_var = '@', True

	GREEK        = {'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'rho', 'sigma', \
			'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega', 'Gamma', 'Delta', 'Theta', 'Lambda', 'Upsilon', 'Xi', 'Phi', 'Pi', 'Psi', 'Sigma', 'Omega'}
	PY           = {'None', 'True', 'False'} | set (no [0] for no in filter (lambda no: not callable (no [1]), _SYMPY_OBJECTS.items ()))
	SHORT2LONG   = {**dict ((v, f'\\text{{{v}}}') for v in PY), 'pi': '\\pi', 'oo': '\\infty', **dict ((f'_{g}', f'\\{g}') for g in GREEK)}
	LONG2SHORT   = {**dict ((f'\\text{{{v}}}', v) for v in PY), '\\pi': 'pi', '\\infty': 'oo'}
	LONG2SHORTPY = {**dict ((f'\\text{{{v}}}', v) for v in PY), '\\pi': 'pi', '\\infty': 'oo', **dict ((f'\\{g}', f'_{g}') for g in GREEK)}

	_rec_diff_start         = re.compile (r'^d(?=[^_])')
	_rec_part_start         = re.compile (r'^\\partial ')
	_rec_diff_or_part_start = re.compile (r'^(d(?=[^_])|\\partial )')
	_rec_diff_or_part_solo  = re.compile (r'^(?:d|\\partial)$')
	_rec_not_single         = re.compile (r"^(?:d.|\\partial |.+[_'])")
	_rec_as_short_split     = re.compile ('(' + '|'.join (v.replace ('\\', '\\\\') for v in LONG2SHORT) + ')')

	def _init (self, var):
		self.var = var # should be long form

	def _is_null_var (self):
		return not self.var

	def _has_short_var (self):
		return self.var in AST_Var.LONG2SHORT

	def _is_differential (self):
		return AST_Var._rec_diff_start.match (self.var)

	def _is_partial (self):
		return AST_Var._rec_part_start.match (self.var)

	def _is_diff_or_part (self):
		return AST_Var._rec_diff_or_part_start.match (self.var)

	def _is_diff_or_part_solo (self):
		return AST_Var._rec_diff_or_part_solo.match (self.var)

	def _is_single_var (self): # is single atomic variable (non-differential, non-subscripted, non-primed)?
		return not AST_Var._rec_not_single.match (self.var)

	def as_var (self): # 'x', dx', '\\partial x' -> 'x'
		return AST ('@', AST.Var._rec_diff_or_part_start.sub ('', self.var))

	def as_differential (self): # 'x', 'dx', '\\partial x' -> 'dx'
		return AST ('@', f'd{AST_Var._rec_diff_or_part_start.sub ("", self.var)}') if self.var else self

	def as_partial (self): # 'x', 'dx', '\\partial x' -> '\\partial x'
		return AST ('@', f'\\partial {AST_Var._rec_diff_or_part_start.sub ("", self.var)}') if self.var else self

	def diff_or_part_start_text (self): # 'dx' -> 'd', '\\partial x' -> '\\partial '
		m = AST_Var._rec_diff_or_part_start.match (self.var)

		return m.group (1) if m else ''

	def as_short_var_text (self):
		vs = AST_Var._rec_as_short_split.split (self.var)
		vs = [AST_Var.LONG2SHORT.get (v, v) for v in vs]

		return ''.join (vs)

	def as_shortpy_var_text (self):
		vs = AST_Var._rec_as_short_split.split (self.var)
		vs = [AST_Var.LONG2SHORTPY.get (v, v) for v in vs]

		return ''.join (vs)

class AST_Attr (AST):
	op, is_attr = '.', True

	def _init (self, obj, attr, arg = None):
		self.obj, self.attr, self.arg = obj, attr, arg

class AST_Str (AST):
	op, is_str = '"', True

	def _init (self, str_):
		self.str_ = str_

class AST_Comma (AST):
	op, is_comma = ',', True

	def _init (self, commas):
		self.commas = commas

class AST_Paren (AST):
	op, is_paren = '(', True

	def _init (self, paren):
		self.paren = paren

class AST_Brack (AST):
	op, is_brack = '[', True

	def _init (self, bracks):
		self.bracks = bracks

class AST_Abs (AST):
	op, is_abs = '|', True

	def _init (self, abs):
		self.abs = abs

class AST_Minus (AST):
	op, is_minus = '-', True

	def _init (self, minus):
		self.minus = minus

class AST_Fact (AST):
	op, is_fact = '!', True

	def _init (self, fact):
		self.fact = fact

class AST_Add (AST):
	op, is_add = '+', True

	def _init (self, adds):
		self.adds = adds

class AST_Mul (AST):
	op, is_mul = '*', True

	def _init (self, muls):
		self.muls = muls

class AST_Div (AST):
	op, is_div = '/', True

	def _init (self, numer, denom):
		self.numer, self.denom = numer, denom

class AST_Pow (AST):
	op, is_pow = '^', True

	def _init (self, base, exp):
		self.base, self.exp = base, exp

class AST_Log (AST):
	op, is_log = 'log', True

	def _init (self, log, base = None):
		self.log, self.base = log, base

class AST_Sqrt (AST):
	op, is_sqrt = 'sqrt', True

	def _init (self, rad, idx = None):
		self.rad, self.idx = rad, idx

class AST_Func (AST):
	op, is_func = 'func', True

	SPECIAL     = {'@', 'vars', 'del', 'delall'}
	BUILTINS    = {'abs', 'pow', 'sum'}
	TRIGH       = {'sin', 'cos', 'tan', 'csc', 'sec', 'cot', 'sinh', 'cosh', 'tanh', 'csch', 'sech', 'coth'}
	PY_ONLY     = SPECIAL | BUILTINS | {f'a{f}' for f in TRIGH} | set (no [0] for no in filter (lambda no: callable (no [1]), _SYMPY_OBJECTS.items ()))
	PY_AND_TEX  = TRIGH | {'arg', 'exp', 'ln', 'max', 'min'}
	PY_ALL      = PY_ONLY | PY_AND_TEX
	TEX_ONLY    = {f'arc{f}' for f in TRIGH}

	_rec_trigh        = re.compile (r'^a?(?:sin|cos|tan|csc|sec|cot)h?$')
	_rec_trigh_inv    = re.compile (r'^a(?:sin|cos|tan|csc|sec|cot)h?$')
	_rec_trigh_noninv = re.compile (r'^(?:sin|cos|tan|csc|sec|cot)h?$')

	def _init (self, func, arg):
		self.func, self.arg = func, arg

	def _is_trigh_func (self):
		return AST_Func._rec_trigh.match (self.func)

	def _is_trigh_func_inv (self):
		return AST_Func._rec_trigh_inv.match (self.func)

	def _is_trigh_func_noninv (self):
		return AST_Func._rec_trigh_noninv.match (self.func)

class AST_Lim (AST):
	op, is_lim = 'lim', True

	def _init (self, lim, lvar, to, dir = None):
		self.lim, self.lvar, self.to, self.dir = lim, lvar, to, dir

class AST_Sum (AST):
	op, is_sum = 'sum', True

	def _init (self, sum, svar, from_, to):
		self.sum, self.svar, self.from_, self.to = sum, svar, from_, to

class AST_Diff (AST):
	op, is_diff = 'diff', True

	def _init (self, diff, dvs):
		self.diff, self.dvs = diff, dvs

class AST_Intg (AST):
	op, is_intg = 'intg', True

	def _init (self, intg, dv, from_ = None, to = None):
		self.intg, self.dv, self.from_, self.to = intg, dv, from_, to

class AST_Vec (AST):
	op, is_vec = 'vec', True

	def _init (self, vec):
		self.vec = vec

class AST_Mat (AST):
	op, is_mat = 'mat', True

	def _init (self, mat):
		self.mat = mat

	def _rows (self):
		return len (self.mat)

	def _cols (self):
		return len (self.mat [0]) if self.mat else 0

#...............................................................................................
_AST_OP2CLS = {
	'=': AST_Eq,
	'#': AST_Num,
	'@': AST_Var,
	'.': AST_Attr,
	'"': AST_Str,
	',': AST_Comma,
	'(': AST_Paren,
	'[': AST_Brack,
	'|': AST_Abs,
	'-': AST_Minus,
	'!': AST_Fact,
	'+': AST_Add,
	'*': AST_Mul,
	'/': AST_Div,
	'^': AST_Pow,
	'log': AST_Log,
	'sqrt': AST_Sqrt,
	'func': AST_Func,
	'lim': AST_Lim,
	'sum': AST_Sum,
	'diff': AST_Diff,
	'intg': AST_Intg,
	'vec': AST_Vec,
	'mat': AST_Mat,
}

_AST_CLS2OP = dict ((b, a) for (a, b) in _AST_OP2CLS.items ())

for cls in _AST_CLS2OP:
	setattr (AST, cls.__name__ [4:], cls)

AST.Zero     = AST ('#', '0')
AST.One      = AST ('#', '1')
AST.NegOne   = AST ('#', '-1')
AST.VarNull  = AST ('@', '')
AST.I        = AST ('@', 'i')
AST.E        = AST ('@', 'e')
AST.Pi       = AST ('@', '\\pi')
AST.Infty    = AST ('@', '\\infty')
AST.None_    = AST ('@', '\\text{None}')
AST.True_    = AST ('@', '\\text{True}')
AST.False_   = AST ('@', '\\text{False}')
AST.NaN      = AST ('@', '\\text{nan}')
AST.MatEmpty = AST ('func', 'Matrix', ('[', ()))

def sympyEI (yes = True):
	AST.E, AST.I = (AST ('@', 'E'), AST ('@', 'I')) if yes else (AST ('@', 'e'), AST ('@', 'i'))

class sast: # for single script
	AST     = AST
	sympyEI = sympyEI
# TODO: Concretize empty matrix stuff.
# TODO: Concretize empty variable stuff.
# TODO: remap \begin{matrix} \end{matrix}?

# Builds expression tree from text, nodes are nested AST tuples.

import ast as py_ast
from collections import OrderedDict
import os
import re


def _FUNC_name (FUNC):
	return f'a{FUNC.grp [2] [3:]}' if FUNC.grp [2] else \
			FUNC.grp [0] or FUNC.grp [1] or FUNC.grp [3] or FUNC.grp [4].replace ('\\_', '_') or FUNC.text

def _ast_from_tok_digit_or_var (tok, i = 0):
	return AST ('#', tok.grp [i]) if tok.grp [i] else \
			AST ('@', AST.Var.SHORT2LONG.get (tok.grp [i + 1] or tok.grp [i + 3], tok.grp [i + 2]))

def _expr_mul_imp (expr_mul_imp, expr_int): # convert x.y * (...) -> x.y (...)
	if expr_mul_imp.is_attr and expr_mul_imp.arg is None:
		if expr_int.is_paren:
			return AST ('.', expr_mul_imp.obj, expr_mul_imp.attr, expr_int.strip_paren (1))
		elif expr_int.is_attr:
			return AST ('.', _expr_mul_imp (expr_mul_imp, expr_int.obj), expr_int.attr)

	return AST.flatcat ('*', expr_mul_imp, expr_int)

def _expr_diff (ast): # convert possible cases of derivatives in ast: ('*', ('/', 'd', 'dx'), expr) -> ('diff', expr, 'dx')
	def _interpret_divide (ast):
		if ast.numer.is_diff_or_part_solo:
			p = 1
			v = ast.numer.var

		elif ast.numer.is_pow and ast.numer.base.is_diff_or_part_solo and ast.numer.exp.is_pos_int:
			p = int (ast.numer.exp.num)
			v = ast.numer.base.var

		else:
			return None

		ast_dv_check = (lambda n: n.is_differential) if v [0] == 'd' else (lambda n: n.is_partial)

		ns = ast.denom.muls if ast.denom.is_mul else (ast.denom,)
		ds = []
		cp = p

		for i in range (len (ns)):
			n = ns [i]

			if ast_dv_check (n):
				dec = 1
			elif n.is_pow and ast_dv_check (n.base) and n.exp.is_pos_int:
				dec = int (n.exp.num)
			else:
				return None

			cp -= dec

			if cp < 0:
				return None # raise SyntaxError?

			ds.append (n)

			if not cp:
				if i == len (ns) - 1:
					return AST ('diff', None, tuple (ds))
				elif i == len (ns) - 2:
					return AST ('diff', ns [-1], tuple (ds))
				else:
					return AST ('diff', AST ('*', ns [i + 1:]), tuple (ds))

		return None # raise SyntaxError?

	# start here
	if ast.is_div: # this part handles d/dx
		diff = _interpret_divide (ast)

		if diff and diff [1]:
			return diff

	elif ast.is_mul: # this part needed to handle \frac{d}{dx}
		tail = []
		end  = len (ast.muls)

		for i in range (end - 1, -1, -1):
			if ast.muls [i].is_div:
				diff = _interpret_divide (ast.muls [i])

				if diff:
					if diff.expr:
						if i < end - 1:
							tail [0 : 0] = ast.muls [i + 1 : end]

						tail.insert (0, diff)

					elif i < end - 1:
						tail.insert (0, AST ('diff', ast.muls [i + 1] if i == end - 2 else AST ('*', ast [i + 1 : end]), diff.dvs))

					else:
						continue

					end = i

		if tail:
			tail = tail [0] if len (tail) == 1 else AST ('*', tuple (tail))

			return tail if end == 0 else AST.flatcat ('*', ast.muls [0], tail) if end == 1 else AST.flatcat ('*', AST ('*', ast.muls [:end]), tail)

	return ast

def _expr_int (ast, from_to = ()): # find differential for integration if present in ast and return integral ast
	if ast.is_differential or ast.is_null_var: # null_var is for autocomplete
		return AST ('intg', None, ast, *from_to)

	elif ast.is_div:
		if ast.denom.is_mul and ast.denom.muls [-1].is_differential:
			return AST ('intg', ('/', ast.numer, ast.denom.muls [0] if len (ast.denom.muls) == 2 else \
					AST ('*', ast.denom.muls [:-1])), ast.denom.muls [-1], *from_to)

		if ast.numer.is_differential:
			return AST ('intg', ('/', ast.One, ast.denom), ast.numer, *from_to)

	elif ast.is_mul and (ast.muls [-1].is_differential or ast.muls [-1].is_null_var): # null_var is for autocomplete
		return AST ('intg', ast.muls [0] if len (ast.muls) == 2 else AST ('*', ast.muls [:-1]), ast.muls [-1], *from_to)

	elif ast.is_add:
		if ast.adds [-1].is_differential:
			return AST ('intg', \
					AST ('+', ast.adds [:-1])
					if len (ast.adds) > 2 else \
					ast.adds [0] \
					, ast.adds [-1], *from_to)

		if ast.adds [-1].is_mul and ast.adds [-1].muls [-1].is_differential:
			return AST ('intg', \
					AST ('+', ast.adds [:-1] + (AST ('*', ast.adds [-1].muls [:-1]),))
					if len (ast.adds [-1].muls) > 2 else \
					AST ('+', ast.adds [:-1] + (ast.adds [-1].muls [0],)) \
					, ast.adds [-1].muls [-1], *from_to)

	elif ast.is_intg and ast.intg is not None:
		return AST ('intg', _expr_int (ast.intg, () if ast.from_ is None else (ast.from_, ast.to)), ast.dv, *from_to)

	raise SyntaxError ('integration expecting a differential')

def _expr_func (iparm, *args, strip_paren = 0): # rearrange ast tree for explicit parentheses like func (x)^y to give (func (x))^y instead of func((x)^y)
	if args [iparm].is_fact:
		if args [iparm].fact.is_paren:
			return AST ('!', args [:iparm] + (args [iparm].fact.strip_paren (strip_paren),) + args [iparm + 1:])

	elif args [iparm].is_pow:
		if args [iparm].base.is_paren:
			return AST ('^', args [:iparm] + (args [iparm].base.strip_paren (strip_paren),) + args [iparm + 1:], args [iparm].exp)

	return AST (*(args [:iparm] + (args [iparm].strip_paren (strip_paren),) + args [iparm + 1:]))

def _expr_func_remap (_remap_func, ast): # rearrange ast tree for a given function remapping like 'Derivative' or 'Limit'
	expr = _expr_func (1, None, ast, strip_paren = None) # strip all parentheses

	if expr.op is None:
		return _remap_func (expr [1])
	else:
		return AST (expr.op, _remap_func (expr [1] [1]), *expr [2:])

_remap_func_Limit_dirs = {'+': ('+',), '-': ('-',), '+-': ()}

def _remap_func_Limit (ast): # remap function 'Limit' to native ast representation for pretty rendering
	if ast.is_null_var:
		return AST ('lim', ast, AST.VarNull, AST.VarNull)
	elif not ast.is_comma:
		raise lalr1.Incomplete (AST ('lim', ast, AST.VarNull, AST.VarNull))

	commas = ast.commas
	l      = len (commas)

	if l == 1:
		ast = AST ('lim', commas [0], AST.VarNull, AST.VarNull)
	elif l == 2:
		ast = AST ('lim', commas [0], commas [1], AST.VarNull)
	elif l == 3:
		return AST ('lim', commas [0], commas [1], commas [2], '+')
	elif commas [3].is_str:
		return AST ('lim', *(commas [:3] + _remap_func_Limit_dirs.get (commas [3].str_, ('+',))))
	elif commas [3].is_eq_eq and commas [3].lhs.as_identifier () == 'dir' and commas [3].rhs.is_str:
		return AST ('lim', *(commas [:3] + _remap_func_Limit_dirs.get (commas [3].rhs.str_, ('+',))))
	else:
		ast = AST ('lim', commas [0], commas [1], commas [2])

	if commas [-1].is_null_var:
		return ast

	raise lalr1.Incomplete (ast)

def _remap_func_Sum (ast): # remap function 'Sum' to native ast representation for pretty rendering
	if ast.is_null_var:
		return AST ('sum', ast, AST.VarNull, AST.VarNull, AST.VarNull)
	elif not ast.is_comma:
		ast = AST ('sum', ast, AST.VarNull, AST.VarNull, AST.VarNull)

	else:
		commas = ast.commas

		if len (commas) == 1:
			ast = AST ('sum', commas [0], AST.VarNull, AST.VarNull, AST.VarNull)

		else:
			ast2 = commas [1].strip_paren (1)

			if not ast2.is_comma:
				ast = AST ('sum', commas [0], ast2, AST.VarNull, AST.VarNull)
			elif len (ast2.commas) == 3:
				return AST ('sum', commas [0], ast2.commas [0], ast2.commas [1], ast2.commas [2])

			else:
				commas = ast2.commas
				ast    = AST (*(('sum', ast.commas [0], *commas) + (AST.VarNull, AST.VarNull, AST.VarNull)) [:5])

		if commas [-1].is_null_var:
			return ast

	raise lalr1.Incomplete (ast)

def _remap_func_Derivative (ast): # remap function 'Derivative' to native ast representation for pretty rendering
	if ast.is_null_var:
		return AST ('diff', ast, (AST.VarNull,))
	elif not ast.is_comma:
		raise lalr1.Incomplete (AST ('diff', ast, (AST.VarNull,)))
	elif len (ast.commas) == 1:
		raise lalr1.Incomplete (AST ('diff', ast.commas [0], (AST.VarNull,)))

	commas = list (ast.commas [:0:-1])
	ds     = []

	while commas:
		d = commas.pop ().as_differential ()

		if commas and commas [-1].is_num:
			ds.append (AST ('^', d, commas.pop ()))
		else:
			ds.append (d)

	return AST ('diff', ast.commas [0], AST (*ds))

def _remap_func_Integral (ast): # remap function 'Integral' to native ast representation for pretty rendering
	if not ast.is_comma:
		return AST ('intg', ast, ast.as_differential () if ast.is_var else AST.VarNull)
	elif len (ast.commas) == 1:
		ast = AST ('intg', ast.commas [0], AST.VarNull)

	else:
		ast2 = ast.commas [1].strip_paren (1)

		if not ast2.is_comma:
			return AST ('intg', ast.commas [0], ast2.as_differential ())
		elif len (ast2.commas) == 3:
			return AST ('intg', ast.commas [0], ast2.commas [0].as_differential (), ast2.commas [1], ast2.commas [2])
		else:
			ast = AST (*(('intg', ast.commas [0], ast2.commas [0].as_differential ()) + ast2.commas [1:] + (AST.VarNull, AST.VarNull)) [:5])

	raise lalr1.Incomplete (ast)

def _remap_func_Pow (ast):
	if not ast.is_comma:
		raise lalr1.Incomplete (AST ('^', ast, AST.VarNull))

	if len (ast.commas) == 1:
		raise lalr1.Incomplete (AST ('^', ast.commas [0], AST.VarNull))

	if len (ast.commas) == 2:
		ast = AST ('^', ast.commas [0], ast.commas [1])

		if ast.exp.is_null_var:
			raise lalr1.Incomplete (ast)
		else:
			return ast

	raise SyntaxError ('too many parameters')

def _remap_func_Matrix (ast):
	if ast.is_brack and ast.bracks:
		if not ast.bracks [0].is_brack: # single layer or brackets, column matrix?
			return AST ('mat', tuple ((e,) for e in ast.bracks))

		elif ast.bracks [0].bracks:
			rows = [ast.bracks [0].bracks]
			cols = len (rows [0])

			for row in ast.bracks [1 : -1]:
				if len (row.bracks) != cols:
					break

				rows.append (row.bracks)

			else:
				l = len (ast.bracks [-1].bracks)

				if l <= cols:
					if len (ast.bracks) > 1:
						rows.append (ast.bracks [-1].bracks + (AST.VarNull,) * (cols - l))

					if l != cols:
						raise lalr1.Incomplete (AST ('mat', tuple (rows)))

					return AST ('mat', tuple (rows))

	return AST ('func', 'Matrix', ast)

def _expr_curly (ast): # convert curly expression to vector or matrix if appropriate
	if ast.op != ',':
		return ast
	elif not ast.commas: # empty {}?
		return AST.VarNull

	c = sum (bool (c.is_vec) for c in ast.commas)

	if not c:
		return AST ('vec', ast.commas)

	if c == len (ast.commas) and len (set (len (c.vec) for c in ast.commas)) == 1:
		return AST ('mat', tuple (c.vec for c in ast.commas))

	raise SyntaxError ('invalid matrix syntax')

#...............................................................................................
class Parser (lalr1.Parser):
	_PARSER_TABLES = \
			b'eJztXW2P3DaS/jMHZAZQA+K75G924s0aaztZxwn2MAgMx3EWwcZJzrH37nDIf7+qekhRlNRSd0/PjLo9GI4kskWyqlgP34qkLq4++4+3v/74WfXZsyfPv/2G7k+ev6Tr0yfP6PrNt3L9+wsJ+upLuv7l2+efs+fxXzjs0cMXdP364YvHz59y3C+ff/Xi8avP' \
			b'v33x9D/53RcPP483Fe+aIz3+8tWzhy9fPPlH9DwqfN8Vvq87n6TKuTyidP72+CU/fvPyhZD5iK7PhdjvhKLPv3r27GGK8yLH6ajlhxdPvvwrM/Hw2dd0/eLR02+ePvzmr/T4+PkXmUD2PCp83xW+TCCn8BLZUxac8uO/i0Dl9vVTEe8XT7578sVjfueLr14K' \
			b'Bw8jCyyihy9fdvHZ//gfnzObX7948uwxx375FV3evH7/9sOr396/+vGHX/748Po9Bf3x8Yd/y8Pb//n9/at3rz+8evPbL33v+9/+e+D9I/n/+Pj72y7qTx9/ffPq9ft/5h9/oMde2r9+fJceP7x93z3/8P71m3+9/ZC8bz6+/+V/exl2ydNr6fl3YuPX5Hn9' \
			b'Q0fP6w8futx+z2T/9PrNhz6VmcKOiB6Zv/zchf78axfv3cdfXv387vfk/fHnf+fHn37qWHz7z34EeuhI+/HHnOrb/0rP3VPH/m/v3r0uPH989n11dbExvjL+ssJDkIdqY/mu6+qiqdqKAnRbtZcpTEI670YrfvLyb8kfLrNfZe9G0lYtLtZdRi+lISk5zozT' \
			b'U5ybRjQOjWFdwEYLuVr+2W/wCz9wkjEc6dPbMRAv2eqC86T0fAqgNPmJQ4USVeNiKbJSl4OgIpAf6YkS3bjKNNUGuVp+4DcCLha009NGNZIrEa+IYG34/7ILKrzKxgcO4+gkUua2vsw+lg2VTiiC/dCn2yIkjHyqH0J0ihYwez4+XSjxXAqjXJqGkkz+jbxF' \
			b'/FzomJdKP8bAzrNRYMVUF0Q28chSt5WFklHezeX231lDScF2eU2Vb22UlAeJGzqmWI66ItdTNfqxC88hHiEmhwSE2BzSIMSlENIqkZvFhSWJ+OSBkhqDi0geKRkjj/yk04+X0Uu+9IMEBfm3OrEY/Sb7N6JnSuFCor+8zI/01EiRAsQNPzDloYKmacVyUh0W' \
			b'kSiHxrBegBLhmw5PjDhArsFlE9ngR4V8qA4QtY5iptpA+CbpX9hecTKgoBUspliYrtNKyt34Ti2jV5UBocuFvBb1hq9QY/GDjg+bCDYGC+opLjvdVJZpiHVJDCI/BV+Wbw3fSH7ySu5OWI6MRVnlQG0mw9iXwyEkSp60i2ruK1LjUJFU6V2SCimqyEqLHlhb' \
			b'hYrrbu8q7ysfqlBXQbFwOS/L9aZvKs8VMcmFaijmlPDj6sqpqiHHKk46XUmzwGVBkGf0NawSgRIUDaHytxWlVQVTBcrUVcGzwpO4BTaV05WjK73kKucrFxh/pCVUGRAwSRgNEdpUDTUwddWqqtVVS62LrVpKit6p6++rC8rnktoq5vdS8CY3YpoEwRBlr8E7' \
			b'Gj4d5MerCyvhFyQQviGBJv7Wis873HwMDZLbiUrKg0MqakhDQxoQgraRRR1ZFkGeBl8tGLKg3Eoph7Zq6rNSdBsim1BxCw11NTS9aWKpioZ+MuhvohQUwBtvGrIwALYRvaD+mV0R5Vfco/uESupKWuBLaXe70gBI10QjsGXaTGNjqoZiu6rxa6LU1qi2U3ul' \
			b'AYQg0u3RLK1WbBRjVaFiAxCbPdT/Dq0BEyHpCWbOVhsvPEQQ7KeEwYuAFjJE7o3o0FFSNrGLZdTxkoy1uJOkva68qbytfF15Vbmmcu35lhRxbT9Jrt0nybX/9Li+cBiNaHTZFBqjBoFtHNS1+LFF29SipWrxaiuq0vqqDVVLYmm5fouNWJ0HhRqjQX3GjZkM' \
			b'bInBM2SMWCLGzoolUckz4aU5I168VBInzoM/dR54hk3LPIYgn6elWMVOh37fgH4r6jQYiFkpn8FMY8DIDRM4x58gqbtZI41ZI41ZI81DQS3S5nkTvhkL2o1Ds2kwBuyGR2g/MUg6u8bmwqZhsXQi1kOXAhKMj4UjDcjKZrN44gTUtSukjhoqdB0bu6qiJbrc' \
			b'zYDep8khjTkhjekf1Exn3hkOgpdPZU7nimfuNGbuPiG2L9BEhdhihXMf4RkB79EUpjfVy1N20iUwEKXHrx41pq9jL8VjKO7Qa7lw0e5iERel4WIT1SLFVlIsRuhXPJbXGMRr2FlRVbVx4B+Tb9tkxuVFB1Sq5hKjQTPuPknY0FDbTISy18BrYhfTnJSl84q7' \
			b'w+aUusPSDzZnNYLn/rqOPWqDHrVBj5pugziIoGvoGzGy5RXpcnMqKmqq1akHbmAyM7BK8a2JQG3QkK9GLg0qAQuMGvBMKRtULp/eDKeKvEMgUS7wmTqJxcQ6V6Oy5Ur+vMVyxW3IOTfW3CgaNIoGjSLfWoWbRom3mAlo0TVvRSLTNQOxb0+slWIqR+00U4zq' \
			b'0qK6tLJsRbFX6j+7unEjV7FSxYMdA1IpZZv6S0C5BbDlVx+RnfpJaCTa2OVoUZO3EjroGZGAHATkICB3xiCR1vCcGWSNluKUK+Xkou64VO9Ddxy0w6IysFAOG/sXHvrgoQ90I2kANB5LNjzed/H9cNqTv1fMbACzQeSDaQzMyxGxYTCjyiLg94mnBqJqELuJ' \
			b'EZozEEh76jwQWSfOA6tSG9dc1nHRZS2tWl1dUWpUjUUiqjYSFZN3MiPTSp6aKzqQzwQa4axhniZlAMK5q6ylz+xEhFpYDFFCQAMbxmvKsmZyLf1z54FGEjVlXbOUiCihit5hupgkXicqUiA/LwHm9b+8PpoX8PDKG147yQsneUUcL4fj9WY8Q86z47xgmhfb' \
			b'sjh4nQrPDfC0Ac8Z8JCbx9u82JjFx6XEFg6e6eRpySaQ2GRvjyz697IrgzepUKK8z4bibYJsFKhkQw9pyMbyngV6m8po43i5P/3Gu4l4P0ngVHhPCT1yYkb2W2wcr+5XsqJ+QwW8obLdUIFuAu8zqXmnAudDd1LCjfVIn7dg8M4e3jrAGwwaXvJP98Cbc2ps' \
			b'NSBZb1omlTmQDUcUh8KYREqNKfZx8w7FsLKthWLyxhCK0fA2DHqHKeH9HvQKlfHG8a4gDqaoLWfCzDMxFEbluwlO1vvz5qHAO1bo55ZfZcZ4ZxHLg+mlqLzPxdXf8+CRVXNCJW3SyqanmAmTaI2zkgqEGIedqkoXDc31jNr28YYBDcZ8nS6TlFAjRI32EdK8' \
			b'JLSn2lh3SSXI4Byq+Tb1pt+YxTk15+WSI1Vn9Q8LKt9ktec5MJ4fK9TfTkCATWgUzqvveOldBwn6jQ0TbJUo4NGw1LaAoengUAKCMmmkDjQjbLBe8qWHjyb+LeKkKf4YMYr12YNEAWUtwGk66DAFRmhRTPMARF1SAzBxciMMcbR2FknNEEvgahpPlAcTFxEF' \
			b'KjKq3BhZVFCMKS6BDmWR/B7Wqv/z9gFXIqQhdHd/Sp/lKu0+WAafvSXMFYALu+NsCmMm4uwmMHYIvpYwpaR54WsPVOJFaASV4CCjSn4p0SRx5NrDE4siuUVM9V/OsUKNpMv2SM03SUUKw+apgFN+bQZNQn0Bp8TSGFCqbJ8SDbN4kqQAo0xPgSSlH3BNp+TO' \
			b'2ROytGVEmXtErQxRXhDlS0R5IMpnRPkSUX6MKC+IKntwyme3jCg/4QRRfowoP4+ofgrziOpem0OUHyEqsjSBKF8iKtIwjyifEdXRsyOi7D2i1oUoVvGWx6Z9RIkXoRFR/NhDlPxSIkriyLWHKK2yW0RU/+UcK9RIukSUELAdUUUKs4jKr80gSqgvEJVYGiNK' \
			b'KMuISjTMIkqSAqIyPTsiyu2DqLsdcpmDR11zSJsbdbk7Gnktos4I6kyJOgPUmYw6U6LOZDeCnxH4mRJ+/QiL8DMTTuBnSvjF0ZcQgYwNcjZNijWEYz/FeTjmjLcPwnREpRmhMnI6gUojqNR5KJaomQemycDskt8RmP4emCcITCfAdCUwMQ3CtwRMVwLTZTcC' \
			b'phNguhKY/QiLwHQTToDppoHpAEwHYDoAE7GGwOynOA/MnPEMMB2AOZptTJxOANMBmL0WM1IzD0yXgdlF2RGY4R6YJwhMGfnpcuSnMfLTeeSny5Efl1pyI2DKEFCXQ8AiwiIw/YQTYPppYGIYKCcI4V3TpFhDYPZTnAdmzngGmB7AHI0ME6cTwMTIUGJGYEZq' \
			b'5oGZB4eZsh2B2RwbmD0T3i3Bs96OUHX+IBVFlUPEeiA1GEyaPJg05WCSzabJDUEqkeVKYm7l5DHcBtGWoNp/OccKNTIAVDndiFSD4aXBCFNuTYwkb5Vg7acpxM3htZf7dryKhBw4K/Ca2B3j1WDcKTGB1/juPF5NHnpmyqbw6t0DmVobw7Zl2CZb9PXAq9bV' \
			b'sBK/U23rnJn7NuFb3wSE9cA6zgETNkEOTnDWJZx7bmQWdEhPrr1mt4iziGU94QTLerLZFTpEswTMGmBGrCGSU3LKxAgDKG81vScqZjCtgWk9wnRke7tBXqJaKV0BNiIsADubD7OQhsBmTuON8Gz0n9izdYRmeGVI/hS6yAZ4Lc2NBuZGk82NpjQ3cgElN4Kr' \
			b'R3y59uHaj7MIVzvhBK52Gq4wP8rZpMjZNCnWEK79FOdb3ZzxDEItEDqySCZOJ1rdCFCbW91IzTw4s1EyU7ZjL1mp+/HrCYJTJpZMObFkYluaJ5ZMObHESxGTG3WNZWLJlBNLRYRFZLoJJ8icnlgymFgymFgymFiKsYbI7Kc4j8yc8QwyMbFkRhNLidMJZGJi' \
			b'yeSJpUTNPDLzxFKmbFdk7rUCZ23InBm6nj04ZekbX/vgDABnyOAMJThDdiNwBgFnKMHZj7AIzjDhBJyhA6cQFLEZgM0AbAZgs4s3hGc/zXl45qxn4BkAzzCCZ+R1Ap4B8AwZnpGaeXiGDM/M3F7DVbXXqp57lK4Hpa2gtFyjKl6EJpS2JUrb7EYobav47YA+' \
			b'SvsRFlHaTjhBaZtR2maUtkBpC5S2QGkXb4jSfprzKM1Zz6C0BUrbEUojrxMobYHSNqM0UjOP0jajNDO3H0r3Wil0j9LVoJQhJjPufZSKF6ERpfzYQykXTXJDlEpkfMolo7SIsIRSO+UYpTbvxhCCgFKhAfniEx+bqDyIMEBpkeYsSntZb0ep5ODAVoHSxOsY' \
			b'pUIvokSUJmpmUSqpAaU95vZD6dFXH92bbG4ZrmKysaXJxsJkY7PJxpYmGy6a5EZwFZONhclG1ugZ3AbRFkGrJpyANptshKwIWphs4qJAC5NNjjcErYRycaQ4s8DN2c8AFzYbO7LZJH4ngAubjc02m0TNPHCzzabH4H7APfrqpHvg3jJwtQC3tM6IF6EJuKVx' \
			b'xvbcCLhimbGwzFjYWi1srUW0ReDqCSfAzfYZm22tFuYZC/OMhXkmxxsCd5DsPG5z7jO4hV3Gjuwyid0J3GrgVmfcRmrmcZtNMj3+9sPt0Rcv3eP2lnErS39tufTXYumvzUt/bbn0lwsluRFuZemvxdJfvhm8ZgbRFnFrJpzgNi8AFrIibrH+12L9r8X63xxv' \
			b'iNtBsvO4zbnP4BargO1oFXBidwK3WAVs8yrgRM08bvMq4B5/++H2fm3TqeNWrKu2tK5aWFdttq7a0rrKJZLcCLdiWrUwrfLNGNwG0RZxayec4DYbWIWsiFvYVy3sqxb21RxviNtBsvO4zbnP4BZWVjuysiZ2J3ALK6vNVtZEzTxus5W1x99+uG2PitvRySJH' \
			b'hC6pJanicQBszhTEfP4H/17uH22wfzQfc6DKcw5Uk91oI6mcdKBkoRjjWL4waqr4DdYi5uKO0mbCyY7SpsOxgjVW8a5LFTeX4hgE8cX8+/GHe00HyffwrKRrMtpyminZjmnJyIHLAtOJ9TGmhWxESZtPI0WzmJbU4ubTzONemNY3scBpbc2xPv8WWUuLrMsW' \
			b'WaNF1rlF1mWLzAdC2ehG650C4ss14GYMbjpH0zs0yv2Xc6xQIwOAWedGWaNR1miUNRrlHG+4O6BMtlky4vYImNkjgHZZj9rlxPEYw3F5os7tcnx3YY9Abpd7LO6H4aMvglobgM8dvVaaYls2xRZNsc1NsS2bYttkN+pPS1PM14Ab96fRDhfRFvvTzYST/nRu' \
			b'h21eFWXR/lq0vxbtb4437E8Pkp3vT+fcZ/rTaHvtqO1N7E70p9H22tz2Jmrm+9O57e3xtx9u55dI+RK66h69R0Rvc+zOtKyaUuWqKYVVUx5LGn3sT+eFU3y2XiOvkfNSVY+61LJ2SmHtFN+4Px3Qnw7ZTeGYRy65Px0mnPSn8woqlVdQKaygUlhBpbCCKscb' \
			b'9qMHyXLp1Ntw3Mt9pg+NRVRqtIgqsTvRh8YiKpUXUcnQLVI034/OC6l6PE5g2dUPuHZMkK7VA66vpqB99HVV96AuQW1uoVl2Yg92pT3YwR7ssj3YlfZgLoDkhnCWyHINuPEBqbAHF9GWmuX+yzlWqJEB4OyyPdjBHuxgD3awB+d4AzgPk51tlnu5b4ezgznY' \
			b'jczBid0JODsI1iJahHSiaBbOLpuEezzu1zQffcXVqePXA8PM9+nhWMzDrjQPO5iHXTYPu9I87HpuhGMxDzuYhx3Mww7m4SLaIo71hBMcZ/Owy+ZhB/Owg3nYwTyc4w1xPEh2Hsc5dwhFg4gpNMNI7EZG4sT0GM1JioiVwBzJmgdzthP3GN0PzK66urEjom/q' \
			b'fGj+hNiNnRE9BaQEogI4XB68zrC6iyOib/54aDnxb6zgRzgiekKTtxwTTRQua2dztDPMSaC3eoy52U9N+avkPDjbdqQ5f4aF7RMycumrLc/mq2p4zHmzr/6q9rg6PHHMuZIBydF1eV6PWbj76HIS+JZjz3PbW+p2an+HOh72qYHtMc7pR6/IrrE2Ngun9quZ' \
			b'Gvmap/ar8b6Po53cr7CfQ+ljqrWS6bmjVNEs5JmT/Fne26pp6mSo9gHJ/U981fXw7oQ92kcn+IMZN1Fh76rF6uBvT1xLgye0V7VH0uC5Y4mnDsC4re9PsHAP+wYFSermur67KiqGnUfUVf4Iumb9rG+xL3yC30uRr7xMbJc7WG9xzI6SNux6HWRu5XbRYap5' \
			b'+eMOzvyJrzZe3eUgDh+M2/38o2NWt9yF4wLwh1S5JzN+U7Knua12O2foyJ/4QebNAdUsUX63iunudfMWdJPCvLo7/dz4+lD91NfVT3VtFbVH1tKtM81L2qpXqbF+h3VUh2kt02SOqbl+tCpq46enfctO7LW12FxXi/XRKtq2uaG6dhcN/nS0t6+5LJfj17s7' \
			b'aO41tdZeV2vN8bS2vdfaW9fam+gt3LzWuutq7Xbb9v6d2vpebW9bbeXoktNTW7+r2vpDx2KmXH2xkyFtTl/nFkfdgK1XjGdaDDfH1NkAw0K4/pBMUopKG5c97GUp266oC58yPa7Fl782y4rKmU7Oa+nmAYFcprXCvdLeidKyehFJfLum0kpK56C0XpSWWVhS' \
			b'2qa6Wstympue4wrXXUZjT2F+q1DIm5zP4oV911szQ/lerUP1bmFq9TCVcyelbjc+dXqQmpFUVqJmtzSLv6hqVvo1SvaiTKqdvwu1c4dpHUe7CcUTcnbSO162Vn7dfum79sTe1RoUcg3KONkRzNrHI9n7Om+vOo/XOVEHTz59QoTca9pcC9ucTPPKu0fWp2rh' \
			b'Ae+YrGlEwa1b+2DTiNqZe7WbVbvT6dU5cSeidra6UrKJy8m+F1EG15DA+TQhL0qBjbSiHVa6h072/bJe7q6LbkrbRLPUblokmjOrNdwMRlVgQR1S8rIUfmqeokbZ7VBWYalsRIS+E+EBc1tmzymto0xb7QreMCwKhckmdTAeOeqhE0xHmEbaDXRMJJVtf6qI' \
			b'Si4V8r4lvHuFfWvlWpSpvl4Fe0i38VZKMRYh1ZW2liLk2b5YMUaBZ6Hw8Qe1itWjHMXb9hMTnLc5fq/QOuH7QXoiJhFRn/Vua/AgfYpwsZFDcJScokMiDQrrjpk22fMkC+Z5/IqFw0zURm+LQn2M/Cevmt6r8qWz/iZeEmBQxQ5brE6K+16xl5U/2lHxH3+W' \
			b'Q4zxyclaaNlhEuQF3jQVfxGro2x3EirsMaigWLv8SYZuIUNnd8uTmtXRH1sYJsIlXzmRm/cez2ZNuj3MneNMUuClAzjxx5MrPZ912SekhF1JwU7tnQmiV7f8pc7n5K9CU7MfTdg9vhtl2NaVt1ITpW0195e6yFt+HXRgmXo5RrK5PfqJQA6/QSdsqfq2+VLV' \
			b'DTvwpQ7ji1rSEWtmH/Z0dYibCOKB11wksKkjm/oonOppbpmU7Rxz3c9jVTxcx40TmUoWjJu7Z9xVt+vAuB0y3jvII37ZNciZHTvIwUtbxMdw+N4BHOWhG+WpGnyiBmfuBoIycaagd0TVWGBtdTdOZqNDGebCtvchZnfn+sXzRrfqwLhf1K8dJVCo1VZpDBVp' \
			b'SYl4Kq3nQrqGMnzR8bgL0XjENf0KDQDGeZUOMgsrl1moVuMgsGblAmuq1TgIrF25wGQ6cR0Oo+R63QLjuaS1OAhMrVxgplqNg8BGXe+DBLbYBbum2Hx1fcdz0MMgfXh6EN+oA3+b/dj95dhU8w7H0y2+tovjKd99IkCedzou2FuePHm+Ugdxjvr/6xanr9bq' \
			b'IM7lUcWqxBmqtTqIc3nAsSpxttVaHcS5PBxZ65wK26fW7iDjNq5VYLMGCwcWKuqms7BF0hAY8cuGhjqaTzu7qMfELp9awWb3hi3pKrDhiyI1UZZNNHxp+S5uV1YkVzYJWN4BLdtJa95Sj1fN5Kuu6jm8aEcvclnxy77qO+ViBCfFkxdliAWRrYceTTbv+1K+' \
			b'lYPY7feX31/+PyjTlW8=' 

	_PARSER_TOP             = 'expr_commas'
	_PARSER_CONFLICT_REDUCE = {'BAR'}

	_GREEK       = '|'.join (reversed (sorted (f'\\\\{g}' for g in AST.Var.GREEK)))
	_SPECIAL     =  r'\\partial|\\pi|\\infty'
	_CHAR        = fr'[a-zA-Z]'
	_PYVAR       = '|'.join (reversed (sorted (AST.Var.PY | {f'_{g}' for g in AST.Var.GREEK})))
	_TEXTVAR     = fr'\\text\s*\{{\s*({_PYVAR})\s*\}}'
	_ONEVAR      = fr'{_CHAR}|{_GREEK}'
	_DSONEVARSP  = fr'(?:(\d)|({_PYVAR})|({_CHAR}|{_GREEK}|{_SPECIAL})|{_TEXTVAR})'
	_STR         =  r'\'(?:\\.|[^\'])*\'|"(?:\\.|[^"])*["]'

	_FUNCPYONLY  = '|'.join (reversed (sorted (AST.Func.PY_ONLY)))
	_FUNCPYTEX   = '|'.join (reversed (sorted (AST.Func.PY_AND_TEX)))
	_FUNCTEXONLY = '|'.join (reversed (sorted (AST.Func.TEX_ONLY)))

	TOKENS       = OrderedDict ([ # order matters
		('IGNORE_CURLY',  r'\\underline|\\mathcal|\\mathbb|\\mathfrak|\\mathsf|\\mathbf|\\textbf'),
		('SQRT',          r'\\?sqrt'),
		('LOG',           r'\\?log'),
		('FUNC',         fr'({_FUNCPYONLY})|\\?({_FUNCPYTEX})|\\({_FUNCTEXONLY})|\$({_CHAR}\w*)|\\operatorname\s*\{{\s*({_CHAR}(?:\w|\\_)*)\s*\}}'),
		('LIM',           r'\\lim'),
		('SUM',           r'\\sum'),
		('INT',           r'\\int(?:\s*\\limits)?'),
		('LEFT',          r'\\left'),
		('RIGHT',         r'\\right'),
		('CDOT',          r'\\cdot'),
		('TO',            r'\\to'),
		('BEG_MATRIX',    r'\\begin\s*\{\s*matrix\s*\}'),
		('END_MATRIX',    r'\\end\s*\{\s*matrix\s*\}'),
		('BEG_BMATRIX',   r'\\begin\s*\{\s*bmatrix\s*\}'),
		('END_BMATRIX',   r'\\end\s*\{\s*bmatrix\s*\}'),
		('BEG_VMATRIX',   r'\\begin\s*\{\s*vmatrix\s*\}'),
		('END_VMATRIX',   r'\\end\s*\{\s*vmatrix\s*\}'),
		('BEG_PMATRIX',   r'\\begin\s*\{\s*pmatrix\s*\}'),
		('END_PMATRIX',   r'\\end\s*\{\s*pmatrix\s*\}'),
		('FRAC2',        fr'\\frac\s*{_DSONEVARSP}\s*{_DSONEVARSP}'),
		('FRAC1',        fr'\\frac\s*{_DSONEVARSP}'),
		('FRAC',          r'\\frac'),
		('NUM',           r'(?:(\d*\.\d+)|(\d+)\.?)([eE][+-]?\d+)?'),
		('VAR',          fr"({_PYVAR})|(d|\\partial\s?)?({_ONEVAR})|{_SPECIAL}|{_TEXTVAR}"),
		('ATTR',         fr'\.(?:({_CHAR}\w*)|\\text\s*{{\s*({_CHAR}\w*)\s*}})'),
		('STR',          fr"(?<!\d|{_CHAR}|['}}])({_STR})|\\text\s*\{{\s*({_STR})\s*\}}"),
		('PRIMES',        r"'+|(?:_prime)+"),
		('SUB1',         fr'_{_DSONEVARSP}'),
		('SUB',           r'_'),
		('CARET1',       fr'\^{_DSONEVARSP}'),
		('CARET',         r'\^'),
		('DBLSTAR',       r'\*\*'),
		('PARENL',        r'\('),
		('PARENR',        r'\)'),
		('CURLYL',        r'{'),
		('CURLYR',        r'}'),
		('BRACKETL',      r'\['),
		('BRACKETR',      r'\]'),
		('BAR',           r'\|'),
		('PLUS',          r'\+'),
		('MINUS',         r'-'),
		('STAR',          r'\*'),
		('INEQ',          r'==|!=|\\neq?|<=|\\le|<|\\lt|>=|\\ge|>|\\gt'),
		('EQ',            r'='),
		('DIVIDE',        r'/'),
		('EXCL',          r'!'),
		('AMP',           r'&'),
		('DBLSLASH',      r'\\\\'),
		('COMMA',         r','),
		('ignore',        r'\\,|\\:|\\?\s+'),
	])

	_FUNC_AST_REMAP = {
		'Abs'       : lambda expr: _expr_func (1, '|', expr, strip_paren = 1),
		'abs'       : lambda expr: _expr_func (1, '|', expr, strip_paren = 1),
		'Derivative': lambda expr: _expr_func_remap (_remap_func_Derivative, expr),
		'diff'      : lambda expr: _expr_func_remap (_remap_func_Derivative, expr),
		'exp'       : lambda expr: _expr_func (2, '^', AST.E, expr, strip_paren = 1),
		'factorial' : lambda expr: _expr_func (1, '!', expr, strip_paren = 1),
		'Integral'  : lambda expr: _expr_func_remap (_remap_func_Integral, expr),
		'integrate' : lambda expr: _expr_func_remap (_remap_func_Integral, expr),
		'Limit'     : lambda expr: _expr_func_remap (_remap_func_Limit, expr),
		'limit'     : lambda expr: _expr_func_remap (_remap_func_Limit, expr),
		'Matrix'    : lambda expr: _expr_func_remap (_remap_func_Matrix, expr),
		'ln'        : lambda expr: _expr_func (1, 'log', expr),
		'Pow'       : lambda expr: _expr_func_remap (_remap_func_Pow, expr),
		'pow'       : lambda expr: _expr_func_remap (_remap_func_Pow, expr),
		'Sum'       : lambda expr: _expr_func_remap (_remap_func_Sum, expr),
	}

	def expr_commas_1   (self, expr_comma, COMMA):                              return expr_comma if expr_comma.is_comma else AST (',', (expr_comma,))
	def expr_commas_2   (self, expr_comma):                                     return expr_comma
	def expr_commas_3   (self):                                                 return AST (',', ())
	def expr_comma_1    (self, expr_comma, COMMA, expr):                        return AST.flatcat (',', expr_comma, expr)
	def expr_comma_2    (self, expr):                                           return expr

	def expr            (self, expr_eq):                      	                return expr_eq

	def expr_eq_1       (self, expr_ineq1, EQ, expr_ineq2):                     return AST ('=', '=', expr_ineq1, expr_ineq2)
	def expr_eq_2       (self, expr_ineq):                                      return expr_ineq
	def expr_ineq_2     (self, expr_add1, INEQ, expr_add2):                     return AST ('=', AST.Eq.LONG2SHORT.get (INEQ.text, INEQ.text), expr_add1, expr_add2)
	def expr_ineq_3     (self, expr_add):                                       return expr_add

	def expr_add_1      (self, expr_add, PLUS, expr_mul_exp):                   return AST.flatcat ('+', expr_add, expr_mul_exp)
	def expr_add_2      (self, expr_add, MINUS, expr_mul_exp):                  return AST.flatcat ('+', expr_add, expr_mul_exp.neg (stack = True))
	def expr_add_3      (self, expr_mul_exp):                                   return expr_mul_exp

	def expr_mul_exp_1  (self, expr_mul_exp, CDOT, expr_neg):                   return AST.flatcat ('*', expr_mul_exp, expr_neg)
	def expr_mul_exp_2  (self, expr_mul_exp, STAR, expr_neg):                   return AST.flatcat ('*', expr_mul_exp, expr_neg)
	def expr_mul_exp_3  (self, expr_neg):                                       return expr_neg

	def expr_neg_1      (self, MINUS, expr_diff):                               return expr_diff.neg (stack = True)
	def expr_neg_2      (self, expr_diff):                                      return expr_diff

	def expr_diff       (self, expr_div):                                       return _expr_diff (expr_div)

	def expr_div_1      (self, expr_div, DIVIDE, expr_mul_imp):                 return AST ('/', expr_div, expr_mul_imp)
	def expr_div_2      (self, expr_div, DIVIDE, MINUS, expr_mul_imp):          return AST ('/', expr_div, expr_mul_imp.neg (stack = True))
	def expr_div_3      (self, expr_mul_imp):                                   return expr_mul_imp

	def expr_mul_imp_1  (self, expr_mul_imp, expr_int):                         return _expr_mul_imp (expr_mul_imp, expr_int)
	def expr_mul_imp_2  (self, expr_int):                                       return expr_int

	def expr_int_1      (self, INT, expr_sub, expr_super, expr_add):            return _expr_int (expr_add, (expr_sub, expr_super))
	def expr_int_2      (self, INT, expr_add):                                  return _expr_int (expr_add)
	def expr_int_3      (self, expr_lim):                                       return expr_lim

	def expr_lim_1      (self, LIM, SUB, CURLYL, expr_var, TO, expr, CURLYR, expr_neg):                           return AST ('lim', expr_neg, expr_var, expr)
	def expr_lim_2      (self, LIM, SUB, CURLYL, expr_var, TO, expr, caret_or_dblstar, PLUS, CURLYR, expr_neg):   return AST ('lim', expr_neg, expr_var, expr, '+')
	def expr_lim_3      (self, LIM, SUB, CURLYL, expr_var, TO, expr, caret_or_dblstar, MINUS, CURLYR, expr_neg):  return AST ('lim', expr_neg, expr_var, expr, '-')
	def expr_lim_6      (self, expr_sum):                                                                         return expr_sum

	def expr_sum_1      (self, SUM, SUB, CURLYL, expr_var, EQ, expr, CURLYR, expr_super, expr_neg):               return AST ('sum', expr_neg, expr_var, expr, expr_super)
	def expr_sum_2      (self, expr_func):                                                                        return expr_func

	def expr_func_1     (self, SQRT, expr_func_arg):                            return _expr_func (1, 'sqrt', expr_func_arg)
	def expr_func_2     (self, SQRT, BRACKETL, expr, BRACKETR, expr_func_arg):  return _expr_func (1, 'sqrt', expr_func_arg, expr)
	def expr_func_3     (self, LOG, expr_func_arg):                             return _expr_func (1, 'log', expr_func_arg)
	def expr_func_4     (self, LOG, expr_sub, expr_func_arg):                   return _expr_func (1, 'log', expr_func_arg, expr_sub)
	def expr_func_5     (self, FUNC, expr_func_arg):
		func  = _FUNC_name (FUNC)
		remap = self._FUNC_AST_REMAP.get (func)

		return remap (expr_func_arg) if remap else _expr_func (2, 'func', func, expr_func_arg)

	def expr_func_6     (self, FUNC, expr_super, expr_func_arg):
		ast = self.expr_func_5 (FUNC, expr_func_arg)

		return \
				AST ('^', ast, expr_super) \
				if expr_super != AST.NegOne or not ast.is_trigh_func_noninv else \
				AST ('func', f'a{ast.func}', ast.arg)

	def expr_func_7     (self, expr_fact):                                      return expr_fact

	def expr_func_arg_1 (self, expr_func):                                      return expr_func
	def expr_func_arg_2 (self, MINUS, expr_func):                               return expr_func.neg (stack = True)

	def expr_fact_1     (self, expr_fact, EXCL):                                return AST ('!', expr_fact)
	def expr_fact_2     (self, expr_pow):                                       return expr_pow

	def expr_pow_1      (self, expr_pow, expr_super):                           return AST ('^', expr_pow, expr_super)
	def expr_pow_2      (self, expr_attr):                                      return expr_attr

	def expr_attr_1     (self, expr_attr, ATTR):                                return AST ('.', expr_attr, ATTR.grp [0] or ATTR.grp [1])
	def expr_attr_2     (self, expr_abs):                                       return expr_abs

	def expr_abs_1      (self, LEFT, BAR1, expr, RIGHT, BAR2):                  return AST ('|', expr)
	def expr_abs_2      (self, BAR1, expr, BAR2):                               return AST ('|', expr)
	def expr_abs_3      (self, expr_paren):                                     return expr_paren

	def expr_paren_1    (self, LEFT, PARENL, expr_commas, RIGHT, PARENR):       return AST ('(', expr_commas)
	def expr_paren_2    (self, PARENL, expr_commas, PARENR):                    return AST ('(', expr_commas)
	def expr_paren_3    (self, IGNORE_CURLY, CURLYL, expr, CURLYR):             return expr
	def expr_paren_4    (self, expr_frac):                                      return expr_frac

	def expr_frac_1     (self, FRAC, expr_mat1, expr_mat2):                     return AST ('/', expr_mat1, expr_mat2)
	def expr_frac_2     (self, FRAC1, expr_mat):                                return AST ('/', _ast_from_tok_digit_or_var (FRAC1), expr_mat)
	def expr_frac_3     (self, FRAC2):                                          return AST ('/', _ast_from_tok_digit_or_var (FRAC2), _ast_from_tok_digit_or_var (FRAC2, 4))
	def expr_frac_4     (self, expr_mat):                                       return expr_mat

	def expr_mat_1      (self, LEFT, BRACKETL, BEG_MATRIX, expr_mat_rows, END_MATRIX, RIGHT, BRACKETR):  return AST ('mat', expr_mat_rows) if expr_mat_rows else AST.MatEmpty
	def expr_mat_2      (self, BEG_MATRIX, expr_mat_rows, END_MATRIX):                                   return AST ('mat', expr_mat_rows) if expr_mat_rows else AST.MatEmpty
	def expr_mat_3      (self, BEG_BMATRIX, expr_mat_rows, END_BMATRIX):                                 return AST ('mat', expr_mat_rows) if expr_mat_rows else AST.MatEmpty
	def expr_mat_4      (self, BEG_VMATRIX, expr_mat_rows, END_VMATRIX):                                 return AST ('mat', expr_mat_rows) if expr_mat_rows else AST.MatEmpty
	def expr_mat_5      (self, BEG_PMATRIX, expr_mat_rows, END_PMATRIX):                                 return AST ('mat', expr_mat_rows) if expr_mat_rows else AST.MatEmpty
	def expr_mat_6      (self, expr_curly):                                                              return expr_curly
	def expr_mat_rows_1 (self, expr_mat_row, DBLSLASH):                         return expr_mat_row
	def expr_mat_rows_2 (self, expr_mat_row):                                   return expr_mat_row
	def expr_mat_rows_3 (self):                                                 return ()
	def expr_mat_row_1  (self, expr_mat_row, DBLSLASH, expr_mat_col):           return expr_mat_row + (expr_mat_col,)
	def expr_mat_row_2  (self, expr_mat_col):                                   return (expr_mat_col,)
	def expr_mat_col_1  (self, expr_mat_col, AMP, expr):                        return expr_mat_col + (expr,)
	def expr_mat_col_2  (self, expr):                                           return (expr,)

	def expr_curly_1    (self, CURLYL, expr_commas, CURLYR):                    return _expr_curly (expr_commas)
	def expr_curly_2    (self, expr_bracket):                                   return expr_bracket

	def expr_bracket_1  (self, LEFT, BRACKETL, expr_commas, RIGHT, BRACKETR):   return AST ('[', expr_commas.commas if expr_commas.is_comma else (expr_commas,))
	def expr_bracket_2  (self, BRACKETL, expr_commas, BRACKETR):                return AST ('[', expr_commas.commas if expr_commas.is_comma else (expr_commas,))
	def expr_bracket_3  (self, expr_term):                                      return expr_term

	def expr_term_1     (self, STR):                                            return AST ('"', py_ast.literal_eval (STR.grp [0] or STR.grp [1]))
	def expr_term_2     (self, SUB):                                            return AST ('@', '_') # for last expression variable
	def expr_term_3     (self, expr_var):                                       return expr_var
	def expr_term_4     (self, expr_num):                                       return expr_num

	def expr_num        (self, NUM):                                            return AST ('#', NUM.text) if NUM.grp [0] or NUM.grp [2] else AST ('#', NUM.grp [1])

	def expr_var_1      (self, var, PRIMES, subvar):                            return AST ('@', f'''{var}{subvar}{PRIMES.text.replace ("_prime", "'")}''')
	def expr_var_2      (self, var, subvar, PRIMES):                            return AST ('@', f'''{var}{subvar}{PRIMES.text.replace ("_prime", "'")}''')
	def expr_var_3      (self, var, PRIMES):                                    return AST ('@', f'''{var}{PRIMES.text.replace ("_prime", "'")}''')
	def expr_var_4      (self, var, subvar):                                    return AST ('@', f'{var}{subvar}')
	def expr_var_5      (self, var):                                            return AST ('@', var)

	def var_2           (self, VAR):
		return \
				f'\\partial {VAR.grp [2]}' \
				if VAR.grp [1] and VAR.grp [1] != 'd' else \
				AST.Var.SHORT2LONG.get (VAR.grp [0] or VAR.grp [3], VAR.text)

	def subvar_1        (self, SUB, CURLYL, expr_var, CURLYR):                  return f'_{expr_var.var}' if expr_var.var and expr_var.is_single_var else f'_{{{expr_var.var}}}'
	def subvar_2        (self, SUB, CURLYL, NUM, CURLYR):                       return f'_{{{NUM.text}}}'
	def subvar_3        (self, SUB, CURLYL, NUM, subvar, CURLYR):               return f'_{{{NUM.text}{subvar}}}'
	def subvar_4        (self, SUB1):                                           return f'_{AST.Var.SHORT2LONG.get (SUB1.grp [1] or SUB1.grp [3], SUB1.text [1:])}'

	def expr_sub_1      (self, SUB, expr_frac):                                 return expr_frac
	def expr_sub_2      (self, SUB1):                                           return _ast_from_tok_digit_or_var (SUB1)

	def expr_super_1    (self, DBLSTAR, expr_func):                             return expr_func
	def expr_super_2    (self, DBLSTAR, MINUS, expr_func):                      return expr_func.neg (stack = True)
	def expr_super_3    (self, CARET, expr_frac):                               return expr_frac
	def expr_super_4    (self, CARET1):                                         return _ast_from_tok_digit_or_var (CARET1)

	def caret_or_dblstar_1 (self, DBLSTAR):                                     return '**'
	def caret_or_dblstar_2 (self, CARET):                                       return '^'

	#...............................................................................................
	_AUTOCOMPLETE_SUBSTITUTE = { # autocomplete means autocomplete AST tree so it can be rendered, not necessarily expression
		'CARET1'             : 'CARET',
		'SUB1'               : 'SUB',
		'FRAC2'              : 'FRAC',
		'FRAC1'              : 'FRAC',
		'expr_super'         : 'CARET',
		'caret_or_doublestar': 'CARET',
	}

	_AUTOCOMPLETE_CONTINUE = {
		'RIGHT'   : ' \\right',
		'COMMA'   : ',',
		'PARENL'  : '(',
		'PARENR'  : ')',
		'CURLYR'  : '}',
		'BRACKETR': ']',
		'BAR'     : '|',
	}

	def _insert_symbol (self, sym, tokinc = 0):
		tokidx       = self.tokidx
		self.tokidx += tokinc

		for sym in ((sym,) if isinstance (sym, str) else sym):
			if sym in self.TOKENS:
				self.tokens.insert (tokidx, lalr1.Token (self._AUTOCOMPLETE_SUBSTITUTE.get (sym, sym), '', self.tok.pos))

				if self.autocompleting:
					if sym in self._AUTOCOMPLETE_CONTINUE:
						self.autocomplete.append (self._AUTOCOMPLETE_CONTINUE [sym])
					else:
						self.autocompleting = False

			else:
				self.tokens.insert (tokidx, lalr1.Token (self._AUTOCOMPLETE_SUBSTITUTE.get (sym, 'VAR'), '', self.tok.pos, ('', '', '', '')))
				self._mark_error ()

			tokidx += 1

		return True # for convenience

	def _mark_error (self, sym_ins = None, tokinc = 0, at = None):
		self.autocompleting = False

		if self.erridx is None:
			self.erridx = self.tokens [self.tokidx].pos if at is None else at

		if sym_ins is not None:
			return self._insert_symbol (sym_ins, tokinc)

	def _parse_autocomplete_expr_commas (self, rule, pos):
		idx = -pos + (self.stack [-pos].sym == 'LEFT')

		if self.stack [idx].sym != 'CURLYL':
			if self.tokens [self.tokidx - 1] == 'COMMA':
				self._mark_error ()

			if self.stack [idx - 1].sym == 'LEFT':
				return self._insert_symbol ('RIGHT')

			return self._insert_symbol ('PARENR' if self.stack [idx].sym == 'PARENL' else 'BRACKETR')

		# vector or matrix potentially being entered
		if self.stack [idx - 1].sym == 'CURLYL':
			if self.stack [-1].red.is_null_var:
				return self._mark_error (('CURLYR', 'CURLYR'))
			elif not self.stack [-1].red.is_comma:
				return self._insert_symbol (('COMMA', 'CURLYR', 'COMMA', 'CURLYR'), 1)
			elif len (self.stack [-1].red.commas) == 1 or self.tokens [self.tokidx - 1] != 'COMMA':
				return self._insert_symbol (('CURLYR', 'COMMA', 'CURLYR'))
			else:
				return self._mark_error (('CURLYR', 'CURLYR'))

		if self.stack [-3].sym != 'COMMA' or self.stack [-4].sym != 'expr_comma' or self.stack [-5].sym != 'CURLYL':
			if self.stack [-1].red.is_vec:
				return self._insert_symbol (('COMMA', 'CURLYR'), 1)
			elif self.stack [-1].red.is_comma:
				if len (self.stack [-1].red.commas) == 1 or self.tokens [self.tokidx - 1] != 'COMMA':
					return self._insert_symbol ('CURLYR')
				else:
					return self._mark_error ('CURLYR')

		else:
			cols = \
					len (self.stack [-4].red.vec)             if self.stack [-4].red.is_vec else \
					len (self.stack [-4].red.commas [0].vec)  if self.stack [-4].red.is_comma and self.stack [-4].red.commas [0].is_vec else \
					None

			if cols is not None:
				vec             = self.stack [-1].red.commas if self.stack [-1].red.is_comma else (self.stack [-1].red,)
				self.stack [-1] = lalr1.State (self.stack [-1].idx, self.stack [-1].sym, AST (',', vec + (AST.VarNull,) * (cols - len (vec))))

				return self._mark_error (('CURLYR', 'CURLYR')) if len (vec) != cols else self._insert_symbol (('CURLYR', 'CURLYR'))

		return self._insert_symbol ('CURLYR')

	def _parse_autocomplete_expr_int (self):
		s               = self.stack [-1]
		self.stack [-1] = lalr1.State (s.idx, s.sym, AST ('*', (s.red, AST.VarNull)))
		expr_vars       = set ()
		expr_diffs      = set ()

		if self.autocompleting:
			stack = [s [2]]

			while stack:
				ast = stack.pop ()

				if ast.is_var:
					(expr_diffs if ast.is_differential else expr_vars).add (ast.var)
				else:
					stack.extend (filter (lambda a: isinstance (a, tuple), ast))

		expr_vars = expr_vars - {'_', AST.E.var, AST.I.var} - set (AST.Var.LONG2SHORT) - set (var [1:] for var in expr_diffs)

		if len (expr_vars) == 1:
			self.autocomplete.append (f' d{expr_vars.pop ()}')
		else:
			self._mark_error ()

		return True

	def parse_getextrastate (self):
		return (self.autocomplete [:], self.autocompleting, self.erridx)

	def parse_setextrastate (self, state):
		self.autocomplete, self.autocompleting, self.erridx = state

	def parse_error (self): # add tokens to continue parsing for autocomplete if syntax allows
		if isinstance (self.rederr, lalr1.Incomplete):
			self.parse_results.append ((self.rederr.red, self.tok.pos, []))

			return False

		if self.tok != '$end':
			self.parse_results.append ((None, self.tok.pos, []))

			return False

		if self.tokidx and self.tokens [self.tokidx - 1] == 'LEFT':
			for irule, pos in self.strules [self.stidx]:
				if self.rules [irule] [1] [pos] == 'PARENL':
					break
			else:
				raise RuntimeError ('could not find left parenthesis rule')

		else:
			irule, pos = self.strules [self.stidx] [0]

		rule = self.rules [irule]

		if pos == 1 and rule == ('expr_func', ('FUNC', 'expr_func_arg')): # and _FUNC_name (self.stack [-1].sym) in AST.Func.NO_PARMS:
			return self._insert_symbol (('PARENL', 'PARENR'))

		if pos and rule [1] [pos - 1] == 'expr_commas':
			return self._parse_autocomplete_expr_commas (rule, pos)

		assert rule [1] [pos - 1] != 'expr_comma'

		if pos >= len (rule [1]): # end of rule
			if rule [0] == 'expr_int':
				return self._parse_autocomplete_expr_int ()

			return False

		return self._insert_symbol (rule [1] [pos])

	def parse_success (self, red):
		self.parse_results.append ((red, self.erridx, self.autocomplete))

		return True # continue parsing if conflict branches remain to find best resolution

	def parse (self, text):
		if not text.strip ():
			return (AST.VarNull, 0, [])

		self.parse_results  = [] # [(reduction, erridx, autocomplete), ...]
		self.autocomplete   = []
		self.autocompleting = True
		self.erridx         = None

		lalr1.Parser.parse (self, text)

		if not self.parse_results:
			return (None, 0, [])

		rated = sorted ((r is None, -e if e is not None else float ('-inf'), len (a), i, (r, e, a)) \
				for i, (r, e, a) in enumerate (self.parse_results))

		if os.environ.get ('SYMPAD_DEBUG'):
			rated = list (rated)
			print ()
			for res in rated:
				print ('parse:', res [-1])

		return next (iter (rated)) [-1]

class sparser: # for single script
	Parser = Parser

# if __name__ == '__main__':
# 	p = Parser ()
# 	a = p.parse ('1 + {{1,2,3},{3,4}')
# 	print (a)
# Convert between internal AST and sympy expressions and write out LaTeX, simple and python code

# TODO: native sp.Piecewise: \int_0^\infty e^{-st} dt
# TODO: fix nested identical Piecewise returned from SymPy like for Sum (x**n/x, (n, 0, oo)).doit ()
# TODO: sequence(factorial(k), (k,1,oo))

import re
import sympy as sp
sp.numbers = sp.numbers # medication for pylint
sp.boolalg = sp.boolalg


_SYMPY_FLOAT_PRECISION = None

_rec_num_deconstructed = re.compile (r'^(-?)(\d*[^0.e])?(0*)(?:(\.)(0*)(\d*[^0e])?(0*))?(?:([eE])([+-]?\d+))?$') # -101000.000101000e+123 -> (-) (101) (000) (.) (000) (101) (000) (e) (+123)

#...............................................................................................
class AST_Text (AST): # for displaying elements we do not know how to handle, only returned from SymPy processing, not passed in
	op = 'text'

	def _init (self, tex, simple, py):
		self.tex, self.simple, self.py = tex, simple, py

def _ast_is_neg (ast):
	return ast.is_minus or ast.is_neg_num or (ast.is_mul and _ast_is_neg (ast.muls [0]))

def _trail_comma (obj):
	return ',' if len (obj) == 1 else ''

def set_precision (ast): # recurse through ast to set sympy float precision according to largest string of digits found
	global _SYMPY_FLOAT_PRECISION

	prec  = 15
	stack = [ast]

	while stack:
		ast = stack.pop ()

		if not isinstance (ast, AST):
			pass # nop
		elif ast.is_num:
			prec = max (prec, len (ast.num)) # will be a little more than number of digits to compensate for falling precision with some calculations
		else:
			stack.extend (ast [1:])

	_SYMPY_FLOAT_PRECISION = prec if prec > 15 else None

#...............................................................................................
def ast2tex (ast): # abstract syntax tree -> LaTeX text
	return _ast2tex_funcs [ast.op] (ast)

def _ast2tex_curly (ast):
	return f'{ast2tex (ast)}' if ast.is_single_unit else f'{{{ast2tex (ast)}}}'

def _ast2tex_paren (ast):
	return ast2tex (ast) if ast.is_paren else f'\\left({ast2tex (ast)} \\right)'

def _ast2tex_paren_mul_exp (ast, ret_has = False, also = {'+'}):
	if ast.is_mul:
		s, has = _ast2tex_mul (ast, True)
	else:
		s, has = ast2tex (ast), ast.op in also

	s = f'\\left({s} \\right)' if has else s

	return (s, has) if ret_has else s

def _ast2tex_num (ast):
	m, e = ast.mant_and_exp ()

	return m if e is None else f'{m} \\cdot 10^{_ast2tex_curly (AST ("#", e))}'

def _ast2tex_mul (ast, ret_has = False):
	t   = []
	p   = None
	has = False

	for n in ast.muls:
		s = f'{_ast2tex_paren (n) if n.is_add or (p and _ast_is_neg (n)) else ast2tex (n)}'

		if p and (n.op in {'!', '#', 'mat'} or n.is_null_var or p.op in {'lim', 'sum', 'intg', 'mat'} or \
				(n.is_pow and n.base.is_pos_num) or (n.op in {'/', 'diff'} and p.op in {'#', '/', 'diff'})):
			t.append (f' \\cdot {s}')
			has = True

		elif p and (p.is_diff_or_part_solo or p.op in {'sqrt'} or n.is_diff_or_part or p.is_diff_or_part):
			t.append (f'\\ {s}')
		else:
			t.append (f'{"" if not p else " "}{s}')

		p = n

	return (''.join (t), has) if ret_has else ''.join (t)

def _ast2tex_pow (ast):
	b = _ast2tex_curly (ast.base) if ast.base.is_mat else ast2tex (ast.base)
	p = _ast2tex_curly (ast.exp)

	if ast.base.is_trigh_func_noninv and ast.exp.is_single_unit:
		i = len (ast.base.func) + (15 if ast.base.func in {'sech', 'csch'} else 1)

		return f'{b [:i]}^{p}{b [i:]}'

	if ast.base.op in {'@', '(', '|', 'mat'} or ast.base.is_pos_num:
		return f'{b}^{p}'

	return f'\\left({b} \\right)^{p}'

def _ast2tex_log (ast):
	return \
			f'\\ln{_ast2tex_paren (ast.log)}' \
			if ast.base is None else \
			f'\\log_{_ast2tex_curly (ast.base)}{_ast2tex_paren (ast.log)}'

def _ast2tex_func (ast):
	if ast.is_trigh_func:
		n = (f'\\operatorname{{{ast.func [1:]}}}^{{-1}}' \
				if ast.func in {'asech', 'acsch'} else \
				f'\\{ast.func [1:]}^{{-1}}') \
				if ast.func [0] == 'a' else \
				(f'\\operatorname{{{ast.func}}}' if ast.func in {'sech', 'csch'} else f'\\{ast.func}')

		return f'{n}{_ast2tex_paren (ast.arg)}'

	return \
			f'\\{ast.func}{_ast2tex_paren (ast.arg)}' \
			if ast.func in AST.Func.PY_AND_TEX else \
			'\\operatorname{' + ast.func.replace ('_', '\\_') + f'}}{_ast2tex_paren (ast.arg)}'

def _ast2tex_lim (ast):
	s = ast2tex (ast.to) if ast.dir is None else (ast2tex (AST ('^', ast.to, AST.Zero)) [:-1] + ast.dir)

	return f'\\lim_{{{ast2tex (ast.lvar)} \\to {s}}} {_ast2tex_paren_mul_exp (ast.lim)}'

def _ast2tex_sum (ast):
	return f'\\sum_{{{ast2tex (ast.svar)} = {ast2tex (ast.from_)}}}^{_ast2tex_curly (ast.to)} {_ast2tex_paren_mul_exp (ast.sum)}' \

_rec_diff_var_single_start = re.compile (r'^d(?=[^_])')

def _ast2tex_diff (ast):
	ds = set ()
	p  = 0

	for n in ast.dvs:
		if n.is_var:
			p += 1

			if n.var:
				ds.add (n.var)

		else: # n = ('^', ('@', 'diff or part'), ('#', 'int'))
			p += int (n.exp.num)
			ds.add (n.base.var)

	if not ds:
		return f'\\frac{{d}}{{}}{_ast2tex_paren (ast.diff)}'

	if len (ds) == 1 and ds.pop () [0] != '\\': # is not '\\partial'
		return f'\\frac{{d{"" if p == 1 else f"^{p}"}}}{{{"".join (ast2tex (n) for n in ast.dvs)}}}{_ast2tex_paren (ast.diff)}'

	else:
		s = ''.join (_rec_diff_var_single_start.sub (r'\\partial ', ast2tex (n)) for n in ast.dvs)

		return f'\\frac{{\\partial{"" if p == 1 else f"^{p}"}}}{{{s}}}{_ast2tex_paren (ast.diff)}'

def _ast2tex_intg (ast):
	if ast.from_ is None:
		return \
				f'\\int \\ {ast2tex (ast.dv)}' \
				if ast.intg is None else \
				f'\\int {ast2tex (ast.intg)} \\ {ast2tex (ast.dv)}'
	else:
		return \
				f'\\int_{_ast2tex_curly (ast.from_)}^{_ast2tex_curly (ast.to)} \\ {ast2tex (ast.dv)}' \
				if ast.intg is None else \
				f'\\int_{_ast2tex_curly (ast.from_)}^{_ast2tex_curly (ast.to)} {ast2tex (ast.intg)} \\ {ast2tex (ast.dv)}'

_ast2tex_funcs = {
	'=': lambda ast: f'{ast2tex (ast.lhs)} {AST.Eq.SHORT2LONG.get (ast.rel, ast.rel)} {ast2tex (ast.rhs)}',
	'#': _ast2tex_num,
	'@': lambda ast: str (ast.var) if ast.var else '{}',
	'.': lambda ast: f'{ast2tex (ast.obj)}.\\text{{{ast.attr}}}{"" if ast.arg is None else _ast2tex_paren (ast.arg)}',
	'"': lambda ast: f'\\text{{{repr (ast.str_)}}}',
	',': lambda ast: f'{", ".join (ast2tex (parm) for parm in ast.commas)}{_trail_comma (ast.commas)}',
	'(': lambda ast: f'\\left({ast2tex (ast.paren)} \\right)',
	'[': lambda ast: f'\\left[{", ".join (ast2tex (b) for b in ast.bracks)} \\right]',
	'|': lambda ast: f'\\left|{ast2tex (ast.abs)} \\right|',
	'-': lambda ast: f'-{_ast2tex_paren (ast.minus)}' if ast.minus.is_add else f'-{ast2tex (ast.minus)}',
	'!': lambda ast: f'{_ast2tex_paren (ast.fact)}!' if (ast.fact.op not in {'#', '@', '(', '|', '!', '^', 'vec', 'mat'} or ast.fact.is_neg_num) else f'{ast2tex (ast.fact)}!',
	'+': lambda ast: ' + '.join (ast2tex (n) for n in ast.adds).replace (' + -', ' - '),
	'*': _ast2tex_mul,
	'/': lambda ast: f'\\frac{{{ast2tex (ast.numer)}}}{{{ast2tex (ast.denom)}}}',
	'^': _ast2tex_pow,
	'log': _ast2tex_log,
	'sqrt': lambda ast: f'\\sqrt{{{ast2tex (ast.rad.strip_paren (1))}}}' if ast.idx is None else f'\\sqrt[{ast2tex (ast.idx)}]{{{ast2tex (ast.rad.strip_paren (1))}}}',
	'func': _ast2tex_func,
	'lim': _ast2tex_lim,
	'sum': _ast2tex_sum,
	'diff': _ast2tex_diff,
	'intg': _ast2tex_intg,
	'vec': lambda ast: '\\begin{bmatrix} ' + r' \\ '.join (ast2tex (e) for e in ast.vec) + ' \\end{bmatrix}',
	'mat': lambda ast: '\\begin{bmatrix} ' + r' \\ '.join (' & '.join (ast2tex (e) for e in row) for row in ast.mat) + f'{" " if ast.mat else ""}\\end{{bmatrix}}',
	'text': lambda ast: ast.tex,
}

#...............................................................................................
def ast2nat (ast): # abstract syntax tree -> simple text
	return _ast2nat_funcs [ast.op] (ast)

def _ast2nat_curly (ast):
	return f'{ast2nat (ast)}' if ast.is_single_unit else f'{{{ast2nat (ast)}}}'

def _ast2nat_paren (ast):
	return ast2nat (ast) if ast.is_paren else f'({ast2nat (ast)})'

def _ast2nat_paren_mul_exp (ast, ret_has = False, also = {'+'}):
	if ast.is_mul:
		s, has = _ast2nat_mul (ast, True)
	else:
		s, has = ast2nat (ast), ast.op in also

	s = f'({s})' if has else s

	return (s, has) if ret_has else s

def _ast2nat_mul (ast, ret_has = False):
	t   = []
	p   = None
	has = False

	for n in ast.muls:
		s = f'{_ast2nat_paren (n) if n.is_add or (p and _ast_is_neg (n)) else ast2nat (n)}'

		if p and (n.op in {'!', '#', 'lim', 'sum', 'intg'} or n.is_null_var or \
				(n.is_pow and n.base.is_pos_num) or n.op in {'/', 'diff'} or p.op in {'/', 'diff'}):
			t.append (f' * {ast2nat (n)}')
			has = True

		elif p and (p.is_diff_or_part_solo or \
				(n.op not in {'#', '@', '(', '|', '^'} or p.op not in {'#', '@', '(', '|', '^'}) or \
				n.has_short_var or p.has_short_var or n.is_diff_or_part or p.is_diff_or_part):
			t.append (f' {s}')

		else:
			t.append (s)

		p = n

	return (''.join (t), has) if ret_has else ''.join (t)

def _ast2nat_div (ast):
	n, ns = _ast2nat_paren_mul_exp (ast.numer, True, {'+', '/', 'lim', 'sum', 'diff'})
	d, ds = _ast2nat_paren_mul_exp (ast.denom, True, {'+', '/', 'lim', 'sum', 'diff'})
	s     = ns or ds or ast.numer.strip_minus ().op not in {'#', '@', '*'} or ast.denom.strip_minus ().op not in {'#', '@', '*'}

	return f'{n}{" / " if s else "/"}{d}'

def _ast2nat_pow (ast):
	b = ast2nat (ast.base)
	p = f'{_ast2nat_paren (ast.exp)}' if ast.exp.strip_minus ().op in {'+', '*', '/', 'lim', 'sum', 'diff', 'intg'} else ast2nat (ast.exp)

	if ast.base.is_trigh_func_noninv and ast.exp.is_single_unit:
		i = len (ast.base.func)

		return f'{b [:i]}^{p}{b [i:]}'

	if ast.base.op in {'@', '(', '|', 'mat'} or ast.base.is_pos_num:
		return f'{b}**{p}'

	return f'({b})**{p}'

def _ast2nat_log (ast):
	return \
			f'ln{_ast2nat_paren (ast.log)}' \
			if ast.base is None else \
			f'log_{_ast2nat_curly (ast.base)}{_ast2nat_paren (ast.log)}'

def _ast2nat_func (ast):
	if ast.is_trigh_func:
		return f'{ast.func}{_ast2nat_paren (ast.arg)}'

	return \
			f'{ast.func}{_ast2nat_paren (ast.arg)}' \
			if ast.func in AST.Func.PY_ALL else \
			f'${ast.func}{_ast2nat_paren (ast.arg)}'

def _ast2nat_lim (ast):
	s = ast2nat (ast.to) if ast.dir is None else ast2nat (AST ('^', ast [3], AST.Zero)) [:-1] + ast [4]

	return f'\\lim_{{{ast2nat (ast.lvar)} \\to {s}}} {_ast2nat_paren_mul_exp (ast.lim)}'

def _ast2nat_sum (ast):
	return f'\\sum_{{{ast2nat (ast.svar)}={ast2nat (ast.from_)}}}^{_ast2nat_curly (ast.to)} {_ast2nat_paren_mul_exp (ast.sum)}' \

_ast2nat_diff_single_rec = re.compile ('^d')

def _ast2nat_diff (ast):
	p = 0

	for n in ast.dvs:
		if n.is_var:
			d  = n.diff_or_part_start_text ()
			p += 1
		else: # n = ('^', ('@', 'differential'), ('#', 'int'))
			d  = n.base.diff_or_part_start_text ()
			p += int (n.exp.num)

	return f'{d.strip ()}{"" if p == 1 else f"^{p}"}/{"".join (ast2nat (n) for n in ast.dvs)}{_ast2nat_paren (ast.diff)}'

def _ast2nat_intg (ast):
	if ast.from_ is None:
		return \
				f'\\int {ast2nat (ast.dv)}' \
				if ast.intg is None else \
				f'\\int {ast2nat (ast.intg)} {ast2nat (ast.dv)}'
	else:
		return \
				f'\\int_{_ast2nat_curly (ast.from_)}^{_ast2nat_curly (ast.to)} {ast2nat (ast.dv)}' \
				if ast.intg is None else \
				f'\\int_{_ast2nat_curly (ast.from_)}^{_ast2nat_curly (ast.to)} {ast2nat (ast.intg)} {ast2nat (ast.dv)}'

_ast2nat_funcs = {
	'=': lambda ast: f'{ast2nat (ast.lhs)} {ast.rel} {ast2nat (ast.rhs)}',
	'#': lambda ast: ast.num,
	'@': lambda ast: ast.as_short_var_text (),
	'.': lambda ast: f'{ast2nat (ast.obj)}.{ast.attr}' if ast.arg is None else f'{ast2nat (ast.obj)}.{ast.attr}{_ast2nat_paren (ast.arg)}',
	'"': lambda ast: repr (ast.str_),
	',': lambda ast: f'{", ".join (ast2nat (parm) for parm in ast.commas)}{_trail_comma (ast.commas)}',
	'(': lambda ast: f'({ast2nat (ast.paren)})',
	'[': lambda ast: f'[{", ".join (ast2nat (b) for b in ast.bracks)}]',
	'|': lambda ast: f'|{ast2nat (ast.abs)}|',
	'-': lambda ast: f'-{_ast2nat_paren (ast.minus)}' if ast.minus.is_add else f'-{ast2nat (ast.minus)}',
	'!': lambda ast: f'{_ast2nat_paren (ast.fact)}!' if (ast.fact.op not in {'#', '@', '(', '|', '!', '^', 'vec', 'mat'} or ast.fact.is_neg_num) else f'{ast2nat (ast.fact)}!',
	'+': lambda ast: ' + '.join (ast2nat (n) for n in ast.adds).replace (' + -', ' - '),
	'*': _ast2nat_mul,
	'/': _ast2nat_div,
	'^': _ast2nat_pow,
	'log': _ast2nat_log,
	'sqrt': lambda ast: f'\\sqrt{{{ast2nat (ast.rad.strip_paren (1))}}}' if ast.idx is None else f'\\sqrt[{ast2nat (ast.idx)}]{{{ast2nat (ast.rad.strip_paren (1))}}}',
	'func': _ast2nat_func,
	'lim': _ast2nat_lim,
	'sum': _ast2nat_sum,
	'diff': _ast2nat_diff,
	'intg': _ast2nat_intg,
	'vec': lambda ast: f'{{{",".join (ast2nat (e) for e in ast.vec)}{_trail_comma (ast.vec)}}}',
	'mat': lambda ast: ('{' + ','.join (f'{{{",".join (ast2nat (e) for e in row)}{_trail_comma (row)}}}' for row in ast.mat) + f'{_trail_comma (ast.mat)}}}') if ast.mat else 'Matrix([])',
	'text': lambda ast: ast.simple,
}

#...............................................................................................
def ast2py (ast): # abstract syntax tree -> Python code text
	return _ast2py_funcs [ast.op] (ast)

def _ast2py_curly (ast):
	return \
			_ast2py_paren (ast) \
			if ast.strip_minus ().op in {'+', '*', '/'} or (ast.is_log and ast.base is not None) else \
			ast2py (ast)

def _ast2py_paren (ast):
	return ast2py (ast) if ast.is_paren else f'({ast2py (ast)})'

def _ast2py_div (ast):
	n = _ast2py_curly (ast.numer)
	d = _ast2py_curly (ast.denom)

	return f'{n}{" / " if ast.numer.strip_minus ().op not in {"#", "@"} or ast.denom.strip_minus ().op not in {"#", "@"} else "/"}{d}'

def _ast2py_pow (ast):
	b = _ast2py_paren (ast.base) if _ast_is_neg (ast.base) else _ast2py_curly (ast.base)
	e = _ast2py_curly (ast.exp)

	return f'{b}**{e}'

def _ast2py_log (ast):
	return \
			f'log{_ast2py_paren (ast.log)}' \
			if ast.base is None else \
			f'log{_ast2py_paren (ast.log)} / log{_ast2py_paren (ast.base)}' \

def _ast2py_lim (ast):
	return \
		f'''Limit({ast2py (ast.lim)}, {ast2py (ast.lvar)}, {ast2py (ast.to)}''' \
		f'''{", dir='+-'" if ast.dir is None else ", dir='-'" if ast.dir == '-' else ""})'''

def _ast2py_diff (ast):
	args = sum ((
			(ast2py (n.as_var ()),) \
			if n.is_var else \
			(ast2py (n.base.as_var ()), str (n.exp.num)) \
			for n in ast.dvs \
			), ())

	return f'Derivative({ast2py (ast.diff)}, {", ".join (args)})'

def _ast2py_intg (ast):
	if ast.from_ is None:
		return \
				f'Integral(1, {ast2py (ast.dv.as_var ())})' \
				if ast.intg is None else \
				f'Integral({ast2py (ast.intg)}, {ast2py (ast.dv.as_var ())})'
	else:
		return \
				f'Integral(1, ({ast2py (ast.dv.as_var ())}, {ast2py (ast.from_)}, {ast2py (ast.to)}))' \
				if ast.intg is None else \
				f'Integral({ast2py (ast.intg)}, ({ast2py (ast.dv.as_var ())}, {ast2py (ast.from_)}, {ast2py (ast.to)}))'

_rec_ast2py_varname_sanitize = re.compile (r'\{|\}')

_ast2py_funcs = {
	'=': lambda ast: f'{ast2py (ast.lhs)} {ast.rel} {ast2py (ast.rhs)}',
	'#': lambda ast: ast.num,
	'@': lambda ast: _rec_ast2py_varname_sanitize.sub ('_', ast.as_shortpy_var_text ()).replace ('\\', '_').replace ("'", '_prime'),
	'.': lambda ast: f'{ast2py (ast.obj)}.{ast.attr}' if ast.arg is None else f'{ast2py (ast.obj)}.{ast.attr}{_ast2py_paren (ast.arg)}',
	'"': lambda ast: repr (ast.str_),
	',': lambda ast: f'{", ".join (ast2py (parm) for parm in ast.commas)}{_trail_comma (ast.commas)}',
	'(': lambda ast: f'({ast2py (ast.paren)})',
	'[': lambda ast: f'[{", ".join (ast2py (b) for b in ast.bracks)}]',
	'|': lambda ast: f'abs({ast2py (ast.abs)})',
	'-': lambda ast: f'-{_ast2py_paren (ast.minus)}' if ast.minus.is_add else f'-{ast2py (ast.minus)}',
	'!': lambda ast: f'factorial({ast2py (ast.fact)})',
	'+': lambda ast: ' + '.join (ast2py (n) for n in ast.adds).replace (' + -', ' - '),
	'*': lambda ast: '*'.join (_ast2py_paren (n) if n.is_add else ast2py (n) for n in ast.muls),
	'/': _ast2py_div,
	'^': _ast2py_pow,
	'log': _ast2py_log,
	'sqrt': lambda ast: f'sqrt{_ast2py_paren (ast.rad.strip_paren (1))}' if ast.idx is None else ast2py (AST ('^', ast.rad.strip_paren (1), ('/', AST.One, ast.idx))),
	'func': lambda ast: f'{ast.func}{_ast2py_paren (ast.arg)}',
	'lim': _ast2py_lim,
	'sum': lambda ast: f'Sum({ast2py (ast.sum)}, ({ast2py (ast.svar)}, {ast2py (ast.from_)}, {ast2py (ast.to)}))',
	'diff': _ast2py_diff,
	'intg': _ast2py_intg,
	'vec': lambda ast: 'Matrix([' + ','.join (f'[{ast2py (e)}]' for e in ast.vec) + '])',
	'mat': lambda ast: 'Matrix([' + ','.join (f'[{",".join (ast2py (e) for e in row)}]' for row in ast.mat) + '])',
	'text': lambda ast: ast.py,
}

#...............................................................................................
def ast2spt (ast, doit = False): # abstract syntax tree -> sympy tree (expression)
	spt = _ast2spt_funcs [ast.op] (ast)

	if doit and callable (getattr (spt, 'doit', None)): # and spt.__class__ != sp.Piecewise
		try:
			spt = sp.piecewise_fold (spt.doit ()) # = spt.doit ()
		except TypeError:
			pass

	return spt

def _ast2spt_call_func (func, arg):
	kw   = {}
	args = []
	arg  = arg.strip_paren ()

	for arg in (arg.commas if arg.is_comma else (arg,)):
		if arg.is_ass and arg.rhs.is_str:
			name = arg.lhs.as_identifier ()

			if name is not None:
				kw [name] = ast2spt (arg.rhs)
				continue

		args.append (ast2spt (arg))

	return func (*args, **kw) if len (args) != 1 else func (args [0], **kw)

def _ast2spt_attr (ast):
	obj = ast2spt (ast.obj)
	mbr = getattr (obj, ast.attr)

	return mbr if ast.arg is None else _ast2spt_call_func (mbr, ast.arg)

# Potentially bad __builtins__: eval, exec, globals, locals, vars, hasattr, getattr, setattr, delattr, exit, help, input, license, open, quit, __import__
_builtins_dict               = __builtins__.__dict__ if __name__ == '__main__' else __builtins__
_ast2spt_func_builtins_names = ['abs', 'all', 'any', 'ascii', 'bin', 'callable', 'chr', 'compile', 'dir', 'divmod', 'format', 'hash', 'hex', 'id',
		'isinstance', 'issubclass', 'iter', 'len', 'max', 'min', 'next', 'oct', 'ord', 'pow', 'print', 'repr', 'round', 'sorted', 'sum', 'bool', 'memoryview',
		'bytearray', 'bytes', 'classmethod', 'complex', 'dict', 'enumerate', 'filter', 'float', 'frozenset', 'property', 'int', 'list', 'map', 'object', 'range',
		'reversed', 'set', 'slice', 'staticmethod', 'str', 'super', 'tuple', 'type', 'zip']

_ast2spt_func_builtins       = dict (no for no in filter (lambda no: no [1], ((n, _builtins_dict.get (n)) for n in _ast2spt_func_builtins_names)))

def _ast2spt_func (ast):
	if ast.func == '@': # special reference meta-function
		return ast2spt (ast.arg)

	func = getattr (sp, ast.func, _ast2spt_func_builtins.get (ast.func))

	if func is None:
		raise NameError (f'name {ast.func!r} is not defined')

	return _ast2spt_call_func (func, ast.arg)

def _ast2spt_diff (ast):
	args = sum ((
			(ast2spt (n.as_var ()),) \
			if n.is_var else \
			(ast2spt (n.base.as_var ()), sp.Integer (n.exp.num)) \
			for n in ast.dvs \
			), ())

	return sp.Derivative (ast2spt (ast [1]), *args)

def _ast2spt_intg (ast):
	if ast.from_ is None:
		return \
				sp.Integral (1, ast2spt (ast.dv.as_var ())) \
				if ast.intg is None else \
				sp.Integral (ast2spt (ast.intg), ast2spt (ast.dv.as_var ()))
	else:
		return \
				sp.Integral (1, (ast2spt (ast.dv.as_var ()), ast2spt (ast.from_), ast2spt (ast.to))) \
				if ast.intg is None else \
				sp.Integral (ast2spt (ast [1]), (ast2spt (ast.dv.as_var ()), ast2spt (ast.from_), ast2spt (ast.to)))

_ast2spt_eq = {
	'=':  sp.Eq,
	'==': sp.Eq,
	'!=': sp.Ne,
	'<':  sp.Lt,
	'<=': sp.Le,
	'>':  sp.Gt,
	'>=': sp.Ge,
}

_ast2spt_consts = { # 'e' and 'i' dynamically set on use from AST.E or I
	'\\pi'         : sp.pi,
	'\\infty'      : sp.oo,
	'\\text{None}' : None,
	'\\text{True}' : sp.boolalg.true,
	'\\text{False}': sp.boolalg.false,
	'\\text{nan}'  : sp.nan,
}

_ast2spt_funcs = {
	'=': lambda ast: _ast2spt_eq [ast.rel] (ast2spt (ast.lhs), ast2spt (ast.rhs)),
	'#': lambda ast: sp.Integer (ast [1]) if ast.is_int_text (ast.num) else sp.Float (ast.num, _SYMPY_FLOAT_PRECISION),
	'@': lambda ast: {**_ast2spt_consts, AST.E.var: sp.E, AST.I.var: sp.I}.get (ast.var, sp.Symbol (ast.var)),
	'.': _ast2spt_attr,
	'"': lambda ast: ast.str_,
	',': lambda ast: tuple (ast2spt (p) for p in ast.commas),
	'(': lambda ast: ast2spt (ast.paren),
	'[': lambda ast: [ast2spt (b) for b in ast.bracks],
	'|': lambda ast: sp.Abs (ast2spt (ast.abs)),
	'-': lambda ast: -ast2spt (ast.minus),
	'!': lambda ast: sp.factorial (ast2spt (ast.fact)),
	'+': lambda ast: sp.Add (*(ast2spt (n) for n in ast.adds)),
	'*': lambda ast: sp.Mul (*(ast2spt (n) for n in ast.muls)),
	'/': lambda ast: sp.Mul (ast2spt (ast.numer), sp.Pow (ast2spt (ast.denom), -1)),
	'^': lambda ast: sp.Pow (ast2spt (ast.base), ast2spt (ast.exp)),
	'log': lambda ast: sp.log (ast2spt (ast.log)) if ast.base is None else sp.log (ast2spt (ast.log), ast2spt (ast.base)),
	'sqrt': lambda ast: sp.Pow (ast2spt (ast.rad), sp.Pow (2, -1)) if ast.idx is None else sp.Pow (ast2spt (ast.rad), sp.Pow (ast2spt (ast.idx), -1)),
	'func': _ast2spt_func,
	'lim': lambda ast: (sp.Limit if ast.dir else sp.limit) (ast2spt (ast.lim), ast2spt (ast.lvar), ast2spt (ast.to), dir = ast.dir or '+-'),
	'sum': lambda ast: sp.Sum (ast2spt (ast.sum), (ast2spt (ast.svar), ast2spt (ast.from_), ast2spt (ast.to))),
	'diff': _ast2spt_diff,
	'intg': _ast2spt_intg,
	'vec': lambda ast: sp.Matrix ([[ast2spt (e)] for e in ast.vec]),
	'mat': lambda ast: sp.Matrix ([[ast2spt (e) for e in row] for row in ast.mat]),
}

#...............................................................................................
def spt2ast (spt): # sympy tree (expression) -> abstract syntax tree
	for cls in spt.__class__.__mro__:
		func = _spt2ast_funcs.get (cls)

		if func:
			return func (spt)

		if cls is sp.Function:
			if len (spt.args) != 1:
				break

			return AST ('func', spt.__class__.__name__, spt2ast (spt.args [0]))

	tex = sp.latex (spt)

	if tex [0] == '<' and tex [-1] == '>': # for Python repr style of objects <class something>
		tex = '\\text{' + tex.replace ("<", "&lt;").replace (">", "&gt;").replace ("\n", "") + '}'

	return AST_Text (tex, 'nan', str (spt))

def _spt2ast_num (spt):
	m = _rec_num_deconstructed.match (str (spt))
	g = [g or '' for g in m.groups ()]

	if g [5]:
		return AST ('#', ''.join (g [:6] + g [7:]))

	e = len (g [2]) + (int (g [8]) if g [8] else 0)

	return AST ('#', \
			f'{g [0]}{g [1]}e+{e}'     if e >= 16 else \
			f'{g [0]}{g [1]}{"0" * e}' if e >= 0 else \
			f'{g [0]}{g [1]}e{e}')

def _spt2ast_add (spt):
	args = spt._sorted_args

	for arg in args:
		if isinstance (arg, sp.Order):
			break
	else:
		args = args [::-1]

	return AST ('+', tuple (spt2ast (arg) for arg in args))

def _spt2ast_mul (spt):
	if spt.args [0] == -1:
		return AST ('-', spt2ast (sp.Mul (*spt.args [1:])))

	if spt.args [0].is_negative and isinstance (spt, sp.Number):
		return AST ('-', spt2ast (sp.Mul (-spt.args [0], *spt.args [1:])))

	numer = []
	denom = []

	for arg in spt.args:
		if isinstance (arg, sp.Pow) and arg.args [1].is_negative:
			denom.append (spt2ast (sp.Pow (arg.args [0], -arg.args [1])))
		else:
			numer.append (spt2ast (arg))

	if not denom:
		return AST ('*', tuple (numer)) if len (numer) > 1 else numer [0]

	if not numer:
		return AST ('/', AST.One, AST ('*', tuple (denom)) if len (denom) > 1 else denom [0])

	return AST ('/', AST ('*', tuple (numer)) if len (numer) > 1 else numer [0], \
			AST ('*', tuple (denom)) if len (denom) > 1 else denom [0])

def _spt2ast_pow (spt):
	if spt.args [1].is_negative:
		return AST ('/', AST.One, spt2ast (sp.Pow (spt.args [0], -spt.args [1])))

	if spt.args [1] == 0.5:
		return AST ('sqrt', spt2ast (spt.args [0]))

	return AST ('^', spt2ast (spt.args [0]), spt2ast (spt.args [1]))

def _spt2ast_func (spt):
	return AST ('func', spt.__class__.__name__, spt2ast (spt.args [0]))

def _spt2ast_integral (spt):
	return \
			AST ('intg', spt2ast (spt.args [0]), AST ('@', f'd{spt2ast (spt.args [1] [0]) [1]}'), spt2ast (spt.args [1] [1]), spt2ast (spt.args [1] [2])) \
			if len (spt.args [1]) == 3 else \
			AST ('intg', spt2ast (spt.args [0]), AST ('@', f'd{spt2ast (spt.args [1] [0]) [1]}'))

_spt2ast_funcs = {
	None.__class__: lambda spt: AST.None_,
	True.__class__: lambda spt: AST.True_,
	False.__class__: lambda spt: AST.False_,
	str: lambda spt: AST ('"', spt),
	tuple: lambda spt: AST ('(', (',', tuple (spt2ast (e) for e in spt))),
	list: lambda spt: AST ('[', tuple (spt2ast (e) for e in spt)),
	sp.Tuple: lambda spt: spt2ast (spt.args),

	sp.Integer: _spt2ast_num,
	sp.Float: _spt2ast_num,
	sp.Rational: lambda spt: AST ('/', ('#', str (spt.p)), ('#', str (spt.q))) if spt.p >= 0 else AST ('-', ('/', ('#', str (-spt.p)), ('#', str (spt.q)))),
	sp.numbers.ImaginaryUnit: lambda ast: AST.I,
	sp.numbers.Pi: lambda spt: AST.Pi,
	sp.numbers.Exp1: lambda spt: AST.E,
	sp.numbers.Infinity: lambda spt: AST.Infty,
	sp.numbers.NegativeInfinity: lambda spt: AST ('-', AST.Infty),
	sp.numbers.ComplexInfinity: lambda spt: AST.Infty, # not exactly but whatever
	sp.numbers.NaN: lambda spt: AST.NaN,
	sp.Symbol: lambda spt: AST ('@', spt.name),

	sp.boolalg.BooleanTrue: lambda spt: AST.True_,
	sp.boolalg.BooleanFalse: lambda spt: AST.False_,
	sp.Eq: lambda spt: AST ('=', '=', spt2ast (spt.args [0]), spt2ast (spt.args [1])),
	sp.Ne: lambda spt: AST ('=', '!=', spt2ast (spt.args [0]), spt2ast (spt.args [1])),
	sp.Lt: lambda spt: AST ('=', '<', spt2ast (spt.args [0]), spt2ast (spt.args [1])),
	sp.Le: lambda spt: AST ('=', '<=', spt2ast (spt.args [0]), spt2ast (spt.args [1])),
	sp.Gt: lambda spt: AST ('=', '>', spt2ast (spt.args [0]), spt2ast (spt.args [1])),
	sp.Ge: lambda spt: AST ('=', '>=', spt2ast (spt.args [0]), spt2ast (spt.args [1])),

	sp.Add: _spt2ast_add,
	sp.Mul: _spt2ast_mul,
	sp.Pow: _spt2ast_pow,
	sp.MatPow: lambda spt: spt2ast (spt.args [0] ** spt.args [1]), # for some reason MatPow won't doit () for [[0,1],[1,0]]**x

	sp.Abs: lambda spt: AST ('|', spt2ast (spt.args [0])),
	sp.arg: lambda spt: AST ('func', 'arg', spt2ast (spt.args [0])),
	sp.exp: lambda spt: AST ('^', AST.E, spt2ast (spt.args [0])),
	sp.factorial: lambda spt: AST ('!', spt2ast (spt.args [0])),
	sp.log: lambda spt: AST ('log', spt2ast (spt.args [0])) if len (spt.args) == 1 else AST ('log', spt2ast (spt.args [0]), spt2ast (spt.args [1])),
	sp.functions.elementary.trigonometric.TrigonometricFunction: _spt2ast_func,
	sp.functions.elementary.hyperbolic.HyperbolicFunction: _spt2ast_func,
	sp.functions.elementary.trigonometric.InverseTrigonometricFunction: _spt2ast_func,
	sp.functions.elementary.hyperbolic.InverseHyperbolicFunction: _spt2ast_func,
	sp.Order: lambda spt: AST ('func', 'O', spt2ast (spt.args [0]) if spt.args [1] [1] == 0 else spt2ast (spt.args)),

	sp.Sum: lambda spt: AST ('sum', spt2ast (spt.args [0]), spt2ast (spt.args [1] [0]), spt2ast (spt.args [1] [1]), spt2ast (spt.args [1] [2])),
	sp.Integral: _spt2ast_integral,

	sp.matrices.MatrixBase: lambda spt: AST ('mat', tuple (tuple (spt2ast (e) for e in spt [row, :]) \
			for row in range (spt.rows))) if not (spt.rows == spt.cols == 1) else spt2ast (spt [0]),
}

#...............................................................................................
class sym: # for single script
	AST_Text      = AST_Text
	set_precision = set_precision
	ast2tex       = ast2tex
	ast2nat    = ast2nat
	ast2py        = ast2py
	ast2spt       = ast2spt
	spt2ast       = spt2ast
#!/usr/bin/env python
# python 3.6+

# TODO: Exception prevents restart on file date change?

import getopt
import json
import os
import re
import subprocess
import sys
import time
import threading
import traceback
import webbrowser

from urllib.parse import parse_qs
from socketserver import ThreadingMixIn
from http.server import HTTPServer, SimpleHTTPRequestHandler


_SYMPAD_FIRST_RUN         = os.environ.get ('SYMPAD_FIRST_RUN')
_SYMPAD_CHILD             = os.environ.get ('SYMPAD_CHILD')

if _SYMPAD_CHILD: # sympy slow to import if not precompiled so don't do it for watcher process as is unnecessary there
	import sympy as sp

	_var_last = AST ('@', '_')
	_vars     = {_var_last: AST.Zero} # This is individual session STATE! Threading can corrupt this! It is GLOBAL to survive multiple Handlers.
	_parser   = sparser.Parser ()

_DEFAULT_ADDRESS = ('localhost', 8000)

_STATIC_FILES    = {'/style.css': 'css', '/script.js': 'javascript', '/index.html': 'html', '/help.html': 'html'}

_HELP = f"""
usage: {os.path.basename (sys.argv [0])} [--help] [--debug] [--nobrowser] [--sympyEI] [host:port]
"""

#...............................................................................................
# class ThreadingHTTPServer (ThreadingMixIn, HTTPServer):
# 	pass

def _ast_remap (ast, map_):
	return \
			ast                                        if not isinstance (ast, AST) or (ast.is_func and ast.func == '@') else \
			_ast_remap (map_ [ast], map_)              if ast in map_ else \
			AST (*(_ast_remap (a, map_) for a in ast))

def _ast_prepare_ass (ast): # check and prepare for simple or tuple assignment
	vars = None

	if ast.is_ass:
		if ast.lhs.is_var: # simple assignment?
			ast, vars = ast.rhs, [ast.lhs]

	elif ast.is_comma: # tuple assignment? ('x, y = y, x' comes from parser as ('x', 'y = y', 'x')) so remap
		lhss = []
		itr  = iter (ast.commas)

		for c in itr:
			if c.is_var:
				lhss.append (c)
			elif not c.is_ass or not c.lhs.is_var:
				break

			else:
				t    = (c.rhs,) + tuple (itr)
				ast  = t [0] if len (t) == 1 else AST (',', t)
				vars = lhss + [c.lhs]

	return _ast_remap (ast, _vars), vars

def _ast_execute_ass (ast, vars): # execute assignment if it was detected
	global _vars

	asts = None

	if not vars: # no assignment
		_vars [_var_last] = ast

	else:
		if len (vars) == 1: # simple assignment
			new_vars = {**_vars, vars [0]: ast}

		else: # tuple assignment
			ast  = ast.strip_paren ()
			asts = ast.commas if ast.is_comma else tuple (sym.spt2ast (a) for a in sym.ast2spt (ast))

			if len (vars) < len (asts):
				raise ValueError (f'too many values to unpack (expected {len (vars)})')
			elif len (vars) > len (asts):
				raise ValueError (f'not enough values to unpack (expected {len (vars)}, got {len (asts)})')
			else:
				new_vars = {**_vars, **dict ((vars [i], asts [i]) for i in range (len (vars)))}

			asts = [AST ('=', '=', vars [i], asts [i]) for i in range (len (vars))]

		try: # check for circular references
			_ast_remap (AST (',', tuple (vars)), new_vars)
		except RecursionError:
			raise RecursionError ("I'm sorry, Dave. I'm afraid I can't do that. (circular reference detected)") from None

		_vars = new_vars

	return asts or [ast]

def _admin_vars (ast):
	if len (_vars) == 1:
		return 'No variables defined.'
	else:
		return [AST ('=', '=', v, e) for v, e in filter (lambda ve: ve [0] != _var_last, sorted (_vars.items ()))]

def _admin_del (ast):
	ast = ast.arg.strip_paren ()

	try:
		del _vars [ast]
	except KeyError:
		raise NameError (f'Variable {sym.ast2nat (ast)!r} is not defined, it can only be attributable to human error.')

	return f'Variable {sym.ast2nat (ast)!r} deleted.'

def _admin_delall (ast):
	global _vars

	_vars = {_var_last: _vars [_var_last]}

	return 'All variables deleted.'

def _admin_sympyEI (ast):
	arg = ast.arg.strip_paren ()
	arg = \
		bool (sym.ast2spt (arg))             if not arg.is_comma else \
		True                                 if not len (arg.commas) else \
		bool (sym.ast2spt (arg.commas [0]))

	sast.sympyEI (arg)

	return f'Constant representation set to {AST.E.var!r} and {AST.I.var!r}.'

#...............................................................................................
class Handler (SimpleHTTPRequestHandler):
	def do_GET (self):
		if self.path == '/':
			self.path = '/index.html'

		if self.path not in _STATIC_FILES:
			self.send_error (404, f'Invalid path {self.path!r}')

		elif not _RUNNING_AS_SINGLE_SCRIPT:
			return SimpleHTTPRequestHandler.do_GET (self)

		else:
			self.send_response (200)
			self.send_header ('Content-type', f'text/{_STATIC_FILES [self.path]}')
			self.end_headers ()
			self.wfile.write (_FILES [self.path [1:]])

	def do_POST (self):
		request = parse_qs (self.rfile.read (int (self.headers ['Content-Length'])).decode ('utf8'), keep_blank_values = True)

		for key, val in list (request.items ()):
			if len (val) == 1:
				request [key] = val [0]

		if request ['mode'] == 'validate':
			response = self.validate (request)
		else: # request ['mode'] == 'evaluate':
			response = self.evaluate (request)

		response ['mode'] = request ['mode']
		response ['idx']  = request ['idx']
		response ['text'] = request ['text']

		self.send_response (200)
		self.send_header ("Content-type", "application/json")
		self.end_headers ()
		self.wfile.write (json.dumps (response).encode ('utf8'))

	def validate (self, request):
		ast, erridx, autocomplete = _parser.parse (request ['text'])
		tex = simple = py         = None

		if ast is not None:
			ast    = _ast_remap (ast, {_var_last: _vars [_var_last]}) # just remap last evaluated _
			tex    = sym.ast2tex (ast)
			simple = sym.ast2nat (ast)
			py     = sym.ast2py (ast)

			if os.environ.get ('SYMPAD_DEBUG'):
				print ()
				print ('ast:   ', ast)
				print ('tex:   ', tex)
				print ('simple:', simple)
				print ('py:    ', py)
				print ()

		return {
			'tex'         : tex,
			'simple'      : simple,
			'py'          : py,
			'erridx'      : erridx,
			'autocomplete': autocomplete,
		}

	def evaluate (self, request):
		try:
			ast, _, _ = _parser.parse (request ['text'])

			if ast.is_func and ast.func in {'vars', 'del', 'delall', 'sympyEI'}: # special admin function?
				asts = globals () [f'_admin_{ast.func}'] (ast)

				if isinstance (asts, str):
					return {'msg': asts}

			else: # not admin function, normal evaluation
				ast, vars = _ast_prepare_ass (ast)

				sym.set_precision (ast)

				spt = sym.ast2spt (ast, doit = True)
				ast = sym.spt2ast (spt)

				if os.environ.get ('SYMPAD_DEBUG'):
					print ()
					print ('spt:        ', repr (spt))
					print ('spt type:   ', type (spt))
					print ('sympy latex:', sp.latex (spt))
					print ()

				asts = _ast_execute_ass (ast, vars)

			return {'math': [{
				'tex'   : sym.ast2tex (ast),
				'simple': sym.ast2nat (ast),
				'py'    : sym.ast2py (ast),
			} for ast in asts]}

		except Exception:
			return {'err': ''.join (traceback.format_exception (*sys.exc_info ())).replace ('  ', '&emsp;').strip ().split ('\n')}

#...............................................................................................
_month_name = (None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

if __name__ == '__main__':
	try:
		opts, argv = getopt.getopt (sys.argv [1:], '', ['help', 'debug', 'nobrowser', 'sympyEI'])

		if ('--help', '') in opts:
			print (_HELP.strip ())
			sys.exit (0)

		if not _SYMPAD_CHILD:
			args      = [sys.executable] + sys.argv
			first_run = '1'

			while 1:
				ret       = subprocess.run (args, env = {**os.environ, 'SYMPAD_CHILD': '1', 'SYMPAD_FIRST_RUN': first_run})
				first_run = ''

				if ret.returncode != 0:
					sys.exit (0)

		if ('--debug', '') in opts:
			os.environ ['SYMPAD_DEBUG'] = '1'

		if ('--sympyEI', '') in opts:
			sast.sympyEI ()

		if not argv:
			host, port = _DEFAULT_ADDRESS
		else:
			host, port = (re.split (r'(?<=\]):' if argv [0].startswith ('[') else ':', argv [0]) + [_DEFAULT_ADDRESS [1]]) [:2]
			host, port = host.strip ('[]'), int (port)

		watch   = ('sympad.py',) if _RUNNING_AS_SINGLE_SCRIPT else ('lalr1.py', 'sparser.py', 'sym.py', 'server.py')
		tstamps = [os.stat (fnm).st_mtime for fnm in watch]
		httpd   = HTTPServer ((host, port), Handler) # ThreadingHTTPServer ((host, port), Handler)
		thread  = threading.Thread (target = httpd.serve_forever, daemon = True)

		thread.start ()

		def log_message (msg):
			y, m, d, hh, mm, ss, _, _, _ = time.localtime (time.time ())

			sys.stderr.write (f'{httpd.server_address [0]} - - ' \
					f'[{"%02d/%3s/%04d %02d:%02d:%02d" % (d, _month_name [m], y, hh, mm, ss)}] {msg}\n')

		if _SYMPAD_FIRST_RUN:
			print ('Sympad server running. If a browser window does not automatically open to the address below then try navigating to that URL manually.\n')

		log_message (f'Serving at http://{httpd.server_address [0]}:{httpd.server_address [1]}/')

		if os.environ.get ('SYMPAD_FIRST_RUN') and ('--nobrowser', '') not in opts:
			webbrowser.open (f'http://{httpd.server_address [0] if httpd.server_address [0] != "0.0.0.0" else "127.0.0.1"}:{httpd.server_address [1]}/')

		while 1:
			time.sleep (0.5)

			if [os.stat (fnm).st_mtime for fnm in watch] != tstamps:
				log_message ('Files changed, restarting...')
				sys.exit (0)

	except OSError as e:
		if e.errno != 98:
			raise

		print (f'Port {port} seems to be in use, try specifying different port as a command line parameter, e.g. localhost:8001')

	except KeyboardInterrupt:
		sys.exit (0)

	sys.exit (-1)
