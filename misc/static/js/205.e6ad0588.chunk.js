(this.webpackJsonpmizaweb2=this.webpackJsonpmizaweb2||[]).push([[205,17],{587:function(e,n,i){!function e(){e.warned||(e.warned=!0,console.log('Deprecation (warning): Using file extension in specifier is deprecated, use "highlight.js/lib/languages/aspectj" instead of "highlight.js/lib/languages/aspectj.js"'))}(),e.exports=i(96)},96:function(e,n){function i(e){return e?"string"===typeof e?e:e.source:null}function t(){for(var e=arguments.length,n=new Array(e),t=0;t<e;t++)n[t]=arguments[t];var a=n.map((function(e){return i(e)})).join("");return a}e.exports=function(e){var n=["false","synchronized","int","abstract","float","private","char","boolean","static","null","if","const","for","true","while","long","throw","strictfp","finally","protected","import","native","final","return","void","enum","else","extends","implements","break","transient","new","catch","instanceof","byte","super","volatile","case","assert","short","package","default","double","public","try","this","switch","continue","throws","privileged","aspectOf","adviceexecution","proceed","cflowbelow","cflow","initialization","preinitialization","staticinitialization","withincode","target","within","execution","getWithinTypeName","handler","thisJoinPoint","thisJoinPointStaticPart","thisEnclosingJoinPointStaticPart","declare","parents","warning","error","soft","precedence","thisAspectInstance"],i=["get","set","args","call"];return{name:"AspectJ",keywords:n,illegal:/<\/|#/,contains:[e.COMMENT(/\/\*\*/,/\*\//,{relevance:0,contains:[{begin:/\w+@/,relevance:0},{className:"doctag",begin:/@[A-Za-z]+/}]}),e.C_LINE_COMMENT_MODE,e.C_BLOCK_COMMENT_MODE,e.APOS_STRING_MODE,e.QUOTE_STRING_MODE,{className:"class",beginKeywords:"aspect",end:/[{;=]/,excludeEnd:!0,illegal:/[:;"\[\]]/,contains:[{beginKeywords:"extends implements pertypewithin perthis pertarget percflowbelow percflow issingleton"},e.UNDERSCORE_TITLE_MODE,{begin:/\([^\)]*/,end:/[)]+/,keywords:n.concat(i),excludeEnd:!1}]},{className:"class",beginKeywords:"class interface",end:/[{;=]/,excludeEnd:!0,relevance:0,keywords:"class interface",illegal:/[:"\[\]]/,contains:[{beginKeywords:"extends implements"},e.UNDERSCORE_TITLE_MODE]},{beginKeywords:"pointcut after before around throwing returning",end:/[)]/,excludeEnd:!1,illegal:/["\[\]]/,contains:[{begin:t(e.UNDERSCORE_IDENT_RE,/\s*\(/),returnBegin:!0,contains:[e.UNDERSCORE_TITLE_MODE]}]},{begin:/[:]/,returnBegin:!0,end:/[{;]/,relevance:0,excludeEnd:!1,keywords:n,illegal:/["\[\]]/,contains:[{begin:t(e.UNDERSCORE_IDENT_RE,/\s*\(/),keywords:n.concat(i),relevance:0},e.QUOTE_STRING_MODE]},{beginKeywords:"new throw",relevance:0},{className:"function",begin:/\w+ +\w+(\.\w+)?\s*\([^\)]*\)\s*((throws)[\w\s,]+)?[\{;]/,returnBegin:!0,end:/[{;=]/,keywords:n,excludeEnd:!0,contains:[{begin:t(e.UNDERSCORE_IDENT_RE,/\s*\(/),returnBegin:!0,relevance:0,contains:[e.UNDERSCORE_TITLE_MODE]},{className:"params",begin:/\(/,end:/\)/,relevance:0,keywords:n,contains:[e.APOS_STRING_MODE,e.QUOTE_STRING_MODE,e.C_NUMBER_MODE,e.C_BLOCK_COMMENT_MODE]},e.C_LINE_COMMENT_MODE,e.C_BLOCK_COMMENT_MODE]},e.C_NUMBER_MODE,{className:"meta",begin:/@[A-Za-z]+/}]}}}}]);
//# sourceMappingURL=205.e6ad0588.chunk.js.map