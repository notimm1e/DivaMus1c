(this.webpackJsonpmizaweb2=this.webpackJsonpmizaweb2||[]).push([[103],{182:function(e,i){e.exports=function(e){var i={className:"variable",variants:[{begin:"\\$\\("+e.UNDERSCORE_IDENT_RE+"\\)",contains:[e.BACKSLASH_ESCAPE]},{begin:/\$[@%<?\^\+\*]/}]},a={className:"string",begin:/"/,end:/"/,contains:[e.BACKSLASH_ESCAPE,i]},n={className:"variable",begin:/\$\([\w-]+\s/,end:/\)/,keywords:{built_in:"subst patsubst strip findstring filter filter-out sort word wordlist firstword lastword dir notdir suffix basename addsuffix addprefix join wildcard realpath abspath error warning shell origin flavor foreach if or and call eval file value"},contains:[i]},s={begin:"^"+e.UNDERSCORE_IDENT_RE+"\\s*(?=[:+?]?=)"},r={className:"section",begin:/^[^\s]+:/,end:/$/,contains:[i]};return{name:"Makefile",aliases:["mk","mak","make"],keywords:{$pattern:/[\w-]+/,keyword:"define endef undefine ifdef ifndef ifeq ifneq else endif include -include sinclude override export unexport private vpath"},contains:[e.HASH_COMMENT_MODE,i,a,n,s,{className:"meta",begin:/^\.PHONY:/,end:/$/,keywords:{$pattern:/[\.\w]+/,keyword:".PHONY"}},r]}}}}]);
//# sourceMappingURL=103.acd2738d.chunk.js.map