(this.webpackJsonpmizaweb2=this.webpackJsonpmizaweb2||[]).push([[363,175],{254:function(e,n){var a="[A-Za-z$_][0-9A-Za-z$_]*",t=["as","in","of","if","for","while","finally","var","new","function","do","return","void","else","break","catch","instanceof","with","throw","case","default","try","switch","continue","typeof","delete","let","yield","const","class","debugger","async","await","static","import","from","export","extends"],s=["true","false","null","undefined","NaN","Infinity"],r=["Intl","DataView","Number","Math","Date","String","RegExp","Object","Function","Boolean","Error","Symbol","Set","Map","WeakSet","WeakMap","Proxy","Reflect","JSON","Promise","Float64Array","Int16Array","Int32Array","Int8Array","Uint16Array","Uint32Array","Float32Array","Array","Uint8Array","Uint8ClampedArray","ArrayBuffer","BigInt64Array","BigUint64Array","BigInt"],c=["EvalError","InternalError","RangeError","ReferenceError","SyntaxError","TypeError","URIError"],i=["setInterval","setTimeout","clearInterval","clearTimeout","require","exports","eval","isFinite","isNaN","parseFloat","parseInt","decodeURI","decodeURIComponent","encodeURI","encodeURIComponent","escape","unescape"],o=["arguments","this","super","console","window","document","localStorage","module","global"],l=[].concat(i,r,c);function b(e){return e?"string"===typeof e?e:e.source:null}function d(e){return u("(?=",e,")")}function u(){for(var e=arguments.length,n=new Array(e),a=0;a<e;a++)n[a]=arguments[a];var t=n.map((function(e){return b(e)})).join("");return t}function g(e){var n=a,b="<>",g="</>",m={begin:/<[A-Za-z0-9\\._:-]+/,end:/\/[A-Za-z0-9\\._:-]+>|\/>/,isTrulyOpeningTag:function(e,n){var a=e[0].length+e.index,t=e.input[a];"<"!==t?">"===t&&(function(e,n){var a=n.after,t="</"+e[0].slice(1);return-1!==e.input.indexOf(t,a)}(e,{after:a})||n.ignoreMatch()):n.ignoreMatch()}},f={$pattern:a,keyword:t,literal:s,built_in:l,"variable.language":o},p="[0-9](_?[0-9])*",E="\\.(".concat(p,")"),y="0|[1-9](_?[0-9])*|0[0-7]*[89][0-9]*",v={className:"number",variants:[{begin:"(\\b(".concat(y,")((").concat(E,")|\\.)?|(").concat(E,"))")+"[eE][+-]?(".concat(p,")\\b")},{begin:"\\b(".concat(y,")\\b((").concat(E,")\\b|\\.)?|(").concat(E,")\\b")},{begin:"\\b(0|[1-9](_?[0-9])*)n\\b"},{begin:"\\b0[xX][0-9a-fA-F](_?[0-9a-fA-F])*n?\\b"},{begin:"\\b0[bB][0-1](_?[0-1])*n?\\b"},{begin:"\\b0[oO][0-7](_?[0-7])*n?\\b"},{begin:"\\b0[0-7]+n?\\b"}],relevance:0},A={className:"subst",begin:"\\$\\{",end:"\\}",keywords:f,contains:[]},N={begin:"html`",end:"",starts:{end:"`",returnEnd:!1,contains:[e.BACKSLASH_ESCAPE,A],subLanguage:"xml"}},_={begin:"css`",end:"",starts:{end:"`",returnEnd:!1,contains:[e.BACKSLASH_ESCAPE,A],subLanguage:"css"}},h={className:"string",begin:"`",end:"`",contains:[e.BACKSLASH_ESCAPE,A]},w={className:"comment",variants:[e.COMMENT(/\/\*\*(?!\/)/,"\\*/",{relevance:0,contains:[{begin:"(?=@[A-Za-z]+)",relevance:0,contains:[{className:"doctag",begin:"@[A-Za-z]+"},{className:"type",begin:"\\{",end:"\\}",excludeEnd:!0,excludeBegin:!0,relevance:0},{className:"variable",begin:n+"(?=\\s*(-)|$)",endsParent:!0,relevance:0},{begin:/(?=[^\n])\s/,relevance:0}]}]}),e.C_BLOCK_COMMENT_MODE,e.C_LINE_COMMENT_MODE]},S=[e.APOS_STRING_MODE,e.QUOTE_STRING_MODE,N,_,h,v,e.REGEXP_MODE];A.contains=S.concat({begin:/\{/,end:/\}/,keywords:f,contains:["self"].concat(S)});var x=[].concat(w,A.contains),O=x.concat([{begin:/\(/,end:/\)/,keywords:f,contains:["self"].concat(x)}]),R={className:"params",begin:/\(/,end:/\)/,excludeBegin:!0,excludeEnd:!0,keywords:f,contains:O},I={variants:[{match:[/class/,/\s+/,n],scope:{1:"keyword",3:"title.class"}},{match:[/extends/,/\s+/,u(n,"(",u(/\./,n),")*")],scope:{1:"keyword",3:"title.class.inherited"}}]},T={relevance:0,match:/\b[A-Z][a-z]+([A-Z][a-z]+)*/,className:"title.class",keywords:{_:[].concat(r,c)}},k={variants:[{match:[/function/,/\s+/,n,/(?=\s*\()/]},{match:[/function/,/\s*(?=\()/]}],className:{1:"keyword",3:"title.function"},label:"func.def",contains:[R],illegal:/%/};var M,C={match:u(/\b/,(M=[].concat(i,["super"]),u("(?!",M.join("|"),")")),n,d(/\(/)),className:"title.function",relevance:0},B={begin:u(/\./,d(u(n,/(?![0-9A-Za-z$_(])/))),end:n,excludeBegin:!0,keywords:"prototype",className:"property",relevance:0},D={match:[/get|set/,/\s+/,n,/(?=\()/],className:{1:"keyword",3:"title.function"},contains:[{begin:/\(\)/},R]},U="(\\([^()]*(\\([^()]*(\\([^()]*\\)[^()]*)*\\)[^()]*)*\\)|"+e.UNDERSCORE_IDENT_RE+")\\s*=>",z={match:[/const|var|let/,/\s+/,n,/\s*/,/=\s*/,d(U)],className:{1:"keyword",3:"title.function"},contains:[R]};return{name:"Javascript",aliases:["js","jsx","mjs","cjs"],keywords:f,exports:{PARAMS_CONTAINS:O},illegal:/#(?![$_A-z])/,contains:[e.SHEBANG({label:"shebang",binary:"node",relevance:5}),{label:"use_strict",className:"meta",relevance:10,begin:/^\s*['"]use (strict|asm)['"]/},e.APOS_STRING_MODE,e.QUOTE_STRING_MODE,N,_,h,w,v,T,{className:"attr",begin:n+d(":"),relevance:0},z,{begin:"("+e.RE_STARTERS_RE+"|\\b(case|return|throw)\\b)\\s*",keywords:"return throw case",relevance:0,contains:[w,e.REGEXP_MODE,{className:"function",begin:U,returnBegin:!0,end:"\\s*=>",contains:[{className:"params",variants:[{begin:e.UNDERSCORE_IDENT_RE,relevance:0},{className:null,begin:/\(\s*\)/,skip:!0},{begin:/\(/,end:/\)/,excludeBegin:!0,excludeEnd:!0,keywords:f,contains:O}]}]},{begin:/,/,relevance:0},{match:/\s+/,relevance:0},{variants:[{begin:b,end:g},{begin:m.begin,"on:begin":m.isTrulyOpeningTag,end:m.end}],subLanguage:"xml",contains:[{begin:m.begin,end:m.end,skip:!0,contains:["self"]}]}]},k,{beginKeywords:"while if switch catch for"},{begin:"\\b(?!function)"+e.UNDERSCORE_IDENT_RE+"\\([^()]*(\\([^()]*(\\([^()]*\\)[^()]*)*\\)[^()]*)*\\)\\s*\\{",returnBegin:!0,label:"func.def",contains:[R,e.inherit(e.TITLE_MODE,{begin:n,className:"title.function"})]},{match:/\.\.\./,relevance:0},B,{match:"\\$"+n,relevance:0},{match:[/\bconstructor(?=\s*\()/],className:{1:"title.function"},contains:[R]},C,{relevance:0,match:/\b[A-Z][A-Z_0-9]+\b/,className:"variable.constant"},I,D,{match:/\$[(.]/}]}}e.exports=function(e){var n={$pattern:a,keyword:t.concat(["type","namespace","typedef","interface","public","private","protected","implements","declare","abstract","readonly"]),literal:s,built_in:l.concat(["any","void","number","boolean","string","object","never","enum"]),"variable.language":o},r={className:"meta",begin:"@[A-Za-z$_][0-9A-Za-z$_]*"},c=function(e,n,a){var t=e.contains.findIndex((function(e){return e.label===n}));if(-1===t)throw new Error("can not find mode to replace");e.contains.splice(t,1,a)},i=g(e);return Object.assign(i.keywords,n),i.exports.PARAMS_CONTAINS.push(r),i.contains=i.contains.concat([r,{beginKeywords:"namespace",end:/\{/,excludeEnd:!0},{beginKeywords:"interface",end:/\{/,excludeEnd:!0,keywords:"interface extends"}]),c(i,"shebang",e.SHEBANG()),c(i,"use_strict",{className:"meta",relevance:10,begin:/^\s*['"]use strict['"]/}),i.contains.find((function(e){return"func.def"===e.label})).relevance=0,Object.assign(i,{name:"TypeScript",aliases:["ts","tsx"]}),i}},750:function(e,n,a){!function e(){e.warned||(e.warned=!0,console.log('Deprecation (warning): Using file extension in specifier is deprecated, use "highlight.js/lib/languages/typescript" instead of "highlight.js/lib/languages/typescript.js"'))}(),e.exports=a(254)}}]);
//# sourceMappingURL=363.d5359124.chunk.js.map