(this.webpackJsonpmizaweb2=this.webpackJsonpmizaweb2||[]).push([[30],{109:function(e,a){e.exports=function(e){var a=["assembly","module","package","import","alias","class","interface","object","given","value","assign","void","function","new","of","extends","satisfies","abstracts","in","out","return","break","continue","throw","assert","dynamic","if","else","switch","case","for","while","try","catch","finally","then","let","this","outer","super","is","exists","nonempty"],s={className:"subst",excludeBegin:!0,excludeEnd:!0,begin:/``/,end:/``/,keywords:a,relevance:10},n=[{className:"string",begin:'"""',end:'"""',relevance:10},{className:"string",begin:'"',end:'"',contains:[s]},{className:"string",begin:"'",end:"'"},{className:"number",begin:"#[0-9a-fA-F_]+|\\$[01_]+|[0-9_]+(?:\\.[0-9_](?:[eE][+-]?\\d+)?)?[kMGTPmunpf]?",relevance:0}];return s.contains=n,{name:"Ceylon",keywords:{keyword:a.concat(["shared","abstract","formal","default","actual","variable","late","native","deprecated","final","sealed","annotation","suppressWarnings","small"]),meta:["doc","by","license","see","throws","tagged"]},illegal:"\\$[^01]|#[^0-9a-fA-F]",contains:[e.C_LINE_COMMENT_MODE,e.COMMENT("/\\*","\\*/",{contains:["self"]}),{className:"meta",begin:'@[a-z]\\w*(?::"[^"]*")?'}].concat(n)}}}}]);
//# sourceMappingURL=30.b8c7dbbf.chunk.js.map