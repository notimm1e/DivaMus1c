(this.webpackJsonpmizaweb2=this.webpackJsonpmizaweb2||[]).push([[133],{212:function(e,t){function a(e){return e?"string"===typeof e?e:e.source:null}function r(e){return n("(?=",e,")")}function n(){for(var e=arguments.length,t=new Array(e),r=0;r<e;r++)t[r]=arguments[r];var n=t.map((function(e){return a(e)})).join("");return n}function s(e){var t=e[e.length-1];return"object"===typeof t&&t.constructor===Object?(e.splice(e.length-1,1),t):{}}function o(){for(var e=arguments.length,t=new Array(e),r=0;r<e;r++)t[r]=arguments[r];var n=s(t),o="("+(n.capture?"":"?:")+t.map((function(e){return a(e)})).join("|")+")";return o}e.exports=function(e){var t=["displayHeight","displayWidth","mouseY","mouseX","mousePressed","pmouseX","pmouseY","key","keyCode","pixels","focused","frameCount","frameRate","height","width","size","createGraphics","beginDraw","createShape","loadShape","PShape","arc","ellipse","line","point","quad","rect","triangle","bezier","bezierDetail","bezierPoint","bezierTangent","curve","curveDetail","curvePoint","curveTangent","curveTightness","shape","shapeMode","beginContour","beginShape","bezierVertex","curveVertex","endContour","endShape","quadraticVertex","vertex","ellipseMode","noSmooth","rectMode","smooth","strokeCap","strokeJoin","strokeWeight","mouseClicked","mouseDragged","mouseMoved","mousePressed","mouseReleased","mouseWheel","keyPressed","keyPressedkeyReleased","keyTyped","print","println","save","saveFrame","day","hour","millis","minute","month","second","year","background","clear","colorMode","fill","noFill","noStroke","stroke","alpha","blue","brightness","color","green","hue","lerpColor","red","saturation","modelX","modelY","modelZ","screenX","screenY","screenZ","ambient","emissive","shininess","specular","add","createImage","beginCamera","camera","endCamera","frustum","ortho","perspective","printCamera","printProjection","cursor","frameRate","noCursor","exit","loop","noLoop","popStyle","pushStyle","redraw","binary","boolean","byte","char","float","hex","int","str","unbinary","unhex","join","match","matchAll","nf","nfc","nfp","nfs","split","splitTokens","trim","append","arrayCopy","concat","expand","reverse","shorten","sort","splice","subset","box","sphere","sphereDetail","createInput","createReader","loadBytes","loadJSONArray","loadJSONObject","loadStrings","loadTable","loadXML","open","parseXML","saveTable","selectFolder","selectInput","beginRaw","beginRecord","createOutput","createWriter","endRaw","endRecord","PrintWritersaveBytes","saveJSONArray","saveJSONObject","saveStream","saveStrings","saveXML","selectOutput","popMatrix","printMatrix","pushMatrix","resetMatrix","rotate","rotateX","rotateY","rotateZ","scale","shearX","shearY","translate","ambientLight","directionalLight","lightFalloff","lights","lightSpecular","noLights","normal","pointLight","spotLight","image","imageMode","loadImage","noTint","requestImage","tint","texture","textureMode","textureWrap","blend","copy","filter","get","loadPixels","set","updatePixels","blendMode","loadShader","PShaderresetShader","shader","createFont","loadFont","text","textFont","textAlign","textLeading","textMode","textSize","textWidth","textAscent","textDescent","abs","ceil","constrain","dist","exp","floor","lerp","log","mag","map","max","min","norm","pow","round","sq","sqrt","acos","asin","atan","atan2","cos","degrees","radians","sin","tan","noise","noiseDetail","noiseSeed","random","randomGaussian","randomSeed"],a=e.IDENT_RE,s={variants:[{match:n(o.apply(void 0,t),r(/\s*\(/)),className:"built_in"},{relevance:0,match:n(/\b(?!for|if|while)/,a,r(/\s*\(/)),className:"title.function"}]},i={match:[/new\s+/,a],className:{1:"keyword",2:"class.title"}},l={relevance:0,match:[/\./,a],className:{2:"property"}},c={variants:[{match:[/class/,/\s+/,a,/\s+/,/extends/,/\s+/,a]},{match:[/class/,/\s+/,a]}],className:{1:"keyword",3:"title.class",5:"keyword",7:"title.class.inherited"}};return{name:"Processing",aliases:["pde"],keywords:{keyword:[].concat(["abstract","assert","break","case","catch","const","continue","default","else","enum","final","finally","for","if","import","instanceof","long","native","new","package","private","private","protected","protected","public","public","return","static","strictfp","switch","synchronized","throw","throws","transient","try","void","volatile","while"]),literal:"P2D P3D HALF_PI PI QUARTER_PI TAU TWO_PI null true false",title:"setup draw",variable:"super this",built_in:[].concat(t,["BufferedReader","PVector","PFont","PImage","PGraphics","HashMap","String","Array","FloatDict","ArrayList","FloatList","IntDict","IntList","JSONArray","JSONObject","Object","StringDict","StringList","Table","TableRow","XML"]),type:["boolean","byte","char","color","double","float","int","long","short"]},contains:[c,i,s,l,e.C_LINE_COMMENT_MODE,e.C_BLOCK_COMMENT_MODE,e.APOS_STRING_MODE,e.QUOTE_STRING_MODE,e.C_NUMBER_MODE]}}}}]);
//# sourceMappingURL=133.1c7d8106.chunk.js.map