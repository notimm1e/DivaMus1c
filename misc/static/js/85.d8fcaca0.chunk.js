(this.webpackJsonpmizaweb2=this.webpackJsonpmizaweb2||[]).push([[85],{164:function(e,a){var n="[0-9](_*[0-9])*",t="\\.(".concat(n,")"),c="[0-9a-fA-F](_*[0-9a-fA-F])*",s={className:"number",variants:[{begin:"(\\b(".concat(n,")((").concat(t,")|\\.)?|(").concat(t,"))")+"[eE][+-]?(".concat(n,")[fFdD]?\\b")},{begin:"\\b(".concat(n,")((").concat(t,")[fFdD]?\\b|\\.([fFdD]\\b)?)")},{begin:"(".concat(t,")[fFdD]?\\b")},{begin:"\\b(".concat(n,")[fFdD]\\b")},{begin:"\\b0[xX]((".concat(c,")\\.?|(").concat(c,")?\\.(").concat(c,"))")+"[pP][+-]?(".concat(n,")[fFdD]?\\b")},{begin:"\\b(0|[1-9](_*[0-9])*)[lL]?\\b"},{begin:"\\b0[xX](".concat(c,")[lL]?\\b")},{begin:"\\b0(_*[0-7])*[lL]?\\b"},{begin:"\\b0[bB][01](_*[01])*[lL]?\\b"}],relevance:0};function i(e,a,n){return-1===n?"":e.replace(a,(function(t){return i(e,a,n-1)}))}e.exports=function(e){var a="[\xc0-\u02b8a-zA-Z_$][\xc0-\u02b8a-zA-Z_$0-9]*",n=a+i("(?:<"+a+"~~~(?:\\s*,\\s*"+a+"~~~)*>)?",/~~~/g,2),t={keyword:["synchronized","abstract","private","var","static","if","const ","for","while","strictfp","finally","protected","import","native","final","void","enum","else","break","transient","catch","instanceof","volatile","case","assert","package","default","public","try","switch","continue","throws","protected","public","private","module","requires","exports","do"],literal:["false","true","null"],type:["char","boolean","long","float","int","byte","short","double"],built_in:["super","this"]},c={className:"meta",begin:"@"+a,contains:[{begin:/\(/,end:/\)/,contains:["self"]}]},o={className:"params",begin:/\(/,end:/\)/,keywords:t,relevance:0,contains:[e.C_BLOCK_COMMENT_MODE],endsParent:!0};return{name:"Java",aliases:["jsp"],keywords:t,illegal:/<\/|#/,contains:[e.COMMENT("/\\*\\*","\\*/",{relevance:0,contains:[{begin:/\w+@/,relevance:0},{className:"doctag",begin:"@[A-Za-z]+"}]}),{begin:/import java\.[a-z]+\./,keywords:"import",relevance:2},e.C_LINE_COMMENT_MODE,e.C_BLOCK_COMMENT_MODE,e.APOS_STRING_MODE,e.QUOTE_STRING_MODE,{match:[/\b(?:class|interface|enum|extends|implements|new)/,/\s+/,a],className:{1:"keyword",3:"title.class"}},{begin:[a,/\s+/,a,/\s+/,/=/],className:{1:"type",3:"variable",5:"operator"}},{begin:[/record/,/\s+/,a],className:{1:"keyword",3:"title.class"},contains:[o,e.C_LINE_COMMENT_MODE,e.C_BLOCK_COMMENT_MODE]},{beginKeywords:"new throw return else",relevance:0},{begin:["(?:"+n+"\\s+)",e.UNDERSCORE_IDENT_RE,/\s*(?=\()/],className:{2:"title.function"},keywords:t,contains:[{className:"params",begin:/\(/,end:/\)/,keywords:t,relevance:0,contains:[c,e.APOS_STRING_MODE,e.QUOTE_STRING_MODE,s,e.C_BLOCK_COMMENT_MODE]},e.C_LINE_COMMENT_MODE,e.C_BLOCK_COMMENT_MODE]},s,c]}}}}]);
//# sourceMappingURL=85.d8fcaca0.chunk.js.map